import { useQuery } from 'react-query';
import { motion } from 'framer-motion';
import {
  ChartBarIcon,
  UserGroupIcon,
  BriefcaseIcon,
  DocumentCheckIcon,
} from '@heroicons/react/24/outline';
import { getAnalytics } from '@/services/api';

const stats = [
  {
    name: 'Total Applications',
    icon: DocumentCheckIcon,
    color: 'bg-blue-500',
  },
  {
    name: 'Active Jobs',
    icon: BriefcaseIcon,
    color: 'bg-green-500',
  },
  {
    name: 'Total Candidates',
    icon: UserGroupIcon,
    color: 'bg-purple-500',
  },
  {
    name: 'Interview Success Rate',
    icon: ChartBarIcon,
    color: 'bg-yellow-500',
  },
];

export default function Analytics() {
  const { data: analytics, isLoading } = useQuery('analytics', getAnalytics);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className="bg-white overflow-hidden shadow rounded-lg"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className={`flex-shrink-0 rounded-md p-3 ${stat.color}`}>
                  <stat.icon className="h-6 w-6 text-white" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {stat.name}
                    </dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-gray-900">
                        {analytics?.[stat.name.toLowerCase().replace(/\s+/g, '_')] || 0}
                      </div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        {/* Applications Over Time */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Applications Over Time
          </h3>
          <div className="h-64">
            {/* Add your chart component here */}
            <div className="flex items-center justify-center h-full text-gray-500">
              Chart placeholder - Applications over time
            </div>
          </div>
        </div>

        {/* Job Categories Distribution */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Job Categories Distribution
          </h3>
          <div className="h-64">
            {/* Add your chart component here */}
            <div className="flex items-center justify-center h-full text-gray-500">
              Chart placeholder - Job categories distribution
            </div>
          </div>
        </div>

        {/* Interview Success Rate by Department */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Interview Success Rate by Department
          </h3>
          <div className="h-64">
            {/* Add your chart component here */}
            <div className="flex items-center justify-center h-full text-gray-500">
              Chart placeholder - Interview success rate by department
            </div>
          </div>
        </div>

        {/* Candidate Sources */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Candidate Sources
          </h3>
          <div className="h-64">
            {/* Add your chart component here */}
            <div className="flex items-center justify-center h-full text-gray-500">
              Chart placeholder - Candidate sources
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Recent Activity
        </h3>
        <div className="flow-root">
          <ul className="-mb-8">
            {analytics?.recent_activity?.map((activity, index) => (
              <li key={index}>
                <div className="relative pb-8">
                  {index !== analytics.recent_activity.length - 1 && (
                    <span
                      className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                      aria-hidden="true"
                    />
                  )}
                  <div className="relative flex space-x-3">
                    <div>
                      <span className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white ${
                        activity.type === 'application'
                          ? 'bg-blue-500'
                          : activity.type === 'interview'
                          ? 'bg-green-500'
                          : 'bg-yellow-500'
                      }`}>
                        {/* Add appropriate icon based on activity type */}
                      </span>
                    </div>
                    <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                      <div>
                        <p className="text-sm text-gray-500">
                          {activity.description}
                        </p>
                      </div>
                      <div className="text-right text-sm whitespace-nowrap text-gray-500">
                        <time dateTime={activity.timestamp}>
                          {new Date(activity.timestamp).toLocaleDateString()}
                        </time>
                      </div>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
} 