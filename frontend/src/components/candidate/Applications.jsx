import { useState } from 'react';
import { useQuery } from 'react-query';
import { motion } from 'framer-motion';
import {
  DocumentTextIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';
import { getApplications } from '@/services/api';

const statusIcons = {
  pending: ClockIcon,
  accepted: CheckCircleIcon,
  rejected: XCircleIcon,
};

const statusColors = {
  pending: 'text-yellow-600 bg-yellow-100',
  accepted: 'text-green-600 bg-green-100',
  rejected: 'text-red-600 bg-red-100',
};

export default function Applications() {
  const [selectedApplication, setSelectedApplication] = useState(null);
  const { data: applications, isLoading } = useQuery('applications', getApplications);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!applications?.length) {
    return (
      <div className="text-center py-12">
        <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">No applications</h3>
        <p className="mt-1 text-sm text-gray-500">
          Get started by applying to a job.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {applications.map((application) => {
        const StatusIcon = statusIcons[application.status];
        return (
          <motion.div
            key={application._id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"
          >
            <div className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <DocumentTextIcon className="h-8 w-8 text-gray-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">
                      {application.jobTitle}
                    </h3>
                    <p className="text-sm text-gray-500">
                      Applied on {new Date(application.appliedAt).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      statusColors[application.status]
                    }`}
                  >
                    <StatusIcon className="h-4 w-4 mr-1" />
                    {application.status.charAt(0).toUpperCase() + application.status.slice(1)}
                  </span>
                </div>
              </div>

              {application.status === 'accepted' && (
                <div className="mt-4 bg-green-50 p-4 rounded-md">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <CheckCircleIcon className="h-5 w-5 text-green-400" />
                    </div>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-green-800">
                        Interview Invitation
                      </h3>
                      <div className="mt-2 text-sm text-green-700">
                        <p>
                          Congratulations! You've been invited for an interview.
                          Please check your email for details.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {application.status === 'rejected' && (
                <div className="mt-4 bg-red-50 p-4 rounded-md">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <XCircleIcon className="h-5 w-5 text-red-400" />
                    </div>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-red-800">
                        Application Status
                      </h3>
                      <div className="mt-2 text-sm text-red-700">
                        <p>
                          Thank you for your interest. Unfortunately, we have decided
                          to move forward with other candidates.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {application.status === 'pending' && (
                <div className="mt-4 bg-yellow-50 p-4 rounded-md">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <ClockIcon className="h-5 w-5 text-yellow-400" />
                    </div>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-yellow-800">
                        Application Under Review
                      </h3>
                      <div className="mt-2 text-sm text-yellow-700">
                        <p>
                          Your application is being reviewed by our team.
                          We'll get back to you soon.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {application.resumeScore && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium text-gray-700">Resume Match Score</h4>
                  <div className="mt-1">
                    <div className="relative pt-1">
                      <div className="flex mb-2 items-center justify-between">
                        <div>
                          <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-blue-600 bg-blue-200">
                            {application.resumeScore}% Match
                          </span>
                        </div>
                      </div>
                      <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-blue-200">
                        <div
                          style={{ width: `${application.resumeScore}%` }}
                          className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-500"
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
} 