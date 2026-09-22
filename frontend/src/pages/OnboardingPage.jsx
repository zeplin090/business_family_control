import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../api/axios';

export default function OnboardingPage() {
  const [familyName, setFamilyName] = useState('');
  const [inviteCode, setInviteCode] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleCreateFamily = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await apiClient.post('/family/', { name: familyName });
      // После успешного создания направляем в дашборд/бюджет
      navigate('/budget');
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка при создании семьи');
    } finally {
      setLoading(false);
    }
  };

  const handleJoinFamily = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await apiClient.post('/family/join', { invite_code: inviteCode });
      // После успешного присоединения направляем в дашборд/бюджет
      navigate('/budget');
    } catch (err) {
      if (err.response?.status === 404) {
        setError('Неверный код приглашения. Проверьте код и попробуйте снова.');
      } else {
        setError(err.response?.data?.detail || 'Ошибка при присоединении к семье');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-lg w-full bg-white p-8 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-center text-gray-900 mb-2">
          Добро пожаловать!
        </h2>
        <p className="text-center text-gray-600 mb-8 text-sm">
          Для начала работы создайте новую семейную группу или присоединитесь к существующей по коду приглашения.
        </p>

        {error && (
          <div className="bg-red-100 text-red-700 p-3 rounded mb-6 text-sm text-center">
            {error}
          </div>
        )}

        {/* Блок создания семьи */}
        <div className="mb-8">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Создать новую семью</h3>
          <form onSubmit={handleCreateFamily} className="flex gap-3">
            <input
              type="text"
              required
              placeholder="Например, Семья Ивановых"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={familyName}
              onChange={(e) => setFamilyName(e.target.value)}
            />
            <button
              type="submit"
              disabled={loading || !familyName.trim()}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              Создать
            </button>
          </form>
        </div>

        {/* Разделитель */}
        <div className="relative mb-8">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">ИЛИ</span>
          </div>
        </div>

        {/* Блок присоединения */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Присоединиться по коду</h3>
          <form onSubmit={handleJoinFamily} className="flex gap-3">
            <input
              type="text"
              required
              placeholder="Введите инвайт-код (например, aB3_f8Kx)"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              value={inviteCode}
              onChange={(e) => setInviteCode(e.target.value)}
            />
            <button
              type="submit"
              disabled={loading || !inviteCode.trim()}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
            >
              Войти
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}