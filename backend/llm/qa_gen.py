from .llm_api import cached_chat
from .tools import parse_json_list, parse_response


def fill_theory_qa_gen_prompt(position, requirements, resume, que_num=5):
    json_item = ""
    for i in range(que_num):
        json_item += f'{{"question": "<вопрос {i}>", "answer": "<ответ {i}>"}},\n'
    
    prompt = f"""Ты — интеллектуальный интервьюер. Твоя задача — подготовить набор из {que_num} теоретических вопросов‑ответов на русском языке, которые могли бы задать кандидату на указанную должность по заданному языку программирования.  

    Ввод (от пользователя) содержит четыре элемента, каждый из которых начинается с метки и завершается пустой строкой:

    1. **Должность** – название вакансии (например, Junior Python Developer) - <POSITION>
    2. **Требования к должности** – список ключевых навыков/технологий, указанных в объявлении (можно перечислить через запятую) - <REQUIREMENTS>  
    3. **Резюме кандидата** – краткое описание опыта, проектов, знаний, полученных сертификатов и пр. - <RESUME>

    Твоя реакция должна быть **только** валидным JSON‑массивом из {que_num} объектов, каждый объект имеет два поля:
    - `"question"` – формулировка вопроса, соответствующая уровню и требованиям должности, учитывая опыт, указанный в резюме.  
    - `"answer"` – корректный, лаконичный ответ, который ожидается от компетентного специалиста.  

    Формат вывода **строго** следующий (без каких‑либо дополнительных символов, комментариев или пояснений):

    ```json
    [
        {json_item}
    ]

    <POSITION>
    {position}
    </POSITION>
    <REQUIREMENTS>
    {requirements}
    </REQUIREMENTS>
    <RESUME>
    {resume}
    </RESUME>
    """
    return prompt

def fill_code_qa_gen_prompt(position, requirements, resume, code, que_num=5):
    json_item = ""
    for i in range(que_num):
        json_item += f'{{"question": "<вопрос {i}>", "answer": "<ответ {i}>"}},\n'

    prompt = f"""Ты — интеллектуальный интервьюер‑генератор. Твоя задача — составить набор из **{que_num}** теоретических вопросов‑ответов, которые можно задать кандидату в рамках собеседования по конкретному языку программирования.  
    Вопросы формулируются на русском языке **на основе** четырёх блоков, переданных пользователем (каждый блок начинается с метки и завершается пустой строкой):

    1. **Должность** – название вакансии (например, Junior Python Developer) - <POSITION>
    2. **Требования к вакансии** – список ключевых навыков, технологий и уровней, указанных в объявлении (перечисляются через запятую) - <REQUIREMENTS>
    3. **Резюме кандидата** – краткое описание опыта, реализованных проектов, знаний, сертификатов и пр. - <RESUME>
    4. **Код пользователя** – фрагмент (или несколько фрагментов) кода, написанного кандидатом, который будет использован как «техническая основа» для вопросов - <CODE>

    **Требования к генерируемому результату**

    - Вывод — **только** валидный JSON‑массив из {que_num} объектов.  
    - Каждый объект имеет два поля:  
    - `"question"` – формулировка вопроса, соответствующая уровню позиции, требованиям вакансии и особенностям предоставленного кода.  
    - `"answer"` – лаконичный (1‑3 предложения) правильный ответ, который ожидает увидеть опытный специалист.  
    - Вопросы должны охватывать разнообразные аспекты: синтаксис, алгоритмы, паттерны, оптимизацию, безопасность, инструменты (IDE, CI/CD, тестирование), лучшие практики и типичные подводные камни языка/технологий, указанных в требованиях.  
    - Учитывай уровень позиции (Junior, Middle, Senior и т.д.) и релевантный опыт из резюме: если в резюме указано, что кандидат уже работал с Django, не задавай базовый вопрос «Что такое Django?», а сосредоточься на более продвинутых темах (middleware, ORM, миграции и пр.).  
    - Если в коде присутствуют ошибки, недочёты или потенциальные улучшения, сформулируй хотя бы один вопрос, раскрывающий эту проблему (например, «Почему в данном фрагменте используется mutable default argument и как это исправить?»).  
    - Если какой‑либо из четырёх блоков полностью отсутствует или пуст, **выведи пустой массив `[]`** без дополнительных пояснений.

    **Формат вывода (строго, без лишних символов):**

    ```json
    [
        {json_item}
    ]```
    <POSITION>
    {position}
    </POSITION>
    <REQUIREMENTS>
    {requirements}
    </REQUIREMENTS>
    <RESUME>
    {resume}
    </RESUME>
    <CODE>
    {code}
    </CODE>
    """
    return prompt

