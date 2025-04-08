import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/store/auth';
import { motion } from 'framer-motion';

const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const { isAuthenticated, user, checkAuth } = useAuthStore();
  const location = useLocation();

  // Check if token is valid
  const isValidToken = checkAuth();

  // If not authenticated or token is invalid, redirect to login
  if (!isAuthenticated || !isValidToken) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // If user role is not allowed, redirect to appropriate dashboard
  if (allowedRoles.length > 0 && !allowedRoles.includes(user?.role)) {
    const redirectPath = (() => {
      switch (user?.role) {
        case 'admin':
          return '/admin';
        case 'recruiter':
          return '/recruiter';
        case 'candidate':
          return '/candidate';
        default:
          return '/login';
      }
    })();

    return <Navigate to={redirectPath} replace />;
  }

  // Wrap children in motion.div for page transitions
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      {children}
    </motion.div>
  );
};

export default ProtectedRoute; 