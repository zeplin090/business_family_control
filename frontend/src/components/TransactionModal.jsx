import { useState, useEffect } from 'react';
import { apiClient } from '../api/axios';

export default function TransactionModal({ isOpen, onClose, onSuccess }) {
  // Состояния формы
  const [type, setType] = useState('expense'); // 'expense' или 'income'
  const [amount, setAmount] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]); // Сегодня по умолчанию
  const [comment, setComment] = useState('');

  // Состояния данных и UI
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [warning, setWarning] = useState(null); // Для предупреждений о лимитах

  // Загрузка категорий при открытии модалки
  useEffect(() => {
    if (isOpen) {
      fetchCategories();
      // Сброс формы
      setAmount('');
      setComment('');
      setError(null);
      setWarning(null);
    }
  }, [isOpen]);

  const fetchCategories = async () => {
    try {
      const response = await apiClient.get('/categories/');
      setCategories(response.data);
    } catch (err) {
      setError('Не удалось загрузить список категорий');
    }
  };

  // Фильтруем категории в зависимости от выбранного типа (доход/расход)
  const filteredCategories = categories.filter((cat) => cat.type === type);

  // Автоматически выбираем первую категорию при смене типа
  useEffect(() => {
    if (filteredCategories.length > 0 && !filteredCategories.find(c => c.id === Number(categoryId))) {
      setCategoryId(filteredCategories[0].id);
    } else if (filteredCategories.length === 0) {
      setCategoryId('');
    }
  }, [type, categories]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setWarning(null);

    // 1. Клиентская валидация (п. 7.2 ТЗ - Ввод невалидных данных)
    const numAmount = parseFloat(amount);
    if (isNaN(numAmount) || numAmount <= 0) {
      setError('Сумма должна быть числом больше нуля');
      return;
    }
    if (!categoryId) {
      setError('Пожалуйста, создайте и выберите категорию');
      return;
    }

    setLoading(true);
    try {
      const response = await apiClient.post('/transactions/', {
        amount: numAmount,
        date: date,
        comment: comment || null,
        category_id: parseInt(categoryId, 10),
      });

      // 2. Обработка предупреждения о превышении лимита
      if (response.data.limit_warning) {
        setWarning(response.data.limit_warning);
        // Не закрываем модалку сразу, даем пользователю прочитать предупреждение
        setTimeout(() => {
          onSuccess(); 
          onClose();
        }, 4000);
      } else {
        // Успех без превышения лимитов
        onSuccess();
        onClose();
      }
    } catch (err) {
      // 3. Обработка серверных ошибок (например, отвалилась сеть или 400 Bad Request)
      if (err.message === 'Network Error') {
        setError('Отсутствует соединение с сервером. Проверьте интернет.');
      } else {
        setError(err.response?.data?.detail || 'Произошла ошибка при сохранении транзакции');
      }
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md overflow-hidden">
        
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h3 className="text-lg font-semibold text-gray-900">Добавить операцию</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            &#x2715;
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          
          {/* Индикаторы ошибок и предупреждений */}
          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}
          {warning && (
            <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 mb-4">
              <p className="text-sm text-yellow-700 font-medium">{warning}</p>
            </div>
          )}

          {/* Переключатель Доход / Расход */}
          <div className="flex bg-gray-100 p-1 rounded-md mb-4">
            <button
              type="button"
              className={`flex-1 py-2 text-sm font-medium rounded-md transition-colors ${
                type === 'expense' ? 'bg-white shadow text-gray-900' : 'text-gray-500 hover:text-gray-700'
              }`}
              onClick={() => setType('expense')}
            >
              Расход
            </button>
            <button
              type="button"
              className={`flex-1 py-2 text-sm font-medium rounded-md transition-colors ${
                type === 'income' ? 'bg-white shadow text-gray-900' : 'text-gray-500 hover:text-gray-700'
              }`}
              onClick={() => setType('income')}
            >
              Доход
            </button>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Сумма (₽)</label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              required
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="0.00"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Категория</label>
            <select
              required
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 bg-white"
              value={categoryId}
              onChange={(e) => setCategoryId(e.target.value)}
            >
              <option value="" disabled>-- Выберите категорию --</option>
              {filteredCategories.map((cat) => (
                <option key={cat.id} value={cat.id}>{cat.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Дата</label>
            <input
              type="date"
              required
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Комментарий (необязательно)</label>
            <input
              type="text"
              maxLength="255"
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Например: Покупка продуктов в Пятерочке"
            />
          </div>

          <div className="pt-4 flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none"
            >
              Отмена
            </button>
            <button
              type="submit"
              disabled={loading || warning !== null}
              className={`px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                type === 'expense' 
                  ? 'bg-red-600 hover:bg-red-700 focus:ring-red-500' 
                  : 'bg-green-600 hover:bg-green-700 focus:ring-green-500'
              } disabled:opacity-50`}
            >
              {loading ? 'Сохранение...' : 'Сохранить'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}