import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { toast } from 'react-hot-toast';
import { 
  CheckCircleIcon, 
  XCircleIcon, 
  DocumentTextIcon,
  ChevronDownIcon,
  ChevronUpIcon
} from '@heroicons/react/24/outline';
import { getApplications, updateApplicationStatus, sendEmail } from '@/services/api';

export default function ApplicationsList() {
  const [expandedApplication, setExpandedApplication] = useState(null);
  const queryClient = useQueryClient();

  const { data: applications, isLoading } = useQuery('applications', getApplications);

  const updateStatusMutation = useMutation(
    ({ applicationId, status }) => updateApplicationStatus(applicationId, status),
    {
      onSuccess: (data, variables) => {
        queryClient.invalidateQueries('applications');
        toast.success(`Application ${variables.status} successfully`);
        
        // Send email based on status
        sendEmail({
          to: data.candidateEmail,
          subject: `Application ${variables.status}`,
          template: variables.status === 'accepted' ? 'interview_invite' : 'rejection',
          data: {
            candidateName: data.candidateName,
            jobTitle: data.jobTitle,
            companyName: 'Your Company Name',
          },
        });
      },
      onError: (error) => {
        toast.error('Failed to update application status');
      },
    }
  );

  const handleStatusUpdate = (applicationId, status) => {
    updateStatusMutation.mutate({ applicationId, status });
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {applications?.map((application) => (
        <div
          key={application._id}
          className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"
        >
          <div
            className="p-4 cursor-pointer hover:bg-gray-50"
            onClick={() => setExpandedApplication(
              expandedApplication === application._id ? null : application._id
            )}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex-shrink-0">
                  <DocumentTextIcon className="h-8 w-8 text-gray-400" />
                </div>
                <div>
                  <h3 className="text-lg font-medium text-gray-900">
                    {application.candidateName}
                  </h3>
                  <p className="text-sm text-gray-500">
                    Applied for: {application.jobTitle}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  application.status === 'pending'
                    ? 'bg-yellow-100 text-yellow-800'
                    : application.status === 'accepted'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {application.status.charAt(0).toUpperCase() + application.status.slice(1)}
                </span>
                {expandedApplication === application._id ? (
                  <ChevronUpIcon className="h-5 w-5 text-gray-400" />
                ) : (
                  <ChevronDownIcon className="h-5 w-5 text-gray-400" />
                )}
              </div>
            </div>
          </div>

          {expandedApplication === application._id && (
            <div className="border-t border-gray-200 p-4 space-y-4">
              <div>
                <h4 className="text-sm font-medium text-gray-700">Resume Score</h4>
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

              <div>
                <h4 className="text-sm font-medium text-gray-700">Resume Summary</h4>
                <p className="mt-1 text-sm text-gray-600">
                  {application.resumeSummary}
                </p>
              </div>

              {application.status === 'pending' && (
                <div className="flex space-x-4">
                  <button
                    onClick={() => handleStatusUpdate(application._id, 'accepted')}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                  >
                    <CheckCircleIcon className="h-5 w-5 mr-2" />
                    Accept
                  </button>
                  <button
                    onClick={() => handleStatusUpdate(application._id, 'rejected')}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                  >
                    <XCircleIcon className="h-5 w-5 mr-2" />
                    Reject
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
} 