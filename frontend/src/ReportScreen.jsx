import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { FaCheckCircle, FaChartLine, FaBrain, FaCode, FaSync, FaBook } from 'react-icons/fa';

function ReportScreen({ onRestart }) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchReport = () => {
    const userId = localStorage.getItem('currentCandidateId');
    if (!userId) return;

    setIsRefreshing(true);
    axios.get(`http://localhost:8000/api/my-report/${userId}`)
      .then(res => {
        if (res.data.ready) {
            setReport(res.data);
        }
        setLoading(false);
        setIsRefreshing(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
        setIsRefreshing(false);
      });
  };

  useEffect(() => {
    fetchReport();
    const interval = setInterval(() => {
        setReport(prev => {
            if (!prev) fetchReport();
            return prev;
        });
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  // Если отчета нет, ставим нули
  const data = report || {
    final_score: 0,
    integrity_score: 0,
    summary: "Нейросеть анализирует ваше решение... Нажмите 'Обновить'.",
    details: {}
  };

  // Достаем детализацию из details (если её нет, будет 0)
  const psyScore = data.details?.psy_score || 0;
  const theoryScore = data.details?.theory_score || 0;
  const codeScore = data.details?.code_score || 0;

  const getScoreColor = (score) => {
      if (score >= 80) return '#4caf50'; 
      if (score >= 50) return '#ff9800'; 
      return '#f44336'; 
  };

  return (
    <div className="responsive-report-container">
      <div className="report-header-section">
        <h1 className="report-title">Ваши результаты</h1>
        <p className="report-subtitle">Собеседование завершено. Данные сохранены в базе.</p>
      </div>

      {!report && (
        <button 
            onClick={fetchReport} 
            className="big-button" 
            style={{marginBottom: '2rem', background: '#2196f3', border:'none', display: 'flex', alignItems: 'center', gap: '10px'}}
        >
            <FaSync className={isRefreshing ? "spin" : ""} /> 
            {isRefreshing ? "Проверяем..." : "Обновить результаты"}
        </button>
      )}

      <div className="stats-row">
        
        {/* Общий балл */}
        <div className="result-card main-score">
            <div className="icon-wrapper"><FaChartLine /></div>
            <h3>Общий балл</h3>
            <div className="big-number" style={{color: getScoreColor(data.final_score)}}>
                {data.final_score}/100
            </div>
        </div>

        {/* Integrity */}
        <div className="result-card integrity">
            <div className="icon-wrapper"><FaCheckCircle /></div>
            <h3>Integrity</h3>
            <div className="big-number" style={{color: getScoreColor(data.integrity_score)}}>
                {data.integrity_score}%
            </div>
        </div>

        {/* Детализация */}
        <div className="result-card details">
            <h3>Детализация</h3>
            <ul className="details-list" style={{width: '100%', marginTop: '1rem', listStyle: 'none', padding: 0}}>
                
                {/* Soft Skills */}
                <li style={{display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid #333'}}>
                    <span style={{display:'flex', gap:'10px', alignItems:'center'}}>
                        <FaBrain color="#ff79c6"/> Soft Skills
                    </span>
                    <span style={{fontWeight: 'bold', color: getScoreColor(psyScore)}}>
                        {psyScore}%
                    </span>
                </li>

                {/* Теория */}
                <li style={{display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid #333'}}>
                    <span style={{display:'flex', gap:'10px', alignItems:'center'}}>
                        <FaBook color="#8be9fd"/> Теория
                    </span>
                    <span style={{fontWeight: 'bold', color: getScoreColor(theoryScore)}}>
                        {theoryScore}%
                    </span>
                </li>

                {/* Код */}
                <li style={{display: 'flex', justifyContent: 'space-between', padding: '10px 0'}}>
                    <span style={{display:'flex', gap:'10px', alignItems:'center'}}>
                        <FaCode color="#50fa7b"/> Практика
                    </span>
                    <span style={{fontWeight: 'bold', color: getScoreColor(codeScore)}}>
                        {codeScore}%
                    </span>
                </li>
            </ul>
        </div>
      </div>

      <div className="summary-card-full">
          <h3>Заключение системы</h3>
          <div style={{
              lineHeight: '1.6', opacity: 0.9, marginTop: '1rem', whiteSpace: 'pre-wrap', 
              background: 'rgba(0,0,0,0.2)', padding: '1.5rem', borderRadius: '8px'
          }}>
              {data.summary}
          </div>
      </div>

      <button className="big-button restart-btn" onClick={onRestart}>
        Выйти на главный экран
      </button>

      <style>{`
        .spin { animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}

export default ReportScreen;