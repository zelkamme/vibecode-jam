import React from 'react';

// onStart - это функция, которую мы получим от App.jsx
function WelcomeScreen({ onStart }) {
  return (
    <div className="centered-container">
      <h1>Добро пожаловать в VibeCode Jam</h1>
      <p>Платформа для технических собеседований будущего.</p>
      <button className="big-button" onClick={onStart}>
        Начать собеседование
      </button>
    </div>
  );
}

export default WelcomeScreen;