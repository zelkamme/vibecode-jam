// frontend/src/TheoryTest.jsx

import React, { useEffect, useState } from 'react';
import axios from 'axios';

function TheoryTest({ onComplete }) {
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const userLevel = localStorage.getItem('candidateLevel') || 'Intern';
    
    axios.get(`http://localhost:8000/api/questions/theory/${userLevel}`)
      .then(response => {
        setQuestions(response.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const handleNext = () => {
    // Здесь можно отправлять ответ на бэкенд, если нужно
    console.log(`Ответ на вопрос ${questions[currentIndex].id}:`, userAnswer);
    
    const next = currentIndex + 1;
    if (next < questions.length) {
      setCurrentIndex(next);
      setUserAnswer('');
    } else {
      onComplete();
    }
  };

  if (loading) return <div className="centered-container"><h2>Загрузка вопросов...</h2></div>;

  if (questions.length === 0) {
    return (
      <div className="centered-container">
        <div className="glass-card">
          <h2>Вопросов нет</h2>
          <p>HR еще не добавил теоретические вопросы для этого уровня.</p>
          <button className="big-button" onClick={onComplete}>Пропустить</button>
        </div>
      </div>
    );
  }

  const currentQ = questions[currentIndex];
  // Парсим текст вопроса (в HR панели заголовок и описание склеиваются через \n\n)
  const [title, desc] = currentQ.questionText.split('\n\n');

  return (
    <div className="centered-container">
      <div className="quiz-container" style={{textAlign:'left'}}>
        <div className="question-count" style={{textAlign:'center', marginBottom:'1rem'}}>
          Вопрос {currentIndex + 1} из {questions.length}
        </div>
        
        {/* ТЕКСТ ВОПРОСА */}
        <h2 style={{fontSize: '1.5rem', marginBottom:'0.5rem'}}>{title}</h2>
        {desc && <p style={{opacity:0.8, whiteSpace:'pre-wrap', marginBottom:'1.5rem'}}>{desc}</p>}

        {/* ПОЛЕ ДЛЯ СВОБОДНОГО ОТВЕТА */}
        <textarea
          className="glass-input"
          style={{width:'100%', minHeight:'150px', resize:'none', marginBottom:'1rem', fontSize:'1rem'}}
          placeholder="Введите ваш ответ здесь..."
          value={userAnswer}
          onChange={(e) => setUserAnswer(e.target.value)}
        />

        <button className="big-button" onClick={handleNext} style={{width:'100%'}}>
          {currentIndex === questions.length - 1 ? "Завершить теорию" : "Следующий вопрос"}
        </button>
      </div>
    </div>
  );
}

export default TheoryTest;