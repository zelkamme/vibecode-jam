# backend/seed_questions.py
import json
from sqlmodel import Session, select
from database import engine, create_db_and_tables
from models import Question

# 1. SOFT SKILLS (Уже с вариантами)
psy_questions = [
    {
        "text": "Коллега критикует ваш код в грубой форме при всех. Ваши действия?",
        "options": [
            {"answerText": "Отвечу тем же, чтобы защитить авторитет", "isCorrect": False},
            {"answerText": "Предложу обсудить это лично и конструктивно", "isCorrect": True},
            {"answerText": "Проигнорирую и молча исправлю", "isCorrect": False},
            {"answerText": "Пожалуюсь менеджеру", "isCorrect": False}
        ]
    },
    {
        "text": "Вы понимаете, что не успеваете сдать задачу к дедлайну. Когда сообщите об этом?",
        "options": [
            {"answerText": "В момент дедлайна", "isCorrect": False},
            {"answerText": "Как только осознал риск, предложив варианты", "isCorrect": True},
            {"answerText": "Постараюсь успеть, работая ночью, и скажу, если не выйдет", "isCorrect": False},
            {"answerText": "Скрою это и попрошу помощи друга", "isCorrect": False}
        ]
    },
    # ... остальные вопросы soft skills ...
]

# 2. ТЕОРИЯ (ДОБАВИЛ ПОЛЕ correct_answer)
theory_questions = [
    {
        "text": "В чем разница между list и tuple в Python?",
        "level": "Intern",
        "tag": "python",
        "correct_answer": "List — изменяемый (mutable), медленнее. Tuple — неизменяемый (immutable), быстрее, хешируемый (можно использовать как ключ словаря)."
    },
    {
        "text": "Как работает Garbage Collector в Python? Что такое reference counting?",
        "level": "Junior",
        "tag": "python",
        "correct_answer": "Основной механизм — подсчет ссылок (Reference Counting). Когда счетчик ссылок на объект равен 0, память освобождается. Также есть GC для циклических ссылок (Generational GC)."
    },
    {
        "text": "Что такое декоратор и как его написать?",
        "level": "Junior",
        "tag": "python",
        "correct_answer": "Это функция, которая принимает другую функцию и расширяет её поведение, не изменяя её код. Используется через @wrapper."
    },
    {
        "text": "Что такое Docker? Зачем нужны слои в образе?",
        "level": "Middle",
        "tag": "devops",
        "correct_answer": "Платформа для контейнеризации. Слои нужны для кэширования: если меняется только код, пересобирается только последний слой, а не вся ОС и библиотеки."
    },
    {
        "text": "Как работают индексы в базе данных? Что такое B-Tree?",
        "level": "Middle",
        "tag": "db",
        "correct_answer": "Индексы ускоряют поиск (SELECT), но замедляют запись (INSERT/UPDATE). B-Tree — сбалансированное дерево, позволяющее искать данные за логарифмическое время O(log N)."
    },
    {
        "text": "Принципы CAP-теоремы. Что выберете для финансовой системы: CP или AP?",
        "level": "Senior",
        "tag": "architecture",
        "correct_answer": "Consistency, Availability, Partition tolerance. Одновременно возможны только 2 из 3. Для финансов обычно выбирают CP (Consistency + Partition Tolerance), так как важна точность данных, а не 100% доступность."
    }
]

# 3. КОДИНГ (Без изменений)
coding_tasks = [
    {
        "title": "Сумма списка (Intern)",
        "description": "Напишите функцию `sum_list(numbers)`, которая принимает список чисел и возвращает их сумму.",
        "level": "Intern",
        "tag": "python",
        "files": [
            {
                "name": "main.py",
                "content": "def sum_list(numbers):\n    # Ваш код здесь\n    pass\n\nif __name__ == '__main__':\n    print(sum_list([1, 2, 3]))"
            }
        ]
    },
    # ... остальные задачи ...
]

def seed_questions():
    create_db_and_tables()
    with Session(engine) as session:
        print("--- Заполнение базы данных... ---")
        
        # Soft Skills
        for q in psy_questions:
            exists = session.exec(select(Question).where(Question.text == q["text"])).first()
            if not exists:
                db_q = Question(text=q["text"], type="psy", level="All", required_tag="soft", files_json=json.dumps(q["options"]))
                session.add(db_q)

        # Theory
        for q in theory_questions:
            exists = session.exec(select(Question).where(Question.text == q["text"])).first()
            if not exists:
                db_q = Question(
                    text=q["text"], 
                    type="theory", 
                    level=q["level"], 
                    required_tag=q["tag"], 
                    correct_answer=q.get("correct_answer"), # <-- СОХРАНЯЕМ ПРАВИЛЬНЫЙ ОТВЕТ
                    files_json=None
                )
                session.add(db_q)

        # Coding
        for task in coding_tasks:
            full_text = f"{task['title']}\n\n{task['description']}"
            exists = session.exec(select(Question).where(Question.text == full_text)).first()
            if not exists:
                db_q = Question(text=full_text, type="coding", level=task["level"], required_tag=task["tag"], files_json=json.dumps(task["files"]))
                session.add(db_q)

        session.commit()
        print("✅ База данных успешно обновлена!")

if __name__ == "__main__":
    seed_questions()