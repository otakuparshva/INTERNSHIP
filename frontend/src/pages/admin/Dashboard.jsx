import { useState } from 'react';
import { motion } from 'framer-motion';
import { Tab } from '@headlessui/react';
import {
  ChartBarIcon,
  UsersIcon,
  ExclamationTriangleIcon,
  CloudArrowUpIcon,
} from '@heroicons/react/24/outline';
import Analytics from '@/components/admin/Analytics';
import UserManagement from '@/components/admin/UserManagement';
import ErrorLogs from '@/components/admin/ErrorLogs';
import BackupSystem from '@/components/admin/BackupSystem';

function classNames(...classes) {
  return classes.filter(Boolean).join(' ');
}

export default function AdminDashboard() {
  const [selectedTab, setSelectedTab] = useState(0);

  const tabs = [
    {
      name: 'Analytics',
      icon: ChartBarIcon,
      component: Analytics,
    },
    {
      name: 'Users',
      icon: UsersIcon,
      component: UserManagement,
    },
    {
      name: 'Error Logs',
      icon: ExclamationTriangleIcon,
      component: ErrorLogs,
    },
    {
      name: 'Backup',
      icon: CloudArrowUpIcon,
      component: BackupSystem,
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow">
          <Tab.Group selectedIndex={selectedTab} onChange={setSelectedTab}>
            <Tab.List className="flex space-x-1 rounded-t-lg bg-gray-100 p-1">
              {tabs.map((tab) => (
                <Tab
                  key={tab.name}
                  className={({ selected }) =>
                    classNames(
                      'w-full rounded-md py-2.5 text-sm font-medium leading-5',
                      'ring-white ring-opacity-60 ring-offset-2 ring-offset-blue-400 focus:outline-none focus:ring-2',
                      selected
                        ? 'bg-white shadow text-blue-600'
                        : 'text-gray-600 hover:bg-white/[0.12] hover:text-blue-600'
                    )
                  }
                >
                  <div className="flex items-center justify-center space-x-2">
                    <tab.icon className="h-5 w-5" />
                    <span>{tab.name}</span>
                  </div>
                </Tab>
              ))}
            </Tab.List>
            <Tab.Panels className="mt-2">
              {tabs.map((tab, idx) => (
                <Tab.Panel
                  key={idx}
                  className={classNames(
                    'rounded-xl bg-white p-3',
                    'ring-white ring-opacity-60 ring-offset-2 ring-offset-blue-400 focus:outline-none focus:ring-2'
                  )}
                >
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <tab.component />
                  </motion.div>
                </Tab.Panel>
              ))}
            </Tab.Panels>
          </Tab.Group>
        </div>
      </div>
    </div>
  );
} 