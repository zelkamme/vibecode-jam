from fastapi import FastAPI, Depends, HTTPException, APIRouter, UploadFile, File, Form 
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import List, Optional
import shutil
import json
import logging
import tempfile
import os
from contextlib import asynccontextmanager

# Docker SDK
from docker import from_env
from docker.client import DockerClient

# DB imports
from backend.database import create_db_and_tables, get_session
from backend.models import User, Question, Report, TestSession, Vacancy, UserAnswer

from backend.llm.qa_gen import generate_theory_qa, generate_theory_check
from backend.llm.helper_ai import generate_helper_ai  
from ollama import Client as OllamaClient # <--- ИСПРАВЛЕНО: Для работы с LLM (импорт из библиотеки ollama)
from backend.llm.code_review import generate_code_review
from backend.llm.unit_tests_gen import generate_unittests
# --- Добавь это после импортов ---
REDIS_HOST = "localhost"
REDIS_PORT = 6379
# Создаем папку для загрузок, если нет
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)

theory_session_state = {} # ПЕРЕМЕЩЕНО ВВЕРХ! 
# Инициализация Ollama Client
ollama_client: Optional[OllamaClient] = None
try:
    # --- ИСПОЛЬЗОВАНИЕ РЕАЛЬНОГО Ollama Client ---
    # Убедитесь, что ollama установлен: pip install ollama
    # Убедитесь, что ollama-сервер запущен (например, docker run ollama/ollama)
    ollama_client = OllamaClient(host="http://localhost:11434") # Убедитесь, что порт правильный

    # Проверка доступности модели (опционально, для лучшей диагностики)
    try:
         ollama_client.show('gemma3:12b') # Проверка наличия модели
    except Exception as e:
         logging.warning(f"Ollama model 'gemma3:12b' not found or Ollama server issue: {e}")
         # Здесь можно либо использовать Mock, либо выкинуть ошибку

except Exception as e:
    logging.warning(f"Ollama client not initialized: {e}")
    # В случае ошибки, fallback на Mock (для отладки без Ollama)
    class MockOllamaClient:
        def chat(self, model, messages, stream):
            mock_result = {
                "score": 1, 
                "explanation": "LLM-сервис недоступен (Mock).",
                "follow_up_question": "NEXT_QUESTION"
            }
            if not stream:
                return {'message': {'content': json.dumps(mock_result)}}
            else:
                return [{'message': {'content': json.dumps(mock_result)}}]
    ollama_client = MockOllamaClient()


# Хранение состояния интервью (ЗАГЛУШКА: в реальном проекте - Redis/DB)
theory_session_state = {} 
class TheoryStartRequest(BaseModel):
    level: str
    user_id: int 
# ---------------- APP + LIFESPAN ------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- ROUTER ------------------
router = APIRouter()
docker_client: DockerClient = from_env()

# ---------------- MODELS ------------------
# Модели для запроса/ответа
class TheoryChatResponse(BaseModel):
    message: str
    isFinished: bool = False
    
# Найдите эту модель в main.py и добавьте user_id
class TheoryChatMessage(BaseModel):
    message: str
    history: List[dict]
    user_id: int  # <--- ДОБАВЛЕНО ПОЛЕ

class UserAnswerIn(BaseModel):
    user_id: int
    question_id: int
    answer: str # Ответ (для Theory) или ID варианта (для Psy)
    is_correct: Optional[bool] = None # Для Psy
    score: int = 0 # Балл (1/0 для Psy, 1-10 для Theory)


class VacancyUpdate(BaseModel):
    title: Optional[str] = None
    level: Optional[str] = None
    language: Optional[str] = None
    skills: Optional[str] = None
    salary_range: Optional[str] = None
    is_active: Optional[bool] = None

class QuestionUpdate(BaseModel):
    text: str

class VacancyCreateRequest(BaseModel):
    title: str
    level: str
    language: str
    skills: str
    salary_range: Optional[str] = ""

class RegisterRequest(BaseModel):
    username: str
    vacancy_id: int

class TaskCreateRequest(BaseModel):
    title: str
    description: str
    level: str
    envId: str
    type: str
    referenceAnswer: Optional[str] = None
    files: list 

class RunCodeRequest(BaseModel):
    code: str
    language: Optional[str] = None # Можно передать явно с фронта
    task_id: Optional[int] = None
    user_id: Optional[int] = None  # <--- ВАЖНО: нужно знать, кто запускает

