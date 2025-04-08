import api from '@/api/axios';

// Auth APIs
export const login = (credentials) => api.post('/auth/token', credentials);
export const register = (userData) => api.post('/auth/register', userData);
export const resetPassword = (email) => api.post('/auth/reset-password', { email });
export const updatePassword = (passwordData) => api.put('/auth/update-password', passwordData);

// Job APIs
export const createJob = (jobData) => api.post('/jobs', jobData);
export const getJobs = () => api.get('/jobs');
export const getJobById = (id) => api.get(`/jobs/${id}`);
export const updateJob = (id, jobData) => api.put(`/jobs/${id}`, jobData);
export const deleteJob = (id) => api.delete(`/jobs/${id}`);

// Application APIs - Candidate
export const getMyApplications = () => api.get('/candidates/applications');
export const applyForJob = (jobId, applicationData) => api.post(`/candidates/apply/${jobId}`, applicationData);
export const uploadResume = (formData) => api.post('/candidates/upload-resume', formData);

// Application APIs - Recruiter
export const getRecruiterApplications = () => api.get('/recruiter/applications');
export const reviewApplication = (applicationId, reviewData) => 
  api.post(`/recruiter/applications/${applicationId}/review`, reviewData);
export const scheduleInterview = (applicationId, scheduleData) => 
  api.post(`/recruiter/applications/${applicationId}/schedule-interview`, scheduleData);
export const getRecruiterInterviews = () => api.get('/recruiter/interviews');

// AI APIs
export const generateJobDescription = (data) => api.post('/ai/generate-job-description', data);
export const analyzeResume = (resumeText) => {
  // Create a FormData object with the resume text
  const formData = new FormData();
  const blob = new Blob([resumeText], { type: 'text/plain' });
  formData.append('resume', blob, 'resume.txt');
  return api.post('/ai/analyze-resume', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};
export const generateInterviewQuestions = (jobId, numQuestions) => 
  api.post('/ai/generate-interview-questions', { job_id: jobId, num_questions: numQuestions });

// Admin APIs
export const getUsers = () => api.get('/admin/users');
export const getAnalytics = () => api.get('/admin/stats');
export const getErrorLogs = () => api.get('/admin/logs/errors');
export const getAILogs = () => api.get('/admin/logs/ai');
export const triggerBackup = () => api.post('/admin/backup');
export const triggerMaintenance = () => api.post('/admin/maintenance');

export default api; 