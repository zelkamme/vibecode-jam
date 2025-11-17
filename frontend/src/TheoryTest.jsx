// frontend/src/TheoryTest.jsx

import React, { useEffect, useState } from 'react';
import mermaid from 'mermaid';
import Quiz from './Quiz';
import { theoryQuestions } from './questions';

// --- НОВАЯ СЕКЦИЯ: НАСТРОЙКА ТЕМЫ ДЛЯ MERMAID ---
// Мы создаем свою тему, чтобы управлять цветами и текстом
mermaid.initialize({
  startOnLoad: true,
  theme: 'base', // Используем базовую тему, чтобы переопределить ее
  themeVariables: {
    background: 'transparent', // Прозрачный фон
    primaryColor: '#FFF',       // Цвет фона нод
    primaryTextColor: '#000',  // Цвет текста
    primaryBorderColor: '#7C4DFF',
    lineColor: '#FFF',          // Цвет линий
    secondaryColor: '#FFD180',
    tertiaryColor: '#B2FF59'
  }
});
// ---------------------------------------------------

function TheoryTest({ onComplete }) {
  const [view, setView] = useState('mindmap');

  useEffect(() => {
    if (view === 'mindmap') {
      // Эта функция теперь просто ищет и рендерит диаграммы
      mermaid.contentLoaded();
    }
  }, [view]);

  if (view === 'quiz') {
    return (
      <Quiz
        title="Этап 2: Теоретический тест"
        questions={theoryQuestions}
        onComplete={onComplete}
      />
    );
  }

  return (
    <>
      <h2>Этап 2: Теоретическая подготовка</h2>
      <p className="placeholder-text">
        Ниже представлена карта знаний для Junior Python разработчика. <br />
        Изучите ее перед началом теста.
      </p>

      {/* Убираем лишний div-контейнер, чтобы стили применялись правильно */}
      <div className="mermaid">
        {`
          mindmap
            root((Junior Python Dev))
              Базовый синтаксис
                Типы данных (str, int, float)
                Структуры данных (list, dict, set, tuple)
                Условные операторы и циклы
              Функции и ООП
                Написание функций
                Классы и объекты (базово)
              Инструменты
                Git (основы)
                Виртуальные окружения (venv)
              Фреймворки
                Опыт с одним из: Django / FastAPI / Flask
        `}
      </div>

      <button className="big-button" onClick={() => setView('quiz')}>
        Начать тест
      </button>
    </>
  );
}

export default TheoryTest;