from backend.llm.llm_api import cached_chat
from backend.llm.tools import parse_response


def fill_unittest_gen_prompt(lang, task, code):
    prompt = f"""Ты — помощник, который генерирует набор юнит‑тестов для проверяемого кода, написанного пользователем в рамках технического собеседования.  
    Твоя задача – получить от пользователя три обязательных входных блока, а затем вывести **только** валидный JSON‑объект, содержащий минимум три теста.

    **Входные данные (от пользователя):**

    1. **Задача** – краткое описание требуемой функциональности (что должен делать код). - <TASK>
    2. **Язык программирования** – название языка программирования. - <LANGUAGE>
    3. **Код** – полностью предоставленный пользователем фрагмент/функцию/класс, который необходимо протестировать. - <CODE>

    **Твои инструкции:**

    - Выбери подходящий фреймворк для юнит‑тестов, соответствующий указанному языку (unittest/pytest для Python, JUnit для Java, Mocha/Jest для JavaScript, NUnit/xUnit для C#, testing для Go и т.п.).  
    - Сгенерируй **не менее трех** независимых тестов, каждый из которых проверяет отдельный аспект реализации:
    * типичный (корректный) ввод,  
    * граничные/крайние случаи,  
    * ошибочные/исключительные ситуации (если применимо).  
    - Каждый тест должен быть самодостаточным, читаемым и компилируемым/исполняемым без дополнительных правок кода.  
    - В именах тестов используй понятные описательные названия (например, `test_add_positive_numbers`).  
    - Не добавляй комментарии, пояснения, заголовки или любые другие тексты за пределами требуемого JSON‑формата.  
    - Выводи **только** JSON‑объект следующей структуры, без лишних слов и форматирования markdown:

    ```json
    {{
        "unit_test1": "<тест‑кейс 1>",
        "unit_test2": "<тест‑кейс 2>",
        "unit_test3": "<тест‑кейс 3>"
    }}
    ```
    <LANGUAGE>
    {lang}
    </LANGUAGE>
    <TASK>
    {task}
    </TASK>
    <CODE>
    {code}
    </CODE>
    """
    return prompt

def generate_unittests(lang, task, code, ollama, redis_host="localhost", redis_port=6379):
    prompt = fill_unittest_gen_prompt(lang, task, code)

    stream = cached_chat(
        client=ollama,
        model='gemma3:12b',
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
    
    result = parse_response(result[0], required_keys={"unit_test1", "unit_test2", "unit_test3"})   
    return result

def test_unittest_gen(ollama, redis_host="localhost", redis_port=6379):
    lang = "Python"
    task = "Напишите функцию, которая принимает список целых чисел и возвращает список без дубликатов, сохранив порядок."
    code = """
    def unique_preserve_order(lst):
        seen = set()
        return [x for x in lst if not (x in seen or seen.add(x))]
    """
    #code2 left in for testing purposes
    code2 = """
    def uniq(lst):
        result = []
        for i in lst:
            if i not in result:
                result.append(i)
        return result
    """
    return generate_unittests(lang, task, code, ollama, redis_host, redis_port)

