import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';

// Pages
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import JobListings from './pages/JobListings';
import JobPosting from './pages/JobPosting';
import Contact from './pages/Contact';
import About from './pages/About';

// Role-specific pages
import CandidateDashboard from './pages/candidate/Dashboard';
import RecruiterDashboard from './pages/recruiter/Dashboard';
import AdminDashboard from './pages/admin/Dashboard';
import InterviewBot from './pages/InterviewBot';
import ResumeViewer from './pages/ResumeViewer';
import NotFound from './pages/NotFound';

// Create a client
const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Toaster position="top-right" />
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Layout />}>
            <Route index element={<Home />} />
            <Route path="login" element={<Login />} />
            <Route path="register" element={<Register />} />
            <Route path="jobs" element={<JobListings />} />
            
            {/* Protected Routes */}
            <Route path="candidate" element={<ProtectedRoute role="candidate" />}>
              <Route index element={<CandidateDashboard />} />
              <Route path="resume" element={<ResumeViewer />} />
              <Route path="interview/:jobId" element={<InterviewBot />} />
            </Route>

            <Route path="recruiter" element={<ProtectedRoute role="recruiter" />}>
              <Route index element={<RecruiterDashboard />} />
              <Route path="post-job" element={<JobPosting />} />
              <Route path="applications" element={<RecruiterDashboard />} />
              <Route path="interviews" element={<RecruiterDashboard />} />
            </Route>

            <Route path="admin" element={<ProtectedRoute role="admin" />}>
              <Route index element={<AdminDashboard />} />
              <Route path="users" element={<AdminDashboard />} />
              <Route path="jobs" element={<AdminDashboard />} />
              <Route path="logs" element={<AdminDashboard />} />
            </Route>

            {/* 404 Route */}
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}

export default App; 