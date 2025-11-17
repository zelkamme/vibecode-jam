import React from 'react';

// onSelect - это функция, которую мы получим от App.jsx
function LevelSelection({ onSelect }) {
  const levels = ['Стажер', 'Джун', 'Мидл', 'Сеньор'];

  return (
    <div className="centered-container">
      <h2>Выберите ваш уровень</h2>
      <div className="level-buttons">
        {levels.map(level => (
          <button key={level} className="big-button" onClick={() => onSelect(level)}>
            {level}
          </button>
        ))}
      </div>
    </div>
  );
}

export default LevelSelection;