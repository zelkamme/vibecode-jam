import React, { useState, useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';
import axios from 'axios';

function CodingInterface({ onComplete }) {
  const [code, setCode] = useState('# Введите ваш код на Python здесь\ndef reverse_string(s):\n  return s[::-1]\n');
  const [output, setOutput] = useState({ stdout: '', stderr: '' });
  const [chatHistory, setChatHistory] = useState([
    { sender: 'ai', text: 'Здравствуйте! Напишите функцию для разворота строки.' }
  ]);
  const [userInput, setUserInput] = useState('');

  // --- ШПИОНСКИЕ ДАННЫЕ ---
  const telemetry = useRef({
    focusLost: 0,      // Альт-табы
    mouseLeftWindow: 0, // Уход мыши на второй монитор
    largePastes: 0,    // Копипаста
    codeHistory: []    // История версий кода для анализа стиля
  });

  // Сохраняем первую версию кода при загрузке
  useEffect(() => {
    telemetry.current.codeHistory.push(code);
  }, []);

  // --- СЛУШАТЕЛИ СОБЫТИЙ ---
  useEffect(() => {
    // 1. Потеря фокуса (Alt-Tab)
    const handleVisibilityChange = () => {
      if (document.hidden) {
        telemetry.current.focusLost++;
        console.warn('Violation: Focus Lost');
      }
    };

    // 2. Уход мыши за пределы окна (Второй монитор)
    const handleMouseLeave = () => {
      telemetry.current.mouseLeftWindow++;
      console.warn('Violation: Mouse left window');
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    document.body.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      document.body.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, []);

  // 3. Детектор Копипасты (Monaco Event)
  const handleEditorPaste = (value, event) => {
    // В Monaco onPaste немного сложнее, но мы можем просто следить за резким изменением длины текста
    // Проще сделать через onChange, если разница длин > 50 символов
  };

  // Альтернативный детектор копипасты через сравнение длины
  const handleCodeChange = (newCode) => {
    const lengthDiff = newCode.length - code.length;
    if (lengthDiff > 50) {
      telemetry.current.largePastes++;
      console.warn('Violation: Large Paste Detected');
    }
    setCode(newCode);
  };

  const handleRunCode = async () => {
    // Сохраняем версию кода перед запуском
    telemetry.current.codeHistory.push(code);

    try {
      const response = await axios.post('http://localhost:8000/api/run-code', { code });
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
      const response = await axios.post('http://localhost:8000/api/chat', { message: userInput, history: chatHistory });
      setChatHistory(prev => [...prev, response.data]);
    } catch (error) {
       setChatHistory(prev => [...prev, { sender: 'ai', text: 'Ошибка AI' }]);
    }
  };

  // --- ФИНАЛЬНАЯ ОТПРАВКА ---
  const handleFinish = async () => {
    // Сохраняем финальную версию
    telemetry.current.codeHistory.push(code);

    try {
      // Отправляем ВСЁ на бэкенд для анализа
      console.log("Отправка телеметрии...", telemetry.current);
      
      // В реальном проекте ты бы отправил это на бэкенд:
      // await axios.post('http://localhost:8000/api/analyze-integrity', telemetry.current);
      
      // Но пока просто передаем управление в App.jsx
      onComplete(telemetry.current); 
    } catch (e) {
      console.error(e);
      onComplete(telemetry.current);
    }
  };

  return (
    <div className="main-container">
      <div className="left-panel">
        <div className="controls">
          <h3>Редактор кода</h3>
          <div>
            <button onClick={handleRunCode} className="run-button">▶ Запустить</button>
            <button onClick={handleFinish} className="finish-button">Завершить</button>
          </div>
        </div>
        <div className="editor-container">
          <Editor 
            height="100%" 
            language="python" 
            theme="vs-dark" 
            value={code} 
            onChange={handleCodeChange} 
          />
        </div>
        <div className="output-container"><h3>Вывод:</h3>{output.stdout && <pre className="stdout">{output.stdout}</pre>}{output.stderr && <pre className="stderr">{output.stderr}</pre>}</div>
      </div>
      <div className="right-panel">
        <div className="chat-container">
          <div className="chat-messages">{chatHistory.map((msg, index) => ( <div key={index} className={`message ${msg.sender}`}>{msg.text}</div> ))}</div>
          <form className="chat-input" onSubmit={handleSendMessage}>
            <input type="text" placeholder="Ваше сообщение..." value={userInput} onChange={(e) => setUserInput(e.target.value)}/>
            <button type="submit">Отправить</button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default CodingInterface;