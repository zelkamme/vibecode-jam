import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Quiz from './Quiz';

function PsyTest({ onComplete }) {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Загружаем вопросы из БД
    axios.get('/api/questions/psy')
      .then(response => {
        setQuestions(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error("Ошибка загрузки тестов:", error);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="centered-container"><h2>Загрузка теста...</h2></div>;

  if (questions.length === 0) {
    return (
      <div className="centered-container">
        <div className="glass-card">
          <h2>Вопросов пока нет :(</h2>
          <p style={{ opacity: 0.7, marginBottom: '1.5rem' }}>
            База данных пуста. Добавьте вопросы через админку или включите автозаполнение.
          </p>
          {/* Вот кнопка, которая вызывает onComplete и пускает дальше */}
          <button className="big-button" onClick={onComplete}>
            Пропустить этот этап
          </button>
        </div>
      </div>
    );
  }
  return (
    <div className="centered-container">
      <Quiz 
        title="Этап 1: Психологический тест"
        questions={questions}
        onComplete={onComplete}
      />
    </div>
  );
}

export default PsyTest;