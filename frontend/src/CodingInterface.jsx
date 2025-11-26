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

  // Ссылка на конец чата для автоскролла
  const chatEndRef = useRef(null);

  // Телеметрия (Анти-чит)
  const telemetry = useRef({
    focusLost: 0,
    mouseLeftWindow: 0,
    largePastes: 0,
    codeHistory: []
  });

  // 1. Загрузка задачи при старте
  useEffect(() => {
    const fetchTask = async () => {
      const savedLevel = localStorage.getItem('candidateLevel') || 'Intern';
      setDebugInfo(savedLevel);
      
      try {
        const response = await axios.get(`/api/task/coding/${savedLevel}`);
        const task = response.data;
        setTaskId(task.id);

        if (task.id === 0) {
             setCode(`# ${task.description}`);
             setChatHistory([{ sender: 'ai', text: `**Статус:** ${task.title}\n\n${task.description}` }]);
        } else {
            let initialCode = "# Напишите ваше решение здесь\n";
            if (task.files && Array.isArray(task.files)) {
                const mainFile = task.files.find(f => f.name === 'main.py');
                if (mainFile) initialCode = mainFile.content;
            }
            setCode(initialCode);
            
            // Первая запись истории кода
            telemetry.current.codeHistory.push(initialCode);
            
            // Приветственное сообщение в чат с описанием задачи
            setChatHistory([
              { 
                sender: 'ai', 
                text: `### Задача: ${task.title}\n\n${task.description}\n\n_Вы можете задавать мне вопросы по условию или синтаксису._` 
              }
            ]);
        }

      } catch (error) {
        console.error("Ошибка:", error);
        setCode("# Ошибка соединения с сервером.");
      } finally {
        setLoading(false);
      }
    };

    fetchTask();
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
    // Детекция больших вставок (Copy-Paste)
    if (newCode && code && newCode.length - code.length > 50) {
        telemetry.current.largePastes++;
    }
    setCode(newCode || "");
  };

  const handleRunCode = async () => {
    if (isRunning) return;
    setIsRunning(true);
    
    // Сохраняем снапшот кода для истории
    telemetry.current.codeHistory.push(code);
    
    setOutput({ stdout: '', stderr: 'Запуск контейнера...' });
    
    try {
      const response = await axios.post('/api/run-code', {
        code: code,
        language: 'python',
        task_id: taskId
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
      const response = await axios.post('/api/chat', {
        message: userInput,
        history: chatHistory // Отправляем контекст
      });
      setChatHistory(prev => [...prev, response.data]);
    } catch (error) {
       setChatHistory(prev => [...prev, { sender: 'ai', text: '_AI сейчас недоступен. Попробуйте позже._' }]);
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
        const response = await axios.post('/api/analyze-integrity', {
            user_id: parseInt(currentUserId),
            focusLost: telemetry.current.focusLost,
            mouseLeftWindow: telemetry.current.mouseLeftWindow,
            largePastes: telemetry.current.largePastes,
            codeHistory: telemetry.current.codeHistory
        });
        // Передаем данные, полученные от бэка (там может быть score)
        onComplete(response.data); 
    } catch (error) {
        console.error("Ошибка сохранения:", error);
        // Если бэк упал, всё равно пускаем дальше, но с нулевым скором
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
        
        {/* ВЕРХНЯЯ ЧАСТЬ: РЕДАКТОР (80%) */}
        {/* Класс .split-80 должен быть определен в App.css (height: 80%) */}
        <div className="split-80" style={{ display: 'flex', flexDirection: 'column' }}>
          
          {/* Панель управления */}
          <div className="controls" style={{background: 'rgba(0,0,0,0.3)', borderBottom: '1px solid #333'}}>
            <div style={{display:'flex', alignItems:'center', gap:'1rem'}}>
                <span style={{fontWeight:'bold', color:'#aaa', fontSize:'0.9rem'}}>main.py</span>
                <span style={{fontSize:'0.8rem', background:'#333', padding:'2px 6px', borderRadius:'4px'}}>{debugInfo}</span>
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

          {/* Monaco Editor */}
          <div className="editor-container" style={{flexGrow: 1}}>
            <Editor 
              height="100%" 
              language="python" 
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

        {/* НИЖНЯЯ ЧАСТЬ: КОНСОЛЬ (20%) */}
        {/* Класс .split-20 должен быть определен в App.css (height: 20%) */}
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
          
          {/* Заголовок чата */}
          <div style={{padding:'1rem', borderBottom:'1px solid rgba(255,255,255,0.1)', background:'rgba(0,0,0,0.2)'}}>
            <h3 style={{margin:0, fontSize:'1.1rem', color:'white'}}>AI Interviewer</h3>
            <p style={{margin:0, fontSize:'0.8rem', opacity:0.6}}>Задавайте вопросы по задаче</p>
          </div>

          {/* Сообщения */}
          <div className="chat-messages">
            {chatHistory.map((msg, index) => (
              <div key={index} className={`message ${msg.sender}`}>
                <ReactMarkdown>{msg.text}</ReactMarkdown>
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>

          {/* Ввод */}
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