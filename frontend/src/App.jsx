// frontend/src/App.jsx

import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// Импорт страниц
import LoginPage from './LoginPage';
import RegistrationPage from './RegistrationPage';
import HrDashboard from './HrDashboard';
import HrReport from './HrReport';
import WelcomeScreen from './WelcomeScreen';
import VacancyList from './VacancyList';
import PsyTest from './PsyTest';
import TheoryTest from './TheoryTest';
import CodingInterface from './CodingInterface';
import ReportScreen from './ReportScreen';
import GlareEffect from './GlareEffect';
import TaskBuilder from './TaskBuilder';
import VacancyBuilder from './VacancyBuilder';

// --- Защита роутов ---
function ProtectedRoute({ children, allowedRoles }) {
  const userRole = localStorage.getItem('userRole');
  // Простая проверка: если роль есть в списке разрешенных, пускаем
  if (allowedRoles.includes(userRole)) {
    return children;
  }
  return <Navigate to="/login" replace />;
}

// --- Редирект с корня ---
function RootRedirect() {
  const userRole = localStorage.getItem('userRole');
  if (userRole === 'hr') return <Navigate to="/hr/dashboard" replace />;
  if (userRole === 'candidate') return <Navigate to="/interview" replace />;
  return <Navigate to="/login" replace />;
}

// --- ПОТОК КАНДИДАТА ---
function CandidateFlow() {
  // Начальное состояние - Welcome Screen
  const [appState, setAppState] = useState('welcome');
  
  // Получаем сохраненный при регистрации уровень
  // Это нужно, чтобы CodingInterface знал, какую задачу просить у бэка
  const candidateLevel = localStorage.getItem('candidateLevel') || 'Junior';
  
  const [userData, setUserData] = useState({
    level: candidateLevel,
    telemetry: {}
  });

  // Обработчик кнопки "Начать" на WelcomeScreen
  const handleStart = () => {
    // Сразу переходим к Психологическому тесту (или Theory, как настроишь)
    // Шаг выбора уровня пропускается
    setAppState('psy_test');
  };

  // Завершение всего интервью
  const handleFinishInterview = (telemetryData) => {
    console.log("Финиш. Телеметрия:", telemetryData);
    
    // Обновляем локальный стейт (для отображения в ReportScreen, если нужно)
    setUserData(prev => ({ ...prev, telemetry: telemetryData }));
    
    // Переходим к экрану отчета
    setAppState('report');
  };
  
  // Логика переключения экранов
  const renderCurrentCandidateState = () => {
    switch (appState) {
      case 'welcome':
        return (
          <div className="glass-card">
            <WelcomeScreen onStart={handleStart} />
          </div>
        );
      
      case 'psy_test':
        return (
          <PsyTest 
            onComplete={() => setAppState('theory_test')} 
          />
        );
        
      case 'theory_test':
        return (
          <TheoryTest 
            onComplete={() => setAppState('coding_test')} 
          />
        );
        
      // CodingInterface рендерится отдельно (ниже), чтобы занимать весь экран
      
      case 'report':
        const handleRestart = () => {
          localStorage.clear();
          window.location.href = '/login';
        }
        return <ReportScreen onRestart={handleRestart} />;
        
      default:
        return <WelcomeScreen onStart={handleStart} />;
    }
  };

  // Если этап "Кодинг" - рендерим без centered-container (на весь экран)
  if (appState === 'coding_test') {
    return (
      <CodingInterface 
        userData={userData} 
        onComplete={handleFinishInterview} 
      />
    );
  } 
  
  // Для всех остальных этапов - стандартный лейаут с центрированием
  else {
    return (
      <div className="app-wrapper">
        <GlareEffect /> 
        <div className="centered-container">
          {renderCurrentCandidateState()}
        </div>
      </div>
    );
  }
}

// --- ГЛАВНЫЙ РОУТЕР ---
function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Публичные страницы */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegistrationPage />} />

        {/* HR Зона */}
        <Route 
          path="/hr/dashboard" 
          element={
            <ProtectedRoute allowedRoles={['hr']}>
              <HrDashboard />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/hr/vacancies" 
          element={
            <ProtectedRoute allowedRoles={['hr']}>
              <VacancyList />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/hr/create-vacancy" 
          element={
            <ProtectedRoute allowedRoles={['hr']}>
              <VacancyBuilder />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/hr/create-task" 
          element={
            <ProtectedRoute allowedRoles={['hr']}>
              <TaskBuilder />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/hr/edit-task/:taskId" 
          element={
            <ProtectedRoute allowedRoles={['hr']}>
              <TaskBuilder />
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
        
        {/* Кандидат Зона */}
        <Route 
          path="/interview" 
          element={
            <ProtectedRoute allowedRoles={['candidate']}>
              <CandidateFlow />
            </ProtectedRoute>
          } 
        />
        
        {/* Редиректы */}
        <Route path="/" element={<RootRedirect />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;