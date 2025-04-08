import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  CloudArrowUpIcon, 
  ArrowPathIcon,
  DocumentArrowDownIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { format } from 'date-fns';

export default function BackupSystem() {
  const [isBackingUp, setIsBackingUp] = useState(false);
  const [isRestoring, setIsRestoring] = useState(false);
  const [backupHistory, setBackupHistory] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleBackup = async () => {
    try {
      setIsBackingUp(true);
      setError(null);
      setSuccess(null);

      const response = await fetch('/api/admin/backup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Backup failed');
      }

      const data = await response.json();
      setBackupHistory(prev => [data, ...prev]);
      setSuccess('Backup completed successfully');
    } catch (err) {
      setError('Failed to create backup: ' + err.message);
    } finally {
      setIsBackingUp(false);
    }
  };

  const handleRestore = async () => {
    if (!selectedFile) {
      setError('Please select a backup file to restore');
      return;
    }

    try {
      setIsRestoring(true);
      setError(null);
      setSuccess(null);

      const formData = new FormData();
      formData.append('backup', selectedFile);

      const response = await fetch('/api/admin/restore', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Restore failed');
      }

      setSuccess('System restored successfully');
      setSelectedFile(null);
    } catch (err) {
      setError('Failed to restore backup: ' + err.message);
    } finally {
      setIsRestoring(false);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && file.name.endsWith('.json')) {
      setSelectedFile(file);
      setError(null);
    } else {
      setError('Please select a valid backup file (.json)');
      setSelectedFile(null);
    }
  };

  const downloadBackup = async (backupId) => {
    try {
      const response = await fetch(`/api/admin/backup/${backupId}/download`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `backup-${format(new Date(), 'yyyy-MM-dd')}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError('Failed to download backup: ' + err.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">System Backup</h2>
        
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={handleBackup}
              disabled={isBackingUp}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
            >
              {isBackingUp ? (
                <ArrowPathIcon className="h-5 w-5 animate-spin" />
              ) : (
                <CloudArrowUpIcon className="h-5 w-5" />
              )}
              <span>{isBackingUp ? 'Backing up...' : 'Create Backup'}</span>
            </button>
          </div>

          <div className="border-t border-gray-200 pt-4">
            <h3 className="text-md font-medium text-gray-900 mb-2">Restore from Backup</h3>
            <div className="flex items-center space-x-4">
              <input
                type="file"
                accept=".json"
                onChange={handleFileSelect}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-lg file:border-0
                  file:text-sm file:font-semibold
                  file:bg-blue-50 file:text-blue-700
                  hover:file:bg-blue-100"
              />
              <button
                onClick={handleRestore}
                disabled={!selectedFile || isRestoring}
                className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50"
              >
                {isRestoring ? (
                  <ArrowPathIcon className="h-5 w-5 animate-spin" />
                ) : (
                  <ArrowPathIcon className="h-5 w-5" />
                )}
                <span>{isRestoring ? 'Restoring...' : 'Restore'}</span>
              </button>
            </div>
          </div>
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-4 bg-red-50 rounded-lg flex items-start space-x-3"
          >
            <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
            <p className="text-sm text-red-700">{error}</p>
          </motion.div>
        )}

        {success && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-4 bg-green-50 rounded-lg flex items-start space-x-3"
          >
            <DocumentArrowDownIcon className="h-5 w-5 text-green-400" />
            <p className="text-sm text-green-700">{success}</p>
          </motion.div>
        )}
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Backup History</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Size</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {backupHistory.map((backup, index) => (
                <motion.tr
                  key={backup.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {format(new Date(backup.timestamp), 'yyyy-MM-dd HH:mm:ss')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {(backup.size / 1024 / 1024).toFixed(2)} MB
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                      Completed
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <button
                      onClick={() => downloadBackup(backup.id)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      Download
                    </button>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
} 