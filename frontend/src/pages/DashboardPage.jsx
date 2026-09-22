import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../api/axios';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export default function DashboardPage() {
  const [transactions, setTransactions] = useState([]);
  const [members, setMembers] = useState([]);
  
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    authorId: ''
  });

  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    apiClient.get('/analytics/members')
      .then(res => setMembers(res.data))
      .catch(err => console.error("Ошибка загрузки участников:", err));
  }, []);

  const fetchFilteredTransactions = useCallback(async () => {
    setIsLoading(true);
    try {
      const params = {};
      if (filters.startDate) params.start_date = filters.startDate;
      if (filters.endDate) params.end_date = filters.endDate;
      if (filters.authorId) params.author_id = filters.authorId;

      const response = await apiClient.get('/analytics/filter', { params });
      
      const data = response.data;
      setTransactions(data.transactions || (Array.isArray(data) ? data : []));
    } catch (error) {
      console.error("Ошибка загрузки транзакций:", error);
      setTransactions([]); 
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchFilteredTransactions();
  }, [fetchFilteredTransactions]);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const clearFilters = () => {
    setFilters({ startDate: '', endDate: '', authorId: '' });
  };

  // --- Подготовка данных для статистики и графиков ---
  const totalIncome = transactions
    .filter(t => t.type === 'income')
    .reduce((sum, t) => sum + Number(t.amount), 0);

  const totalExpense = transactions
    .filter(t => t.type === 'expense')
    .reduce((sum, t) => sum + Number(t.amount), 0);

  const balance = totalIncome - totalExpense;

  // Группировка расходов по категориям
  const expensesByCategory = transactions
    .filter(t => t.type === 'expense')
    .reduce((acc, t) => {
      acc[t.category_name] = (acc[t.category_name] || 0) + Number(t.amount);
      return acc;
    }, {});
    
  const expenseChartData = Object.keys(expensesByCategory).map(key => ({
    name: key,
    value: expensesByCategory[key]
  }));

  // Группировка доходов по категориям
  const incomesByCategory = transactions
    .filter(t => t.type === 'income')
    .reduce((acc, t) => {
      acc[t.category_name] = (acc[t.category_name] || 0) + Number(t.amount);
      return acc;
    }, {});

  const incomeChartData = Object.keys(incomesByCategory).map(key => ({
    name: key,
    value: incomesByCategory[key]
  }));

  // Палитры цветов для графиков
  const EXPENSE_COLORS = ['#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16', '#10b981', '#06b6d4', '#3b82f6', '#6366f1', '#8b5cf6'];
  const INCOME_COLORS = ['#22c55e', '#10b981', '#14b8a6', '#06b6d4', '#0ea5e9', '#3b82f6'];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-800">История и Аналитика</h1>

      {/* Дашборд со сводкой */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm flex flex-col justify-center">
          <h3 className="text-sm font-medium text-slate-500 mb-1">Всего доходов</h3>
          <p className="text-3xl font-bold text-green-600">+{totalIncome} ₽</p>
        </div>
        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm flex flex-col justify-center">
          <h3 className="text-sm font-medium text-slate-500 mb-1">Всего расходов</h3>
          <p className="text-3xl font-bold text-red-600">-{totalExpense} ₽</p>
        </div>
        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm flex flex-col justify-center">
          <h3 className="text-sm font-medium text-slate-500 mb-1">Баланс за период</h3>
          <p className={`text-3xl font-bold ${balance >= 0 ? 'text-slate-800' : 'text-red-600'}`}>
            {balance > 0 ? '+' : ''}{balance} ₽
          </p>
        </div>
      </div>

      {/* Графики */}
      {(expenseChartData.length > 0 || incomeChartData.length > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          
          {/* График расходов */}
          {expenseChartData.length > 0 && (
            <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
              <h3 className="text-lg font-semibold text-slate-700 mb-4 text-center">Структура расходов</h3>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={expenseChartData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {expenseChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={EXPENSE_COLORS[index % EXPENSE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `${value} ₽`} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* График доходов */}
          {incomeChartData.length > 0 && (
            <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
              <h3 className="text-lg font-semibold text-slate-700 mb-4 text-center">Структура доходов</h3>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={incomeChartData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {incomeChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={INCOME_COLORS[index % INCOME_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `${value} ₽`} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
          
        </div>
      )}

      {/* Панель фильтров */}
      <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm flex flex-col md:flex-row gap-4 items-end">
        <div className="flex flex-col w-full md:w-1/4">
          <label className="text-sm font-medium text-slate-600 mb-1">От даты</label>
          <input 
            type="date" 
            name="startDate"
            value={filters.startDate}
            onChange={handleFilterChange}
            className="p-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
        </div>
        
        <div className="flex flex-col w-full md:w-1/4">
          <label className="text-sm font-medium text-slate-600 mb-1">До даты</label>
          <input 
            type="date" 
            name="endDate"
            value={filters.endDate}
            onChange={handleFilterChange}
            className="p-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
        </div>

        <div className="flex flex-col w-full md:w-1/3">
          <label className="text-sm font-medium text-slate-600 mb-1">Автор</label>
          <select 
            name="authorId"
            value={filters.authorId}
            onChange={handleFilterChange}
            className="p-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:outline-none bg-white"
          >
            <option value="">Все участники</option>
            {members.map(m => (
              <option key={m.id} value={m.id}>{m.full_name}</option>
            ))}
          </select>
        </div>

        <button 
          onClick={clearFilters}
          className="w-full md:w-auto px-4 py-2 bg-slate-100 text-slate-700 font-medium rounded-md hover:bg-slate-200 transition-colors"
        >
          Сбросить
        </button>
      </div>

      {/* Таблица транзакций */}
      <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-slate-500">Загрузка данных...</div>
        ) : transactions.length === 0 ? (
          <div className="p-8 text-center text-slate-500">Транзакции не найдены.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Дата</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Категория</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Сумма</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Автор</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Комментарий</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {transactions.map((t) => (
                  <tr key={t.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-700">
                      {new Date(t.date).toLocaleDateString('ru-RU')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-700">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-800">
                        {t.category_name}
                      </span>
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${t.type === 'income' ? 'text-green-600' : 'text-red-600'}`}>
                      {t.type === 'income' ? '+' : '-'}{t.amount} ₽
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                      {t.author_name}
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-500 max-w-xs truncate">
                      {t.description || '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}