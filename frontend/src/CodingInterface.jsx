// frontend/src/CodingInterface.jsx

import React, { useState, useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

function CodingInterface({ onComplete }) {
  const [code, setCode] = useState('# Загрузка задачи...\n');
  const [output, setOutput] = useState({ stdout: '', stderr: '' });
  const [chatHistory, setChatHistory] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [taskId, setTaskId] = useState(0);
  const [loading, setLoading] = useState(true);
  const [debugInfo, setDebugInfo] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  
  // Новый стейт для языка редактора (для подсветки синтаксиса)
  const [editorLang, setEditorLang] = useState('python');

  // Ссылка на конец чата для автоскролла
  const chatEndRef = useRef(null);

  // Телеметрия (Анти-чит)
  const telemetry = useRef({
    focusLost: 0,
    mouseLeftWindow: 0,
    largePastes: 0,
    codeHistory: []
  });

  // 1. Инициализация: Определяем язык и загружаем задачу
  useEffect(() => {
    const initInterface = async () => {
      const savedLevel = localStorage.getItem('candidateLevel') || 'Intern';
      const userId = localStorage.getItem('currentCandidateId');
      
      setDebugInfo(savedLevel);

      // ШАГ 1: Определяем язык программирования по вакансии пользователя
      let detectedLang = 'python'; // Дефолт
      
      if (userId) {
          try {
              // Запрашиваем инфо о кандидате (предполагаем, что бэк возвращает поле "language")
              const userRes = await axios.get(`http://localhost:8000/api/candidates/${userId}`);
              const rawLang = userRes.data.language; // Например: "C++", "Java", "JavaScript"

              if (rawLang) {
                  // Маппинг названий с бэкенда в ID языков Monaco Editor
                  const monacoMap = {
                      'Python': 'python',
                      'JavaScript': 'javascript',
                      'Java': 'java',
                      'C++': 'cpp',
                      'Go': 'go'
                  };
                  detectedLang = monacoMap[rawLang] || 'python';
              }
          } catch (e) {
              console.error("Не удалось определить язык вакансии, используем Python:", e);
          }
      }
      setEditorLang(detectedLang);

      // ШАГ 2: Загружаем задачу
      try {
        const response = await axios.get(`http://localhost:8000/api/task/coding/${savedLevel}`, {
            params: { user_id: userId } 
        });
        const task = response.data;
        setTaskId(task.id);

        if (task.id === 0) {
             setCode(`# ${task.description}`);
             setChatHistory([{ sender: 'ai', text: `**Статус:** ${task.title}\n\n${task.description}` }]);
        } else {
            let initialCode = "";
            
            // Пытаемся найти файл, подходящий под определенный язык
            // (Если задача мультифайловая или универсальная)
            if (task.files && Array.isArray(task.files) && task.files.length > 0) {
                // Простая логика: берем первый файл, или ищем main.*
                const mainFile = task.files.find(f => f.name.startsWith('main') || f.name.startsWith('index'));
                initialCode = mainFile ? mainFile.content : task.files[0].content;
            } else {
                initialCode = "// Напишите ваше решение здесь\n";
            }
            
            setCode(initialCode);
            
            // Первая запись истории кода
            telemetry.current.codeHistory.push(initialCode);
            
            // Приветственное сообщение
            setChatHistory([
              { 
                sender: 'ai', 
                text: `### Задача: ${task.title}\n\n${task.description}\n\n_Язык среды: ${detectedLang.toUpperCase()}. Вы можете задавать вопросы._` 
              }
            ]);
        }

      } catch (error) {
        console.error("Ошибка загрузки задачи:", error);
        setCode("# Ошибка соединения с сервером.");
      } finally {
        setLoading(false);
      }
    };

    initInterface();
  }, []);

  // 2. Анти-чит слушатели
  useEffect(() => {
    const handleVisibilityChange = () => { if (document.hidden) telemetry.current.focusLost++; };
    const handleMouseLeave = () => { telemetry.current.mouseLeftWindow++; };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    document.body.addEventListener('mouseleave', handleMouseLeave);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      document.body.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, []);

  // 3. Автоскролл чата
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const handleCodeChange = (newCode) => {
    if (newCode && code && newCode.length - code.length > 50) {
        telemetry.current.largePastes++;
    }
    setCode(newCode || "");
  };

  // --- ОБНОВЛЕННЫЙ ЗАПУСК КОДА ---
  const handleRunCode = async () => {
    if (isRunning) return;
    setIsRunning(true);
    
    // Сохраняем снапшот кода
    telemetry.current.codeHistory.push(code);
    setOutput({ stdout: '', stderr: 'Запуск контейнера...' });
    
    const userId = localStorage.getItem('currentCandidateId'); // Берем ID пользователя

    try {
      // Отправляем user_id, чтобы бэк выбрал правильный Docker-образ (Python/Java/JS...)
      const response = await axios.post('http://localhost:8000/api/run-code', {
        code: code,
        language: editorLang, // Можно передать для справки
        task_id: taskId,
        user_id: userId ? parseInt(userId) : null 
      });
      setOutput(response.data);
    } catch (error) {
      setOutput({ stdout: '', stderr: `Ошибка выполнения: ${error.message}` });
    } finally {
      setIsRunning(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;
    
    const newUserMessage = { sender: 'user', text: userInput };
    setChatHistory(prev => [...prev, newUserMessage]);
    setUserInput('');
    
    try {
      const response = await axios.post('http://localhost:8000/api/chat', {
        message: userInput,
        history: chatHistory,
        code_context: code,
        task_id: taskId
      });
      setChatHistory(prev => [...prev, response.data]);
    } catch (error) {
        console.error(error);
        setChatHistory(prev => [...prev, { sender: 'ai', text: '_AI сейчас недоступен._' }]);    
    }
  };

  const handleFinish = async () => {
    if (!window.confirm("Вы уверены, что хотите завершить выполнение задачи?")) return;

    const currentUserId = localStorage.getItem('currentCandidateId');
    if (!currentUserId) {
        alert("Ошибка авторизации. Результат будет сохранен локально.");
        onComplete({ finalScore: 0, ...telemetry.current });
        return;
    }

    try {
        const response = await axios.post('http://localhost:8000/api/analyze-integrity', {
            user_id: parseInt(currentUserId),
            focusLost: telemetry.current.focusLost,
            mouseLeftWindow: telemetry.current.mouseLeftWindow,
            largePastes: telemetry.current.largePastes,
            codeHistory: telemetry.current.codeHistory,
            coding_task_id: taskId // Передаем ID задачи для ревью
        });
        onComplete(response.data); 
    } catch (error) {
        console.error("Ошибка сохранения:", error);
        onComplete({ finalScore: 0, ...telemetry.current });
    }
  };

  if (loading) {
    return (
        <div className="centered-container">
            <div className="glass-card"><h2>Загрузка среды разработки...</h2></div>
        </div>
    );
  }

  return (
    <div className="main-container">
      
      {/* --- ЛЕВАЯ ПАНЕЛЬ: ЭДИТОР И ТЕРМИНАЛ --- */}
      <div className="left-panel" style={{ display: 'flex', flexDirection: 'column' }}>
        
        {/* ВЕРХНЯЯ ЧАСТЬ: РЕДАКТОР */}
        <div className="split-80" style={{ display: 'flex', flexDirection: 'column' }}>
          
          <div className="controls" style={{background: 'rgba(0,0,0,0.3)', borderBottom: '1px solid #333'}}>
            <div style={{display:'flex', alignItems:'center', gap:'1rem'}}>
                <span style={{fontWeight:'bold', color:'#aaa', fontSize:'0.9rem'}}>editor.src</span>
                <span style={{fontSize:'0.8rem', background:'#005bb5', padding:'2px 6px', borderRadius:'4px', color: 'white'}}>
                    {editorLang.toUpperCase()}
                </span>
                <span style={{fontSize:'0.8rem', background:'#333', padding:'2px 6px', borderRadius:'4px'}}>
                    {debugInfo}
                </span>
            </div>
            
            <div>
              <button 
                onClick={handleRunCode} 
                className="run-button" 
                disabled={isRunning}
                style={{opacity: isRunning ? 0.7 : 1}}
              >
                {isRunning ? 'Running...' : '▶ Run Code'}
              </button>
              <button onClick={handleFinish} className="finish-button" style={{marginLeft: '10px'}}>
                Submit Solution
              </button>
            </div>
          </div>

          <div className="editor-container" style={{flexGrow: 1}}>
            <Editor 
              height="100%" 
              // Используем динамический язык
              language={editorLang} 
              theme="vs-dark" 
              value={code} 
              onChange={handleCodeChange}
              options={{ 
                fontSize: 15, 
                minimap: { enabled: false }, 
                scrollBeyondLastLine: false,
                automaticLayout: true,
                padding: { top: 16 }
              }}
            />
          </div>
        </div>

        {/* НИЖНЯЯ ЧАСТЬ: КОНСОЛЬ */}
        <div className="split-20" style={{background: '#0d0d0d', borderTop: '2px solid #333', overflow: 'hidden', display:'flex', flexDirection:'column'}}>
            <div style={{padding: '5px 10px', background: '#1a1a1a', color: '#888', fontSize:'0.8rem', fontWeight:'bold', textTransform:'uppercase'}}>
                Terminal Output
            </div>
            <div className="output-container" style={{padding: '1rem', fontFamily: 'monospace', fontSize:'0.9rem', overflowY: 'auto', flexGrow: 1}}>
                {output.stdout ? (
                    <span className="stdout" style={{color: '#e0e0e0'}}>{output.stdout}</span>
                ) : null}
                
                {output.stderr ? (
                    <span className="stderr" style={{color: '#ff6b6b', marginTop:'0.5rem', display:'block'}}>{output.stderr}</span>
                ) : null}

                {!output.stdout && !output.stderr && (
                    <div style={{opacity:0.3, fontStyle:'italic'}}>Waiting for execution results...</div>
                )}
            </div>
        </div>

      </div>
      
      {/* --- ПРАВАЯ ПАНЕЛЬ: AI ЧАТ --- */}
      <div className="right-panel">
        <div className="chat-container">
          
          <div style={{padding:'1rem', borderBottom:'1px solid rgba(255,255,255,0.1)', background:'rgba(0,0,0,0.2)'}}>
            <h3 style={{margin:0, fontSize:'1.1rem', color:'white'}}>AI Interviewer</h3>
            <p style={{margin:0, fontSize:'0.8rem', opacity:0.6}}>Задавайте вопросы по задаче</p>
          </div>

          <div className="chat-messages">
            {chatHistory.map((msg, index) => (
              <div key={index} className={`message ${msg.sender}`}>
                <ReactMarkdown>{msg.text}</ReactMarkdown>
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>

          <form className="chat-input" onSubmit={handleSendMessage}>
            <input 
                type="text" 
                placeholder="Напишите вопрос..." 
                value={userInput} 
                onChange={(e) => setUserInput(e.target.value)}
            />
            <button type="submit">➤</button>
          </form>
        </div>
      </div>

    </div>
  );
}

export default CodingInterface;