# backend/seed_questions.py
import json
from sqlmodel import Session, select
from database import engine, create_db_and_tables
from models import Question

# 20 Вопросов на Soft Skills (универсальные)
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
    {
        "text": "Вам поручили задачу с технологией, которую вы не знаете. Что сделаете?",
        "options": [
            {"answerText": "Откажусь от задачи", "isCorrect": False},
            {"answerText": "Скажу, что знаю, и буду гуглить по ходу", "isCorrect": False},
            {"answerText": "Предупрежу о рисках и попрошу время на изучение", "isCorrect": True},
            {"answerText": "Передам задачу стажеру", "isCorrect": False}
        ]
    },
    {
        "text": "На дейли-митинге (standup) вы понимаете, что коллега говорит неправду о прогрессе. Вы:",
        "options": [
            {"answerText": "Разоблачу его при всех", "isCorrect": False},
            {"answerText": "Промолчу, это не мое дело", "isCorrect": False},
            {"answerText": "Задам уточняющий вопрос, который мягко подсветит проблему", "isCorrect": True},
            {"answerText": "Напишу ему гневное сообщение", "isCorrect": False}
        ]
    },
    {
        "text": "Менеджер меняет требования к задаче третий раз за неделю. Ваша реакция?",
        "options": [
            {"answerText": "Молча делаю, мне за это платят", "isCorrect": False},
            {"answerText": "Начинаю скандалить", "isCorrect": False},
            {"answerText": "Обсуждаю с ним влияние изменений на сроки и качество", "isCorrect": True},
            {"answerText": "Игнорирую новые требования", "isCorrect": False}
        ]
    },
    {
        "text": "Вы нашли критический баг на продакшене в пятницу вечером. Ваши действия?",
        "options": [
            {"answerText": "Сделаю вид, что не видел, до понедельника", "isCorrect": False},
            {"answerText": "Оценю критичность. Если блокирует бизнес — чиню/сообщаю", "isCorrect": True},
            {"answerText": "Сразу пойду домой, рабочий день окончен", "isCorrect": False},
            {"answerText": "Напишу в общий чат панику", "isCorrect": False}
        ]
    },
    {
        "text": "Как вы относитесь к рутинным задачам (написание тестов, документация)?",
        "options": [
            {"answerText": "Ненавижу, стараюсь спихнуть", "isCorrect": False},
            {"answerText": "Понимаю их важность и делаю качественно", "isCorrect": True},
            {"answerText": "Делаю, но кое-как", "isCorrect": False},
            {"answerText": "Считаю, что это работа для джунов", "isCorrect": False}
        ]
    },
    {
        "text": "У вас возник конфликт интересов: качество кода vs скорость доставки. Что выберете?",
        "options": [
            {"answerText": "Всегда только идеальный код", "isCorrect": False},
            {"answerText": "Всегда только скорость", "isCorrect": False},
            {"answerText": "Найду баланс, согласовав технический долг с бизнесом", "isCorrect": True},
            {"answerText": "Сделаю быстро и плохо, никому не скажу", "isCorrect": False}
        ]
    },
    {
        "text": "Новый сотрудник в команде постоянно задает вам вопросы, отвлекая от работы.",
        "options": [
            {"answerText": "Скажу, чтобы не мешал", "isCorrect": False},
            {"answerText": "Выделю специальное время для ответов или направлю на документацию", "isCorrect": True},
            {"answerText": "Буду игнорировать сообщения", "isCorrect": False},
            {"answerText": "Пожалуюсь HR", "isCorrect": False}
        ]
    },
    {
        "text": "Вы допустили ошибку, которая уронила сервис. Что сделаете первым?",
        "options": [
            {"answerText": "Признаю ошибку и приступлю к починке", "isCorrect": True},
            {"answerText": "Попытаюсь скрыть логи", "isCorrect": False},
            {"answerText": "Найду кого обвинить", "isCorrect": False},
            {"answerText": "Уйду на обед", "isCorrect": False}
        ]
    },
    {
        "text": "Вам нужно убедить команду использовать новый инструмент. Как поступите?",
        "options": [
            {"answerText": "Заставлю их административно", "isCorrect": False},
            {"answerText": "Подготовлю презентацию с плюсами, минусами и демо", "isCorrect": True},
            {"answerText": "Просто начну использовать сам", "isCorrect": False},
            {"answerText": "Скажу, что так модно", "isCorrect": False}
        ]
    },
    {
        "text": "Как вы реагируете на неудачу в проекте?",
        "options": [
            {"answerText": "Впадаю в депрессию", "isCorrect": False},
            {"answerText": "Ищу виноватых", "isCorrect": False},
            {"answerText": "Анализирую причины (Retrospective) и делаю выводы", "isCorrect": True},
            {"answerText": "Мне все равно", "isCorrect": False}
        ]
    },
    {
        "text": "Задача описана крайне туманно. Ваши действия?",
        "options": [
            {"answerText": "Сделаю как понял", "isCorrect": False},
            {"answerText": "Буду ждать, пока опишут лучше", "isCorrect": False},
            {"answerText": "Задам уточняющие вопросы заказчику до начала работы", "isCorrect": True},
            {"answerText": "Не буду делать", "isCorrect": False}
        ]
    },
    {
        "text": "Вы видите способ оптимизировать процесс работы команды, но это требует усилий.",
        "options": [
            {"answerText": "Промолчу, инициатива наказуема", "isCorrect": False},
            {"answerText": "Предложу идею и план реализации", "isCorrect": True},
            {"answerText": "Сделаю молча и буду ждать похвалы", "isCorrect": False},
            {"answerText": "Пожалуюсь, что всё работает плохо", "isCorrect": False}
        ]
    },
    {
        "text": "Вам нужно ревьюить код сеньора, и вы нашли ошибку. Скажете?",
        "options": [
            {"answerText": "Нет, он же сеньор, ему виднее", "isCorrect": False},
            {"answerText": "Да, вежливо укажу на ошибку в комментарии", "isCorrect": True},
            {"answerText": "Рассмеюсь над ним", "isCorrect": False},
            {"answerText": "Исправлю сам без его ведома", "isCorrect": False}
        ]
    },
    {
        "text": "Что для вас 'успешный продукт'?",
        "options": [
            {"answerText": "Где написан красивый код", "isCorrect": False},
            {"answerText": "Который решает проблему пользователя и приносит пользу", "isCorrect": True},
            {"answerText": "Где использованы новейшие фреймворки", "isCorrect": False},
            {"answerText": "Тот, который я написал", "isCorrect": False}
        ]
    },
    {
        "text": "Как вы обучаетесь новому?",
        "options": [
            {"answerText": "Только если заставит работодатель", "isCorrect": False},
            {"answerText": "Регулярно читаю статьи, пробую пет-проекты", "isCorrect": True},
            {"answerText": "Мне хватает знаний из университета", "isCorrect": False},
            {"answerText": "Жду пока коллега расскажет", "isCorrect": False}
        ]
    },
    {
        "text": "Вы сильно устали, но команда просит помочь. Что сделаете?",
        "options": [
            {"answerText": "Помогу через силу и выгорю", "isCorrect": False},
            {"answerText": "Оценю ресурс. Если критично — помогу, иначе вежливо откажу", "isCorrect": True},
            {"answerText": "Грубо пошлю", "isCorrect": False},
            {"answerText": "Проигнорирую просьбу", "isCorrect": False}
        ]
    },
    {
        "text": "Как вы относитесь к переработкам (овертаймам)?",
        "options": [
            {"answerText": "Обожаю жить на работе", "isCorrect": False},
            {"answerText": "Допускаю в критических ситуациях, но не на постоянной основе", "isCorrect": True},
            {"answerText": "Категорически против, ровно в 18:00 ухожу", "isCorrect": False},
            {"answerText": "Постоянно перерабатываю, так как не умею планировать", "isCorrect": False}
        ]
    },
    {
        "text": "Ваше главное качество как разработчика?",
        "options": [
            {"answerText": "Скорость печати", "isCorrect": False},
            {"answerText": "Умение решать проблемы и работать в команде", "isCorrect": True},
            {"answerText": "Знание всех функций наизусть", "isCorrect": False},
            {"answerText": "Высокое IQ", "isCorrect": False}
        ]
    }
]


def seed_questions():
    create_db_and_tables()
    with Session(engine) as session:
        print("--- Заливаем вопросы... ---")
        
        # Добавляем PSY
        for q in psy_questions:
            # Проверка на дубликаты (простая)
            exists = session.exec(select(Question).where(Question.text == q["text"])).first()
            if not exists:
                db_q = Question(
                    text=q["text"], 
                    type="psy", 
                    level="All", 
                    required_tag="soft", 
                    files_json=json.dumps(q["options"])
                )
                session.add(db_q)

       
        session.commit()
        print("✅ Вопросы (Psy + Theory) успешно добавлены!")

if __name__ == "__main__":
    seed_questions()