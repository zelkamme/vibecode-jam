# backend/main.py

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import List, Optional
import httpx
import json
import logging

from database import create_db_and_tables, get_session, engine
from models import User, Question, Report, TestSession, Vacancy

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # НИКАКИХ ВОПРОСОВ НЕ СОЗДАЕМ. ТОЛЬКО ТАБЛИЦЫ.

# --- MODELS ---
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
    codeHistory: list[str]

# --- ENDPOINTS ---

@app.get("/api/vacancies")
def get_vacancies(session: Session = Depends(get_session)):
    vacs = session.exec(select(Vacancy)).all()
    if not vacs:
        # Создаем ТОЛЬКО вакансию, чтобы ты мог зайти
        vac = Vacancy(title="Intern Python (Default)", level="Intern")
        session.add(vac)
        session.commit()
        session.refresh(vac)
        return [vac]
    return vacs

@app.post("/api/register")
def register_candidate(data: RegisterRequest, session: Session = Depends(get_session)):
    vacancy = session.get(Vacancy, data.vacancy_id)
    level = vacancy.level if vacancy else "Intern"
    user = User(username=data.username, role="candidate", level=level, vacancy_id=data.vacancy_id)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"status": "ok", "user_id": user.id, "level": user.level}

@app.post("/api/tasks")
def create_task(task_data: TaskCreateRequest, session: Session = Depends(get_session)):
    print(f"🔥 СОЗДАНИЕ: {task_data.title} (Тип: {task_data.type})")
    
    full_text = f"{task_data.title}\n\n{task_data.description}"
    
    # Если тип coding - мапим теги, если theory - нам пофиг
    req_tag = "python"
    if task_data.envId == "data-science": req_tag = "python,pandas"

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
    # Ищем строго по уровню
    q = session.exec(select(Question).where(Question.type == "coding").where(Question.level == level)).first()
    
    # Если нет - ищем любую задачу кодинга (фоллбэк)
    if not q:
        q = session.exec(select(Question).where(Question.type == "coding")).first()

    if not q:
        return {"id": 0, "title": "Задач нет", "description": "HR не добавил задачи.", "files": []}

    parts = q.text.split("\n\n", 1)
    return {
        "id": q.id,
        "title": parts[0],
        "description": parts[1] if len(parts)>1 else "",
        "files": json.loads(q.files_json) if q.files_json else []
    }
@app.get("/api/candidates")
def get_candidates(session: Session = Depends(get_session)):
    users = session.exec(select(User).where(User.role == "candidate")).all()
    results = []
    
    for user in users:
        # Ищем ПОСЛЕДНЮЮ сессию пользователя
        last_session = session.exec(
            select(TestSession)
            .where(TestSession.user_id == user.id)
            .order_by(TestSession.created_at.desc())
        ).first()
        
        status = "Не начинал"
        score = "N/A"
        
        if last_session:
            status = "В процессе"
            # Проверяем, есть ли отчет
            if last_session.report:
                status = "Завершено"
                score = f"{last_session.report.final_score}/100"
            # Или если статус сессии completed
            elif last_session.status == "completed":
                status = "Завершено"
                score = "Ожидание..."

        results.append({
            "id": user.id,
            "name": user.username,
            "level": user.level,
            "status": status,
            "score": score
        })
    return results
@app.get("/api/candidates/{user_id}")
def get_candidate_detail(user_id: int, session: Session = Depends(get_session)):
    # 1. Ищем юзера
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Ищем его последнюю сессию
    last_session = session.exec(
        select(TestSession)
        .where(TestSession.user_id == user.id)
        .order_by(TestSession.created_at.desc())
    ).first()

    # 3. Собираем данные отчета
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
        
        # Если есть отчет в базе
        if last_session.report:
            report_data["score"] = last_session.report.final_score
            report_data["integrity_score"] = last_session.report.integrity_score
            try:
                report_data["telemetry"] = json.loads(last_session.report.telemetry_json)
            except:
                pass

    # 4. Возвращаем всё вместе
    return {
        "id": user.id,
        "name": user.username,
        "level": user.level,
        **report_data
    }
# --- СОХРАНЕНИЕ РЕЗУЛЬТАТОВ (ФИНИШ) ---
@app.post("/api/analyze-integrity")
async def analyze_integrity(payload: IntegrityPayload, session: Session = Depends(get_session)):
    print(f"🏁 ЗАВЕРШЕНИЕ ТЕСТА user_id={payload.user_id}")
    
    # 1. Создаем сессию
    test_session = TestSession(user_id=payload.user_id, status="completed")
    session.add(test_session)
    session.commit()
    session.refresh(test_session)

    # 2. Считаем простой балл (заглушка, потом тут будет AI)
    score = 100
    score -= payload.focusLost * 5
    if score < 0: score = 0

    telemetry = {
        "focusLost": payload.focusLost,
        "largePastes": payload.largePastes
    }

    # 3. Создаем ОТЧЕТ
    report = Report(
        session_id=test_session.id,
        final_score=score,
        integrity_score=score,
        summary_text="Тест завершен.",
        telemetry_json=json.dumps(telemetry)
    )
    session.add(report)
    session.commit()
    
    print(f"✅ Отчет создан для User {payload.user_id}. Score: {score}")
    return {"finalScore": score, "details": telemetry}
@app.get("/api/questions/theory/{level}")
def get_theory(level: str, session: Session = Depends(get_session)):
    # Ищем теорию для уровня (или для всех)
    qs = session.exec(select(Question).where(Question.type == "theory")).all()
    
    # Фильтруем по уровню Python-кодом (проще) или отдаем всё, если вопросов мало
    filtered = [q for q in qs if q.level == level or q.level == "Intern"] 
    if not filtered and qs: filtered = qs # Если нет для уровня, отдаем что есть

    res = []
    for q in filtered:
        # Так как мы создаем через HR панель без вариантов ответа,
        # мы просто отдаем текст и флаг, что это свободный ответ
        res.append({
            "id": q.id,
            "questionText": q.text,
            "type": "open_ended", # <-- Флаг свободного ответа
            "correctAnswer": q.correct_answer
        })
    return res

@app.post("/api/run-code")
async def run_code(payload: RunCodeRequest, session: Session = Depends(get_session)):
    files_to_send = []
    env_to_use = "basic"
    if payload.task_id:
        q = session.get(Question, payload.task_id)
        if q:
            if "pandas" in q.required_tag: env_to_use = "data-science"
            if q.files_json:
                files_to_send = json.loads(q.files_json)
                for f in files_to_send:
                    if f['name'] == 'main.py': f['content'] = payload.code

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post("http://localhost:3000/api/run-code", json={
                "code": payload.code,
                "language": payload.language,
                "environment": env_to_use,
                "files": files_to_send
            })
            return resp.json()
        except:
            return {"stdout": "", "stderr": "Docker Error"}

@app.post("/api/analyze-integrity")
async def analyze_integrity(payload: IntegrityPayload, session: Session = Depends(get_session)):
    # Заглушка финиша
    return {"finalScore": 100}