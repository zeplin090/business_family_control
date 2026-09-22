import { useState, useEffect } from 'react';
import { apiClient } from '../api/axios';

export default function FamilySettingsPage() {
  const [family, setFamily] = useState(null);
  const [joinCode, setJoinCode] = useState('');
  const [newFamilyName, setNewFamilyName] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  // Запрашиваем текущую семью при загрузке
  useEffect(() => {
    fetchMyFamily();
  }, []);

  const fetchMyFamily = async () => {
    try {
      const response = await apiClient.get('/family/me');
      setFamily(response.data);
    } catch (error) {
      // 404 означает, что семьи нет — это нормальная ситуация
      setFamily(null);
    } finally {
      setIsLoading(false);
    }
  };

  // Создание новой семьи (эндпоинт POST /family/)
  const createFamily = async () => {
    if (!newFamilyName.trim()) return;
    try {
      // Предполагаем, что схема FamilyCreate требует поле name. 
      // Если у вас другие поля, измените этот объект.
      const response = await apiClient.post('/family/', { name: newFamilyName.trim() });
      setFamily(response.data);
      setMessage('Семья успешно создана!');
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Ошибка при создании семьи.');
    }
  };

  // Вступление в семью (эндпоинт POST /family/join)
  const joinFamily = async () => {
    if (!joinCode.trim()) return;
    try {
      // Отправляем invite_code согласно вашей схеме FamilyJoin
      const response = await apiClient.post('/family/join', { invite_code: joinCode.trim() });
      setFamily(response.data);
      setMessage('Вы успешно присоединились к семье!');
      setJoinCode('');
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Неверный код приглашения.');
    }
  };

  if (isLoading) {
    return <div className="text-center mt-10 text-slate-500">Загрузка данных...</div>;
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-slate-800">Управление семейной группой</h1>

      {message && (
        <div className="p-4 rounded-md bg-blue-50 text-blue-700 border border-blue-100">
          {message}
        </div>
      )}

      {/* СЦЕНАРИЙ 1: ПОЛЬЗОВАТЕЛЬ УЖЕ В СЕМЬЕ */}
      {family ? (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
            <h2 className="text-xl font-semibold mb-4 text-slate-800">
              {family.name || 'Ваша семья'}
            </h2>
            <p className="text-sm text-slate-600 mb-4">
              Отправьте этот код вашим близким, чтобы они могли присоединиться к общему бюджету.
            </p>
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-md text-center font-mono text-2xl tracking-widest text-slate-800 font-bold">
              {family.invite_code || 'Код не найден'}
            </div>
          </div>

          {/* НОВЫЙ БЛОК: Список участников */}
          <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
            <h3 className="text-lg font-semibold mb-4 text-slate-800">Участники группы</h3>
            {/* Используем family.users (или family.members, если вы назвали связь так) */}
            {(family.users || family.members || []).length > 0 ? (
              <ul className="divide-y divide-slate-100">
                {(family.users || family.members).map((user) => (
                  <li key={user.id} className="py-3 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold">
                        {user.full_name ? user.full_name.charAt(0).toUpperCase() : '?'}
                      </div>
                      <div>
                        <p className="font-medium text-slate-700">{user.full_name}</p>
                        <p className="text-sm text-slate-500">{user.email}</p>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-slate-500">Загрузка участников...</p>
            )}
          </div>
        </div>
      ) : (
        /* СЦЕНАРИЙ 2: ПОЛЬЗОВАТЕЛЬ БЕЗ СЕМЬИ */
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Блок создания */}
          <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm flex flex-col">
            <h2 className="text-lg font-semibold mb-2 text-slate-700">Создать новую семью</h2>
            <p className="text-sm text-slate-500 mb-6 flex-grow">Станьте администратором и пригласите других участников.</p>
            <div className="space-y-4">
              <input 
                type="text" 
                value={newFamilyName}
                onChange={(e) => setNewFamilyName(e.target.value)}
                placeholder="Название семьи (напр. Ивановы)"
                className="w-full p-2.5 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
              <button 
                onClick={createFamily}
                disabled={!newFamilyName.trim()}
                className="w-full bg-blue-600 text-white py-2.5 rounded-md hover:bg-blue-700 transition-colors font-medium disabled:opacity-50"
              >
                Создать
              </button>
            </div>
          </div>

          {/* Блок присоединения */}
          <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm flex flex-col">
            <h2 className="text-lg font-semibold mb-2 text-slate-700">Присоединиться</h2>
            <p className="text-sm text-slate-500 mb-6 flex-grow">Введите код, который вам отправил создатель группы.</p>
            <div className="space-y-4">
              <input 
                type="text" 
                value={joinCode}
                onChange={(e) => setJoinCode(e.target.value)}
                placeholder="Вставьте код приглашения"
                className="w-full p-2.5 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:outline-none font-mono text-center"
              />
              <button 
                onClick={joinFamily}
                disabled={!joinCode.trim()}
                className="w-full bg-slate-800 text-white py-2.5 rounded-md hover:bg-slate-900 transition-colors font-medium disabled:opacity-50"
              >
                Войти в семью
              </button>
            </div>
          </div>
          
        </div>
      )}
    </div>
  );
}