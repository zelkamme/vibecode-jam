// frontend/src/HrDashboard.jsx

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function HrDashboard() {
  const [candidates, setCandidates] = useState([]);

  useEffect(() => {
    const db = JSON.parse(localStorage.getItem('vibecode_candidates_db')) || [];
    setCandidates(db);
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    window.location.href = '/login';
  };

  return (
    <div className="hr-dashboard-page">
      <header className="hr-header">
        <h1>Панель управления HR</h1>
        <button onClick={handleLogout} className="logout-button">Выйти</button>
      </header>
      <main className="hr-main">
        <div className="candidate-list-container">
          <h3>Список кандидатов</h3>
          <div className="candidate-list">
            <table>
              <thead>
                <tr>
                  <th>Кандидат</th>
                  <th>Уровень</th>
                  <th>Статус</th>
                  <th>Общий балл</th>
                  <th>Действия</th>
                </tr>
              </thead>
              {/* --- ПОЛНОСТЬЮ ПЕРЕПИСАННАЯ ЛОГИКА ОТОБРАЖЕНИЯ --- */}
              <tbody>
                {candidates.length > 0 ? (
                  candidates.map(candidate => (
                    <tr key={candidate.id}>
                      <td>{candidate.name || 'Нет имени'}</td>
                      <td>{candidate.level || 'N/A'}</td>
                      <td>{candidate.status || 'N/A'}</td>
                      <td>{candidate.score || 'N/A'}</td>
                      <td>
                        {/* Показываем ссылку только если статус "Завершено" */}
                        {candidate.status === 'Завершено' ? (
                          <Link to={`/report/${candidate.id}`} className="view-report-link">
                            Смотреть отчет
                          </Link>
                        ) : (
                          <span>-</span>
                        )}
                      </td>
                    </tr>
                  ))
                ) : (
                  // --- ВОТ ФИКС ДЛЯ "ПОКА НЕТ КАНДИДАТОВ" ---
                  <tr>
                    <td colSpan="5" className="no-candidates-cell">
                      Пока нет ни одного кандидата.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}

export default HrDashboard;