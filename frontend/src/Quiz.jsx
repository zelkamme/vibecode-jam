import React, { useState } from 'react';
import axios from 'axios'; // <--- НЕ ЗАБУДЬТЕ ИМПОРТ

function Quiz({ title, questions, onComplete }) {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [showResults, setShowResults] = useState(false);

  const currentQuestion = questions[currentQuestionIndex];

  // Обработка клика по ответу
  const handleAnswerClick = async (option) => {
    const isCorrect = option.isCorrect;
    
    // --- ОТПРАВКА НА БЭКЕНД ---
    try {
        const userId = localStorage.getItem('currentCandidateId');
        if (userId) {
            await axios.post('http://localhost:8000/api/answers', {
                user_id: parseInt(userId),
                question_id: currentQuestion.id,
                answer: option.answerText,
                is_correct: isCorrect,
                score: isCorrect ? 1 : 0 // 1 балл за правильный ответ
            });
            console.log("Ответ сохранен в БД");
        }
    } catch (error) {
        console.error("Ошибка сохранения ответа:", error);
    }
    // ---------------------------

    const nextQuestion = currentQuestionIndex + 1;
    if (nextQuestion < questions.length) {
      setCurrentQuestionIndex(nextQuestion);
    } else {
      setShowResults(true);
    }
  };

  if (showResults) {
    return (
      <div className="quiz-container">
        <h2>{title} — Завершено</h2>
        <p className="quiz-results">
          Ваши ответы сохранены в базе данных.
        </p>
        <button className="big-button" onClick={onComplete}>
          Перейти к следующему этапу
        </button>
      </div>
    );
  }

  if (!currentQuestion) return <div>Ошибка данных</div>;
  const options = currentQuestion.answerOptions || [];

  return (
    <div className="quiz-container">
      <h2 style={{fontSize: '1.5rem', marginBottom: '1rem', color:'#aaa'}}>{title}</h2>
      
      <div className="question-section">
        <div className="question-count" style={{marginBottom: '1rem', opacity: 0.7}}>
          Вопрос {currentQuestionIndex + 1} из {questions.length}
        </div>
        <div className="question-text" style={{fontSize: '1.3rem', fontWeight: 'bold', marginBottom: '2rem', minHeight: '60px'}}>
            {currentQuestion.questionText}
        </div>
      </div>

      <div className="answer-section" style={{display:'flex', flexDirection:'column', gap:'0.8rem'}}>
        {options.map((option, index) => (
            <button
              key={index}
              className="answer-button"
              // ВАЖНО: Передаем весь объект option, а не просто isCorrect
              onClick={() => handleAnswerClick(option)} 
              style={{
                  padding: '1rem',
                  background: 'rgba(255,255,255,0.1)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  color: 'white',
                  textAlign: 'left',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
              }}
              onMouseOver={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.2)'}
              onMouseOut={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.1)'}
            >
              {option.answerText}
            </button>
        ))}
      </div>
    </div>
  );
}

export default Quiz;