// frontend/src/RegistrationPage.jsx

import React, { useState } from 'react';

function RegistrationPage() {
  const [name, setName] = useState('');
  const [level, setLevel] = useState('Джун');

  const handleRegister = () => {
    if (!name.trim()) {
      alert('Пожалуйста, введите ваше имя.');
      return;
    }

    // 1. Получаем текущую "базу данных" кандидатов из localStorage
    const db = JSON.parse(localStorage.getItem('vibecode_candidates_db')) || [];

    // 2. Создаем нового кандидата
    const newCandidate = {
      id: Date.now(), // Простой уникальный ID
      name: name,
      level: level,
      status: 'В процессе',
      // Остальные поля будут добавлены после завершения
    };

    // 3. Добавляем его в базу и сохраняем обратно
    db.push(newCandidate);
    localStorage.setItem('vibecode_candidates_db', JSON.stringify(db));

    // 4. "Логиним" этого кандидата, чтобы система знала, кто сейчас проходит тест
    localStorage.setItem('userRole', 'candidate');
    localStorage.setItem('currentCandidateId', newCandidate.id);

    // 5. Отправляем на начало собеседования
    window.location.href = '/interview';
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>Регистрация кандидата</h2>
        <div className="registration-form">
          <input 
            type="text" 
            placeholder="Ваше имя и фамилия" 
            value={name} 
            onChange={(e) => setName(e.target.value)} 
          />
          <select value={level} onChange={(e) => setLevel(e.target.value)}>
            <option>Стажер</option>
            <option>Джун</option>
            <option>Мидл</option>
            <option>Сеньор</option>
          </select>
          <button className="big-button candidate-btn" onClick={handleRegister}>
            Начать собеседование
          </button>
        </div>
      </div>
    </div>
  );
}

export default RegistrationPage;