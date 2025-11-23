import React, { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import axios from 'axios';
import { FaPlus, FaTrash, FaFile, FaArrowLeft } from 'react-icons/fa';
import { useNavigate, useParams } from 'react-router-dom';

function TaskBuilder() {
  const navigate = useNavigate();
  const { taskId } = useParams();
  const isEditMode = !!taskId;

  const [taskType, setTaskType] = useState('coding');
  const [loading, setLoading] = useState(false);

  const [task, setTask] = useState({
    title: '',
    description: '',
    referenceAnswer: '', // Для теории (текст) и для Psy (JSON строка)
    level: 'Intern',
    envId: 'basic'
  });

  const [files, setFiles] = useState([
    { name: 'main.py', content: 'print("Hello World")', readonly: false }
  ]);
  const [activeFileIndex, setActiveFileIndex] = useState(0);
  const [newFileName, setNewFileName] = useState('');

  // --- ЗАГРУЗКА ДАННЫХ ПРИ РЕДАКТИРОВАНИИ ---
  useEffect(() => {
    if (isEditMode) {
      setLoading(true);
      axios.get(`http://localhost:8000/api/questions/${taskId}`)
        .then(res => {
          const data = res.data;
          
          setTaskType(data.type);

          // ЛОГИКА ДЛЯ SOFT SKILLS и THEORY
          let refAnswer = data.referenceAnswer || '';
          
          // Если это Psy, то варианты ответов лежат в data.files (массив)
          // Нам нужно превратить их в красивый JSON для текстового поля
          if (data.type === 'psy' && data.files && data.files.length > 0) {
             refAnswer = JSON.stringify(data.files, null, 2);
          }

          setTask({
            title: data.title,
            description: data.description,
            referenceAnswer: refAnswer,
            level: data.level,
            envId: (data.required_tag && data.required_tag.includes('pandas')) ? 'data-science' : 'basic'
          });

          // Если это Кодинг, загружаем файлы в редактор
          if (data.type === 'coding' && data.files && data.files.length > 0) {
            setFiles(data.files);
          }
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          alert("Ошибка загрузки задачи");
          navigate('/hr/dashboard');
        });
    }
  }, [taskId]);


  // --- ФАЙЛОВЫЕ ФУНКЦИИ ---
  const handleAddFile = () => { if(!newFileName.trim()) return; setFiles([...files, { name: newFileName, content: '', readonly: false }]); setNewFileName(''); setActiveFileIndex(files.length); };
  const handleDeleteFile = (index) => { const newFiles = files.filter((_, i) => i !== index); setFiles(newFiles); setActiveFileIndex(0); };
  const handleFileContentChange = (value) => { 
      setFiles(prev => {
          const newFiles = [...prev];
          newFiles[activeFileIndex] = { ...newFiles[activeFileIndex], content: value };
          return newFiles;
      });
  };

  // --- СОХРАНЕНИЕ ---
  const handleSaveTask = async () => {
    if (!task.title.trim() || !task.description.trim()) {
      alert("Заполните название и описание.");
      return;
    }
    setLoading(true);

    // Подготовка payload
    let finalFiles = [];
    
    if (taskType === 'coding') {
        finalFiles = files;
    } else if (taskType === 'psy') {
        // Для Psy пытаемся распарсить JSON из текстового поля обратно в массив
        try {
            if (task.referenceAnswer.trim()) {
                finalFiles = JSON.parse(task.referenceAnswer);
            }
        } catch (e) {
            alert("Ошибка в JSON формате вариантов ответов! Проверьте синтаксис.");
            setLoading(false);
            return;
        }
    }

    const payload = {
      ...task,
      type: taskType,
      files: finalFiles // Отправляем файлы (код или варианты ответов)
    };

    try {
      if (isEditMode) {
        await axios.put(`http://localhost:8000/api/questions/${taskId}`, payload);
        alert("✅ Задача успешно обновлена!");
      } else {
        await axios.post('http://localhost:8000/api/tasks', payload);
        alert("✅ Задача создана!");
        setTask({ title: '', description: '', referenceAnswer: '', level: 'Intern', envId: 'basic' });
      }
    } catch (error) {
      console.error(error);
      alert("Ошибка сохранения.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="task-builder-page" style={{ padding: '2rem', color: '#fff', height: '100vh', boxSizing: 'border-box', display: 'flex', flexDirection: 'column' }}>
      
      <div style={{ marginBottom: '1rem', display:'flex', justifyContent:'space-between' }}>
        <button 
          onClick={() => navigate(-1)} 
          className="link-button"
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', border: 'none', background: 'transparent', color: '#aaa' }}
        >
          <FaArrowLeft /> Назад
        </button>
        <h2 style={{margin:0, fontSize:'1.2rem', color:'white'}}>
            {isEditMode ? `Редактирование задачи #${taskId}` : 'Создание новой задачи'}
        </h2>
      </div>

      <div className="glass-card task-builder-container" style={{ flexGrow: 1, overflow: 'hidden' }}>
        
        {/* ЛЕВАЯ ПАНЕЛЬ */}
        <div className="settings-panel">
          
          <div className="task-type-tabs">
            <div className={`type-tab ${taskType === 'coding' ? 'active' : ''}`} onClick={() => setTaskType('coding')}>💻 Кодинг</div>
            <div className={`type-tab ${taskType === 'theory' ? 'active' : ''}`} onClick={() => setTaskType('theory')}>📖 Теория</div>
            <div className={`type-tab ${taskType === 'psy' ? 'active' : ''}`} onClick={() => setTaskType('psy')}>🧠 Soft Skills</div>
          </div>
          
          <div style={{marginTop: '1rem'}}>
            <label>Название</label>
            <input className="glass-input" value={task.title} onChange={e => setTask({...task, title: e.target.value})} />
          </div>

          <div>
            <label>Уровень</label>
            <select className="glass-input" value={task.level} onChange={e => setTask({...task, level: e.target.value})}>
              <option value="Intern">Intern</option>
              <option value="Junior">Junior</option>
              <option value="Middle">Middle</option>
              <option value="Senior">Senior</option>
              <option value="Lead">Lead</option> {/* ДОБАВЛЕН УРОВЕНЬ LEAD */}
              <option value="All">All (Для Soft Skills)</option>
            </select>
          </div>

          {taskType === 'coding' && (
             <div>
                <label>Среда выполнения</label>
                <div className="env-selector">
                   <div className={`env-card ${task.envId === 'basic' ? 'active' : ''}`} onClick={() => setTask({...task, envId: 'basic'})}>Python Basic</div>
                   <div className={`env-card ${task.envId === 'data-science' ? 'active' : ''}`} onClick={() => setTask({...task, envId: 'data-science'})}>Data Science</div>
                </div>
             </div>
          )}

          {/* ПОЛЕ ДЛЯ ПРАВИЛЬНОГО ОТВЕТА ИЛИ JSON ОПЦИЙ */}
          {(taskType === 'theory' || taskType === 'psy') && (
            <div>
               <label>{taskType === 'psy' ? 'JSON с вариантами ответов' : 'Правильный ответ (для HR)'}</label>
               <textarea 
                className="glass-input" 
                style={{ height: '120px', resize: 'vertical', borderColor: '#4caf50', fontFamily: 'monospace', fontSize: '0.9rem' }}
                value={task.referenceAnswer}
                onChange={e => setTask({...task, referenceAnswer: e.target.value})}
                placeholder={taskType === 'psy' ? '[ {"answerText": "...", "isCorrect": true}, ... ]' : 'Текст правильного ответа...'}
              />
            </div>
          )}

          <div style={{flexGrow: 1, display: 'flex', flexDirection: 'column', marginTop: '1rem'}}>
            <label>Текст задания (Markdown)</label>
            <textarea 
              className="glass-input" 
              style={{ flexGrow: 1, resize: 'none', minHeight: '150px', fontFamily: 'monospace' }}
              value={task.description}
              onChange={e => setTask({...task, description: e.target.value})}
            />
          </div>

          <button className="big-button save-task-btn" onClick={handleSaveTask} disabled={loading} style={{background: isEditMode ? '#ff9800' : '#22c55e'}}>
            {loading ? "Сохранение..." : (isEditMode ? "Сохранить изменения" : "Создать задачу")}
          </button>
        </div>

        {/* ПРАВАЯ ПАНЕЛЬ: РЕДАКТОР КОДА ИЛИ ПРЕВЬЮ */}
        <div className="content-panel" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          {taskType === 'coding' ? (
             <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: 'rgba(0,0,0,0.2)', borderRadius: '12px', overflow: 'hidden' }}>
                 <div className="file-tabs" style={{ display: 'flex', background: 'rgba(255,255,255,0.05)', padding: '0.5rem', gap: '0.5rem' }}>
                    {files.map((file, index) => (
                        <div key={index} className={`file-tab ${activeFileIndex === index ? 'active' : ''}`} onClick={() => setActiveFileIndex(index)}>
                            <FaFile size={12} /> {file.name}
                            {index !== 0 && <FaTrash className="delete-icon" onClick={(e) => { e.stopPropagation(); handleDeleteFile(index); }} />}
                        </div>
                    ))}
                    <div className="add-file-wrapper" style={{marginLeft:'auto', display:'flex', gap:'0.5rem'}}>
                         <input className="glass-input-small" value={newFileName} onChange={e => setNewFileName(e.target.value)} placeholder="new.py" />
                         <button className="icon-button" onClick={handleAddFile}><FaPlus /></button>
                    </div>
                 </div>
                 <div style={{flexGrow: 1}}>
                    <Editor height="100%" theme="vs-dark" defaultLanguage="python" 
                        path={files[activeFileIndex]?.name} 
                        value={files[activeFileIndex]?.content} 
                        onChange={handleFileContentChange} 
                    />
                 </div>
             </div>
          ) : (
             <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', flexDirection: 'column' }}>
                <h3 style={{opacity:0.5}}>Превью (текст)</h3>
                <div className="glass-card" style={{width: '90%', maxHeight:'500px', overflowY:'auto', textAlign:'left'}}>
                    <h4 style={{marginTop:0}}>{task.title}</h4>
                    <p style={{whiteSpace: 'pre-wrap'}}>{task.description}</p>
                </div>
             </div>
          )}
        </div>

      </div>
    </div>
  );
}

export default TaskBuilder;