import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

function TheoryTest({ onComplete }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const chatEndRef = useRef(null);

  // Загружаем первый вопрос при старте (или приветствие AI)
  useEffect(() => {
    const userLevel = localStorage.getItem('candidateLevel') || 'Intern';
    
    // Эмулируем первый запрос к AI для начала интервью
    axios.post(`http://localhost:8000/api/theory/start`, { level: userLevel })
      .then(response => {
        // Бэк должен вернуть { message: "Привет! Первый вопрос..." }
        setMessages([{ sender: 'ai', text: response.data.message }]);
        setLoading(false);
      })
      .catch(err => {
        // Фолбэк, если бэка нет
        console.error(err);
        setMessages([{ sender: 'ai', text: "**Вопрос 1:** Расскажите, как работает Garbage Collector в Python?" }]);
        setLoading(false);
      });
  }, []);

  // Автоскролл вниз
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { sender: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setSending(true);

    try {
      // Отправляем историю чата, чтобы AI понимал контекст (уточняющий вопрос или следующий)
      const response = await axios.post('http://localhost:8000/api/theory/chat', {
        message: userMsg.text,
        history: messages // Отправляем предыдущую историю
      });

      const aiMsg = { sender: 'ai', text: response.data.message };
      setMessages(prev => [...prev, aiMsg]);

      // Если бэк сообщает, что интервью закончено
      if (response.data.isFinished) {
        setTimeout(onComplete, 3000); // Даем прочитать и перекидываем
      }

    } catch (error) {
      setMessages(prev => [...prev, { sender: 'ai', text: "_Ошибка соединения с AI-интервьюером._" }]);
    } finally {
      setSending(false);
    }
  };

  if (loading) return <div className="centered-container"><h2>Подключение AI-интервьюера...</h2></div>;

  return (
    <div className="centered-container" style={{ height: '90vh', justifyContent: 'flex-start' }}>
      <h2 style={{margin: '1rem 0'}}>Теоретическое собеседование</h2>
      
      <div className="glass-card theory-chat-container">
        <div className="chat-messages-area">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.sender}`}>
              <ReactMarkdown>{msg.text}</ReactMarkdown>
            </div>
          ))}
          {sending && <div className="message ai typing">... печатает</div>}
          <div ref={chatEndRef} />
        </div>

        <form className="chat-input-area" onSubmit={handleSend}>
          <input 
            type="text" 
            className="glass-input"
            style={{marginTop:0}}
            placeholder="Введите ваш ответ..." 
            value={input}
            autoFocus
            onChange={(e) => setInput(e.target.value)}
          />
          <button type="submit" className="icon-button" style={{width: '50px', height:'auto'}}>
            ➤
          </button>
        </form>
      </div>
      
      <button className="link-button" onClick={onComplete} style={{marginTop:'1rem', fontSize:'0.9rem', opacity:0.6}}>
        Пропустить теорию (Debug)
      </button>
    </div>
  );
}

export default TheoryTest;