class ChatMessage(BaseModel):
    message: str
    history: List[dict]
    user_id: Optional[int] = None
    question_id: Optional[int] = None
    # Новые поля для кодинга:
    code_context: Optional[str] = None 
    task_id: Optional[int] = None

class IntegrityPayload(BaseModel):
    user_id: int
    focusLost: int
    mouseLeftWindow: int
    largePastes: int
    codeHistory: List[str]
    coding_task_id: Optional[int] = None  # <--- У ТЕБЯ НЕТ ЭТОЙ СТРОКИ. ДОБАВЬ ЕЁ.

# ---------------- ENDPOINTS ------------------

# ДОБАВЛЕНИЕ НОВОГО ЭНДПОИНТА
@app.post("/api/answers")
def save_answer(data: UserAnswerIn, session: Session = Depends(get_session)):
    # 1. Находим активную сессию (или создаем, если ее нет)
    current_session = session.exec(
        select(TestSession)
        .where(TestSession.user_id == data.user_id)
        .where(TestSession.status == "started")
    ).first()
    
    if not current_session:
        current_session = TestSession(user_id=data.user_id, status="started")
        session.add(current_session)
        session.commit()
        session.refresh(current_session)
        
    # 2. Создаем/обновляем ответ
    answer_entry = UserAnswer(
        session_id=current_session.id,
        question_id=data.question_id,
        user_answer_text=data.answer,
        is_correct=data.is_correct,
        score=data.score
    )
    
    session.add(answer_entry)
    session.commit()
    session.refresh(answer_entry)
    
    return {"status": "ok", "answer_id": answer_entry.id}

@app.delete("/api/vacancies/{vacancy_id}")
def delete_vacancy(vacancy_id: int, session: Session = Depends(get_session)):
    vac = session.get(Vacancy, vacancy_id)
    if not vac:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    session.delete(vac)
    session.commit()
    return {"status": "deleted"}

@app.put("/api/vacancies/{vacancy_id}")
def update_vacancy(vacancy_id: int, data: VacancyUpdate, session: Session = Depends(get_session)):
    vac = session.get(Vacancy, vacancy_id)
    if not vac:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    
    hero_data = data.dict(exclude_unset=True)
    for key, value in hero_data.items():
        setattr(vac, key, value)
        
    session.add(vac)
    session.commit()
    session.refresh(vac)
    return vac

@app.get("/api/vacancies")
def get_vacancies(session: Session = Depends(get_session)):
    vacs = session.exec(select(Vacancy)).all()
    # Если пусто, создадим дефолтную, чтобы фронт не падал
    if not vacs:
        vac = Vacancy(title="Python Intern", level="Intern", language="Python", skills="Basic Python")
        session.add(vac)
        session.commit()
        session.refresh(vac)
        return [vac]
    return vacs

@app.post("/api/vacancies")
def create_vacancy(data: VacancyCreateRequest, session: Session = Depends(get_session)):
    vac = Vacancy(
        title=data.title, 
        level=data.level, 
        language=data.language, 
        skills=data.skills,
        salary_range=data.salary_range
    )
    session.add(vac)
    session.commit()
    return {"status": "ok", "id": vac.id}

@app.get("/api/vacancies/{vacancy_id}/preview-tasks")
def preview_vacancy_tasks(vacancy_id: int, session: Session = Depends(get_session)):
    vacancy = session.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    
    # Ищем задачи (Coding и Theory), которые соответствуют уровню вакансии
    # Или уровню "All" (общие вопросы)
    tasks = session.exec(
        select(Question)
        .where((Question.level == vacancy.level) | (Question.level == "All"))
    ).all()
    
    return tasks

