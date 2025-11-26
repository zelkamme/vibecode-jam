import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { FaCheckCircle, FaChartLine, FaBrain, FaCode } from 'react-icons/fa';

function ReportScreen({ onRestart }) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const userId = localStorage.getItem('currentCandidateId');
    if (!userId) return;

    axios.get(`http://localhost:8000/api/my-report/${userId}`)
      .then(res => {
        if (res.data.ready) setReport(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="centered-container"><h2>Генерация отчета...</h2></div>;

  const data = report || {
    final_score: 0,
    integrity_score: 0,
    summary: "Данные обрабатываются..."
  };

  return (
    <div className="responsive-report-container">
      <div className="report-header-section">
        <h1 className="report-title">Ваши результаты</h1>
        <p className="report-subtitle">Собеседование завершено. Данные сохранены в базе.</p>
      </div>

      {/* 3 БЛОКА В ОДНУ ЛИНИЮ */}
      <div className="stats-row">
        
        {/* 1. Общий балл */}
        <div className="result-card main-score">
            <div className="icon-wrapper"><FaChartLine /></div>
            <h3>Общий балл</h3>
            <div className="big-number">{data.final_score}/100</div>
            <p className="card-desc">Совокупная оценка</p>
        </div>

        {/* 2. Integrity */}
        <div className="result-card integrity">
            <div className="icon-wrapper"><FaCheckCircle /></div>
            <h3>Integrity Score</h3>
            <div className="big-number" style={{color: data.integrity_score > 80 ? '#4caf50' : '#ff9800'}}>
                {data.integrity_score}%
            </div>
            <p className="card-desc">Честность прохождения</p>
        </div>

        {/* 3. Детали (ПЕРЕНЕС СЮДА) */}
        <div className="result-card details">
            <h3>Детализация</h3>
            <ul className="details-list">
                <li>
                    <span className="label"><FaBrain /> Soft Skills</span>
                    <span className="value">Пройдено</span>
                </li>
                <li>
                    <span className="label">📖 Теория</span>
                    <span className="value">Обработано</span>
                </li>
                <li>
                    <span className="label"><FaCode /> Практика</span>
                    <span className="value">Ревью</span>
                </li>
            </ul>
        </div>
      </div>

      {/* НИЖНИЙ БЛОК НА ВСЮ ШИРИНУ */}
      <div className="summary-card-full">
          <h3>Заключение системы</h3>
          <p style={{lineHeight: '1.6', opacity: 0.9, marginTop: '1rem'}}>
              {data.summary || "Ваши результаты переданы HR-отделу. Вы продемонстрировали хорошие навыки владения инструментарием."}
          </p>
      </div>

      <button className="big-button restart-btn" onClick={onRestart}>
        Выйти на главный экран
      </button>
    </div>
  );
}

export default ReportScreen;