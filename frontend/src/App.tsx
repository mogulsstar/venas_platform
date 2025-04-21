import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

import { AppDispatch, RootState } from './store';
import { checkAuth } from './features/auth/authSlice';
import Layout from './components/layout/Layout';
import ProtectedRoute from './components/auth/ProtectedRoute';
import LoginPage from './pages/auth/LoginPage';
import DashboardPage from './pages/dashboard/DashboardPage';
import RegulationsPage from './pages/regulations/RegulationsPage';
import RegulationDetailPage from './pages/regulations/RegulationDetailPage';
import TestCasesPage from './pages/testcases/TestCasesPage';
import TestCaseDetailPage from './pages/testcases/TestCaseDetailPage';
import ProjectsPage from './pages/projects/ProjectsPage';
import ProjectDetailPage from './pages/projects/ProjectDetailPage';
import AnalysisPage from './pages/analysis/AnalysisPage';
import AnalysisDetailPage from './pages/analysis/AnalysisDetailPage';
import MonitorPage from './pages/monitor/MonitorPage';
import HelpCenterPage from './pages/help/HelpCenterPage';
import HelpArticlePage from './pages/help/HelpArticlePage';
import ProfilePage from './pages/user/ProfilePage';
import NotFoundPage from './pages/NotFoundPage';

const App: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { isAuthenticated, loading } = useSelector((state: RootState) => state.auth);

  useEffect(() => {
    // 检查本地存储中是否有令牌
    const token = localStorage.getItem('token');
    console.log('App initialization - token in localStorage:', token ? 'exists' : 'not found');

    if (token) {
      console.log('Checking authentication status...');
      dispatch(checkAuth())
        .unwrap()
        .then(user => {
          console.log('Authentication successful, user:', user);
        })
        .catch(error => {
          console.error('Authentication check failed:', error);
        });
    } else {
      console.log('No token found, skipping authentication check');
    }
  }, [dispatch]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Routes>
        <Route path="/login" element={!isAuthenticated ? <LoginPage /> : <Navigate to="/" />} />

        <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route index element={<DashboardPage />} />
          <Route path="regulations" element={<RegulationsPage />} />
          <Route path="regulations/:id" element={<RegulationDetailPage />} />
          <Route path="testcases" element={<TestCasesPage />} />
          <Route path="testcases/:id" element={<TestCaseDetailPage />} />
          <Route path="projects" element={<ProjectsPage />} />
          <Route path="projects/:id" element={<ProjectDetailPage />} />
          <Route path="analysis" element={<AnalysisPage />} />
          <Route path="analysis/:id" element={<AnalysisDetailPage />} />
          <Route path="monitor" element={<MonitorPage />} />
          <Route path="help" element={<HelpCenterPage />} />
          <Route path="help/articles/:slug" element={<HelpArticlePage />} />
          <Route path="profile" element={<ProfilePage />} />
        </Route>

        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </LocalizationProvider>
  );
};

export default App;
