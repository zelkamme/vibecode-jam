// frontend/src/CodingInterface.jsx

import React, { useState, useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown'; // <-- ИМПОРТ ДЛЯ MD

function CodingInterface({ onComplete }) {
  const [code, setCode] = useState('# Загрузка задачи...\n');
  const [output, setOutput] = useState({ stdout: '', stderr: '' });
  const [chatHistory, setChatHistory] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [taskId, setTaskId] = useState(0);
  const [loading, setLoading] = useState(true);
  const [debugInfo, setDebugInfo] = useState('');

  const telemetry = useRef({
    focusLost: 0,
    mouseLeftWindow: 0,
    largePastes: 0,
    codeHistory: []
  });

  useEffect(() => {
    const fetchTask = async () => {
      const savedLevel = localStorage.getItem('candidateLevel') || 'Intern';
      setDebugInfo(savedLevel);
      
      try {
        const response = await axios.get(`http://localhost:8000/api/task/coding/${savedLevel}`);
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
            telemetry.current.codeHistory.push(initialCode);
            
            // ВОТ ТУТ ТЕКСТ БУДЕТ С MD
            setChatHistory([
              { 
                sender: 'ai', 
                text: `**Задача:** ${task.title}\n\n${task.description}` 
              }
            ]);
        }

      } catch (error) {
        console.error("Ошибка:", error);
        setCode("# Ошибка сети.");
      } finally {
        setLoading(false);
      }
    };

    fetchTask();
  }, []);

  // --- АНТИ-ЧИТ ---
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

  const handleCodeChange = (newCode) => {
    if (newCode.length - code.length > 50) telemetry.current.largePastes++;
    setCode(newCode);
  };

  const handleRunCode = async () => {
    telemetry.current.codeHistory.push(code);
    setOutput({ stdout: 'Запуск контейнера...', stderr: '' });
    try {
      const response = await axios.post('http://localhost:8000/api/run-code', {
        code: code,
        language: 'python',
        task_id: taskId
      });
      setOutput(response.data);
    } catch (error) {
      setOutput({ stdout: '', stderr: `Ошибка: ${error.message}` });
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
        history: chatHistory
      });
      setChatHistory(prev => [...prev, response.data]);
    } catch (error) {
       setChatHistory(prev => [...prev, { sender: 'ai', text: 'AI недоступен.' }]);
    }
  };

  const handleFinish = async () => {
    const currentUserId = localStorage.getItem('currentCandidateId');
    if (!currentUserId) {
        alert("Ошибка: ID пользователя не найден. Перезайдите.");
        onComplete({ finalScore: 0 });
        return;
    }

    try {
        const response = await axios.post('http://localhost:8000/api/analyze-integrity', {
            user_id: parseInt(currentUserId),
            focusLost: telemetry.current.focusLost,
            mouseLeftWindow: telemetry.current.mouseLeftWindow,
            largePastes: telemetry.current.largePastes,
            codeHistory: telemetry.current.codeHistory
        });
        onComplete(response.data); 
    } catch (error) {
        console.error("Ошибка сохранения:", error);
        alert("Не удалось сохранить результат в БД. Проверьте консоль.");
        onComplete({ finalScore: 0, ...telemetry.current });
    }
  };

  if (loading) return <div className="glass-card" style={{margin: '2rem'}}><h2>Загрузка...</h2></div>;

  return (
    <div className="main-container">
      <div className="left-panel">
        <div className="controls">
          <h3>Редактор ({debugInfo})</h3>
          <div>
            <button onClick={handleRunCode} className="run-button">▶ Запустить</button>
            <button onClick={handleFinish} className="finish-button">Завершить</button>
          </div>
        </div>
        <div className="editor-container">
          <Editor 
            height="100%" language="python" theme="vs-dark" 
            value={code} onChange={handleCodeChange}
            options={{ fontSize: 14, minimap: { enabled: false } }}
          />
        </div>
        <div className="output-container">
          <h3>Терминал:</h3>
          {output.stdout && <pre className="stdout">{output.stdout}</pre>}
          {output.stderr && <pre className="stderr">{output.stderr}</pre>}
        </div>
      </div>
      
      <div className="right-panel">
        <div className="chat-container">
          <div className="chat-messages">
            {chatHistory.map((msg, index) => (
              <div key={index} className={`message ${msg.sender}`}>
                {/* ИСПОЛЬЗУЕМ REACT-MARKDOWN */}
                <ReactMarkdown>{msg.text}</ReactMarkdown>
              </div>
            ))}
          </div>
          <form className="chat-input" onSubmit={handleSendMessage}>
            <input type="text" placeholder="Вопрос..." value={userInput} onChange={(e) => setUserInput(e.target.value)}/>
            <button type="submit">Send</button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default CodingInterface;