import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

function TheoryTest({ onComplete }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  
  // ⚠️ ВАЖНО: Храним ID текущего вопроса, чтобы знать, на что отвечает юзер
  const [currentQId, setCurrentQId] = useState(null);
  
  const chatEndRef = useRef(null);

  // 1. Старт интервью (загрузка первого вопроса)
  useEffect(() => {
    const userLevel = localStorage.getItem('candidateLevel') || 'Intern';
    const userId = localStorage.getItem('currentCandidateId'); // Если есть ID юзера

    axios.post(`http://localhost:8000/api/theory/start`, { 
      level: userLevel,
      user_id: userId 
    })
      .then(response => {
        // Добавляем сообщение от AI
        setMessages([{ sender: 'ai', text: response.data.message }]);
        
        // ⚠️ Сохраняем ID первого вопроса, если он пришел
        if (response.data.question_id) {
            setCurrentQId(response.data.question_id);
        }
        
        setLoading(false);
      })
      .catch(err => {
        console.error("Ошибка старта:", err);
        setMessages([{ sender: 'ai', text: "**Ошибка:** Не удалось соединиться с сервером." }]);
        setLoading(false);
      });
  }, []);

  // Автоскролл
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 2. Отправка ответа пользователя
  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { sender: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setSending(true);

    try {
      const userId = localStorage.getItem('currentCandidateId');

      const response = await axios.post('http://localhost:8000/api/theory/chat', {
        message: userMsg.text,
        history: messages,
        user_id: userId,
        question_id: currentQId // ⚠️ Отправляем ID вопроса, на который ответили
      });

      const aiMsg = { sender: 'ai', text: response.data.message };
      setMessages(prev => [...prev, aiMsg]);

      // ⚠️ Обновляем ID на следующий вопрос (или null, если конец)
      if (response.data.question_id) {
          setCurrentQId(response.data.question_id);
      }

      // Если интервью закончено
      if (response.data.isFinished) {
        setTimeout(onComplete, 3000); 
      }

    } catch (error) {
      console.error(error);
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
          {sending && <div className="message ai typing">... анализирует ответ</div>}
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
            disabled={sending}
          />
          <button type="submit" className="icon-button" style={{width: '50px', height:'auto'}} disabled={sending}>
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