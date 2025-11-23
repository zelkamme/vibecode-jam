import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { FaCloudUploadAlt, FaFilePdf, FaCheckCircle, FaBriefcase, FaCode, FaMoneyBillWave } from 'react-icons/fa';

function RegistrationPage() {
  const [name, setName] = useState('');
  const [vacancies, setVacancies] = useState([]);
  const [selectedVacancyId, setSelectedVacancyId] = useState(null);
  const [resumeFile, setResumeFile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dragActive, setDragActive] = useState(false);
  
  const navigate = useNavigate();

  useEffect(() => {
    axios.get('http://localhost:8000/api/vacancies')
      .then(res => {
        // Показываем только активные вакансии
        const activeVacs = res.data.filter(v => v.is_active !== false);
        setVacancies(activeVacs);
        if (activeVacs.length > 0) setSelectedVacancyId(activeVacs[0].id);
        setLoading(false);
      })
      .catch(err => console.error("Ошибка загрузки вакансий:", err));
  }, []);

  // --- Drag & Drop логика ---
  const handleDrag = (e) => {
    e.preventDefault(); e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") setDragActive(true);
    else if (e.type === "dragleave") setDragActive(false);
  };
  const handleDrop = (e) => {
    e.preventDefault(); e.stopPropagation(); setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === "application/pdf") setResumeFile(file);
      else alert("Пожалуйста, загрузите PDF");
    }
  };
  const handleFileSelect = (e) => { if (e.target.files[0]) setResumeFile(e.target.files[0]); };

  // --- Регистрация ---
  const handleRegister = async () => {
    if (!name.trim()) return alert('Введите имя');
    if (!selectedVacancyId) return alert('Выберите вакансию');

    const selectedVacancy = vacancies.find(v => v.id === selectedVacancyId);

    try {
      const formData = new FormData();
      formData.append('username', name);
      formData.append('vacancy_id', selectedVacancyId);
      if (resumeFile) formData.append('resume', resumeFile);

      const response = await axios.post('http://localhost:8000/api/register', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      const data = response.data;
      localStorage.setItem('userRole', 'candidate');
      localStorage.setItem('currentCandidateId', data.user_id);
      
      // Сохраняем уровень, который пришел с вакансией
      localStorage.setItem('candidateLevel', selectedVacancy.level); 

      window.location.href = '/interview'; 
    } catch (error) {
      alert('Ошибка регистрации. Проверьте консоль.');
      console.error(error);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card" style={{maxWidth: '800px', width: '100%', padding: '2rem'}}>
        <h2 style={{fontSize: '2rem', marginBottom: '0.5rem'}}>Регистрация</h2>
        <p style={{opacity: 0.6, marginBottom: '2rem'}}>Выберите вакансию и начните тестирование</p>
        
        <div className="registration-content-grid">
            
            {/* ЛЕВАЯ КОЛОНКА: ИМЯ И РЕЗЮМЕ */}
            <div className="reg-left">
                <label style={{display:'block', marginBottom:'0.5rem', opacity:0.8}}>1. Представьтесь</label>
                <input 
                    type="text" 
                    placeholder="Имя Фамилия" 
                    value={name} 
                    onChange={(e) => setName(e.target.value)} 
                    className="glass-input"
                    style={{marginBottom: '1.5rem'}}
                />

                <label style={{display:'block', marginBottom:'0.5rem', opacity:0.8}}>2. Загрузите резюме</label>
                <div 
                    className={`drop-zone ${dragActive ? 'active' : ''}`}
                    onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}
                    onClick={() => document.getElementById('resumeInput').click()}
                >
                    <input id="resumeInput" type="file" accept=".pdf" onChange={handleFileSelect} style={{display: 'none'}} />
                    {resumeFile ? (
                    <div className="file-info">
                        <FaFilePdf size={24} color="#e53935" />
                        <span>{resumeFile.name}</span>
                        <button onClick={(e) => {e.stopPropagation(); setResumeFile(null)}} className="remove-file">×</button>
                    </div>
                    ) : (
                    <div className="upload-placeholder">
                        <FaCloudUploadAlt size={30} style={{marginBottom: '0.5rem'}}/>
                        <p>PDF файл сюда</p>
                    </div>
                    )}
                </div>
            </div>

            {/* ПРАВАЯ КОЛОНКА: ВЫБОР ВАКАНСИИ (КАРТОЧКИ) */}
            <div className="reg-right">
                <label style={{display:'block', marginBottom:'0.5rem', opacity:0.8}}>3. Выберите вакансию</label>
                {loading ? <p>Загрузка списка...</p> : (
                    <div className="vacancies-grid-select">
                        {vacancies.map(vac => (
                            <div 
                                key={vac.id} 
                                className={`vacancy-select-card ${selectedVacancyId === vac.id ? 'active' : ''}`}
                                onClick={() => setSelectedVacancyId(vac.id)}
                            >
                                <div className="vac-header">
                                    <h4>{vac.title}</h4>
                                    {selectedVacancyId === vac.id && <FaCheckCircle color="#4caf50" />}
                                </div>
                                
                                <div className="vac-badges">
                                    <span className="badge-level">{vac.level}</span>
                                    <span className="badge-lang">{vac.language}</span>
                                </div>

                                <div className="vac-details">
                                    {vac.salary_range && (
                                        <div className="vac-detail-item" style={{color: '#81c784'}}>
                                            <FaMoneyBillWave /> {vac.salary_range}
                                        </div>
                                    )}
                                    <div className="vac-detail-item">
                                        <FaCode /> {vac.skills ? vac.skills.substring(0, 30) + '...' : 'General Skills'}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>

        <div className="reg-actions" style={{marginTop: '2rem', display: 'flex', gap: '1rem'}}>
            <button className="link-button" onClick={() => navigate('/login')}>Назад</button>
            <button className="big-button candidate-btn" onClick={handleRegister} style={{flexGrow: 1}}>
                Начать тестирование
            </button>
        </div>

      </div>
    </div>
  );
}

export default RegistrationPage;