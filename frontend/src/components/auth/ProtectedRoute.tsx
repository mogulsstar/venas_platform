import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'admin' | 'manager' | 'analyst';
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredRole 
}) => {
  const { isAuthenticated, user, loading } = useSelector((state: RootState) => state.auth);
  const location = useLocation();

  // Show loading state
  if (loading) {
    return <div>Loading...</div>;
  }

  // Check if user is authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check if user has required role
  if (requiredRole && user) {
    if (
      (requiredRole === 'admin' && !user.is_admin) ||
      (requiredRole === 'manager' && !user.is_manager && !user.is_admin) ||
      (requiredRole === 'analyst' && !user.is_analyst && !user.is_manager && !user.is_admin)
    ) {
      return <Navigate to="/" replace />;
    }
  }

  return <>{children}</>;
};

export default ProtectedRoute;
