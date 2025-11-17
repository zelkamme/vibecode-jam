// frontend/src/PsyTest.jsx
import React from 'react';
import Quiz from './Quiz';
import { psyQuestions } from './questions'; // Импортируем вопросы

function PsyTest({ onComplete }) {
  return (
    <div className="centered-container">
      <Quiz 
        title="Этап 1: Психологический тест"
        questions={psyQuestions}
        onComplete={onComplete}
      />
    </div>
  );
}

export default PsyTest;