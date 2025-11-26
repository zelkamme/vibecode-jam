from .llm_api import cached_chat
from .tools import parse_response


def fill_helper_ai_prompt(lang, task, code, user_question):
    prompt = f"""Ты — ИИ‑интервьюер, проверяющий решение задачи по программированию.  
    Тебе будет предоставлено три элемента (в произвольном порядке, каждый в отдельном блоке кода):  

    1. **Задание** – формулировка задачи. - <TASK>
    2. **Язык** – название языка программирования (например, Python, Java, C++ и т.д.). - <LANGUAGE>
    3. **Код** – код, написанный пользователем. - <CODE>
    4. **Вопрос** - вопрос, заданный пользователем. - <USER_QUESTION>

    Твоя задача — проанализировать код относительно задания и языка и выдать **одну** короткую подсказку (1–2 предложения, максимум ≈ 30 слов). Подсказка должна:

    - указать на ошибку/недочёт, если он есть, **или**
    - предложить, как улучшить/дополнить решение, **или**
    - сообщить, что решение полностью не соответствует условию задачи.  

    **Запрещено**:  
    - генерировать или предлагать полный рабочий код;  
    - давать развернутые объяснения, примеры, выводы, уточнения.  

    **Формат вывода** — строго JSON без лишних символов, пробелов в начале/конце строки и без дополнительных полей:

    ```json
    {{
        "suggestion": "Твоя короткая подсказка"
    }}```
        <LANGUAGE>
    {lang}
    </LANGUAGE>
    <TASK>
    {task}
    </TASK>
    <CODE>
    {code}
    </CODE>
    <USER_QUESTION>
    {user_question}
    </USER_QUESTION>
    """
    return prompt

def generate_helper_ai(lang, task, code, user_question, ollama, redis_host="localhost", redis_port=6379):
    prompt = fill_helper_ai_prompt(lang, task, code, user_question)

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
        #print(chunk['message']['content'], end='', flush=True)
        result.append(chunk['message']['content'])
    
    result = parse_response(result[0], required_keys={"suggestion"})
    return result

def test_helper_ai(ollama, redis_host="localhost", redis_port=6379):
    lang = "Python"
    task = "Напишите функцию, которая принимает список целых чисел и возвращает список без дубликатов, сохранив порядок."
    code = """
    def unique_preserve_order(lst):
        seen = set()
        return 
    """
    user_question = """
    Как доделать этот код""" 
    return generate_helper_ai(lang, task, code, user_question, ollama, redis_host, redis_port)
