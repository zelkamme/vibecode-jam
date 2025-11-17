// frontend/src/LoginPage.jsx

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function LoginPage() {
  const navigate = useNavigate();
  const [isHrLogin, setIsHrLogin] = useState(false);
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleHrLoginAttempt = () => {
    // В реальном приложении здесь будет запрос к бэкенду
    // А у нас - хардкод. Правильный пароль - 'admin'
    if (password === 'admin') {
      localStorage.setItem('userRole', 'hr');
      window.location.href = '/hr/dashboard';
    } else {
      setError('Неверный пароль');
    }
  };
  

    // Если не показываем форму для HR
    if (!isHrLogin) {
        return (
        <div className="login-container">
            <div className="login-card">
            <h1>VibeCode Jam</h1>
            <p>Платформа для технических собеседований</p>
            <div className="login-buttons">
                <button className="big-button" onClick={() => navigate('/register')}>
                Я Кандидат
                </button>
                <button className="link-button" onClick={() => setIsHrLogin(true)}>
                Войти как HR
                </button>
            </div>
            </div>
        </div>
        );
    }
    // ...
    
  // Если показываем форму для HR
  return (
    <div className="login-container">
      <div className="login-card">
        <h2>Вход для HR</h2>
        <div className="registration-form">
          <input 
            type="password" 
            placeholder="Пароль" 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <p className="error-message">{error}</p>}
          <button className="big-button" onClick={handleHrLoginAttempt}>
            Войти
          </button>
          <button className="link-button" onClick={() => setIsHrLogin(false)}>
            Назад
          </button>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;