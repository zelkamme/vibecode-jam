import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { FaArrowLeft } from 'react-icons/fa';

function HrReport() {
  const { candidateId } = useParams();
  const [candidate, setCandidate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get(`/api/candidates/${candidateId}`)
      .then(response => {
        setCandidate(response.data);
        setLoading(false);
      })
      .catch(err => {
        setError("Ошибка загрузки");
        setLoading(false);
      });
  }, [candidateId]);

  if (loading) return <div className="hr-page"><h2 style={{color:'white'}}>Загрузка данных...</h2></div>;
  if (error || !candidate) return <div className="hr-page"><h2 style={{color:'white'}}>Не найдено</h2></div>;

  const { name, level, status, score, integrity_score, telemetry } = candidate;
  const iScore = integrity_score || 100;
  const integrityColor = iScore < 50 ? '#e53935' : (iScore < 80 ? '#f57c00' : '#43a047');

  return (
    <div className="hr-page">
      <header className="hr-header">
        <div style={{display:'flex', alignItems:'center', gap:'1rem'}}>
             <Link to="/hr/dashboard" className="back-link"><FaArrowLeft /> Назад</Link>
             <h1 style={{margin:0}}>Отчет по кандидату</h1>
        </div>
        <div className="candidate-info">
          <span style={{fontSize:'1.2rem', fontWeight:'bold'}}>{name}</span>
          <span className="level-badge" style={{background: '#333', padding: '0.3rem 0.6rem', borderRadius:'4px', marginLeft:'1rem'}}>{level}</span>
        </div>
      </header>
      
      <main className="hr-main" style={{marginTop:'2rem'}}>
        {/* ИСПОЛЬЗУЕМ RESPONSIVE GRID */}
        <div className="report-grid">
          
          {/* КАРТОЧКА 1: ОСНОВНЫЕ РЕЗУЛЬТАТЫ */}
          <div className="report-section">
            <h3 style={{color:'white', borderBottom:'1px solid #333', paddingBottom:'0.5rem'}}>Результаты</h3>
            <div className="glass-card report-card">
              <div className="report-item">
                <h4>Текущий статус</h4>
                <p style={{fontWeight:'bold', color: status === 'Завершено' ? '#4caf50' : '#ff9800'}}>{status}</p>
              </div>
              <div className="report-item">
                <h4>Общий балл</h4>
                <p className="score">{score || 0} / 100</p>
              </div>
            </div>
          </div>
          
          {/* КАРТОЧКА 2: АНТИЧИТ */}
          <div className="report-section">
            <h3 style={{color:'white', borderBottom:'1px solid #333', paddingBottom:'0.5rem'}}>Anti-Cheat Анализ</h3>
            <div className="glass-card report-card">
              <div className="report-item">
                <h4 style={{ color: integrityColor }}>Integrity Score</h4>
                <p className="score" style={{ color: integrityColor }}>{iScore}%</p>
              </div>
              
              <div style={{marginTop:'1rem'}}>
                 {telemetry ? (
                  <ul className="integrity-details" style={{listStyle: 'none', padding:0}}>
                    <li style={{marginBottom:'0.5rem', display:'flex', justifyContent:'space-between'}}>
                        <span>👀 Потеря фокуса:</span> <strong>{telemetry.focusLost || 0}</strong>
                    </li>
                    <li style={{marginBottom:'0.5rem', display:'flex', justifyContent:'space-between'}}>
                        <span>🐭 Уход курсора:</span> <strong>{telemetry.mouseLeftWindow || 0}</strong>
                    </li>
                    <li style={{marginBottom:'0.5rem', display:'flex', justifyContent:'space-between'}}>
                        <span>📋 Copy/Paste (Large):</span> <strong>{telemetry.largePastes || 0}</strong>
                    </li>
                  </ul>
                ) : (
                  <p style={{opacity:0.5, fontSize:'0.9rem'}}>Нет данных телеметрии</p>
                )}
              </div>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}

export default HrReport;