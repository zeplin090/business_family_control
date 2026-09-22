import { useEffect, useState } from 'react';
import { apiClient } from '../api/axios';
import TransactionModal from '../components/TransactionModal';

export default function BudgetPage() {
  // Состояния для данных и загрузки
  const [budgetData, setBudgetData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Состояние для управления модальным окном
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Выносим функцию загрузки отдельно, чтобы вызывать ее и при старте, и после добавления транзакции
  const fetchBudget = async () => {
    try {
      const response = await apiClient.get('/budget/progress');
      setBudgetData(response.data);
    } catch (error) {
      console.error('Ошибка загрузки бюджета:', error);
    } finally {
      setLoading(false);
    }
  };

  // Загружаем данные при монтировании компонента
  useEffect(() => {
    fetchBudget();
  }, []);

  const handleTransactionSuccess = () => {
    // Эта функция сработает после успешного сохранения транзакции.
    // Заново запрашиваем данные с бэкенда, чтобы обновить прогресс-бары.
    fetchBudget(); 
    console.log("Данные успешно обновлены");
  };

  // Показываем загрузку только при первичном рендере (когда данных еще нет)
  if (loading && !budgetData) return <div className="p-8 text-center">Загрузка данных...</div>;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex flex-col sm:flex-row justify-between items-center mb-6 gap-4">
        <h1 className="text-2xl font-bold">Бюджет на текущий месяц</h1>
        
        {/* Кнопка открытия модалки */}
        <button 
          onClick={() => setIsModalOpen(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded shadow hover:bg-blue-700"
        >
          + Добавить операцию
        </button>
      </div>
      
      {/* Рендер прогресс-баров */}
      <div className="space-y-6">
        {budgetData?.progress_bars?.map((item) => (
          <div key={item.category_id} className="bg-white p-4 rounded-lg shadow">
            <div className="flex justify-between mb-2">
              <span className="font-semibold">{item.category_name}</span>
              <span className="text-gray-600">
                {item.spent} / {item.monthly_limit} ₽
              </span>
            </div>
            
            {/* Прогресс-бар */}
            <div className="w-full bg-gray-200 rounded-full h-4">
              <div 
                className={`h-4 rounded-full ${item.percentage >= 90 ? 'bg-red-500' : 'bg-blue-500'}`}
                style={{ width: `${Math.min(item.percentage, 100)}%` }}
              ></div>
            </div>
            
            {item.percentage >= 100 && (
              <p className="text-red-500 text-sm mt-2">Лимит превышен на {item.remaining * -1} ₽!</p>
            )}
          </div>
        ))}

        {(!budgetData?.progress_bars || budgetData.progress_bars.length === 0) && (
          <p className="text-gray-500 text-center py-4">Нет данных о бюджетах на этот месяц.</p>
        )}
      </div>

      {/* Внедрение компонента модального окна */}
      <TransactionModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        onSuccess={handleTransactionSuccess} 
      />
    </div>
  );
}