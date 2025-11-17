// Вопросы для психологического теста
export const psyQuestions = [
  {
    questionText: 'Когда вы сталкиваетесь со сложной задачей, ваша первая реакция:',
    answerOptions: [
      { answerText: 'Разбить ее на более мелкие подзадачи', isCorrect: true },
      { answerText: 'Отложить на потом, чтобы подумать', isCorrect: false },
      { answerText: 'Сразу спросить помощи у коллег', isCorrect: false },
      { answerText: 'Почувствовать стресс и беспокойство', isCorrect: false },
    ],
  },
  // ... добавьте еще 9 похожих вопросов ...
  {
    questionText: 'Наиболее важным в командной работе вы считаете:',
    answerOptions: [
      { answerText: 'Четкое разделение обязанностей', isCorrect: false },
      { answerText: 'Открытое общение и взаимопомощь', isCorrect: true },
      { answerText: 'Сильного лидера', isCorrect: false },
      { answerText: 'Минимум совещаний', isCorrect: false },
    ],
  },
];

// Вопросы для теоретического теста по Python
export const theoryQuestions = [
  {
    questionText: 'Какой тип данных является неизменяемым (immutable) в Python?',
    answerOptions: [
      { answerText: 'list', isCorrect: false },
      { answerText: 'dict', isCorrect: false },
      { answerText: 'tuple', isCorrect: true },
      { answerText: 'set', isCorrect: false },
    ],
  },
  // ... добавьте еще 9 вопросов по основам Python ...
  {
    questionText: 'Что выведет код: `print(type({1, 2, 3}))`?',
    answerOptions: [
      { answerText: "<class 'list'>", isCorrect: false },
      { answerText: "<class 'dict'>", isCorrect: false },
      { answerText: "<class 'tuple'>", isCorrect: false },
      { answerText: "<class 'set'>", isCorrect: true },
    ],
  },
];

// Для краткости я добавил по 2 вопроса. Вам нужно будет добавить до 10 в каждый массив.