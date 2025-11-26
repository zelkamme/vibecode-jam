// frontend/src/VacancyBuilder.jsx

import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { FaArrowLeft } from 'react-icons/fa';

function VacancyBuilder() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    title: '',
    level: 'Junior',
    language: 'Python',
    skills: '',
    salary_range: ''
  });

  const handleSubmit = async () => {
    if (!form.title || !form.skills) {
        alert("Заполните название и ключевые навыки");
        return;
    }

    try {
        await axios.post(`/api/vacancies`, form);
        alert("Вакансия успешно открыта!");
        navigate('/hr/dashboard');
    } catch (error) {
        console.error(error);
        alert("Ошибка при создании вакансии");
    }
  };

  return (
    <div className="hr-page" style={{minHeight:'100vh', display:'flex', alignItems:'center', justifyContent:'center'}}>
        <div className="glass-card" style={{width: '100%', maxWidth: '600px', padding: '3rem'}}>
            
            <button 
                onClick={() => navigate('/hr/dashboard')} 
                className="link-button"
                style={{ marginBottom: '1.5rem', padding: '0.5rem 0', border: 'none', justifyContent:'flex-start' }}
            >
                <FaArrowLeft /> Назад
            </button>

            <h2 style={{marginBottom: '2rem', color:'white'}}>Открыть новую вакансию</h2>

            <div style={{display:'flex', flexDirection:'column', gap:'1.5rem'}}>
                
                {/* Название */}
                <div>
                    <label style={{color:'#aaa', fontSize:'0.9rem'}}>Название должности</label>
                    <input 
                        className="glass-input" 
                        placeholder="Например: Backend Developer"
                        value={form.title}
                        onChange={e => setForm({...form, title: e.target.value})}
                    />
                </div>

                {/* Группировка: Язык + Уровень */}
                <div style={{display:'flex', gap:'1rem'}}>
                    <div style={{flex:1}}>
                        <label style={{color:'#aaa', fontSize:'0.9rem'}}>Основной язык</label>
                        <select 
                            className="glass-input"
                            value={form.language}
                            onChange={e => setForm({...form, language: e.target.value})}
                        >
                            <option value="Python">Python</option>
                            <option value="JavaScript">JavaScript</option>
                            <option value="Go">Go</option>
                            <option value="Java">Java</option>
                            <option value="C++">C++</option>
                        </select>
                    </div>
                    <div style={{flex:1}}>
                        <label style={{color:'#aaa', fontSize:'0.9rem'}}>Уровень (Grade)</label>
                        <select 
                            className="glass-input"
                            value={form.level}
                            onChange={e => setForm({...form, level: e.target.value})}
                        >
                            <option value="Intern">Intern</option>
                            <option value="Junior">Junior</option>
                            <option value="Middle">Middle</option>
                            <option value="Senior">Senior</option>
                            <option value="Lead">Lead</option>
                        </select>
                    </div>
                </div>

                {/* Навыки */}
                <div>
                    <label style={{color:'#aaa', fontSize:'0.9rem'}}>Ключевые навыки (через запятую)</label>
                    <input 
                        className="glass-input" 
                        placeholder="Docker, FastAPI, SQL, Git..."
                        value={form.skills}
                        onChange={e => setForm({...form, skills: e.target.value})}
                    />
                </div>

                {/* Зарплата (опционально) */}
                <div>
                    <label style={{color:'#aaa', fontSize:'0.9rem'}}>Зарплатная вилка (необязательно)</label>
                    <input 
                        className="glass-input" 
                        placeholder="100 000 - 150 000 руб."
                        value={form.salary_range}
                        onChange={e => setForm({...form, salary_range: e.target.value})}
                    />
                </div>

                <button className="big-button" style={{marginTop:'1rem', background:'#22c55e', border:'none'}} onClick={handleSubmit}>
                    Опубликовать вакансию
                </button>
            </div>
        </div>
    </div>
  );
}

export default VacancyBuilder;
