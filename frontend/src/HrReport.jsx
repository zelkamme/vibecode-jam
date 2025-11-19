// frontend/src/HrReport.jsx

import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';

function HrReport() {
  const { candidateId } = useParams();
  const [candidate, setCandidate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // ЗАПРОС К БЭКЕНДУ
    axios.get(`http://localhost:8000/api/candidates/${candidateId}`)
      .then(response => {
        setCandidate(response.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Ошибка:", err);
        setError("Не удалось загрузить данные кандидата. Проверьте ID.");
        setLoading(false);
      });
  }, [candidateId]);

  if (loading) return <div className="hr-report-page"><h2 style={{padding:'2rem', color:'white'}}>Загрузка данных...</h2></div>;
  
  if (error || !candidate) {
    return (
      <div className="hr-report-page">
        <header className="hr-header">
          <Link to="/hr/dashboard" className="back-link">← Назад к списку</Link>
          <h1>Кандидат не найден</h1>
        </header>
        <div style={{padding:'2rem', color:'white', textAlign:'center'}}>
            <p>{error}</p>
        </div>
      </div>
    );
  }

  const { name, level, status, score, integrity_score, telemetry } = candidate;
  
  // Цвета для Integrity Score
  const iScore = integrity_score || 100;
  const integrityColor = iScore < 50 ? '#e53935' : (iScore < 80 ? '#f57c00' : '#43a047');

  return (
    <div className="hr-report-page">
      <header className="hr-header">
        <Link to="/hr/dashboard" className="back-link">← Назад к списку</Link>
        <h1>Отчет по кандидату</h1>
        <div className="candidate-info">
          <h2>{name}</h2>
          <span className="level-badge" style={{background: '#333', padding: '0.3rem 0.6rem', borderRadius:'4px', marginLeft:'1rem'}}>{level}</span>
        </div>
      </header>
      
      <main className="hr-main">
        <div className="report-grid">
          
          {/* БЛОК 1: ОБЩИЕ РЕЗУЛЬТАТЫ */}
          <div className="report-section">
            <h3>Результаты</h3>
            <div className="report-card hr-card">
              <div className="report-item">
                <h4>Статус</h4>
                <p>{status}</p>
              </div>
              <div className="report-item">
                <h4>Общий балл</h4>
                <p className="score">{score || 0} / 100</p>
              </div>
            </div>
          </div>
          
          {/* БЛОК 2: АНТИЧИТ / ИНТЕГРИТИ */}
          <div className="report-section">
            <h3>Анализ честности (Anti-Cheat)</h3>
            <div className="report-card hr-card">
              <div className="report-item">
                <h4 style={{ color: integrityColor }}>Integrity Score</h4>
                <p className="score" style={{ color: integrityColor }}>{iScore}%</p>
                
                {telemetry ? (
                  <ul className="integrity-details" style={{marginTop: '1rem', listStyle: 'none', padding:0}}>
                    <li style={{marginBottom:'0.5rem'}}>👀 Потеря фокуса (Alt+Tab): <strong>{telemetry.focusLost || 0} раз</strong></li>
                    <li style={{marginBottom:'0.5rem'}}>🐭 Уход мыши из окна: <strong>{telemetry.mouseLeftWindow || 0} раз</strong></li>
                    <li style={{marginBottom:'0.5rem'}}>📋 Крупные вставки кода: <strong>{telemetry.largePastes || 0} раз</strong></li>
                  </ul>
                ) : (
                  <p style={{opacity:0.5, fontSize:'0.9rem'}}>Нет данных телеметрии (кандидат еще не проходил тест)</p>
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