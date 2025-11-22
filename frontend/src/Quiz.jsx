import React, { useState } from 'react';

function Quiz({ title, questions, onComplete }) {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [showResults, setShowResults] = useState(false);

  const currentQuestion = questions[currentQuestionIndex];

  // Обработка клика по ответу
  const handleAnswerClick = (isCorrect) => {
    if (isCorrect) {
      setScore(score + 1);
    }

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
          Ваш результат сохранен.
        </p>
        <button className="big-button" onClick={onComplete}>
          Перейти к следующему этапу
        </button>
      </div>
    );
  }

  // Защита от пустых данных
  if (!currentQuestion) return <div>Ошибка данных</div>;

  // Если options пустые или не пришли
  const options = currentQuestion.answerOptions || [];

  return (
    <div className="quiz-container">
      <h2 style={{fontSize: '1.5rem', marginBottom: '1rem', color:'#aaa'}}>{title}</h2>
      
      <div className="question-section">
        <div className="question-count" style={{marginBottom: '1rem', opacity: 0.7}}>
          Вопрос {currentQuestionIndex + 1} из {questions.length}
        </div>
        
        {/* Текст вопроса */}
        <div className="question-text" style={{fontSize: '1.3rem', fontWeight: 'bold', marginBottom: '2rem', minHeight: '60px'}}>
            {currentQuestion.questionText}
        </div>
      </div>

      <div className="answer-section" style={{display:'flex', flexDirection:'column', gap:'0.8rem'}}>
        {options.length > 0 ? (
          options.map((option, index) => (
            <button
              key={index}
              className="answer-button"
              onClick={() => handleAnswerClick(option.isCorrect)}
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
          ))
        ) : (
          <div style={{color: '#ff5555', border: '1px dashed #ff5555', padding: '1rem'}}>
             ⚠️ У этого вопроса нет вариантов ответа. (Ошибка JSON в БД)
             <br/>
             <button 
                onClick={() => handleAnswerClick(true)} // Пропускаем вопрос
                style={{marginTop:'1rem', padding:'0.5rem', cursor:'pointer'}}
             >
                Пропустить (Debug Skip)
             </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default Quiz;