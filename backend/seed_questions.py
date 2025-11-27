# backend/seed_questions.py
import json
from sqlmodel import Session, select
from database import engine, create_db_and_tables
from models import Question

# ==============================================================================
# 1. SOFT SKILLS (10 вопросов — общие для всех)
# ==============================================================================
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
        "text": "Вам дали задачу, но требования кажутся противоречивыми. Что сделаете?",
        "options": [
            {"answerText": "Сделаю так, как понял, чтобы не тратить время", "isCorrect": False},
            {"answerText": "Сразу задам уточняющие вопросы аналитику или заказчику", "isCorrect": True},
            {"answerText": "Спрошу у коллеги, как он бы сделал", "isCorrect": False},
            {"answerText": "Отложу задачу до лучших времен", "isCorrect": False}
        ]
    },
    {
        "text": "Вы нашли критический баг в продакшене в пятницу вечером. Ваши действия?",
        "options": [
            {"answerText": "Сделаю вид, что не заметил, до понедельника", "isCorrect": False},
            {"answerText": "Оценю критичность, сообщу команде и, если нужно, начну фикс", "isCorrect": True},
            {"answerText": "Сразу начну править код без бэкапов и тестов", "isCorrect": False},
            {"answerText": "Напишу в общий чат 'Всё сломалось' и уйду домой", "isCorrect": False}
        ]
    },
    {
        "text": "Менеджер просит добавить 'маленькую фичу' в обход спринта и тикетов. Ваши действия?",
        "options": [
            {"answerText": "Молча сделаю, чтобы угодить менеджеру", "isCorrect": False},
            {"answerText": "Откажусь и устрою скандал", "isCorrect": False},
            {"answerText": "Объясню риски и попрошу завести задачу в трекер для приоритезации", "isCorrect": True},
            {"answerText": "Сделаю, но никому не скажу", "isCorrect": False}
        ]
    },
    {
        "text": "Новичок в команде задает 'глупые' вопросы и отвлекает вас. Как поступите?",
        "options": [
            {"answerText": "Скажу ему гуглить и не мешать", "isCorrect": False},
            {"answerText": "Выделю время (слот) для ответов или дам ссылки на документацию", "isCorrect": True},
            {"answerText": "Пожалуюсь лиду на его некомпетентность", "isCorrect": False},
            {"answerText": "Буду игнорировать сообщения", "isCorrect": False}
        ]
    },
    {
        "text": "Вы допустили ошибку, которая уронила сервис на 10 минут. Что скажете на ретроспективе?",
        "options": [
            {"answerText": "Это не я, это DevOps плохо настроили сервер", "isCorrect": False},
            {"answerText": "Признаю ошибку, расскажу, почему так вышло и как предотвратить это в будущем", "isCorrect": True},
            {"answerText": "Промолчу, надеюсь, никто не вспомнит", "isCorrect": False},
            {"answerText": "Скажу, что требования были нечеткими", "isCorrect": False}
        ]
    },
    {
        "text": "Вам нужно освоить новую технологию для проекта за 2 дня. Ваша стратегия?",
        "options": [
            {"answerText": "Скажу, что это невозможно", "isCorrect": False},
            {"answerText": "Изучу основы, сделаю MVP и буду углубляться по ходу дела", "isCorrect": True},
            {"answerText": "Буду читать толстые книги всю неделю", "isCorrect": False},
            {"answerText": "Попрошу передать задачу другому", "isCorrect": False}
        ]
    },
    {
        "text": "На код-ревью вам оставили 50 комментариев с правками. Ваша реакция?",
        "options": [
            {"answerText": "Обижусь и буду спорить по каждому пункту", "isCorrect": False},
            {"answerText": "Приму конструктив, исправлю ошибки и обсужу спорные моменты", "isCorrect": True},
            {"answerText": "Удалю код и напишу заново", "isCorrect": False},
            {"answerText": "Молча приму все правки, даже если они ломают логику", "isCorrect": False}
        ]
    },
    {
        "text": "Вы закончили свою задачу раньше срока. Что будете делать?",
        "options": [
            {"answerText": "Буду отдыхать и смотреть ютуб до конца спринта", "isCorrect": False},
            {"answerText": "Возьму следующую задачу из бэклога или помогу коллегам", "isCorrect": True},
            {"answerText": "Буду рефакторить свой код до идеала, пока время не выйдет", "isCorrect": False},
            {"answerText": "Пойду домой пораньше", "isCorrect": False}
        ]
    }
]

