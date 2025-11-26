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
from database import create_db_and_tables, get_session
from models import User, Question, Report, TestSession, Vacancy

# Создаем папку для загрузок, если нет
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)

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
    language: str
    task_id: Optional[int] = None

class ChatMessage(BaseModel):
    message: str
    history: List[dict]

class IntegrityPayload(BaseModel):
    user_id: int
    focusLost: int
    mouseLeftWindow: int
    largePastes: int
    codeHistory: List[str]

# ---------------- ENDPOINTS ------------------

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


@app.get("/api/task/coding/{level}")
def get_coding_task(level: str, session: Session = Depends(get_session)):
    q = session.exec(
        select(Question)
        .where(Question.type == "coding")
        .where(Question.level == level)
    ).first()

    if not q:
        q = session.exec(select(Question).where(Question.type == "coding")).first()

    if not q:
        return {
            "id": 0,
            "title": "Задач нет",
            "description": "HR не добавил задачи.",
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

    return {
        "id": user.id,
        "name": user.username,
        "level": user.level,
        **report_data
    }


# ---------------- RUN CODE (DOCKER) ------------------

@router.post("/run-code")
async def run_code(payload: RunCodeRequest, session: Session = Depends(get_session)):
    files_to_send = []
    env_to_use = "basic"

    if payload.task_id:
        q = session.get(Question, payload.task_id)
        if q:
            if "pandas" in q.required_tag:
                env_to_use = "data-science"

            if q.files_json:
                files_to_send = json.loads(q.files_json)
                for f in files_to_send:
                    if f["name"] == "main.py":
                        f["content"] = payload.code

    temp_dir = tempfile.mkdtemp()
    source_path = os.path.join(temp_dir, "main.py")

    with open(source_path, "w", encoding="utf-8") as f:
        f.write(payload.code)

    env_map = {
        "basic": "python:3.12-alpine",
        "data-science": "python:3.12-slim"
    }

    image = env_map.get(env_to_use, "python:3.12-alpine")

    try:
        container = docker_client.containers.run(
            image=image,
            command=["python", "/work/main.py"],
            volumes={temp_dir: {"bind": "/work", "mode": "rw"}},
            network_disabled=True,
            detach=True,
            mem_limit="256m",
            cpu_period=100000,
            cpu_quota=50000,
            stdout=True,
            stderr=True,
            remove=True
        )

        exit_code = container.wait()
        logs = container.logs(stdout=True, stderr=True).decode()

        stdout = logs
        stderr = "" if exit_code["StatusCode"] == 0 else logs

        return {"stdout": stdout, "stderr": stderr}

    except Exception as e:
        return {"stdout": "", "stderr": f"Docker error: {str(e)}"}


# ---------------- FINISH TEST ------------------

# 2. СОХРАНЕНИЕ РЕЗУЛЬТАТОВ (Обновляем analyze-integrity)
@app.post("/api/analyze-integrity")
async def analyze_integrity(payload: IntegrityPayload, session: Session = Depends(get_session)):
    # 1. Находим юзера и сессию
    user = session.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    last_session = session.exec(
        select(TestSession)
        .where(TestSession.user_id == user.id)
        .order_by(TestSession.created_at.desc())
    ).first()

    if not last_session:
        # Если сессии нет (странно, но бывает), создаем новую завершенную
        last_session = TestSession(user_id=user.id, status="completed")
        session.add(last_session)
        session.commit()
        session.refresh(last_session)
    else:
        last_session.status = "completed"
        session.add(last_session)

    # 2. Расчет Integrity Score (простая логика)
    integrity_score = 100
    integrity_score -= (payload.focusLost * 2)
    integrity_score -= (payload.mouseLeftWindow * 1)
    integrity_score -= (payload.largePastes * 10)
    if integrity_score < 0: integrity_score = 0

    # 3. Расчет Final Score (заглушка, в идеале считать по ответам Psy/Theory/Code)
    # Для демо ставим случайный высокий балл, если integrity хороший
    final_score = 85 if integrity_score > 80 else 40

    # 4. Сохраняем отчет в БД
    telemetry_data = {
        "focusLost": payload.focusLost,
        "mouseLeftWindow": payload.mouseLeftWindow,
        "largePastes": payload.largePastes,
        "codeHistory": payload.codeHistory
    }

    report = Report(
        session_id=last_session.id,
        final_score=final_score,
        integrity_score=integrity_score,
        summary_text="Автоматический анализ завершен.",
        telemetry_json=json.dumps(telemetry_data)
    )
    
    session.add(report)
    session.commit()

    return {
        "status": "completed", 
        "finalScore": final_score, 
        "integrityScore": integrity_score
    }

# 3. ПОЛУЧЕНИЕ СВОЕГО ОТЧЕТА (ДЛЯ КАНДИДАТА)
@app.get("/api/my-report/{user_id}")
def get_my_report(user_id: int, session: Session = Depends(get_session)):
    # Ищем последнюю сессию с отчетом
    last_session = session.exec(
        select(TestSession)
        .where(TestSession.user_id == user_id)
        .order_by(TestSession.created_at.desc())
    ).first()

    if not last_session or not last_session.report:
        return {"ready": False}

    report = last_session.report
    return {
        "ready": True,
        "final_score": report.final_score,
        "integrity_score": report.integrity_score,
        "summary": report.summary_text
    }

# ---------------- ROUTER CONNECT ------------------

# ВАЖНО: подключаем router так, чтобы путь был /api/run-code
app.include_router(router, prefix="/api")
