import React from 'react';
import { motion } from 'framer-motion';
import useAuthStore from '../../store/auth';

const RecruiterDashboard = () => {
  const { user } = useAuthStore();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="container mx-auto px-4 py-8"
    >
      <h1 className="text-3xl font-bold mb-8">Welcome, {user?.full_name || 'Recruiter'}</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Job Postings Overview */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Job Postings Overview</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span>Active Jobs</span>
              <span className="font-bold">0</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Total Applications</span>
              <span className="font-bold">0</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Interviews Scheduled</span>
              <span className="font-bold">0</span>
            </div>
          </div>
        </div>

        {/* Recent Applications */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Applications</h2>
          <p className="text-gray-500">No recent applications</p>
        </div>

        {/* Interview Schedule */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Interview Schedule</h2>
          <p className="text-gray-500">No upcoming interviews</p>
        </div>
      </div>
    </motion.div>
  );
};

export default RecruiterDashboard; 