# ==============================================================================
# 2. ТЕОРИЯ (5 Языков x 10 Вопросов)
# ==============================================================================
theory_questions = [
    # ---------------- PYTHON ----------------
    {
        "text": "В чем разница между list и tuple в Python?",
        "level": "Intern", "tag": "python",
        "correct_answer": "List — изменяемый (mutable). Tuple — неизменяемый (immutable), быстрее, хешируемый."
    },
    {
        "text": "Что такое PEP 8?",
        "level": "Intern", "tag": "python",
        "correct_answer": "Стандарт оформления кода (Style Guide) для Python."
    },
    {
        "text": "Разница между 'is' и '=='?",
        "level": "Junior", "tag": "python",
        "correct_answer": "'==' сравнивает значения. 'is' сравнивает id объектов (ссылаются ли они на одну ячейку памяти)."
    },
    {
        "text": "Как работает Garbage Collector в Python?",
        "level": "Junior", "tag": "python",
        "correct_answer": "Reference Counting (счетчик ссылок) + GC поколений для циклических ссылок."
    },
    {
        "text": "Что делают @staticmethod и @classmethod?",
        "level": "Junior", "tag": "python",
        "correct_answer": "@classmethod получает класс (cls) первым аргументом. @staticmethod — это просто функция внутри пространства имен класса."
    },
    {
        "text": "Что такое GIL?",
        "level": "Middle", "tag": "python",
        "correct_answer": "Global Interpreter Lock — мьютекс, разрешающий выполнение только одного потока Python-кода одновременно."
    },
    {
        "text": "Итератор vs Генератор?",
        "level": "Middle", "tag": "python",
        "correct_answer": "Итератор — объект с __next__. Генератор — функция с yield, которая лениво создает значения."
    },
    {
        "text": "Как работают контекстные менеджеры (with)?",
        "level": "Middle", "tag": "python",
        "correct_answer": "Через методы __enter__ (старт) и __exit__ (финиш/ошибка). Гарантируют закрытие ресурсов."
    },
    {
        "text": "Что такое MRO?",
        "level": "Senior", "tag": "python",
        "correct_answer": "Method Resolution Order. Порядок поиска методов при наследовании (алгоритм C3 Linearization)."
    },
    {
        "text": "Зачем нужны метаклассы?",
        "level": "Senior", "tag": "python",
        "correct_answer": "Для управления созданием классов. Классы — это экземпляры метаклассов (обычно type)."
    },

    # ---------------- JAVASCRIPT ----------------
    {
        "text": "В чем разница между var, let и const?",
        "level": "Intern", "tag": "javascript",
        "correct_answer": "var — функциональная область видимости, hoisting. let/const — блочная. const нельзя переприсвоить."
    },
    {
        "text": "Что такое undefined vs null?",
        "level": "Intern", "tag": "javascript",
        "correct_answer": "Undefined — переменная есть, значения нет. Null — явное пустое значение."
    },
    {
        "text": "Разница == и ===?",
        "level": "Intern", "tag": "javascript",
        "correct_answer": "== делает приведение типов. === строгое сравнение (тип + значение)."
    },
    {
        "text": "Что такое замыкание (Closure)?",
        "level": "Junior", "tag": "javascript",
        "correct_answer": "Функция, запомнившая своё лексическое окружение (переменные), даже при вызове извне."
    },
    {
        "text": "Как работает Event Loop?",
        "level": "Junior", "tag": "javascript",
        "correct_answer": "JS однопоточный. Event Loop перекладывает задачи из очереди (Queue) в стек (Stack), когда стек пуст."
    },
    {
        "text": "Что такое Promise?",
        "level": "Junior", "tag": "javascript",
        "correct_answer": "Объект для асинхронности. Состояния: pending, fulfilled, rejected."
    },
    {
        "text": "Стрелочные функции vs Обычные?",
        "level": "Middle", "tag": "javascript",
        "correct_answer": "У стрелочных нет своего `this` (берут из контекста) и `arguments`."
    },
    {
        "text": "Как работает `this`?",
        "level": "Middle", "tag": "javascript",
        "correct_answer": "Зависит от контекста вызова. Потерянный this чинят через .bind(), call(), apply()."
    },
    {
        "text": "Microtasks vs Macrotasks?",
        "level": "Senior", "tag": "javascript",
        "correct_answer": "Microtasks (Promise) выполняются сразу после текущего кода. Macrotasks (setTimeout) — в следующем цикле."
    },
    {
        "text": "Прототипное наследование?",
        "level": "Senior", "tag": "javascript",
        "correct_answer": "Наследование идет через ссылку `__proto__` по цепочке до null."
    },

    # ---------------- JAVA ----------------
    {
        "text": "В чем разница между JDK, JRE и JVM?",
        "level": "Intern", "tag": "java",
        "correct_answer": "JDK = JRE + инструменты разработки. JRE = JVM + библиотеки. JVM выполняет байт-код."
    },
    {
        "text": "Контракт equals() и hashCode()",
        "level": "Intern", "tag": "java",
        "correct_answer": "Если объекты равны по equals, у них должен быть одинаковый hashCode. Обратное неверно."
    },
    {
        "text": "Почему String неизменяемый (immutable)?",
        "level": "Junior", "tag": "java",
        "correct_answer": "Для безопасности, потокобезопасности и использования String Pool."
    },
    {
        "text": "ArrayList vs LinkedList?",
        "level": "Junior", "tag": "java",
        "correct_answer": "ArrayList — быстрый доступ по индексу, медленная вставка. LinkedList — наоборот."
    },
    {
        "text": "Checked vs Unchecked exceptions?",
        "level": "Junior", "tag": "java",
        "correct_answer": "Checked (IOException) нужно обрабатывать (try-catch) или пробрасывать. Unchecked (RuntimeException) — не обязательно."
    },
    {
        "text": "Как работает HashMap?",
        "level": "Middle", "tag": "java",
        "correct_answer": "Массив 'бакетов'. Ключ -> hashCode -> индекс. При коллизиях используется LinkedList или Red-Black Tree (Java 8+)."
    },
    {
        "text": "Модификатор volatile?",
        "level": "Middle", "tag": "java",
        "correct_answer": "Гарантирует видимость изменений переменной для всех потоков (happens-before), но не атомарность."
    },
    {
        "text": "Жизненный цикл Bean в Spring?",
        "level": "Middle", "tag": "java",
        "correct_answer": "Instantiate -> Populate Properties -> setBeanName -> PostProcessBefore -> Init -> PostProcessAfter."
    },
    {
        "text": "Как работает Garbage Collector в Java?",
        "level": "Senior", "tag": "java",
        "correct_answer": "Generational GC (Young/Old Gen). Minor GC чистит Young, Major/Full GC чистит всё. Алгоритмы: G1, ZGC, Parallel."
    },
    {
        "text": "Проблема Diamond Problem и интерфейсы?",
        "level": "Senior", "tag": "java",
        "correct_answer": "В Java множественное наследование классов запрещено. В интерфейсах с default методами конфликт решается явным переопределением."
    },

    # ---------------- C++ ----------------
    {
        "text": "Разница между указателем (*) и ссылкой (&)?",
        "level": "Intern", "tag": "cpp",
        "correct_answer": "Указатель может быть NULL и переприсвоен. Ссылка должна быть инициализирована сразу и навсегда, не бывает NULL."
    },
    {
        "text": "Зачем нужен виртуальный деструктор?",
        "level": "Junior", "tag": "cpp",
        "correct_answer": "Чтобы при удалении объекта наследника через указатель на базовый класс вызвался деструктор наследника."
    },
    {
        "text": "Разница между malloc/free и new/delete?",
        "level": "Junior", "tag": "cpp",
        "correct_answer": "new/delete вызывают конструкторы/деструкторы и типобезопасны. malloc/free — просто выделяют память (Си)."
    },
    {
        "text": "Что такое `const` correctness?",
        "level": "Junior", "tag": "cpp",
        "correct_answer": "Использование const везде, где значение не должно меняться (параметры, методы, возвращаемые значения)."
    },
    {
        "text": "Умные указатели (smart pointers)?",
        "level": "Middle", "tag": "cpp",
        "correct_answer": "unique_ptr (владеет один), shared_ptr (счетчик ссылок), weak_ptr (не держит объект). Используют RAII."
    },
    {
        "text": "Vector vs List в STL?",
        "level": "Middle", "tag": "cpp",
        "correct_answer": "Vector — непрерывный блок памяти (быстрый доступ, медленная вставка в середину). List — связный список."
    },
    {
        "text": "Что такое RAII?",
        "level": "Middle", "tag": "cpp",
        "correct_answer": "Resource Acquisition Is Initialization. Ресурс захватывается в конструкторе и освобождается в деструкторе."
    },
    {
        "text": "Move semantics (std::move)?",
        "level": "Senior", "tag": "cpp",
        "correct_answer": "Позволяет 'перемещать' ресурсы объекта вместо копирования (C++11), используя rvalue ссылки."
    },
    {
        "text": "Разница static_cast и dynamic_cast?",
        "level": "Senior", "tag": "cpp",
        "correct_answer": "static_cast — во время компиляции (быстро). dynamic_cast — в рантайме проверяет наследование (медленно, нужен RTTI)."
    },
    {
        "text": "Как работает V-Table (таблица виртуальных методов)?",
        "level": "Senior", "tag": "cpp",
        "correct_answer": "Скрытый указатель в объекте указывает на таблицу адресов функций. Используется для полиморфизма."
    },

    # ---------------- GO (GOLANG) ----------------
    {
        "text": "В чем разница между Array и Slice?",
        "level": "Intern", "tag": "go",
        "correct_answer": "Array — фиксированная длина (часть типа). Slice — динамическая 'обертка' (указатель, длина, емкость) над массивом."
    },
    {
        "text": "Разница между make и new?",
        "level": "Junior", "tag": "go",
        "correct_answer": "new выделяет память и возвращает указатель (*T). make инициализирует slice, map, channel (возвращает T)."
    },
    {
        "text": "Как работают Goroutines?",
        "level": "Junior", "tag": "go",
        "correct_answer": "Легковесные потоки, управляемые рантаймом Go (не ОС). Меньше стека, дешевле переключение контекста."
    },
    {
        "text": "Порядок вызова defer?",
        "level": "Junior", "tag": "go",
        "correct_answer": "LIFO (Last In, First Out). Выполняются после return, но перед возвратом управления."
    },
    {
        "text": "Как работают интерфейсы в Go?",
        "level": "Middle", "tag": "go",
        "correct_answer": "Duck typing (неявная реализация). Если тип реализует все методы интерфейса, он его имплементирует."
    },
    {
        "text": "Буферизированные vs Небуферизированные каналы?",
        "level": "Middle", "tag": "go",
        "correct_answer": "Небуферизированный блокирует отправителя, пока получатель не прочтет. Буферизированный блокирует, только если буфер полон."
    },
    {
        "text": "Безопасна ли map при конкурентном доступе?",
        "level": "Middle", "tag": "go",
        "correct_answer": "Нет. При одновременной записи будет `fatal error: concurrent map writes`. Нужно использовать sync.RWMutex или sync.Map."
    },
    {
        "text": "Для чего нужен пакет Context?",
        "level": "Senior", "tag": "go",
        "correct_answer": "Для передачи дедлайнов, сигналов отмены и request-scoped данных между горутинами."
    },
    {
        "text": "Особенности GC в Go?",
        "level": "Senior", "tag": "go",
        "correct_answer": "Tricolor Mark-and-Sweep, concurrent, оптимизирован на низкую задержку (low latency), а не пропускную способность."
    },
    {
        "text": "Что такое Generics в Go (1.18+)?",
        "level": "Senior", "tag": "go",
        "correct_answer": "Позволяют писать функции и структуры, работающие с разными типами, используя параметры типов [T any]."
    }
]

