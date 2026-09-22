import { NavLink, useNavigate, Outlet } from 'react-router-dom';

export default function Layout() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  // Функция для стилизации активных и неактивных ссылок
  const navLinkClass = ({ isActive }) =>
    `inline-flex items-center px-4 py-2 border-b-2 text-sm font-medium transition-colors ${
      isActive
        ? 'border-blue-500 text-blue-600'
        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
    }`;

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900">
      {/* Верхняя навигационная панель */}
      <nav className="bg-white shadow-sm border-b border-slate-200 sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              {/* Логотип / Название */}
              <div className="flex-shrink-0 flex items-center">
                <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
                  FamilyBudget
                </span>
              </div>
              
              {/* Ссылки навигации (десктоп) */}
              <div className="hidden sm:ml-8 sm:flex sm:space-x-4">
                <NavLink to="/budget" className={navLinkClass}>
                  Бюджет
                </NavLink>
                <NavLink to="/dashboard" className={navLinkClass}>
                  Аналитика
                </NavLink>
                <NavLink to="/categories" className={navLinkClass}>
                  Категории
                </NavLink>
                <NavLink 
                    to="/family" 
                    className={navLinkClass}
                    >
                    Семья
                    </NavLink>
              </div>
            </div>

            {/* Правый блок (Выход) */}
            <div className="flex items-center">
              <button
                onClick={handleLogout}
                className="ml-4 px-4 py-2 border border-slate-300 shadow-sm text-sm font-medium rounded-md text-slate-700 bg-white hover:bg-slate-50 focus:outline-none transition-colors"
              >
                Выйти
              </button>
            </div>
          </div>
          
          {/* Мобильная навигация (простой вариант для маленьких экранов) */}
          <div className="sm:hidden flex overflow-x-auto border-t border-slate-100 py-2 space-x-2">
            <NavLink to="/budget" className="px-3 py-1 text-sm font-medium text-slate-600 bg-slate-100 rounded-md">Бюджет</NavLink>
            <NavLink to="/dashboard" className="px-3 py-1 text-sm font-medium text-slate-600 bg-slate-100 rounded-md">Аналитика</NavLink>
            <NavLink to="/categories" className="px-3 py-1 text-sm font-medium text-slate-600 bg-slate-100 rounded-md">Категории</NavLink>
            <NavLink to="/family" className="px-3 py-1 text-sm font-medium text-slate-600 bg-slate-100 rounded-md">Семья</NavLink>
          </div>
        </div>
      </nav>

      {/* Основной контент страницы (здесь будут рендериться BudgetPage, DashboardPage и т.д.) */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
        <Outlet />
      </main>
    </div>
  );
}