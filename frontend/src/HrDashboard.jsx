import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

function HrDashboard() {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Состояние сортировки
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'ascending' });

  useEffect(() => {
    axios.get('http://localhost:8000/api/candidates')
      .then(response => {
        setCandidates(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error("Ошибка:", error);
        setLoading(false);
      });
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    window.location.href = '/login';
  };

  // ЛОГИКА СОРТИРОВКИ
  const handleSort = (key) => {
    let direction = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });

    const sortedData = [...candidates].sort((a, b) => {
      if (a[key] < b[key]) return direction === 'ascending' ? -1 : 1;
      if (a[key] > b[key]) return direction === 'ascending' ? 1 : -1;
      return 0;
    });
    setCandidates(sortedData);
  };

  const getSortClass = (key) => {
    if (sortConfig.key !== key) return 'sortable';
    return `sortable ${sortConfig.direction === 'ascending' ? 'asc' : 'desc'}`;
  };

  return (
    <div className="hr-dashboard-page hr-page">
      <header className="hr-header">
        <h1>Панель управления HR</h1>
        <div style={{display:'flex', gap:'1rem', flexWrap:'wrap'}}>
            
            {/* ОСТАВИЛ ТОЛЬКО СПИСОК ВАКАНСИЙ, КАК ПРОСИЛИ */}
            <Link to="/hr/vacancies" className="big-button" style={{textDecoration: 'none', fontSize: '0.9rem', background: '#005bb5', border:'none'}}>
              📋 Управление вакансиями и задачами
            </Link>

        </div>
        <button onClick={handleLogout} className="logout-button">Выйти</button>
      </header>

      <main className="hr-main" style={{marginTop:'2rem'}}>
        <div className="candidate-list-container glass-card">
          <h3>Кандидаты (Live DB)</h3>
          {loading ? <p style={{color:'white'}}>Загрузка...</p> : (
            <div className="candidate-list" style={{overflowX: 'auto'}}>
              <table>
                <thead>
                  <tr>
                    <th onClick={() => handleSort('name')} className={getSortClass('name')}>Кандидат</th>
                    <th onClick={() => handleSort('vacancy')} className={getSortClass('vacancy')}>Вакансия</th>
                    <th onClick={() => handleSort('level')} className={getSortClass('level')}>Уровень</th>
                    <th onClick={() => handleSort('status')} className={getSortClass('status')}>Статус</th>
                    <th>Резюме</th>
                    <th onClick={() => handleSort('score')} className={getSortClass('score')}>Баллы</th>
                    <th>Отчет</th>
                  </tr>
                </thead>
                <tbody>
                  {candidates.length > 0 ? (
                    candidates.map(candidate => (
                      <tr key={candidate.id}>
                        <td style={{fontWeight:'bold'}}>{candidate.name}</td>
                        <td>{candidate.vacancy}</td>
                        <td>{candidate.level}</td>
                        
                        <td>
                            <span style={{
                                color: candidate.status === 'Завершено' ? '#4caf50' : 
                                       candidate.status === 'В процессе' ? '#ff9800' : '#aaa',
                                fontWeight: 'bold'
                            }}>
                                {candidate.status}
                            </span>
                        </td>

                        <td>
                            {candidate.resume ? (
                                <span title={candidate.resume} style={{cursor:'pointer', textDecoration:'underline'}}>PDF</span>
                            ) : <span style={{opacity:0.3}}>—</span>}
                        </td>
                        
                        <td style={{fontSize:'1.1rem'}}>{candidate.score}</td>
                        
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
                      <td colSpan="7" className="no-candidates-cell">Кандидатов нет</td>
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