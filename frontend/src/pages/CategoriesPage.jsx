import { useState, useEffect } from 'react';
import { apiClient } from '../api/axios';

export default function CategoriesPage() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Состояния формы добавления
  const [newName, setNewName] = useState('');
  const [newType, setNewType] = useState('expense');
  const [newLimit, setNewLimit] = useState('');
  const [isAdding, setIsAdding] = useState(false);

  // Состояния редактирования лимита
  const [editingId, setEditingId] = useState(null);
  const [editLimitValue, setEditLimitValue] = useState('');

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/categories/');
      setCategories(response.data);
      setError(null);
    } catch (err) {
      setError('Не удалось загрузить категории');
    } finally {
      setLoading(false);
    }
  };

  const handleAddCategory = async (e) => {
    e.preventDefault();
    setIsAdding(true);
    setError(null);
    
    try {
      const payload = {
        name: newName,
        type: newType,
        monthly_limit: newType === 'expense' && newLimit ? parseFloat(newLimit) : null,
      };
      
      const response = await apiClient.post('/categories/', payload);
      setCategories([...categories, response.data]);
      setNewName('');
      setNewLimit('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка при добавлении категории');
    } finally {
      setIsAdding(false);
    }
  };

  const handleDeleteCategory = async (id) => {
    if (!window.confirm('Вы уверены, что хотите удалить эту категорию?')) return;
    
    try {
      await apiClient.delete(`/categories/${id}`);
      setCategories(categories.filter((cat) => cat.id !== id));
      setError(null);
    } catch (err) {
      // Перехват ошибки из backend (ondelete="RESTRICT")
      setError(err.response?.data?.detail || 'Ошибка при удалении категории');
    }
  };

  const startEditingLimit = (category) => {
    setEditingId(category.id);
    setEditLimitValue(category.monthly_limit || '');
  };

  const handleSaveLimit = async (id) => {
    try {
      const payload = {
        monthly_limit: editLimitValue ? parseFloat(editLimitValue) : null,
      };
      const response = await apiClient.patch(`/categories/${id}`, payload);
      
      // Обновляем список локально
      setCategories(categories.map(cat => cat.id === id ? response.data : cat));
      setEditingId(null);
      setError(null);
    } catch (err) {
      // Перехват ошибки 403 (если не администратор)
      setError(err.response?.data?.detail || 'Ошибка при обновлении лимита');
    }
  };

  // Разделяем категории для удобного отображения
  const expenses = categories.filter(c => c.type === 'expense');
  const incomes = categories.filter(c => c.type === 'income');

  if (loading) return <div className="p-8 text-center">Загрузка данных...</div>;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Управление категориями</h1>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Форма добавления */}
      <div className="bg-white p-6 rounded-lg shadow mb-8">
        <h2 className="text-lg font-semibold mb-4">Добавить новую категорию</h2>
        <form onSubmit={handleAddCategory} className="flex flex-wrap gap-4 items-end">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-gray-700 mb-1">Название</label>
            <input
              type="text"
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="Например: Транспорт"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Тип</label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white focus:ring-blue-500 focus:border-blue-500"
              value={newType}
              onChange={(e) => setNewType(e.target.value)}
            >
              <option value="expense">Расход</option>
              <option value="income">Доход</option>
            </select>
          </div>

          {newType === 'expense' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Месячный лимит (₽)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                value={newLimit}
                onChange={(e) => setNewLimit(e.target.value)}
                placeholder="Без лимита"
              />
            </div>
          )}

          <button
            type="submit"
            disabled={isAdding || !newName.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 font-medium"
          >
            {isAdding ? 'Добавление...' : 'Добавить'}
          </button>
        </form>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Список Расходов */}
        <div>
          <h3 className="text-xl font-semibold mb-4 text-red-600 border-b pb-2">Категории расходов</h3>
          <ul className="space-y-3">
            {expenses.map((cat) => (
              <li key={cat.id} className="bg-white p-4 rounded-lg shadow flex justify-between items-center">
                <div className="flex-1">
                  <span className="font-medium">{cat.name}</span>
                  
                  {/* Блок редактирования лимита */}
                  {editingId === cat.id ? (
                    <div className="mt-2 flex gap-2">
                      <input
                        type="number"
                        className="px-2 py-1 border border-gray-300 rounded-md text-sm w-32"
                        value={editLimitValue}
                        onChange={(e) => setEditLimitValue(e.target.value)}
                        placeholder="Без лимита"
                      />
                      <button 
                        onClick={() => handleSaveLimit(cat.id)}
                        className="text-sm bg-green-500 text-white px-2 py-1 rounded"
                      >
                        Сохранить
                      </button>
                      <button 
                        onClick={() => setEditingId(null)}
                        className="text-sm bg-gray-300 text-gray-700 px-2 py-1 rounded"
                      >
                        Отмена
                      </button>
                    </div>
                  ) : (
                    <div className="text-sm text-gray-500 mt-1 flex items-center gap-2">
                      Лимит: {cat.monthly_limit ? `${cat.monthly_limit} ₽` : 'Не установлен'}
                      <button 
                        onClick={() => startEditingLimit(cat)}
                        className="text-blue-500 hover:text-blue-700 underline text-xs"
                      >
                        Изменить
                      </button>
                    </div>
                  )}
                </div>
                
                <button 
                  onClick={() => handleDeleteCategory(cat.id)}
                  className="ml-4 text-red-500 hover:text-red-700 font-bold"
                  title="Удалить категорию"
                >
                  &#x2715;
                </button>
              </li>
            ))}
            {expenses.length === 0 && <p className="text-gray-500 italic">Нет категорий расходов</p>}
          </ul>
        </div>

        {/* Список Доходов */}
        <div>
          <h3 className="text-xl font-semibold mb-4 text-green-600 border-b pb-2">Категории доходов</h3>
          <ul className="space-y-3">
            {incomes.map((cat) => (
              <li key={cat.id} className="bg-white p-4 rounded-lg shadow flex justify-between items-center">
                <span className="font-medium">{cat.name}</span>
                <button 
                  onClick={() => handleDeleteCategory(cat.id)}
                  className="text-red-500 hover:text-red-700 font-bold"
                  title="Удалить категорию"
                >
                  &#x2715;
                </button>
              </li>
            ))}
            {incomes.length === 0 && <p className="text-gray-500 italic">Нет категорий доходов</p>}
          </ul>
        </div>
      </div>
    </div>
  );
}