def fill_theory_checker_prompt(question, ideal_answer, user_answer):
    prompt = f"""Ты — автоматический оценщик ответов на вопросы интервью на русском языке.  
    Тебе передаётся три блока текста, каждый начинается с метки и заканчивается пустой строкой:

    1. **Вопрос** – формулировка задания, которое задаёт интервьюер - <QUESTION>
    2. **Ответ системы** – «идеальный» (правильный) ответ, который считается образцом - <IDEAL_ANSWER>
    3. **Ответ пользователя** – то, что написал кандидат - <USER_ANSWER>

    Твоя задача — сравнить ответ пользователя с образцом и вывести оценку от 1 до 10 (1 — совсем неверно, 10 — полностью соответствует образцу). Оценка должна базироваться на следующих критериях (каждый критерий оценивается по 2 балла, суммарно 10 баллов):

    | Критерий                              | Что проверяется                                                                          |
    |--------------------------------------|------------------------------------------------------------------------------------------|
    | **Точность**                         | Насколько фактологически верен ответ (правильные термины, синтаксис, формулы).          |
    | **Полнота**                          | Покрыты ли все основные аспекты, указанные в образце (не упущены важные части).          |
    | **Глубина**                          | Насколько ответ раскрывает тему (приводятся детали, объяснения, причины).               |
    | **Ясность изложения**                | Чёткость формулировок, отсутствие двусмысленностей, логическая последовательность.     |
    | **Соответствие лучшим практикам**   | Учитывает ли ответ рекомендации/паттерны, принятые в индустрии (например, OOP‑принципы, security). |

    **Оценивание:**  
    - 0‑2 балла — ответ почти не соответствует критерию.  
    - 3‑4 балла — удовлетворительный, но есть заметные недостатки.  
    - 5‑6 баллов — хороший, но можно улучшить.  
    - 7‑8 баллов — очень хороший, небольшие мелочи.  
    - 9‑10 баллов — по смыслу полностью соответствует образцу или качественнее\полнее образца.

    **Твой вывод** — **только** валидный JSON‑массив из одного объекта со следующими полями:  

    ```json
    [
        {{
            "score": <число от 1 до 10>,
            "explanation": "<краткое обоснование выставленной оценки, 1‑2 предложения>"
        }}
    ]```
    
    <QUESTION>
    {question}
    </QUESTION>
    <IDEAL_ANSWER>
    {ideal_answer}
    </IDEAL_ANSWER>
    <USER_ANSWER>
    {user_answer}
    </USER_ANSWER>
    """
    print(prompt)
    return prompt


def common_parser(prompt, ollama, redis_host, redis_port):
    stream = cached_chat(
        client=ollama,
        model='gpt-oss:20b',
        messages=[{'role': 'user', 'content': prompt}],
        redis_host=redis_host,
        redis_port=redis_port,
        stream=False,
        illusion=False,
        use_cache=True,
    )
    
    result = []
    for chunk in stream:
        print(chunk)
        #print(chunk['message']['content'], end='', flush=True)
        result.append(chunk['message']['content'])
    
    result = parse_json_list(result[0])
    return result

def generate_theory_qa(position, requirements, resume, ollama, redis_host="localhost", redis_port=6379):
    """Генерируем теор. вопросы по должности, требованиям к должности и резюме
    """
    prompt = fill_theory_qa_gen_prompt(position, requirements, resume)
    return common_parser(prompt, ollama, redis_host, redis_port)

def generate_code_qa(position, requirements, resume, code, ollama, redis_host="localhost", redis_port=6379):
    """Генерируем вопросы по должности, требованиям к должности, коду пользователя и резюме
    """
    prompt = fill_code_qa_gen_prompt(position, requirements, resume, code)
    return common_parser(prompt, ollama, redis_host, redis_port)

def generate_theory_check(question, ideal_answer, user_answer, ollama, redis_host="localhost", redis_port=6379):
    """Генерируем проверку ответов на теор. вопросы по вопросу, правильному ответу и ответу пользователя
    """
    prompt = fill_theory_checker_prompt(question, ideal_answer, user_answer)
    return common_parser(prompt, ollama, redis_host, redis_port)


def test_code_qa(ollama, redis_host="localhost", redis_port=6379):
    position = "Junior Python Developer"
    requirements = "ООП, REST API, Django, PostgreSQL, Git, базовые алгоритмы, написание unit‑тестов"
    resume = """Студент 4‑го курса ИТ‑специальности. 1 год практики в Python. Реализовал небольшое веб‑приложение на Flask, знаком с Git, проходил курс «Введение в Django», написал несколько скриптов для автоматизации.
    """
    code = """
    def get_user_data(user_id):
        \"\"\"Возвращает данные пользователя из БД.\"\"\"
        conn = psycopg2.connect("dbname=test user=postgres")
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM users WHERE id = {user_id}")
        result = cur.fetchone()
        conn.close()
        return result
    """
    return generate_code_qa(position, requirements, resume, code, ollama, redis_host, redis_port)

def test_theory_qa(ollama, redis_host="localhost", redis_port=6379):
    position = "Junior Python Developer"
    requirements = "ООП, REST API, Django, PostgreSQL, Git, базовые алгоритмы, написание unit‑тестов"
    resume = """Студент 4‑го курса ИТ‑специальности. 1 год практики в Python. Реализовал небольшое веб‑приложение на Flask, знаком с Git, проходил курс «Введение в Django», написал несколько скриптов для автоматизации.
    """
    return generate_theory_qa(position, requirements, resume, ollama, redis_host, redis_port)

def test_theory_check(ollama, redis_host="localhost", redis_port=6379):
    question = "Опиши, как работает механизм garbage collection в Python."
    ideal_answer = "В CPython используется подсчёт ссылок (reference counting) и дополнительный сборщик циклических ссылок, который периодически проходит по объектам‑кандидатам и освобождает те, у кого счётчик равен нулю и которые находятся в циклах."
    user_answer = "Python считает ссылки на объекты, и когда их количество становится нулём, объект удаляется. Есть также сборщик, который ищет циклы."
    return generate_theory_check(question, ideal_answer, user_answer, ollama, redis_host, redis_port)