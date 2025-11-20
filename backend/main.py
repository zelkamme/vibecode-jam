from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import List, Optional
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
from backend.models import User, Question, Report, TestSession, Vacancy

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

@app.get("/api/vacancies")
def get_vacancies(session: Session = Depends(get_session)):
    vacs = session.exec(select(Vacancy)).all()
    if not vacs:
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
        last_session = session.exec(
            select(TestSession)
            .where(TestSession.user_id == user.id)
            .order_by(TestSession.created_at.desc())
        ).first()
        
        status = "Не начинал"
        score = "N/A"
        
        if last_session:
            status = "В процессе"
            if last_session.report:
                status = "Завершено"
                score = f"{last_session.report.final_score}/100"
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

@app.post("/api/analyze-integrity")
async def analyze_integrity(payload: IntegrityPayload, session: Session = Depends(get_session)):
    return {"finalScore": 100}


# ---------------- ROUTER CONNECT ------------------

# ВАЖНО: подключаем router так, чтобы путь был /api/run-code
app.include_router(router, prefix="/api")
