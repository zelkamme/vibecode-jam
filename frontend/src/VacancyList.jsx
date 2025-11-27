import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { FaArrowLeft, FaEye, FaEdit, FaTrash, FaPowerOff, FaPen } from 'react-icons/fa';

function VacancyList() {
  const navigate = useNavigate(); // Хук для перехода на другие страницы
  
  // Данные
  const [vacancies, setVacancies] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Состояния модальных окон
  const [previewTasks, setPreviewTasks] = useState(null); // Список задач для просмотра
  const [selectedVacancyName, setSelectedVacancyName] = useState(''); // Название вакансии в модалке
  const [editingVacancy, setEditingVacancy] = useState(null); // Вакансия, которую сейчас редактируем

  // 1. Загрузка вакансий при входе
  useEffect(() => {
    loadVacancies();
  }, []);

  const loadVacancies = () => {
    setLoading(true);
    axios.get('/api/vacancies')
      .then(res => {
        setVacancies(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  };

  // --- ЛОГИКА ВАКАНСИЙ ---

  // Сменить статус (Активна/Скрыта)
  const handleToggleStatus = async (vac) => {
    try {
      await axios.put(`/api/vacancies/${vac.id}`, { is_active: !vac.is_active });
      loadVacancies(); // Перезагружаем список
    } catch (e) { 
        alert("Ошибка обновления статуса"); 
    }
  };

  // Удалить вакансию
  const handleDeleteVacancy = async (id) => {
    if (!window.confirm("Вы уверены? Это действие нельзя отменить.")) return;
    try {
      await axios.delete(`/api/vacancies/${id}`);
      loadVacancies();
    } catch (e) { 
        alert("Ошибка удаления"); 
    }
  };

  // Сохранить изменения в вакансии (из модалки)
  const handleSaveVacancy = async () => {
    try {
        await axios.put(`/api/vacancies/${editingVacancy.id}`, editingVacancy);
        setEditingVacancy(null); // Закрываем модалку
        loadVacancies();
    } catch (e) { 
        alert("Ошибка сохранения"); 
    }
  };

  // --- ЛОГИКА ЗАДАЧ ---

  // Загрузить задачи для вакансии (Превью)
  const handlePreview = async (vacancyId, title) => {
    setSelectedVacancyName(title);
    try {
      const res = await axios.get(`/api/vacancies/${vacancyId}/preview-tasks`);
      setPreviewTasks(res.data); // Открывает модалку
    } catch (error) {
      alert("Не удалось загрузить задачи");
    }
  };

  return (
    <div className="hr-page">
      
      {/* ХЕДЕР */}
      <header className="hr-header">
        <div style={{display:'flex', alignItems:'center', gap:'1rem'}}>
             <Link to="/hr/dashboard" className="back-link"><FaArrowLeft /> Назад</Link>
             <h1>Управление вакансиями</h1>
        </div>
        <Link to="/hr/create-vacancy" className="big-button" style={{textDecoration:'none', border:'none', background:'#22c55e'}}>
            + Новая вакансия
        </Link>
      </header>

      {/* ОСНОВНОЙ СПИСОК */}
      <main className="hr-main" style={{marginTop:'2rem'}}>
        {loading ? <p style={{color:'white'}}>Загрузка...</p> : (
            <div className="report-grid">
                {vacancies.map(vac => (
                    <div key={vac.id} className="glass-card" style={{display:'flex', flexDirection:'column', gap:'0.5rem', opacity: vac.is_active ? 1 : 0.6}}>
                        
                        {/* ЗАГОЛОВОК + СТАТУС */}
                        <div style={{display:'flex', justifyContent:'space-between', alignItems:'start'}}>
                            <h3 style={{margin:0, color:'#fff'}}>{vac.title}</h3>
                            <span style={{
                                fontSize:'0.7rem', fontWeight:'bold', 
                                padding:'2px 6px', borderRadius:'4px',
                                background: vac.is_active ? '#4caf50' : '#e53935',
                                color: 'white'
                            }}>
                                {vac.is_active ? 'АКТИВНА' : 'СКРЫТА'}
                            </span>
                        </div>

                        {/* ТЕГИ */}
                        <div style={{display:'flex', gap:'0.5rem', flexWrap:'wrap'}}>
                            <span className="level-badge" style={{background:'#333', padding:'2px 8px', borderRadius:'4px', fontSize:'0.8rem'}}>{vac.level}</span>
                            <span className="level-badge" style={{background:'#005bb5', padding:'2px 8px', borderRadius:'4px', fontSize:'0.8rem'}}>{vac.language}</span>
                        </div>
                        
                        <p style={{opacity:0.7, fontSize:'0.9rem', flexGrow:1}}>
                            {vac.skills || 'Навыки не указаны'}
                        </p>
                        
                        {/* КНОПКИ УПРАВЛЕНИЯ ВНИЗУ КАРТОЧКИ */}
                        <div style={{marginTop:'auto', display:'grid', gridTemplateColumns:'1fr 1fr', gap:'0.5rem'}}>
                             <button className="link-button" onClick={() => handlePreview(vac.id, vac.title)} title="Просмотр заданий">
                                <FaEye /> Задания
                             </button>
                             <button className="link-button" onClick={() => setEditingVacancy(vac)} title="Редактировать вакансию">
                                <FaEdit /> Изм.
                             </button>
                             <button className="link-button" onClick={() => handleToggleStatus(vac)} 
                                style={{color: vac.is_active ? '#ff9800' : '#4caf50'}}>
                                <FaPowerOff /> {vac.is_active ? 'Скрыть' : 'Открыть'}
                             </button>
                             <button className="link-button" onClick={() => handleDeleteVacancy(vac.id)} style={{color:'#ff5555'}}>
                                <FaTrash /> Удалить
                             </button>
                        </div>
                    </div>
                ))}
            </div>
        )}
      </main>

      {/* --- МОДАЛКА 1: СПИСОК ЗАДАЧ --- */}
      {previewTasks && (
        <div className="modal-overlay" onClick={() => setPreviewTasks(null)}>
            <div className="modal-content" onClick={e => e.stopPropagation()}>
                <button className="close-modal-btn" onClick={() => setPreviewTasks(null)}>×</button>
                <h2 style={{marginTop:0}}>Задания для: {selectedVacancyName}</h2>
                
                <div style={{maxHeight:'60vh', overflowY:'auto', paddingRight:'10px'}}>
                    {previewTasks.length === 0 ? (
                        <p>Задач для этого уровня пока нет.</p>
                    ) : (
                        previewTasks.map(task => (
                            <div key={task.id} className="task-preview-item">
                                <div style={{display:'flex', justifyContent:'space-between', marginBottom:'0.5rem'}}>
                                    
                                    {/* Тип задачи */}
                                    <div style={{display:'flex', alignItems:'center', gap:'0.5rem'}}>
                                        <span style={{
                                            color: task.type === 'coding' ? '#58a6ff' : (task.type === 'psy' ? '#ff79c6' : '#f1fa8c'),
                                            fontWeight: 'bold'
                                        }}>
                                            {task.type === 'coding' ? '💻 Coding' : (task.type === 'psy' ? '🧠 Soft Skills' : '📖 Theory')}
                                        </span>
                                    </div>

                                    {/* ID и Кнопка редактирования */}
                                    <div style={{display:'flex', alignItems:'center', gap:'1rem'}}>
                                        <span style={{opacity:0.5, fontSize:'0.8rem'}}>ID: {task.id}</span>
                                        
                                        {/* ВОТ ЭТА КНОПКА ПЕРЕКИДЫВАЕТ В РЕДАКТОР */}
                                        <button 
                                            onClick={() => navigate(`/hr/edit-task/${task.id}`)} 
                                            style={{background:'none', border:'none', cursor:'pointer', color:'#aaa', fontSize:'1rem'}}
                                            title="Редактировать в конструкторе"
                                        >
                                            <FaPen />
                                        </button>

                                    </div>
                                </div>
                                <div style={{whiteSpace: 'pre-wrap', opacity:0.9, fontSize:'0.9rem'}}>
                                    {/* Показываем только начало текста, чтобы не захламлять */}
                                    {task.text.substring(0, 150)}{task.text.length > 150 ? '...' : ''}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
      )}

      {/* --- МОДАЛКА 2: РЕДАКТИРОВАНИЕ САМОЙ ВАКАНСИИ --- */}
      {editingVacancy && (
        <div className="modal-overlay">
            <div className="modal-content" style={{maxWidth:'500px'}}>
                <h3>Редактировать вакансию</h3>
                
                <label style={{fontSize:'0.8rem', opacity:0.7}}>Название</label>
                <input 
                    className="glass-input" 
                    value={editingVacancy.title} 
                    onChange={e => setEditingVacancy({...editingVacancy, title: e.target.value})} 
                />
                
                <label style={{fontSize:'0.8rem', opacity:0.7, marginTop:'1rem', display:'block'}}>Навыки</label>
                <input 
                    className="glass-input" 
                    value={editingVacancy.skills} 
                    onChange={e => setEditingVacancy({...editingVacancy, skills: e.target.value})} 
                />
                
                <label style={{fontSize:'0.8rem', opacity:0.7, marginTop:'1rem', display:'block'}}>Зарплата</label>
                <input 
                    className="glass-input" 
                    value={editingVacancy.salary_range} 
                    onChange={e => setEditingVacancy({...editingVacancy, salary_range: e.target.value})} 
                />

                <div style={{display:'flex', gap:'1rem', marginTop:'2rem'}}>
                    <button className="big-button" onClick={handleSaveVacancy} style={{flex:1, background:'#4caf50', border:'none'}}>Сохранить</button>
                    <button className="big-button" onClick={() => setEditingVacancy(null)} style={{flex:1, background:'rgba(255,255,255,0.1)'}}>Отмена</button>
                </div>
            </div>
        </div>
      )}

    </div>
  );
}

export default VacancyList;