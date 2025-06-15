import React, { useState, useEffect } from 'react';
import './App.css';

// @ts-ignore
const tg = window?.Telegram?.WebApp;

const API_URL = 'http://127.0.0.1:8000';

interface SessionInfo {
  last_activity: string;
  model: { data: any[] };
}

type SessionsResponse = Record<string, SessionInfo>;

function App() {
  const [authorized, setAuthorized] = useState(false);
  const [adminKey, setAdminKey] = useState('');
  const [error, setError] = useState('');
  const [sessions, setSessions] = useState<SessionsResponse | null>(null);
  const [times, setTimes] = useState<string[]>([]);
  const [view, setView] = useState<'menu' | 'sessions' | 'times' | 'delete'>('menu');
  const [loading, setLoading] = useState(false);

  // Telegram WebApp init
  useEffect(() => {
    if (tg && tg.initDataUnsafe) {
      // Можно использовать tg.initDataUnsafe.user.id для user_id
      // console.log('Telegram WebApp user:', tg.initDataUnsafe.user);
    }
  }, []);

  // Авторизация (через API)
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    // Можно сделать реальный запрос к API для проверки ключа
    // Пока просто считаем любой непустой ключ валидным
    if (adminKey.trim().length > 0) {
      setAuthorized(true);
      setError('');
    } else {
      setError('Введите admin_key');
    }
  };

  // Получить все сессии
  const fetchSessions = async () => {
    setLoading(true);
    setError('');
    try {
      const resp = await fetch(`${API_URL}/root/session`, {
        headers: { 'Master-Key': adminKey }
      });
      if (!resp.ok) throw new Error('Ошибка API: ' + resp.status);
      const data = await resp.json();
      setSessions(data);
      setView('sessions');
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  // Получить время до конца сессий
  const fetchTimes = async () => {
    setLoading(true);
    setError('');
    try {
      const resp = await fetch(`${API_URL}/root/time`, {
        headers: { 'Master-Key': adminKey }
      });
      if (!resp.ok) throw new Error('Ошибка API: ' + resp.status);
      const data = await resp.json();
      setTimes(data);
      setView('times');
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  // Удалить сессию
  const deleteSession = async (sessionId: string) => {
    setLoading(true);
    setError('');
    try {
      const resp = await fetch(`${API_URL}/root/close?session_id=${sessionId}`, {
        method: 'DELETE',
        headers: { 'Master-Key': adminKey }
      });
      if (!resp.ok) throw new Error('Ошибка API: ' + resp.status);
      await fetchSessions(); // обновить список
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  if (!authorized) {
    return (
      <div className="App">
        <h2>Авторизация</h2>
        <form onSubmit={handleLogin}>
          <input
            type="password"
            placeholder="Введите admin_key"
            value={adminKey}
            onChange={e => setAdminKey(e.target.value)}
          />
          <button type="submit">Войти</button>
        </form>
        {error && <div style={{ color: 'red' }}>{error}</div>}
      </div>
    );
  }

  // Главное меню
  if (view === 'menu') {
    return (
      <div className="App">
        <h2>Telegram Mini App — Admin</h2>
        <button onClick={fetchSessions}>Все сессии</button>
        <button onClick={fetchTimes}>Время до конца</button>
        <button onClick={() => fetchSessions().then(() => setView('delete'))}>Удалить сессию</button>
        {error && <div style={{ color: 'red' }}>{error}</div>}
      </div>
    );
  }

  // Список сессий
  if (view === 'sessions' && sessions) {
    return (
      <div className="App">
        <h2>Все сессии</h2>
        {Object.entries(sessions).length === 0 && <div>Нет активных сессий.</div>}
        {Object.entries(sessions).map(([id, info]) => {
          const session = info as SessionInfo;
          const last = session.last_activity || 'нет данных';
          const items = session.model?.data || [];
          const count = items.length;
          let responsible = '-';
          if (count > 0 && typeof items[0] === 'object') {
            responsible = (items[0] as any)?.PC?.Responsible || '-';
          }
          return (
            <div key={id} style={{ border: '1px solid #ccc', margin: 8, padding: 8 }}>
              <b>ID:</b> <code>{id}</code><br />
              <b>Последняя активность:</b> {last}<br />
              <b>Объектов:</b> {count}<br />
              <b>Ответственный:</b> {responsible}
            </div>
          );
        })}
        <button onClick={() => setView('menu')}>Назад</button>
        {error && <div style={{ color: 'red' }}>{error}</div>}
      </div>
    );
  }

  // Время до конца сессий
  if (view === 'times') {
    return (
      <div className="App">
        <h2>Время до конца сессий</h2>
        {times.length === 0 && <div>Нет активных сессий.</div>}
        {times.map((line, idx) => (
          <div key={idx} style={{ border: '1px solid #ccc', margin: 8, padding: 8 }}>{line}</div>
        ))}
        <button onClick={() => setView('menu')}>Назад</button>
        {error && <div style={{ color: 'red' }}>{error}</div>}
      </div>
    );
  }

  // Удаление сессии
  if (view === 'delete' && sessions) {
    return (
      <div className="App">
        <h2>Удалить сессию</h2>
        {Object.entries(sessions).length === 0 && <div>Нет активных сессий.</div>}
        {Object.entries(sessions).map(([id, info]) => {
          const session = info as SessionInfo;
          const items = session.model?.data || [];
          let responsible = '-';
          if (items.length > 0 && typeof items[0] === 'object') {
            responsible = (items[0] as any)?.PC?.Responsible || '-';
          }
          return (
            <div key={id} style={{ border: '1px solid #ccc', margin: 8, padding: 8 }}>
              <b>ID:</b> <code>{id}</code> ({responsible})
              <button style={{ marginLeft: 8 }} onClick={() => deleteSession(id)}>Удалить</button>
            </div>
          );
        })}
        <button onClick={() => setView('menu')}>Назад</button>
        {error && <div style={{ color: 'red' }}>{error}</div>}
      </div>
    );
  }

  return null;
}

export default App;
