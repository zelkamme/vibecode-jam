from llm_api import common_llm_call
from tools import parse_response


def fill_code_review_prompt(lang, question, ideal_answer, user_answer, position):
    prompt = f"""Ты – высококвалифицированный ревьюер кода, проводящий техническое собеседование на должность {position} ({lang}).  
    Тебе передаётся следующая информация (в порядке перечисления):  

    1. Язык программирования – <LANGUAGE>. 
    2. Вопрос/задание, которое было задано кандидату. <QUESTION>
    3. «Эталонный» (идеальный) код‑пример из банка ответов. <IDEAL_ANSWER>
    4. Код, написанный пользователем (кандидатом). <USER_ANSWER> 

    Твоя задача — опираясь на идеальное решение в теге <IDEAL_ANSWER> оценить код написанный пользователем в теге <USER_ANSWER> по двум критериям:  

    * **functional_score** – насколько решение корректно решает поставленную задачу (от 1 — полностью неверно до 10 — полностью правильно, учитывая алгоритмическую точность, обработку граничных случаев и соответствие требованиям задания).  
    * **stylistic_score** – насколько код соответствует принятым в данном языке стилистическим и конвенционным стандартам (от 1 — полный стилистический беспредел до 10 — идеальная читаемость, чистый стиль, следование PEP‑8 / Google Style / Idiomatic …).  

    Если в коде пользователя есть недостатки, дай **краткую, конструктивную критику (на русском языке)** (не более 2‑3 предложений). Если критика не требуется – верни `None`.

    **Вывод** — строго в формате JSON без какого‑либо дополнительного текста:  

    ```json
    {{
    "functional_score": "<число от 1 до 10>",
    "stylistic_score": "<число от 1 до 10>",
    "critique": "<текст критики или None>"
    }}
    ```
    <LANGUAGE>{lang}</LANGUAGE>
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
    return prompt

def generate_code_review(lang, question, ideal_answer, user_answer, position, llm_api, redis_host="localhost", redis_port=6379):
    """Код ревью - общая и стилистическая оценки, критика:
    Вход язык, вопрос, эталонный код, код юзера
    Выход: функциональная оценка, стилистическая оценка, критика
    """
    prompt = fill_code_review_prompt(lang, question, ideal_answer, user_answer, position)
    result = common_llm_call(prompt, llm_api, redis_host, redis_port)
    result = parse_response(result[0], required_keys={"functional_score", "stylistic_score", "critique"})
    
    return result    

def test_code_review(llm_api, redis_host="localhost", redis_port=6379):
    lang = "Python"
    question = "Напишите функцию, которая принимает список целых чисел и возвращает список без дубликатов, сохранив порядок."
    ideal_answer = """
    def unique_preserve_order(lst):
        seen = set()
        return [x for x in lst if not (x in seen or seen.add(x))]
    """
    user_answer = """
    def uniq(lst):
        result = []
        for i in lst:
            if i not in result:
                result.append(i)
        return result
    """
    position = "Junior"
    return generate_code_review(lang, question, ideal_answer, user_answer, position, llm_api, redis_host, redis_port)

def fill_lang_detect_prompt(code):
    prompt = f"""You are a highly qualified code reviewer - you have to output the programming language of the code provided to you in tags <CODE></CODE>.
    You output data ONLY in this json format:
    ```json
    {{
        "lang": "<the programming language of the code>",
    }}
    ```
    <CODE>
    {code}
    </CODE>
    """
    return prompt

def generate_lang_detect(code, llm_api, redis_host="localhost", redis_port=6379):
    """Детект ЯП:
    Вход: код
    Выход: язык
    """
    prompt = fill_lang_detect_prompt(code)
    result = common_llm_call(prompt, llm_api, redis_host, redis_port)
    result = parse_response(result[0], required_keys={"lang"})
    
    return result 

def test_lang_detect(llm_api, redis_host="localhost", redis_port=6379):
    code = """
    def unique_preserve_order(lst):
        seen = set()
        return [x for x in lst if not (x in seen or seen.add(x))]
    """
    code2 = """
    def uniq(lst):
        result = []
        for i in lst:
            if i not in result:
                result.append(i)
        return result
    """

    return generate_lang_detect(code, llm_api, redis_host, redis_port)