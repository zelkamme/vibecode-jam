from ollama import Client
from helper_ai import test_helper_ai, generate_helper_ai
from qa_review import test_qa_review, generate_qa_review
from code_review import test_code_review, generate_code_review
from unit_tests_gen import test_unittest_gen, generate_unittests
from qa_gen import test_code_qa, test_theory_qa, test_theory_check, generate_code_qa, generate_theory_check, generate_theory_qa

ollama = Client(host="localhost")
REDIS_HOST = "localhost"
REDIS_PORT = 6379

print(test_helper_ai(ollama, REDIS_HOST, REDIS_PORT))
#helper_ai_generate

print(test_qa_review(ollama, REDIS_HOST, REDIS_PORT))
#generate_qa_review

print(test_code_review(ollama, REDIS_HOST, REDIS_PORT))
#generate_code_review

print(test_unittest_gen(ollama, REDIS_HOST, REDIS_PORT))
#generate_unittests

print(test_code_qa(ollama, REDIS_HOST, REDIS_PORT))
#generate_code_qa

print(test_theory_qa(ollama, REDIS_HOST, REDIS_PORT))
#generate_theory_qa

print(test_theory_check(ollama, REDIS_HOST, REDIS_PORT))
#generate_theory_check