# ==============================================================================
# 3. КОДИНГ (5 Языков x 3 Задачи)
# ==============================================================================
coding_tasks = [
    # --- PYTHON ---
    {
        "title": "Сумма списка (Intern)", "description": "Напишите функцию sum_list(numbers).", "level": "Intern", "tag": "python",
        "files": [{"name": "main.py", "content": "def sum_list(numbers):\n    pass\n\nif __name__ == '__main__':\n    print(sum_list([1, 2, 3]))"}]
    },
    {
        "title": "Палиндром (Junior)", "description": "Проверьте строку на палиндром (is_palindrome).", "level": "Junior", "tag": "python",
        "files": [{"name": "main.py", "content": "def is_palindrome(text):\n    pass\n\nif __name__ == '__main__':\n    print(is_palindrome('aba'))"}]
    },
    {
        "title": "FizzBuzz (Junior)", "description": "Реализуйте FizzBuzz.", "level": "Junior", "tag": "python",
        "files": [{"name": "main.py", "content": "def fizz_buzz(n):\n    pass\n\nif __name__ == '__main__':\n    print(fizz_buzz(15))"}]
    },

    # --- JAVASCRIPT ---
    {
        "title": "Сумма четных (Intern)", "description": "Функция sumEvens(arr).", "level": "Intern", "tag": "javascript",
        "files": [{"name": "index.js", "content": "function sumEvens(arr) {\n    return 0;\n}\nconsole.log(sumEvens([1, 2, 3]));"}]
    },
    {
        "title": "Разворот строки (Junior)", "description": "Функция reverseString(str).", "level": "Junior", "tag": "javascript",
        "files": [{"name": "index.js", "content": "function reverseString(str) {\n    return '';\n}\nconsole.log(reverseString('hello'));"}]
    },
    {
        "title": "Фильтр массива (Junior)", "description": "Оставьте только числа > 10.", "level": "Junior", "tag": "javascript",
        "files": [{"name": "index.js", "content": "function filterBig(arr) {\n    return [];\n}\nconsole.log(filterBig([5, 12, 8, 130]));"}]
    },

    # --- JAVA ---
    {
        "title": "Сумма массива (Intern)", "description": "Реализуйте метод sumArray в классе Main.", "level": "Intern", "tag": "java",
        "files": [{"name": "Main.java", "content": "public class Main {\n    public static int sumArray(int[] arr) {\n        return 0;\n    }\n    public static void main(String[] args) {\n        System.out.println(sumArray(new int[]{1, 2, 3}));\n    }\n}"}]
    },
    {
        "title": "Разворот строки (Junior)", "description": "Метод reverse(String input). Используйте StringBuilder.", "level": "Junior", "tag": "java",
        "files": [{"name": "Main.java", "content": "public class Main {\n    public static String reverse(String input) {\n        return \"\";\n    }\n    public static void main(String[] args) {\n        System.out.println(reverse(\"Java\"));\n    }\n}"}]
    },
    {
        "title": "Максимум в массиве (Junior)", "description": "Найдите максимальное число.", "level": "Junior", "tag": "java",
        "files": [{"name": "Main.java", "content": "public class Main {\n    public static int max(int[] arr) {\n        return 0;\n    }\n    public static void main(String[] args) {\n        System.out.println(max(new int[]{1, 5, 2}));\n    }\n}"}]
    },

    # --- C++ ---
    {
        "title": "Сумма вектора (Intern)", "description": "Функция sumVector.", "level": "Intern", "tag": "cpp",
        "files": [{"name": "main.cpp", "content": "#include <iostream>\n#include <vector>\nusing namespace std;\n\nint sumVector(vector<int> nums) {\n    return 0;\n}\n\nint main() {\n    cout << sumVector({1, 2, 3}) << endl;\n    return 0;\n}"}]
    },
    {
        "title": "Факториал (Junior)", "description": "Рекурсивная функция factorial(n).", "level": "Junior", "tag": "cpp",
        "files": [{"name": "main.cpp", "content": "#include <iostream>\nusing namespace std;\n\nint factorial(int n) {\n    return 1;\n}\n\nint main() {\n    cout << factorial(5) << endl;\n    return 0;\n}"}]
    },
    {
        "title": "Палиндром C++ (Junior)", "description": "Проверка строки string.", "level": "Junior", "tag": "cpp",
        "files": [{"name": "main.cpp", "content": "#include <iostream>\n#include <string>\nusing namespace std;\n\nbool isPalindrome(string s) {\n    return false;\n}\n\nint main() {\n    cout << isPalindrome(\"madam\") << endl;\n    return 0;\n}"}]
    },

    # --- GO (GOLANG) ---
    {
        "title": "Сумма слайса (Intern)", "description": "Функция SumSlice.", "level": "Intern", "tag": "go",
        "files": [{"name": "main.go", "content": "package main\nimport \"fmt\"\n\nfunc SumSlice(nums []int) int {\n    return 0\n}\n\nfunc main() {\n    fmt.Println(SumSlice([]int{1, 2, 3}))\n}"}]
    },
    {
        "title": "Простое число (Junior)", "description": "Функция IsPrime(n int) bool.", "level": "Junior", "tag": "go",
        "files": [{"name": "main.go", "content": "package main\nimport \"fmt\"\n\nfunc IsPrime(n int) bool {\n    return false\n}\n\nfunc main() {\n    fmt.Println(IsPrime(7))\n}"}]
    },
    {
        "title": "Подсчет слов (Junior)", "description": "WordCount возвращает map.", "level": "Junior", "tag": "go",
        "files": [{"name": "main.go", "content": "package main\nimport \"fmt\"\n\nfunc WordCount(s string) map[string]int {\n    return map[string]int{}\n}\n\nfunc main() {\n    fmt.Println(WordCount(\"foo bar foo\"))\n}"}]
    }
]

