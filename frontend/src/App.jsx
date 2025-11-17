// frontend/src/App.jsx

import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// Импортируем все наши страницы/компоненты
import LoginPage from './LoginPage';
import RegistrationPage from './RegistrationPage';
import HrDashboard from './HrDashboard';
import HrReport from './HrReport';
import WelcomeScreen from './WelcomeScreen';
import LevelSelection from './LevelSelection';
import PsyTest from './PsyTest';
import TheoryTest from './TheoryTest';
import CodingInterface from './CodingInterface';
import ReportScreen from './ReportScreen';
import GlareEffect from './GlareEffect';

// --- Компонент-обертка для защиты роутов ---
// Он проверяет, есть ли нужная роль в localStorage. Если нет - кидает на /login
function ProtectedRoute({ children, allowedRoles }) {
  const userRole = localStorage.getItem('userRole');
  if (allowedRoles.includes(userRole)) {
    return children;
  }
  return <Navigate to="/login" replace />;
}

// --- Компонент для редиректа с главной страницы ---
function RootRedirect() {
  const userRole = localStorage.getItem('userRole');
  if (userRole === 'hr') {
    return <Navigate to="/hr/dashboard" replace />;
  }
  if (userRole === 'candidate') {
    return <Navigate to="/interview" replace />;
  }
  return <Navigate to="/login" replace />;
}

// --- ========================================================== ---
// --- КОМПОНЕНТ, КОТОРЫЙ ОПИСЫВАЕТ ВЕСЬ ПОТОК КАНДИДАТА ---
// --- ========================================================== ---
function CandidateFlow() {
  const [appState, setAppState] = useState('welcome');
  const [userData, setUserData] = useState({});

  const handleLevelSelect = (level) => {
    setUserData(prev => ({ ...prev, level }));
    setAppState('psy_test');
  };

  const handleFinishInterview = (telemetryData) => {
    console.log("Интервью завершено, данные телеметрии:", telemetryData);

    const candidateId = localStorage.getItem('currentCandidateId');
    if (!candidateId) {
      console.error("Не удалось найти ID текущего кандидата!");
      setAppState('report');
      return;
    }

    const db = JSON.parse(localStorage.getItem('vibecode_candidates_db')) || [];
    const candidateIndex = db.findIndex(c => c.id == candidateId);
    
    if (candidateIndex !== -1) {
      // Имитация расчета Integrity Score, как это делал бы бэкенд
      let score = 100;
      score -= (telemetryData.focusLost || 0) * 5;
      score -= (telemetryData.mouseLeftWindow || 0) * 2;
      score -= (telemetryData.largePastes || 0) * 15;
      if (score < 0) score = 0;
      telemetryData.finalScore = score;
      
      // Обновляем данные кандидата в "базе"
      db[candidateIndex].status = 'Завершено';
      db[candidateIndex].telemetry = telemetryData;
      db[candidateIndex].score = `${score}/100`; 
      
      // Сохраняем обновленную базу обратно в localStorage
      localStorage.setItem('vibecode_candidates_db', JSON.stringify(db));
      console.log("Данные кандидата обновлены в DB.");
    }
    
    setUserData(prev => ({ ...prev, telemetry: telemetryData }));
    setAppState('report');
  };
  
  const renderCurrentCandidateState = () => {
    switch (appState) {
      case 'welcome':
        return <div className="glass-card"><WelcomeScreen onStart={() => setAppState('level_selection')} /></div>;
      case 'level_selection':
        return <div className="glass-card"><LevelSelection onSelect={handleLevelSelect} /></div>;
      case 'psy_test':
        return <PsyTest onComplete={() => setAppState('theory_test')} />;
      case 'theory_test':
        return <TheoryTest onComplete={() => setAppState('coding_test')} />;
      case 'report':
        const handleRestart = () => {
          // Выход: очищаем данные текущей сессии и отправляем на логин
          localStorage.removeItem('currentCandidateId');
          localStorage.removeItem('userRole');
          window.location.href = '/login';
        }
        return <ReportScreen onRestart={handleRestart} />;
      default:
        return <WelcomeScreen onStart={() => setAppState('level_selection')} />;
    }
  };

  // Главная логика отображения для потока кандидата
  if (appState === 'coding_test') {
    return <CodingInterface userData={userData} onComplete={handleFinishInterview} />;
  } else {
    return (
      <div className="app-wrapper">
        {/* БЛИКИ НА ФОНЕ */}
        <GlareEffect /> 
        <div className="centered-container">
          {renderCurrentCandidateState()}
        </div>
      </div>
    );
  }
}

// --- ========================================================== ---
// --- ГЛАВНЫЙ КОМПОНЕНТ APP, КОТОРЫЙ ТЕПЕРЬ ТОЛЬКО МАРШРУТИЗАТОР ---
// --- ========================================================== ---
function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* === Публичные роуты === */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegistrationPage />} />

        {/* === Роуты для HR (защищенные) === */}
        <Route 
          path="/hr/dashboard" 
          element={
            <ProtectedRoute allowedRoles={['hr']}>
              <HrDashboard />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/report/:candidateId" 
          element={
            <ProtectedRoute allowedRoles={['hr']}>
              <HrReport />
            </ProtectedRoute>
          } 
        />
        
        {/* === Роут для Кандидата (защищенный) === */}
        <Route 
          path="/interview" 
          element={
            <ProtectedRoute allowedRoles={['candidate']}>
              <CandidateFlow />
            </ProtectedRoute>
          } 
        />
        
        {/* === Главный роут ("/") для автоматического редиректа === */}
        <Route 
          path="/" 
          element={<RootRedirect />} 
        />
        
        {/* === Роут-заглушка на случай, если ничего не найдено === */}
        <Route 
          path="*" 
          element={<Navigate to="/" replace />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;