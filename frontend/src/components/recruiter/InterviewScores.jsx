import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { toast } from 'react-hot-toast';
import {
  ChartBarIcon,
  CheckCircleIcon,
  XCircleIcon,
  ChevronDownIcon,
  ChevronUpIcon,
} from '@heroicons/react/24/outline';
import { getInterviewScores, updateInterviewStatus, sendEmail } from '@/services/api';

export default function InterviewScores() {
  const [expandedInterview, setExpandedInterview] = useState(null);
  const queryClient = useQueryClient();

  const { data: interviews, isLoading } = useQuery('interviewScores', getInterviewScores);

  const updateStatusMutation = useMutation(
    ({ interviewId, status }) => updateInterviewStatus(interviewId, status),
    {
      onSuccess: (data, variables) => {
        queryClient.invalidateQueries('interviewScores');
        toast.success(`Interview ${variables.status} successfully`);
        
        // Send email based on final decision
        sendEmail({
          to: data.candidateEmail,
          subject: `Interview Result - ${variables.status.toUpperCase()}`,
          template: variables.status === 'hired' ? 'offer_letter' : 'rejection',
          data: {
            candidateName: data.candidateName,
            jobTitle: data.jobTitle,
            companyName: 'Your Company Name',
          },
        });
      },
      onError: (error) => {
        toast.error('Failed to update interview status');
      },
    }
  );

  const handleStatusUpdate = (interviewId, status) => {
    updateStatusMutation.mutate({ interviewId, status });
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
      {interviews?.map((interview) => (
        <div
          key={interview._id}
          className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"
        >
          <div
            className="p-4 cursor-pointer hover:bg-gray-50"
            onClick={() => setExpandedInterview(
              expandedInterview === interview._id ? null : interview._id
            )}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex-shrink-0">
                  <ChartBarIcon className="h-8 w-8 text-gray-400" />
                </div>
                <div>
                  <h3 className="text-lg font-medium text-gray-900">
                    {interview.candidateName}
                  </h3>
                  <p className="text-sm text-gray-500">
                    Position: {interview.jobTitle}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  interview.status === 'completed'
                    ? 'bg-blue-100 text-blue-800'
                    : interview.status === 'hired'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {interview.status.charAt(0).toUpperCase() + interview.status.slice(1)}
                </span>
                {expandedInterview === interview._id ? (
                  <ChevronUpIcon className="h-5 w-5 text-gray-400" />
                ) : (
                  <ChevronDownIcon className="h-5 w-5 text-gray-400" />
                )}
              </div>
            </div>
          </div>

          {expandedInterview === interview._id && (
            <div className="border-t border-gray-200 p-4 space-y-4">
              <div>
                <h4 className="text-sm font-medium text-gray-700">Interview Score</h4>
                <div className="mt-1">
                  <div className="relative pt-1">
                    <div className="flex mb-2 items-center justify-between">
                      <div>
                        <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-blue-600 bg-blue-200">
                          {interview.score}%
                        </span>
                      </div>
                    </div>
                    <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-blue-200">
                      <div
                        style={{ width: `${interview.score}%` }}
                        className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-500"
                      ></div>
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-700">Question Analysis</h4>
                <div className="mt-2 space-y-2">
                  {interview.questions.map((question, index) => (
                    <div key={index} className="bg-gray-50 p-3 rounded-md">
                      <p className="text-sm font-medium text-gray-900">
                        Q{index + 1}: {question.text}
                      </p>
                      <p className="mt-1 text-sm text-gray-600">
                        Answer: {question.answer}
                      </p>
                      <p className="mt-1 text-sm text-gray-500">
                        Score: {question.score}/10
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {interview.status === 'completed' && (
                <div className="flex space-x-4">
                  <button
                    onClick={() => handleStatusUpdate(interview._id, 'hired')}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                  >
                    <CheckCircleIcon className="h-5 w-5 mr-2" />
                    Hire Candidate
                  </button>
                  <button
                    onClick={() => handleStatusUpdate(interview._id, 'rejected')}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                  >
                    <XCircleIcon className="h-5 w-5 mr-2" />
                    Reject Candidate
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