def seed_questions():
    create_db_and_tables()
    with Session(engine) as session:
        print("--- Заполнение базы данных... ---")
        
        # Soft Skills
        print(" -> Soft Skills...")
        for q in psy_questions:
            exists = session.exec(select(Question).where(Question.text == q["text"])).first()
            if not exists:
                db_q = Question(text=q["text"], type="psy", level="All", required_tag="soft", files_json=json.dumps(q["options"]))
                session.add(db_q)

        # Theory
        print(" -> Theory...")
        for q in theory_questions:
            exists = session.exec(select(Question).where(Question.text == q["text"])).first()
            if not exists:
                db_q = Question(
                    text=q["text"], 
                    type="theory", 
                    level=q["level"], 
                    required_tag=q["tag"], 
                    correct_answer=q.get("correct_answer"), 
                    files_json=None
                )
                session.add(db_q)

        # Coding
        print(" -> Coding tasks...")
        for task in coding_tasks:
            full_text = f"{task['title']}\n\n{task['description']}"
            exists = session.exec(select(Question).where(Question.text == full_text)).first()
            if not exists:
                db_q = Question(text=full_text, type="coding", level=task["level"], required_tag=task["tag"], files_json=json.dumps(task["files"]))
                session.add(db_q)

        session.commit()
        print("✅ База данных успешно обновлена (Python, JS, Java, C++, Go)!")

if __name__ == "__main__":
    seed_questions()