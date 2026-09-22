import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { apiClient } from './api/axios';

import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import BudgetPage from './pages/BudgetPage';
import OnboardingPage from './pages/OnboardingPage';
import DashboardPage from './pages/DashboardPage';
import CategoriesPage from './pages/CategoriesPage';
import Layout from './components/Layout';
import FamilySettingsPage from './pages/FamilySettingsPage';

const RequireAuth = ({ children, requireFamily = true }) => {
  const [isAllowed, setIsAllowed] = useState(null);
  const token = localStorage.getItem('token');

  useEffect(() => {
    if (!token) {
      setIsAllowed(false);
      return;
    }

    apiClient.get('/family/me')
      .then(() => {
        setIsAllowed(requireFamily ? true : 'REDIRECT_TO_BUDGET');
      })
      .catch((err) => {
        if (err.response?.status === 404) {
          setIsAllowed(requireFamily ? 'REDIRECT_TO_ONBOARDING' : true);
        } else {
          setIsAllowed(false);
        }
      });
  }, [token, requireFamily]);

  if (isAllowed === null) return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <div className="animate-pulse text-lg text-slate-500 font-medium">Загрузка приложения...</div>
    </div>
  );
  
  if (isAllowed === false) return <Navigate to="/login" replace />;
  if (isAllowed === 'REDIRECT_TO_ONBOARDING') return <Navigate to="/onboarding" replace />;
  if (isAllowed === 'REDIRECT_TO_BUDGET') return <Navigate to="/budget" replace />;

  return children;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Публичные роуты */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        
        {/* Онбординг (без Layout, так как это стартовый экран) */}
        <Route path="/onboarding" element={
          <RequireAuth requireFamily={false}>
            <OnboardingPage />
          </RequireAuth>
        } />
        
        {/* Защищенные роуты с общим Layout (Навигацией) */}
        <Route element={<RequireAuth requireFamily={true}><Layout /></RequireAuth>}>
          <Route path="/budget" element={<BudgetPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/categories" element={<CategoriesPage />} />
          <Route path="/family" element={<FamilySettingsPage />} />
        </Route>
        
        {/* Редирект по умолчанию */}
        <Route path="*" element={<Navigate to="/budget" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;