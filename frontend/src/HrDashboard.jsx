import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios'; // Не забудь импортировать axios!

function HrDashboard() {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // ЗАПРОС К БЭКЕНДУ ВМЕСТО localStorage
    axios.get('http://localhost:8000/api/candidates')
      .then(response => {
        setCandidates(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error("Ошибка загрузки кандидатов:", error);
        setLoading(false);
      });
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    window.location.href = '/login';
  };

  return (
    <div className="hr-dashboard-page">
      <header className="hr-header">
        <h1>Панель управления HR</h1>
        <Link to="/hr/create-task" className="big-button" style={{textDecoration: 'none', fontSize: '1rem'}}>
          + Создать задачу
        </Link>
        <button onClick={handleLogout} className="logout-button">Выйти</button>
      </header>

      <main className="hr-main">
        <div className="candidate-list-container">
          <h3>Список кандидатов (Live DB)</h3>
          {loading ? <p style={{color:'white'}}>Загрузка...</p> : (
            <div className="candidate-list">
              <table>
                <thead>
                  <tr>
                    <th>Кандидат</th>
                    <th>Уровень</th>
                    <th>Статус</th>
                    <th>Баллы</th>
                    <th>Отчет</th>
                  </tr>
                </thead>
                <tbody>
                  {candidates.length > 0 ? (
                    candidates.map(candidate => (
                      <tr key={candidate.id}>
                        <td>{candidate.name}</td>
                        <td>{candidate.level}</td>
                        <td>{candidate.status}</td>
                        <td>{candidate.score}</td>
                        <td>
                          {candidate.status === 'Завершено' ? (
                            <Link to={`/report/${candidate.id}`} className="view-report-link">
                              Открыть
                            </Link>
                          ) : (
                            <span style={{opacity:0.3}}>—</span>
                          )}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="5" className="no-candidates-cell">
                        Кандидатов пока нет.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default HrDashboard;