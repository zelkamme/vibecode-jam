# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time

# --- Модели для валидации данных ---
class CodePayload(BaseModel):
    code: str

class ChatMessage(BaseModel):
    message: str
# backend/main.py

class IntegrityPayload(BaseModel):
    focusLost: int
    mouseLeftWindow: int
    largePastes: int
    codeHistory: list[str]

# --- Создание приложения FastAPI ---
app = FastAPI()

# --- Настройка CORS, чтобы фронтенд мог общаться с бэкендом ---
origins = [
    "http://localhost:5173", # Адрес нашего будущего фронтенда
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/analyze-integrity")
async def analyze_integrity(payload: IntegrityPayload):
    # 1. Математический расчет (Жесткая логика)
    score = 100
    score -= payload.focusLost * 5      # -5 баллов за каждый альт-таб
    score -= payload.mouseLeftWindow * 2 # -2 балла за уход мыши
    score -= payload.largePastes * 15    # -15 баллов за копипасту
    
    if score < 0: score = 0

    # 2. Анализ стиля кода через AI (N2)
    # Здесь мы делаем запрос к сервису ML-разработчика
    # В реальности: requests.post('http://localhost:4000/api/analyze-style', json={"history": payload.codeHistory})
    
    # Заглушка ответа от AI по стилю:
    style_analysis = "Стиль кода консистентен."
    if payload.largePastes > 0:
        style_analysis = "Обнаружено резкое изменение стиля, характерное для вставки готового решения."
        score -= 20 # Дополнительный штраф от AI

    return {
        "finalScore": score,
        "details": {
            "focusLost": payload.focusLost,
            "largePastes": payload.largePastes,
            "aiConclusion": style_analysis
        }
    }
# --- Эндпоинты API (заглушки) ---

@app.post("/api/chat")
async def handle_chat(payload: ChatMessage):
    """ Имитирует ответ от LLM-интервьюера. """
    user_message = payload.message.lower()
    time.sleep(1) # Имитация "размышлений" нейросети

    if "привет" in user_message:
        response = "Здравствуйте! Готовы начать техническое собеседование? Давайте начнем с простой задачи."
    elif "задачу" in user_message:
        response = "Конечно. Напишите, пожалуйста, функцию на Python, которая разворачивает строку."
    else:
        response = "Интересная мысль. Давайте вернемся к коду. Как у вас продвигается решение задачи?"

    return {"sender": "ai", "text": response}


@app.post("/api/run-code")
async def run_code(payload: CodePayload):
    """ Имитирует выполнение кода. БЕЗ РЕАЛЬНОГО ЗАПУСКА! """
    code = payload.code
    
    if 'return s[::-1]' in code:
        return {"stdout": "Тесты пройдены успешно!", "stderr": ""}
    if 'print' in code:
        return {"stdout": "Код выполнен.", "stderr": ""}
    else:
        return {"stdout": "", "stderr": "SyntaxError: invalid syntax."}