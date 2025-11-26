import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Quiz from './Quiz';

function PsyTest({ onComplete }) {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Загружаем вопросы из БД
    axios.get('http://localhost:8000/api/questions/psy')
      .then(response => {
        setQuestions(response.data); // Бэк теперь возвращает правильный формат
        setLoading(false);
      })
      .catch(error => {
        console.error("Ошибка загрузки тестов:", error);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="centered-container"><h2>Загрузка теста Soft Skills...</h2></div>;

  if (questions.length === 0) {
    return (
      <div className="centered-container">
        <div className="glass-card">
          <h2>Вопросов пока нет :(</h2>
          <p style={{ opacity: 0.7, marginBottom: '1.5rem' }}>
            База данных пуста. Запустите seed_questions.py на бэкенде.
          </p>
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
        title="Этап 1: Soft Skills & Психология"
        questions={questions}
        onComplete={onComplete}
      />
    </div>
  );
}

export default PsyTest;