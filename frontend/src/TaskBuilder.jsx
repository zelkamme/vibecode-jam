// frontend/src/TaskBuilder.jsx

import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import axios from 'axios';
import { FaPlus, FaTrash, FaFile, FaArrowLeft } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';

// Список доступных Docker-окружений
const ENVIRONMENTS = [
  { id: 'basic', name: 'Python Basic', description: 'Чистый Python 3.11 (Standard Library)', libs: ['sys', 'math', 'random'] },
  { id: 'data-science', name: 'Python Data Science', description: 'Pandas, NumPy included', libs: ['pandas', 'numpy'] },
];

function TaskBuilder() {
  const navigate = useNavigate();
  const [taskType, setTaskType] = useState('coding'); // 'coding' | 'theory'
  const [loading, setLoading] = useState(false);

  // Основные данные задачи
  const [task, setTask] = useState({
    title: '',
    description: '',
    referenceAnswer: '', // Для теории
    level: 'Intern',
    envId: 'basic'       // Для кодинга
  });

  // Файлы (только для кодинга)
  const [files, setFiles] = useState([
    { name: 'main.py', content: '# Напишите код решения здесь\nprint("Hello World")', readonly: false }
  ]);
  const [activeFileIndex, setActiveFileIndex] = useState(0);
  const [newFileName, setNewFileName] = useState('');

  // --- Работа с файлами ---
  const handleAddFile = () => {
    if (!newFileName.trim()) return;
    setFiles([...files, { name: newFileName, content: '', readonly: false }]);
    setNewFileName('');
    setActiveFileIndex(files.length);
  };

  const handleDeleteFile = (index) => {
    const newFiles = files.filter((_, i) => i !== index);
    setFiles(newFiles);
    setActiveFileIndex(0);
  };

  const handleFileContentChange = (value) => {
    setFiles(prevFiles => {
      const newFiles = [...prevFiles];
      newFiles[activeFileIndex] = { ...newFiles[activeFileIndex], content: value };
      return newFiles;
    });
  };

  // --- Сохранение ---
  const handleSaveTask = async () => {
    if (!task.title.trim() || !task.description.trim()) {
      alert("Пожалуйста, заполните название и описание задачи.");
      return;
    }

    setLoading(true);

    const payload = {
      ...task,
      type: taskType,
      // Файлы отправляем только если это задача на кодинг
      files: taskType === 'coding' ? files : []
    };

    console.log("📤 Отправка задачи:", payload);

    try {
      const response = await axios.post('http://localhost:8000/api/tasks', payload);
      
      if (response.data.status === 'ok') {
        alert(`✅ Задача успешно создана! ID: ${response.data.id}`);
        // Очищаем форму
        setTask({ ...task, title: '', description: '', referenceAnswer: '' });
      }
    } catch (error) {
      console.error("Ошибка сохранения:", error);
      alert("❌ Не удалось сохранить задачу. Убедитесь, что бэкенд запущен.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="task-builder-page" style={{ padding: '2rem', color: '#fff', height: '100vh', boxSizing: 'border-box', display: 'flex', flexDirection: 'column' }}>
      
      {/* Кнопка НАЗАД */}
      <div style={{ marginBottom: '1rem' }}>
        <button 
          onClick={() => navigate('/hr/dashboard')} 
          className="link-button"
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem', border: '1px solid rgba(255,255,255,0.3)', background: 'rgba(0,0,0,0.3)', color: 'white' }}
        >
          <FaArrowLeft /> Назад к списку кандидатов
        </button>
      </div>

      {/* Основной контейнер */}
      <div className="glass-card task-builder-container" style={{ flexGrow: 1, overflow: 'hidden' }}>
        
        {/* ЛЕВАЯ ПАНЕЛЬ: НАСТРОЙКИ */}
        <div className="settings-panel">
          <h2 style={{marginTop: 0}}>Конструктор Задач</h2>

          {/* Переключатель Типа */}
          <div className="task-type-tabs">
            <div 
              className={`type-tab ${taskType === 'coding' ? 'active' : ''}`}
              onClick={() => setTaskType('coding')}
            >
              💻 Кодинг (Docker)
            </div>
            <div 
              className={`type-tab ${taskType === 'theory' ? 'active' : ''}`}
              onClick={() => setTaskType('theory')}
            >
              📖 Теория
            </div>
          </div>
          
          {/* Основные поля */}
          <div style={{marginTop: '1rem'}}>
            <label>Название задачи</label>
            <input 
              className="glass-input" 
              value={task.title} 
              onChange={e => setTask({...task, title: e.target.value})} 
              placeholder="Например: Reverse String"
            />
          </div>

          <div>
            <label>Уровень сложности</label>
            <select 
              className="glass-input" 
              value={task.level} 
              onChange={e => setTask({...task, level: e.target.value})}
            >
              <option value="Intern">Intern (Стажер)</option>
              <option value="Junior">Junior</option>
              <option value="Middle">Middle</option>
              <option value="Senior">Senior</option>
            </select>
          </div>

          {/* Настройки для КОДИНГА */}
          {taskType === 'coding' && (
            <div>
              <label>Окружение (Библиотеки)</label>
              <div className="env-selector">
                {ENVIRONMENTS.map(env => (
                  <div 
                    key={env.id} 
                    className={`env-card ${task.envId === env.id ? 'active' : ''}`}
                    onClick={() => setTask({...task, envId: env.id})}
                  >
                    <strong>{env.name}</strong>
                    <p style={{fontSize: '0.8rem', opacity: 0.7, margin: 0}}>{env.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Настройки для ТЕОРИИ */}
          {taskType === 'theory' && (
            <div>
               <label>Эталонный ответ (скрыт от кандидата)</label>
               <textarea 
                className="glass-input" 
                style={{ height: '80px', resize: 'none', borderColor: '#4caf50' }}
                value={task.referenceAnswer}
                onChange={e => setTask({...task, referenceAnswer: e.target.value})}
                placeholder="Напишите здесь краткий правильный ответ для проверки..."
              />
            </div>
          )}

          {/* Описание (Markdown) */}
          <div style={{flexGrow: 1, display: 'flex', flexDirection: 'column', marginTop: '1rem'}}>
            <label>Текст задания (Markdown)</label>
            <textarea 
              className="glass-input" 
              style={{ flexGrow: 1, resize: 'none', minHeight: '150px', fontFamily: 'monospace' }}
              value={task.description}
              onChange={e => setTask({...task, description: e.target.value})}
              placeholder={taskType === 'coding' ? "Опишите, что должна делать функция..." : "Введите текст вопроса..."}
            />
          </div>

          <button className="big-button save-task-btn" onClick={handleSaveTask} disabled={loading}>
            {loading ? "Сохранение..." : "Сохранить задачу"}
          </button>
        </div>

        {/* ПРАВАЯ ПАНЕЛЬ: КОНТЕНТ */}
        <div className="content-panel" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          
          {taskType === 'coding' ? (
            // --- РЕДАКТОР КОДА ---
            <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: 'rgba(0,0,0,0.2)', borderRadius: '12px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.1)' }}>
              
              {/* Табы файлов */}
              <div className="file-tabs" style={{ display: 'flex', background: 'rgba(255,255,255,0.05)', padding: '0.5rem', gap: '0.5rem', alignItems: 'center' }}>
                {files.map((file, index) => (
                  <div 
                    key={index} 
                    className={`file-tab ${activeFileIndex === index ? 'active' : ''}`}
                    onClick={() => setActiveFileIndex(index)}
                  >
                    <FaFile size={12} /> {file.name}
                    {index !== 0 && <FaTrash className="delete-icon" onClick={(e) => { e.stopPropagation(); handleDeleteFile(index); }} />}
                  </div>
                ))}
                <div className="add-file-wrapper" style={{ marginLeft: 'auto', display: 'flex', gap: '0.5rem' }}>
                  <input type="text" className="glass-input-small" placeholder="helper.py" value={newFileName} onChange={e => setNewFileName(e.target.value)} />
                  <button className="icon-button" onClick={handleAddFile}><FaPlus /></button>
                </div>
              </div>

              {/* Monaco Editor */}
              <div className="file-editor-area" style={{ flexGrow: 1 }}>
                <Editor 
                  height="100%" 
                  defaultLanguage="python"
                  theme="vs-dark"
                  path={files[activeFileIndex].name}
                  value={files[activeFileIndex].content}
                  onChange={handleFileContentChange}
                  options={{ 
                    minimap: { enabled: false }, 
                    fontSize: 14,
                    automaticLayout: true
                  }}
                />
              </div>
            </div>
          ) : (
            // --- ПРЕВЬЮ ТЕОРИИ ---
            <div style={{ display: 'flex', flexDirection: 'column', height: '100%', justifyContent: 'center', alignItems: 'center', background: 'rgba(0,0,0,0.2)', borderRadius: '12px', padding: '2rem', textAlign: 'center' }}>
              <h3 style={{opacity: 0.5}}>Предпросмотр вопроса</h3>
              <div className="glass-card" style={{width: '90%', minHeight: '200px', display:'flex', flexDirection:'column', alignItems: 'flex-start', textAlign: 'left'}}>
                <h4 style={{margin: '0 0 1rem 0'}}>{task.title || "Заголовок"}</h4>
                <div style={{whiteSpace: 'pre-wrap', opacity: 0.8}}>{task.description || "Текст вопроса появится здесь..."}</div>
                
                {task.referenceAnswer && (
                  <div style={{marginTop: '2rem', padding: '1rem', background: 'rgba(34, 197, 94, 0.1)', border: '1px solid #22c55e', borderRadius: '8px', width: '100%', boxSizing: 'border-box'}}>
                    <strong style={{color: '#22c55e'}}>Правильный ответ (виден только HR):</strong>
                    <p style={{margin: '0.5rem 0 0 0'}}>{task.referenceAnswer}</p>
                  </div>
                )}
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
}

export default TaskBuilder;