import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { toast } from 'react-hot-toast';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { getJobs, createApplication } from '@/services/api';

export default function JobSearch() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedJob, setSelectedJob] = useState(null);
  const queryClient = useQueryClient();

  const { data: jobs, isLoading } = useQuery('jobs', getJobs);

  const applyMutation = useMutation(createApplication, {
    onSuccess: () => {
      queryClient.invalidateQueries('applications');
      toast.success('Application submitted successfully!');
      setSelectedJob(null);
    },
    onError: (error) => {
      toast.error('Failed to submit application. Please try again.');
    },
  });

  const filteredJobs = jobs?.filter(job =>
    job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    job.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleApply = (job) => {
    applyMutation.mutate({
      jobId: job._id,
      resumeId: localStorage.getItem('resumeId'), // Assuming resume is already uploaded
    });
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Search Bar */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          placeholder="Search jobs..."
        />
      </div>

      {/* Job Listings */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredJobs?.map((job) => (
          <div
            key={job._id}
            className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow duration-200"
          >
            <div className="p-4">
              <h3 className="text-lg font-medium text-gray-900">{job.title}</h3>
              <p className="mt-1 text-sm text-gray-500">{job.company}</p>
              <div className="mt-2">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {job.type}
                </span>
                <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  {job.location}
                </span>
              </div>
              <p className="mt-2 text-sm text-gray-600 line-clamp-3">
                {job.description}
              </p>
              <div className="mt-4 flex justify-end">
                <button
                  onClick={() => setSelectedJob(job)}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  View Details
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Job Details Modal */}
      {selectedJob && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">{selectedJob.title}</h2>
                  <p className="mt-1 text-sm text-gray-500">{selectedJob.company}</p>
                </div>
                <button
                  onClick={() => setSelectedJob(null)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  <span className="sr-only">Close</span>
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="mt-4 space-y-4">
                <div>
                  <h3 className="text-lg font-medium text-gray-900">Job Description</h3>
                  <p className="mt-2 text-gray-600 whitespace-pre-wrap">{selectedJob.description}</p>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-gray-900">Requirements</h3>
                  <ul className="mt-2 list-disc list-inside text-gray-600">
                    {selectedJob.requirements.map((req, index) => (
                      <li key={index}>{req}</li>
                    ))}
                  </ul>
                </div>

                <div className="flex justify-end space-x-4">
                  <button
                    onClick={() => setSelectedJob(null)}
                    className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => handleApply(selectedJob)}
                    disabled={applyMutation.isLoading}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    {applyMutation.isLoading ? 'Applying...' : 'Apply Now'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 