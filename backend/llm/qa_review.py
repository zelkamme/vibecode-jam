from llm_api import cached_chat
from tools import parse_response


def fill_qa_review_prompt(lang, question, answer, skill_level="Junior"):
    prompt = f"""Вы — эксперт по языку программирования {lang}.
    Ваша задача — оценить заданный вопрос для собеседования на позицию {skill_level} {lang}-разработчик и ожидаемый ответ на него.

    Вы получите три фрагмента информации (в указанном порядке, каждый на отдельной строке):
    1. Вопрос собеседования (на русском языке) - <QUESTION>
    2. Ожидаемый ответ (на русском языке) - <ANSWER>
    3. Язык программирования - <LANGUAGE>

    Ваша задача:
    1. **Оценить вопрос** по шкале от 1 до 10 (1 – плохой, 10 – идеальный). Оценка должна учитывать:
    - релевантность к выбранному языку;
    - ясность формулировки;
    - уровень сложности, подходящий для собеседования;
    - отсутствие двусмысленностей и ошибок.

    2. **Перефразировать**:
    - вопрос так, чтобы он стал более понятным, но сохранил исходный смысл;
    - ответ так, чтобы он был коротким, точным и полностью корректным с точки зрения языка.

    3. **Вернуть строго JSON** без какого‑либо дополнительного текста, markdown‑разметки или пояснений:
    
    Если в исходной паре вопрос-ответ есть недостатки, дай **краткую, конструктивную критику** (не более 2‑3 предложений). Если критика не требуется – верни `None`.

    ```json
    {{
        "question_score": "<integer 1‑10>",
        "rephrased_que": "<перефразированный вопрос>",
        "rephrased_ans": "<перефразированный ответ>",
        "critique": "<критика исходной пары вопрос-ответ или None>",
    }}```
    <LANGUAGE>
    {lang}
    </LANGUAGE>
    <QUESTION>
    {question}
    </QUESTION>
    <ANSWER>
    {answer}
    </ANSWER>
    """
    return prompt

def generate_qa_review(lang, question, answer, llm_api, redis_host="localhost", redis_port=6379):
    prompt = fill_qa_review_prompt(lang, question, answer)

    stream = cached_chat(
        client=llm_api,
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
    
    result = parse_response(result[0], {"question_score", "rephrased_que", "rephrased_ans", "critique"})
    return result

def test_qa_review(llm_api, redis_host="localhost", redis_port=6379):
    lang = "Python"
    question = "Напишите функцию, которая принимает список целых чисел и возвращает список без дубликатов, сохранив порядок."
    answer = """
    def unique_preserve_order(lst):
        seen = set()
        return [x for x in lst if not (x in seen or seen.add(x))]
    """
    return generate_qa_review(lang, question, answer, llm_api, redis_host, redis_port)
