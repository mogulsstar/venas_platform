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

  console.log('ProtectedRoute - Auth state:', { isAuthenticated, loading, hasUser: !!user });
  console.log('Current location:', location.pathname);

  // Show loading state
  if (loading) {
    console.log('Auth state is loading, showing loading indicator');
    return <div>Loading...</div>;
  }

  // Check if user is authenticated
  if (!isAuthenticated) {
    console.log('User is not authenticated, redirecting to login');
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check if user has required role
  if (requiredRole && user) {
    console.log('Checking user role:', {
      requiredRole,
      isAdmin: user.is_admin,
      isManager: user.is_manager,
      isAnalyst: user.is_analyst
    });

    if (
      (requiredRole === 'admin' && !user.is_admin) ||
      (requiredRole === 'manager' && !user.is_manager && !user.is_admin) ||
      (requiredRole === 'analyst' && !user.is_analyst && !user.is_manager && !user.is_admin)
    ) {
      console.log('User does not have required role, redirecting to home');
      return <Navigate to="/" replace />;
    }
  }

  return <>{children}</>;
};

export default ProtectedRoute;
