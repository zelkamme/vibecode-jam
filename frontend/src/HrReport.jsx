// frontend/src/HrReport.jsx

import React from 'react';
import { useParams, Link } from 'react-router-dom';

function HrReport() {
  const { candidateId } = useParams();

  // --- ГЛАВНЫЙ ФИКС: ЧИТАЕМ ДАННЫЕ ИЗ LOCALSTORAGE ---
  const db = JSON.parse(localStorage.getItem('vibecode_candidates_db')) || [];
  const candidateData = db.find(c => c.id == candidateId);

  if (!candidateData) {
    return (
      <div className="hr-report-page">
        <header className="hr-header">
          <Link to="/hr/dashboard" className="back-link">← Назад к списку</Link>
          <h1>Кандидат не найден</h1>
        </header>
      </div>
    );
  }

  const { name, level, status, score, telemetry } = candidateData;
  const integrityScore = telemetry?.finalScore || 100; // Если телеметрии нет, считаем 100
  const integrityScoreColor = integrityScore < 50 ? '#e53935' : (integrityScore < 80 ? '#f57c00' : '#43a047');

  return (
    <div className="hr-report-page">
      <header className="hr-header">
        <Link to="/hr/dashboard" className="back-link">← Назад к списку</Link>
        <h1>Отчет по кандидату</h1>
        <div className="candidate-info">
          <h2>{name}</h2>
          <span className="level-badge">{level}</span>
        </div>
      </header>
      
      <main className="hr-main">
        {/* ... остальная JSX-разметка без изменений, но теперь с реальными данными ... */}
        <div className="report-grid">
          <div className="report-section">
            <h3>Результаты</h3>
            <div className="report-card hr-card">
              <div className="report-item"><h4>Статус</h4><p>{status}</p></div>
              <div className="report-item"><h4>Общий балл</h4><p className="score">{score || 'N/A'}</p></div>
            </div>
          </div>
          
          <div className="report-section">
            <h3>Анализ честности</h3>
            <div className="report-card hr-card">
              <div className="report-item">
                <h4 style={{ color: integrityScoreColor }}>Integrity Score</h4>
                <p className="score" style={{ color: integrityScoreColor }}>{integrityScore} / 100</p>
                {telemetry && (
                  <ul className="integrity-details">
                    <li>Переключений вкладок: {telemetry.focusLost}</li>
                    <li>Крупных вставок кода: {telemetry.largePastes}</li>
                    <li>Уходов мыши из окна: {telemetry.mouseLeftWindow}</li>
                  </ul>
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