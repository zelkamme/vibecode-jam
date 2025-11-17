// frontend/src/ReportScreen.jsx

import React from 'react';

// onRestart - функция для начала собеседования заново
function ReportScreen({ onRestart }) {
  // Пока что данные - заглушки. В будущем они будут приходить из userData
  const reportData = {
    psyTestScore: '8/10',
    theoryTestScore: '9/10',
    codingResult: 'Все тесты пройдены',
    aiConclusion: 'Кандидат продемонстрировал уверенное владение базовым синтаксисом Python и хорошие навыки решения проблем. Рекомендуется к следующему этапу.'
  };

  return (
    <>
      <h2>Финальный отчет</h2>
      <div className="report-card">
        <div className="report-item">
          <h4>Психологический тест</h4>
          <p>{reportData.psyTestScore}</p>
        </div>
        <div className="report-item">
          <h4>Теоретический тест</h4>
          <p>{reportData.theoryTestScore}</p>
        </div>
        <div className="report-item">
          <h4>Практическое задание</h4>
          <p>{reportData.codingResult}</p>
        </div>
        <div className="report-item summary">
          <h4>Заключение AI-интервьюера</h4>
          <p>{reportData.aiConclusion}</p>
        </div>
      </div>
        <button className="big-button" onClick={onRestart}>
            Завершить и выйти
        </button>
    </>
  );
}

export default ReportScreen;