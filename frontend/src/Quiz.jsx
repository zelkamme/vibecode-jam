import React, { useState } from 'react';

// Принимаем: заголовок, массив вопросов и функцию "onComplete"
function Quiz({ title, questions, onComplete }) {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [showResults, setShowResults] = useState(false);

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
        <h2>{title} - Результаты</h2>
        <p className="quiz-results">
          Вы ответили правильно на {score} из {questions.length} вопросов.
        </p>
        <button className="big-button" onClick={onComplete}>
          Продолжить
        </button>
      </div>
    );
  }

  return (
    <div className="quiz-container">
      <h2>{title}</h2>
      <div className="question-section">
        <div className="question-count">
          <span>Вопрос {currentQuestionIndex + 1}</span>/{questions.length}
        </div>
        <div className="question-text">{questions[currentQuestionIndex].questionText}</div>
      </div>
      <div className="answer-section">
        {questions[currentQuestionIndex].answerOptions.map((option, index) => (
          <button
            key={index}
            className="answer-button"
            onClick={() => handleAnswerClick(option.isCorrect)}
          >
            {option.answerText}
          </button>
        ))}
      </div>
    </div>
  );
}

export default Quiz;