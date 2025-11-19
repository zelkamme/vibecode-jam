import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function RegistrationPage() {
  const [name, setName] = useState('');
  const [vacancies, setVacancies] = useState([]);
  const [selectedVacancy, setSelectedVacancy] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate(); // Используем хук для навигации

  // Загружаем вакансии при старте
  useEffect(() => {
    axios.get('http://localhost:8000/api/vacancies')
      .then(res => {
        setVacancies(res.data);
        if (res.data.length > 0) {
          setSelectedVacancy(res.data[0].id);
        }
        setLoading(false);
      })
      .catch(err => console.error("Ошибка загрузки вакансий:", err));
  }, []);

  const handleRegister = async () => {
    if (!name.trim()) {
      alert('Введите имя');
      return;
    }

    try {
      const response = await axios.post('http://localhost:8000/api/register', {
        username: name,
        vacancy_id: selectedVacancy
      });

      const data = response.data;

      // Сохраняем данные в localStorage
      localStorage.setItem('userRole', 'candidate');
      localStorage.setItem('currentCandidateId', data.user_id);
      localStorage.setItem('candidateLevel', data.level); // Сохраняем уровень!

      // Сразу идем на интервью (пропуская выбор уровня)
      window.location.href = '/interview'; 

    } catch (error) {
      alert('Ошибка регистрации. Проверьте бэкенд.');
      console.error(error);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>Регистрация на вакансию</h2>
        <div className="registration-form">
          <input 
            type="text" 
            placeholder="Ваше имя и фамилия" 
            value={name} 
            onChange={(e) => setName(e.target.value)} 
          />
          
          {loading ? <p>Загрузка вакансий...</p> : (
            <select 
              value={selectedVacancy} 
              onChange={(e) => setSelectedVacancy(e.target.value)}
              className="glass-input"
              style={{background: 'rgba(0,0,0,0.2)', color: 'white', border: '1px solid gray'}}
            >
              {vacancies.map(v => (
                <option key={v.id} value={v.id}>
                  {v.title} ({v.level})
                </option>
              ))}
            </select>
          )}

          <button className="big-button candidate-btn" onClick={handleRegister}>
            Приступить к тестированию
          </button>
          <button className="link-button" onClick={() => navigate('/login')}>
            Назад
          </button>
        </div>
      </div>
    </div>
  );
}

export default RegistrationPage;