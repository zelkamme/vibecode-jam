from helper_ai import test_helper_ai, generate_helper_ai
from qa_review import test_qa_review, generate_qa_review
from code_review import test_code_review, generate_code_review, test_lang_detect, generate_lang_detect
from unit_tests_gen import test_unittest_gen, generate_unittests
from qa_gen import test_code_qa, test_theory_qa, test_theory_check, generate_code_qa, generate_theory_check, generate_theory_qa
from openai import OpenAI

API_KEY = "APIKEY"
# Вариант с доменом без порта (HTTPS):
BASE_URL = "https://llm.t1v.scibox.tech/v1"
# Альтернатива с IP:порт
# BASE_URL = "http://45.145.191.148:4000/v1"
llm_api = OpenAI(api_key=API_KEY, base_url=BASE_URL)
REDIS_HOST = "localhost"
REDIS_PORT = 6379

print(test_helper_ai(llm_api, REDIS_HOST, REDIS_PORT))
#helper_ai_generate

print(test_qa_review(llm_api, REDIS_HOST, REDIS_PORT))
#generate_qa_review

print(test_code_review(llm_api, REDIS_HOST, REDIS_PORT))
#generate_code_review

print(test_unittest_gen(llm_api, REDIS_HOST, REDIS_PORT))
#generate_unittests

print(test_code_qa(llm_api, REDIS_HOST, REDIS_PORT))
#generate_code_qa

print(test_theory_qa(llm_api, REDIS_HOST, REDIS_PORT))
#generate_theory_qa

print(test_theory_check(llm_api, REDIS_HOST, REDIS_PORT))
#generate_theory_check

print(test_lang_detect(llm_api, REDIS_HOST, REDIS_PORT))
#generate_lang_detect