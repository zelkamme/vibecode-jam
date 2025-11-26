# backend/models.py
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime

# 1. ВАКАНСИЯ (Расширенная)
class Vacancy(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str       # Например: "Backend Python"
    level: str       # Junior / Middle / Senior
    language: str    # Python / JS / Go
    skills: str      # "Docker, FastAPI, PostgreSQL" (строка через запятую)
    salary_range: Optional[str] = None # "100k - 150k"
    description: Optional[str] = None
    is_active: bool = Field(default=True) # <-- НОВОЕ ПОЛЕ (Открыта/Скрыта)

# 2. ЮЗЕР
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    role: str = "candidate" # candidate / hr
    
    # Связываем юзера с вакансией (если он кандидат)
    vacancy_id: Optional[int] = Field(default=None, foreign_key="vacancy.id")
    
    # Уровень берем из вакансии, но можно хранить копию для удобства,
    # или вычислять динамически. Для простоты храним тут:
    level: str 
    resume_path: Optional[str] = None  
    sessions: List["TestSession"] = Relationship(back_populates="user")

# 3. КОНТЕЙНЕРЫ И ТЕГИ
class ContainerImage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    docker_image: str
    tags: List["ContainerTag"] = Relationship(back_populates="image")

class ContainerTag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    image_id: int = Field(foreign_key="containerimage.id")
    tag: str
    image: Optional[ContainerImage] = Relationship(back_populates="tags")

# 4. ВОПРОСЫ
class Question(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    type: str           # 'coding', 'theory', 'psy'
    level: str          # Добавили уровень к вопросу, чтобы фильтровать
    required_tag: str   
    correct_answer: Optional[str] = None
    files_json: Optional[str] = None

# 5. СЕССИЯ
class TestSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "started" # started, completed
    
    user: Optional[User] = Relationship(back_populates="sessions")
    report: Optional["Report"] = Relationship(back_populates="session")
    answers: List["UserAnswer"] = Relationship(back_populates="session")

# 6. ОТВЕТЫ
class UserAnswer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="testsession.id")
    question_id: int = Field(foreign_key="question.id")
    user_code: str
    is_correct: bool
    session: Optional[TestSession] = Relationship(back_populates="answers")

# 7. ОТЧЕТ
class Report(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="testsession.id")
    final_score: int
    integrity_score: int
    summary_text: Optional[str] = None
    telemetry_json: Optional[str] = None
    
    session: Optional[TestSession] = Relationship(back_populates="report")