import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '@/store/auth';

const ProtectedRoute = ({ role }) => {
  const { isAuthenticated, user } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (role && user?.role !== role) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
};

export default ProtectedRoute; 