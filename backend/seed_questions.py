# backend/seed_questions.py
import json
from sqlmodel import Session, select
from database import engine, create_db_and_tables
from models import Question

# 1. ЗАДАЧИ ПО КОДИНГУ (Разные языки и уровни)
coding_tasks = [
    # --- PYTHON ---
    {
        "title": "Сумма элементов списка",
        "description": "Напишите функцию `sum_list(numbers)`, которая возвращает сумму чисел.",
        "level": "Intern",
        "tag": "python",
        "files": [{"name": "main.py", "content": "def sum_list(numbers):\n    pass\n\nif __name__ == '__main__':\n    print(sum_list([1, 2, 3]))"}]
    },
    {
        "title": "Проверка палиндрома",
        "description": "Напишите функцию `is_palindrome(s)`, которая возвращает True, если строка читается одинаково с обеих сторон.",
        "level": "Junior",
        "tag": "python",
        "files": [{"name": "main.py", "content": "def is_palindrome(s):\n    pass"}]
    },
    
    # --- JAVA ---
    {
        "title": "Hello World Java",
        "description": "Реализуйте класс Main с методом main, выводящим 'Hello Java'.",
        "level": "Intern",
        "tag": "java",
        "files": [{"name": "Main.java", "content": "public class Main {\n    public static void main(String[] args) {\n        // Code here\n    }\n}"}]
    },
    {
        "title": "Reverse Array (Java)",
        "description": "Напишите метод для разворота массива целых чисел.",
        "level": "Junior",
        "tag": "java",
        "files": [{"name": "Main.java", "content": "import java.util.Arrays;\n\npublic class Main {\n    public static int[] reverse(int[] arr) {\n        return arr;\n    }\n    public static void main(String[] args) {\n        System.out.println(Arrays.toString(reverse(new int[]{1, 2, 3})));\n    }\n}"}]
    },

    # --- JAVASCRIPT ---
    {
        "title": "Фильтрация массива",
        "description": "Напишите функцию `filterEven(arr)`, возвращающую только четные числа.",
        "level": "Junior",
        "tag": "javascript",
        "files": [{"name": "index.js", "content": "function filterEven(arr) {\n  return [];\n}\n\nconsole.log(filterEven([1, 2, 3, 4]));"}]
    }
]

# 2. ТЕОРИЯ (Общая и специфичная)
theory_questions = [
    {
        "text": "Что такое GIL в Python?",
        "level": "Junior",
        "tag": "python",
        "correct_answer": "Global Interpreter Lock — мьютекс, ограничивающий выполнение потоков."
    },
    {
        "text": "В чем отличие `==` от `===` в JS?",
        "level": "Junior",
        "tag": "javascript",
        "correct_answer": "=== проверяет и значение, и тип (строгое сравнение)."
    },
    {
        "text": "Отличие Interface от Abstract Class в Java?",
        "level": "Junior",
        "tag": "java",
        "correct_answer": "Интерфейс описывает поведение, абстрактный класс — иерархию."
    }
]

def seed_questions():
    create_db_and_tables()
    with Session(engine) as session:
        print("--- Заполнение базы вопросами... ---")

        # Добавляем кодинг
        for task in coding_tasks:
            full_text = f"{task['title']}\n\n{task['description']}"
            # Проверка на дубликаты
            exists = session.exec(select(Question).where(Question.text == full_text)).first()
            if not exists:
                db_q = Question(
                    text=full_text, 
                    type="coding", 
                    level=task["level"], 
                    required_tag=task["tag"], 
                    files_json=json.dumps(task["files"])
                )
                session.add(db_q)
                print(f"✅ Добавлена задача: {task['title']} ({task['tag']})")

        # Добавляем теорию
        for q in theory_questions:
            exists = session.exec(select(Question).where(Question.text == q["text"])).first()
            if not exists:
                db_q = Question(
                    text=q["text"], 
                    type="theory", 
                    level=q["level"], 
                    required_tag=q["tag"], 
                    correct_answer=q["correct_answer"]
                )
                session.add(db_q)
                print(f"✅ Добавлен вопрос: {q['text'][:30]}... ({q['tag']})")

        session.commit()
        print("🚀 База данных успешно обновлена!")

if __name__ == "__main__":
    seed_questions()