@app.post("/api/register")
def register_candidate(
    username: str = Form(...),
    vacancy_id: int = Form(...),
    resume: Optional[UploadFile] = File(None), # Файл не обязателен, но желателен
    session: Session = Depends(get_session)
):
    vacancy = session.get(Vacancy, vacancy_id)
    level = vacancy.level if vacancy else "Intern"
    
    resume_link = None
    
    # Логика сохранения файла
    if resume:
        # Генерируем уникальное имя, чтобы файлы не перезаписывались
        # Например: username_filename.pdf
        safe_filename = f"{username.replace(' ', '_')}_{resume.filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)
            
        resume_link = file_path # Сохраняем путь в переменную

    # Создаем юзера с ссылкой на резюме
    user = User(
        username=username, 
        role="candidate", 
        level=level, 
        vacancy_id=vacancy_id,
        resume_path=resume_link # Записываем в БД
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {"status": "ok", "user_id": user.id, "level": user.level}


# 1. ЗАГРУЗКА SOFT SKILLS ВОПРОСОВ

@app.get("/api/questions/psy")
def get_psy_questions(session: Session = Depends(get_session)):
    # Берем все вопросы типа 'psy'
    questions = session.exec(select(Question).where(Question.type == "psy")).all()
    
    result = []
    for q in questions:
        options = []
        # Пытаемся достать варианты ответов из поля files_json
        if q.files_json:
            try:
                options = json.loads(q.files_json)
            except Exception as e:
                print(f"Ошибка парсинга JSON для вопроса {q.id}: {e}")
                options = [] # Если JSON битый, отдаем пустой список
        
        result.append({
            "id": q.id,
            "questionText": q.text,
            "answerOptions": options
        })
    
    return result


# 1. ПОЛУЧЕНИЕ ОДНОЙ ЗАДАЧИ (Полные данные для редактора)
@app.get("/api/questions/{question_id}")
def get_question_detail(question_id: int, session: Session = Depends(get_session)):
    q = session.get(Question, question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Разделяем Текст на Заголовок и Описание
    parts = q.text.split("\n\n", 1)
    title = parts[0]
    desc = parts[1] if len(parts) > 1 else ""

    return {
        "id": q.id,
        "title": title,
        "description": desc,
        "type": q.type,
        "level": q.level,
        "required_tag": q.required_tag,
        "referenceAnswer": q.correct_answer,
        "files": json.loads(q.files_json) if q.files_json else []
    }

# 2. ПОЛНОЕ ОБНОВЛЕНИЕ ЗАДАЧИ (Используем ту же модель TaskCreateRequest)
@app.put("/api/questions/{question_id}")
def update_question_full(
    question_id: int, 
    task_data: TaskCreateRequest, # Используем полную модель
    session: Session = Depends(get_session)
):
    q = session.get(Question, question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    full_text = f"{task_data.title}\n\n{task_data.description}"
    
    req_tag = "python"
    if task_data.envId == "data-science":
        req_tag = "python,pandas"

    # Обновляем поля
    q.text = full_text
    q.type = task_data.type
    q.level = task_data.level
    q.required_tag = req_tag
    q.correct_answer = task_data.referenceAnswer
    q.files_json = json.dumps(task_data.files)

    session.add(q)
    session.commit()
    return {"status": "updated", "id": q.id}

@app.post("/api/tasks")
def create_task(task_data: TaskCreateRequest, session: Session = Depends(get_session)):
    full_text = f"{task_data.title}\n\n{task_data.description}"
    
    req_tag = "python"
    if task_data.envId == "data-science":
        req_tag = "python,pandas"

    new_question = Question(
        text=full_text,
        type=task_data.type,
        level=task_data.level,
        required_tag=req_tag,
        correct_answer=task_data.referenceAnswer,
        files_json=json.dumps(task_data.files)
    )
    session.add(new_question)
    session.commit()
    return {"status": "ok", "id": new_question.id}



@app.post("/api/theory/start", response_model=TheoryChatResponse)
def theory_start(data: TheoryStartRequest, session: Session = Depends(get_session)):
    # 1. Находим теоретический вопрос
    q = session.exec(select(Question).where(Question.type == "theory").where(Question.level == data.level).limit(1)).first()
    
    # Фолбек, если вопросов по уровню нет
    if not q:
         q = session.exec(select(Question).where(Question.type == "theory").limit(1)).first()
         if not q:
            return TheoryChatResponse(message="Ошибка: Вопросов нет в базе.", isFinished=True)

    # 2. Ищем СУЩЕСТВУЮЩУЮ или СОЗДАЕМ НОВУЮ сессию в БД
    db_session = session.exec(
        select(TestSession)
        .where(TestSession.user_id == data.user_id)
        .where(TestSession.status == "started")
        .order_by(TestSession.created_at.desc())
    ).first()

    if not db_session:
       
        db_session = TestSession(user_id=data.user_id, status="started")
        session.add(db_session)
        session.commit()
        session.refresh(db_session)
    else:
        print(f"♻️ Использую существующую сессию {db_session.id} для User {data.user_id}")

    # 3. Сохраняем состояние в RAM. 
    # ВАЖНО: Мы сохраняем db_session.id внутри словаря
    session_key = f"theory_user_{data.user_id}"
    
    theory_session_state[session_key] = {
        "db_session_id": db_session.id,  # <--- ВОТ КЛЮЧЕВОЙ МОМЕНТ
        "current_question_id": q.id,
        "questions_asked": 1,
        "total_score": 0,
        "current_question_text": q.text,
        "current_ideal_answer": q.correct_answer,
        "topic_attempts": 0 
    }

    parts = q.text.split("\n\n", 1)
    formatted_question = f"**Вопрос 1: {parts[0]}**\n\n{parts[1] if len(parts) > 1 else ''}"
    
    return TheoryChatResponse(message=formatted_question)


@app.post("/api/theory/chat", response_model=TheoryChatResponse)
def theory_chat(data: TheoryChatMessage, session: Session = Depends(get_session)):
    # Получаем состояние из RAM по ID пользователя
    session_key = f"theory_user_{data.user_id}" 
    state = theory_session_state.get(session_key)

    if not state:
        return TheoryChatResponse(message="_Ошибка сессии. Обновите страницу и начните заново._", isFinished=True)

    user_answer = data.message
    
    # 1. Спрашиваем LLM оценку
    try:
        # Убедитесь, что ollama_client инициализирован выше в коде
        llm_result = generate_theory_check(
            state["current_question_text"], 
            state["current_ideal_answer"], 
            user_answer, 
            ollama_client
        )
    except Exception as e:
        print(f"Error LLM: {e}")
        llm_result = {"score": 5, "follow_up_question": "NEXT_QUESTION"}

    score = int(llm_result.get("score", 0))
    state["total_score"] += score
    
    # =======================================================
    # 💾 БЛОК СОХРАНЕНИЯ В БАЗУ ДАННЫХ (ЭТОГО НЕ ХВАТАЛО)
    # =======================================================
    try:
        # Достаем ID сессии, который мы сохранили в theory_start
        current_sess_id = state["db_session_id"]
        current_q_id = state["current_question_id"]

        # Проверка на дубликаты (чтобы не записать ответ дважды при лагах)
        existing_answer = session.exec(
            select(UserAnswer)
            .where(UserAnswer.session_id == current_sess_id)
            .where(UserAnswer.question_id == current_q_id)
        ).first()

        if not existing_answer:
            # Создаем новую запись
            db_answer = UserAnswer(
                session_id=current_sess_id,
                question_id=current_q_id,
                user_answer_text=user_answer,
                score=score,            
                is_correct=(score >= 6)
            )
            session.add(db_answer)
            session.commit()
           
        else:
            # Если это уточняющий вопрос - обновляем существующий ответ
            
            if score > existing_answer.score: # Берем лучший балл
                 existing_answer.score = score
            existing_answer.user_answer_text += f" | {user_answer}"
            session.add(existing_answer)
            session.commit()

    except Exception as e:
        print(f"❌ ОШИБКА SQL ПРИ СОХРАНЕНИИ ОТВЕТА: {e}")
    # =======================================================

    # 3. Логика перехода (Follow-up или Next)
    follow_up = llm_result.get("follow_up_question")
    
    if follow_up and follow_up != "NEXT_QUESTION" and state["topic_attempts"] == 0:
        ai_message = f"**Уточняющий вопрос:** {follow_up}"
        state["topic_attempts"] = 1
        theory_session_state[session_key] = state
        return TheoryChatResponse(message=ai_message)

    else:
        # СЛЕДУЮЩИЙ ВОПРОС
        state["questions_asked"] += 1

        # Лимит вопросов (например, 2)
        if state["questions_asked"] > 2: 
            avg_score = state["total_score"] / (state["questions_asked"] - 1)
            final_message = f"**Тест завершен.** Ваш средний балл: **{avg_score:.1f}/10**. Результат сохранен. Переход к кодингу..."
            del theory_session_state[session_key]
            return TheoryChatResponse(message=final_message, isFinished=True)

        # Ищем следующий вопрос
        next_q = session.exec(select(Question).where(Question.type == "theory").offset(state["questions_asked"] - 1).limit(1)).first()
        
        if not next_q:
            avg_score = state["total_score"] / (state["questions_asked"] - 1)
            final_message = f"**Вопросы закончились.** Балл: {avg_score:.1f}/10. Переход..."
            del theory_session_state[session_key]
            return TheoryChatResponse(message=final_message, isFinished=True)
            
        state["current_question_id"] = next_q.id
        state["current_question_text"] = next_q.text
        state["current_ideal_answer"] = next_q.correct_answer
        state["topic_attempts"] = 0
        
        parts = next_q.text.split("\n\n", 1)
        ai_message = f"**Вопрос {state['questions_asked']}: {parts[0]}**\n\n{parts[1] if len(parts) > 1 else ''}"
        
        theory_session_state[session_key] = state
        return TheoryChatResponse(message=ai_message)
    
@app.post("/api/chat")
def handle_coding_chat_assist(payload: ChatMessage, session: Session = Depends(get_session)):
    """AI-помощник в IDE. Анализирует код и дает подсказки."""
    
    user_msg = payload.message
    current_code = payload.code_context or "" # Код из редактора
    task_id = payload.task_id

    # 1. Получаем текст задачи из БД
    task_text = "General Python Task"
    if task_id:
        task_q = session.get(Question, task_id)
        if task_q:
            task_text = task_q.text

    
    
    try:
        # 2. Вызываем твой файл helper_ai.py
        helper_response = generate_helper_ai(
            lang="Python", 
            task=task_text,
            code=current_code,
            user_question=user_msg,
            ollama=ollama_client,
            redis_host=REDIS_HOST,
            redis_port=REDIS_PORT
        )
        
        # helper_ai возвращает dict: {'suggestion': 'Текст подсказки'}
        ai_text = helper_response.get("suggestion", "Я не смог сформулировать подсказку, попробуйте перефразировать.")
        
    except Exception as e:
        print(f"Ошибка Helper AI: {e}")
        ai_text = "Извините, AI-мозги сейчас отключены (ошибка соединения)."

    return {"sender": "ai", "text": ai_text}
    
# backend/main.py

@app.get("/api/task/coding/{level}")
def get_coding_task(
    level: str, 
    user_id: Optional[int] = None, # <-- Принимаем ID пользователя
    session: Session = Depends(get_session)
):
    target_tag = "python" # Дефолтный тег, если юзер не найден
    
    # 1. Если передан user_id, определяем язык по вакансии
    if user_id:
        user = session.get(User, user_id)
        if user and user.vacancy_id:
            vac = session.get(Vacancy, user.vacancy_id)
            if vac:
                # Простая логика маппинга: Вакансия "JavaScript" -> тег "javascript"
                # Приводим к нижнему регистру для надежности
                target_tag = vac.language.lower() 
                print(f"👤 Юзер {user.username} (Вакансия: {vac.title}). Ищем задачи с тегом: {target_tag}")

    # 2. Ищем задачу, совпадающую по УРОВНЮ и ТЕГУ
    # Используем like, чтобы 'python' нашел 'python,pandas'
    query = select(Question).where(Question.type == "coding") \
                            .where(Question.level == level) \
                            .where(Question.required_tag.contains(target_tag))
    
    # Берем первую попавшуюся (или можно random, если добавить func.random())
    q = session.exec(query).first()

    # 3. Если задачи под конкретный язык нет, ищем ЛЮБУЮ задачу этого уровня (Фолбек)
    if not q:
        print(f"⚠️ Задач с тегом {target_tag} для уровня {level} нет. Ищу любую задачу.")
        q = session.exec(
            select(Question)
            .where(Question.type == "coding")
            .where(Question.level == level)
        ).first()

    if not q:
        return {
            "id": 0,
            "title": "Задач нет",
            "description": "Для вашего уровня и языка задач пока не добавлено.",
            "files": []
        }

    parts = q.text.split("\n\n", 1)
    return {
        "id": q.id,
        "title": parts[0],
        "description": parts[1] if len(parts) > 1 else "",
        "files": json.loads(q.files_json) if q.files_json else []
    }


@app.get("/api/candidates")
def get_candidates(session: Session = Depends(get_session)):
    users = session.exec(select(User).where(User.role == "candidate")).all()
    results = []
    
    for user in users:
        # Ищем последнюю сессию
        last_session = session.exec(
            select(TestSession)
            .where(TestSession.user_id == user.id)
            .order_by(TestSession.created_at.desc())
        ).first()
        
        status = "Не начинал"
        score = "-"
        
        if last_session:
            status = "В процессе"
            # Проверяем, есть ли отчет
            if last_session.report:
                status = "Завершено"
                score = f"{last_session.report.final_score}/100"
            elif last_session.status == "completed":
                # Сессия закрыта, но отчета почему-то нет (ошибка или задержка)
                status = "Обработка..."

        # Получаем название вакансии
        vacancy_title = "N/A"
        if user.vacancy_id:
            vac = session.get(Vacancy, user.vacancy_id)
            if vac:
                vacancy_title = vac.title

        results.append({
            "id": user.id,
            "name": user.username,
            "level": user.level,
            "vacancy": vacancy_title, # Добавили поле вакансии
            "status": status,
            "score": score,
            "resume": user.resume_path # Ссылка на файл
        })
    return results


@app.get("/api/candidates/{user_id}")
def get_candidate_detail(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    last_session = session.exec(
        select(TestSession)
        .where(TestSession.user_id == user.id)
        .order_by(TestSession.created_at.desc())
    ).first()

    report_data = {
        "status": "Не начинал",
        "score": 0,
        "integrity_score": 100,
        "telemetry": None
    }

    if last_session:
        report_data["status"] = "В процессе"
        if last_session.status == "completed":
            report_data["status"] = "Завершено"
        
        if last_session.report:
            report_data["score"] = last_session.report.final_score
            report_data["integrity_score"] = last_session.report.integrity_score
            try:
                report_data["telemetry"] = json.loads(last_session.report.telemetry_json)
            except:
                pass

    user_lang = "python"
    if user.vacancy_id:
        vac = session.get(Vacancy, user.vacancy_id)
        if vac:
            user_lang = vac.language
    return {
        "id": user.id,
        "name": user.username,
        "level": user.level,
        "language": user_lang,
        **report_data
    }


# ---------------- RUN CODE (DOCKER) ------------------
LANGUAGE_CONFIG = {
    "Python": {
        "image": "python:3.12-alpine",
        "file_name": "main.py",
        "command": ["python", "/work/main.py"]
    },
    "JavaScript": {
        "image": "node:18-alpine",
        "file_name": "index.js",
        "command": ["node", "/work/index.js"]
    },
    "Java": {
        "image": "openjdk:17-jdk-slim",
        "file_name": "Main.java",
        # Java требует компиляции или запуска одного файла (с Java 11+)
        "command": ["java", "/work/Main.java"] 
    },
    "C++": {
        "image": "gcc:latest",
        "file_name": "main.cpp",
        # Компилируем и запускаем
        "command": ["sh", "-c", "g++ -o /work/app /work/main.cpp && /work/app"]
    },
    "Go": {
        "image": "golang:1.21-alpine",
        "file_name": "main.go",
        "command": ["go", "run", "/work/main.go"]
    }
}

@router.post("/run-code")
async def run_code(payload: RunCodeRequest, session: Session = Depends(get_session)):
    # По умолчанию Python
    target_lang = "Python"

    # АЛГОРИТМ ВЫБОРА ЯЗЫКА:
    # 1. Если передан user_id -> смотрим язык Вакансии
    if payload.user_id:
        user = session.get(User, payload.user_id)
        if user and user.vacancy_id:
            vac = session.get(Vacancy, user.vacancy_id)
            if vac and vac.language in LANGUAGE_CONFIG:
                target_lang = vac.language
                print(f"🕵️ Язык определен по вакансии: {target_lang}")

    # 2. (Опционально) Если задача требует Pandas/DataScience — перекрываем образ Python
    # Это частный случай для Питона, оставляем для совместимости
    env_override = None
    if payload.task_id and target_lang == "Python":
        q = session.get(Question, payload.task_id)
        if q and "pandas" in q.required_tag:
            env_override = "python:3.12-slim" # Образ с библиотеками

    # Получаем конфиг для выбранного языка
    config = LANGUAGE_CONFIG.get(target_lang, LANGUAGE_CONFIG["Python"])
    
    image_to_run = env_override if env_override else config["image"]
    file_name = config["file_name"]
    run_command = config["command"]

    # Создаем временную папку и файл
    temp_dir = tempfile.mkdtemp()
    source_path = os.path.join(temp_dir, file_name)

    with open(source_path, "w", encoding="utf-8") as f:
        f.write(payload.code)

    try:
        container = docker_client.containers.run(
            image=image_to_run,
            command=run_command,
            volumes={temp_dir: {"bind": "/work", "mode": "rw"}},
            network_disabled=True, # Без интернета (безопасность)
            detach=True,
            mem_limit="256m",
            cpu_period=100000,
            cpu_quota=50000,
            remove=True
        )

        exit_code = container.wait()
        logs = container.logs(stdout=True, stderr=True).decode()

        # Очистка
        shutil.rmtree(temp_dir, ignore_errors=True)

        stdout = logs
        stderr = "" if exit_code["StatusCode"] == 0 else logs

        return {"stdout": stdout, "stderr": stderr}

    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        return {"stdout": "", "stderr": f"Docker error: {str(e)}"}


# ---------------- FINISH TEST ------------------

# 2. СОХРАНЕНИЕ РЕЗУЛЬТАТОВ (Обновляем analyze-integrity)

@app.post("/api/analyze-integrity")
def analyze_integrity(payload: IntegrityPayload, session: Session = Depends(get_session)):
    
    
    # 1. Поиск пользователя
    user = session.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 1. Сначала ищем ту сессию, которая сейчас "В ПРОЦЕССЕ" (куда писал theory_chat)
    active_session = session.exec(
        select(TestSession)
        .where(TestSession.user_id == user.id)
        .where(TestSession.status == "started") # <--- Самое важное условие
        .order_by(TestSession.created_at.desc())
    ).first()

    if active_session:
        last_session = active_session
        
    else:
        # 2. Если активной нет (вдруг уже закрыли?), берем самую последнюю по времени (фолбек)
        print(" Активной сессии нет, ищу последнюю архивную...")
        last_session = session.exec(
            select(TestSession)
            .where(TestSession.user_id == user.id)
            .order_by(TestSession.created_at.desc())
        ).first()

    if not last_session:
        print(" ОШИБКА: Сессий вообще нет! Создаю аварийную.")
        last_session = TestSession(user_id=user.id, status="completed")
        session.add(last_session)
        session.commit()
        session.refresh(last_session)
    
    session_id = last_session.id
    print(f" Работаем с сессией ID: {session_id}")

    # =========================================================
    # 🛠️ БЛОК ОТЛАДКИ (Показывает, что реально есть в БД) 🛠️
    # =========================================================
    print("\n🔎 [DEBUG] Проверка содержимого таблицы UserAnswer:")
    
    raw_answers = session.exec(
        select(UserAnswer).where(UserAnswer.session_id == session_id)
    ).all()
    
    print(f" Найдено записей ответов: {len(raw_answers)}")
    
    if len(raw_answers) == 0:
        print(" ВНИМАНИЕ: База ответов пуста! Значит theory_chat не сохранил данные.")
        print(" Проверьте функцию theory_chat в main.py (там должен быть session.add и commit)")
    else:
        for idx, ans in enumerate(raw_answers):
            # Пробуем узнать тип вопроса для каждой записи
            q_type = "Unknown"
            q_obj = session.get(Question, ans.question_id)
            if q_obj:
                q_type = q_obj.type
            
            print(f"   [{idx+1}] Тип: {q_type} | Score: {ans.score} | Ответ: '{str(ans.user_answer_text)[:30]}...'")
    print("------------------------------------------\n")
    # =========================================================

    # 3. Разделение ответов по типам (Теория / Психология)
    # Делаем JOIN с таблицей вопросов
    results = session.exec(
        select(UserAnswer, Question)
        .join(Question, UserAnswer.question_id == Question.id)
        .where(UserAnswer.session_id == session_id)
    ).all()

    theory_answers = [ans for ans, q in results if q.type == 'theory']
    psy_answers = [ans for ans, q in results if q.type == 'psy']

    # 4. Расчет баллов за ТЕОРИЮ (Сумма баллов / Максимум)
    if theory_answers:
        total_theory_score = sum([a.score for a in theory_answers]) # Сумма оценок (например, 8 + 7 + 10 = 25)
        max_possible_theory = len(theory_answers) * 10             # Максимум (3 вопроса * 10 = 30)
        
        if max_possible_theory > 0:
            theory_score_percent = (total_theory_score / max_possible_theory) * 100
        else:
            theory_score_percent = 0
            
        print(f" ТЕОРИЯ: Набрано {total_theory_score} из {max_possible_theory} ({theory_score_percent:.1f}%)")
    else:
        print(" ТЕОРИЯ: Ответов нет. Оценка 0%.")
        theory_score_percent = 0

    # 5. Расчет баллов за SOFT SKILLS (Процент правильных)
    if psy_answers:
        psy_correct = len([a for a in psy_answers if a.is_correct])
        psy_score_percent = (psy_correct / len(psy_answers)) * 100
        print(f" SOFT SKILLS: Правильных {psy_correct} из {len(psy_answers)} ({psy_score_percent:.1f}%)")
    else:
        # Если вопросов не было, даем 100% кредит доверия
        print(" SOFT SKILLS: Вопросов не было. Оценка 100%.")
        psy_score_percent = 100 

    # 6. LLM Code Review (Анализ кода)
    print("\n Запуск LLM Code Review...")
    final_code = payload.codeHistory[-1] if payload.codeHistory else "# No code provided"
    
    task_text = "Python Task"
    if payload.coding_task_id:
        task_q = session.get(Question, payload.coding_task_id)
        if task_q:
            task_text = task_q.text

    try:
        # Вызов LLM для оценки кода
        review_res = generate_code_review(
            lang="Python", 
            question=task_text, 
            ideal_answer="pass", 
            user_answer=final_code,
            ollama=ollama_client, 
            redis_host=REDIS_HOST, 
            redis_port=REDIS_PORT
        )
        func_score = int(review_res.get("functional_score", 5))
        style_score = int(review_res.get("stylistic_score", 5))
        critique = review_res.get("critique", "Решение принято.")
        print(f" Оценка кода: Функционал={func_score}, Стиль={style_score}")
    except Exception as e:
        print(f" Ошибка LLM Review: {e}")
        func_score, style_score, critique = 5, 5, "Не удалось провести автоматическую проверку кода."

    # 7. Генерация Unit-тестов (для отчета)
    tests_json = "{}"
    try:
        tests_res = generate_unittests(
            lang="Python", 
            task=task_text, 
            code=final_code,
            ollama=ollama_client, 
            redis_host=REDIS_HOST, 
            redis_port=REDIS_PORT
        )
        tests_json = json.dumps(tests_res)
    except Exception as e:
        print(f" Ошибка генерации тестов: {e}")

    # 8. Расчет Integrity (Анти-чит)
    integrity = 100
    integrity -= (payload.focusLost * 5)
    integrity -= (payload.mouseLeftWindow * 2)
    if integrity < 0: integrity = 0

    # 9. Финальная формула оценки
    code_percent = ((func_score + style_score) / 20) * 100
    
    # ВЕСА: Код=40%, Теория=30%, Софты=20%, Античит=10%
    final_grade = (
        (code_percent * 0.4) + 
        (theory_score_percent * 0.3) + 
        (psy_score_percent * 0.2) + 
        (integrity * 0.1)
    )
    
    print(f"\n ИТОГОВЫЙ РАСЧЕТ:")
    print(f"   Code:    {code_percent:.1f}%")
    print(f"   Theory:  {theory_score_percent:.1f}%")
    print(f"   Psy:     {psy_score_percent:.1f}%")
    print(f"   Cheat:   {integrity}%")
    print(f" FINAL GRADE: {final_grade:.1f}/100")

    # 10. Сохранение отчета в базу данных
    last_session.status = "completed"
    session.add(last_session)

    telemetry_data = {
        "psy_score": int(psy_score_percent),
        "theory_score": int(theory_score_percent),
        "code_score": int(code_percent),
        "focus_lost": payload.focusLost,
        "generated_tests": json.loads(tests_json)
    }

    # Проверка на существование отчета (update vs create)
    existing_report = session.exec(select(Report).where(Report.session_id == session_id)).first()
    
    if existing_report:
        print(" Обновляем старый отчет")
        existing_report.final_score = int(final_grade)
        existing_report.integrity_score = integrity
        existing_report.summary_text = critique
        existing_report.telemetry_json = json.dumps(telemetry_data)
        session.add(existing_report)
    else:
        print(" Создаем новый отчет")
        report = Report(
            session_id=session_id,
            final_score=int(final_grade),
            integrity_score=integrity,
            summary_text=critique,
            telemetry_json=json.dumps(telemetry_data)
        )
        session.add(report)

    session.commit()
    

    return {
        "status": "completed",
        "finalScore": int(final_grade),
        "integrityScore": integrity,
        "critique": critique
    }

# 3. ПОЛУЧЕНИЕ СВОЕГО ОТЧЕТА (ДЛЯ КАНДИДАТА)
@app.get("/api/my-report/{user_id}")
def get_my_report(user_id: int, session: Session = Depends(get_session)):
    sess = session.exec(select(TestSession).where(TestSession.user_id == user_id).order_by(TestSession.created_at.desc())).first()
    
    if sess and sess.report:
        # Пытаемся достать детализацию баллов из JSON
        try:
            telemetry = json.loads(sess.report.telemetry_json)
        except:
            telemetry = {}

        return {
            "ready": True,
            "final_score": sess.report.final_score,
            "integrity_score": sess.report.integrity_score,
            "summary": sess.report.summary_text,
            "details": telemetry  # <--- ОТПРАВЛЯЕМ ДЕТАЛИ НА ФРОНТ
        }
    return {"ready": False}

# ---------------- ROUTER CONNECT ------------------

# ВАЖНО: подключаем router так, чтобы путь был /api/run-code
app.include_router(router, prefix="/api")
