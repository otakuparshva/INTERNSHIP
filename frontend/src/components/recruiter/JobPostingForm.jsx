import { useState } from 'react';
import { useMutation } from 'react-query';
import { toast } from 'react-hot-toast';
import { SparklesIcon } from '@heroicons/react/24/outline';
import { generateJobDescription, createJob } from '@/services/api';

export default function JobPostingForm() {
  const [formData, setFormData] = useState({
    role: '',
    requirements: [''],
    description: '',
  });
  const [isGenerating, setIsGenerating] = useState(false);

  const generateDescriptionMutation = useMutation(generateJobDescription, {
    onSuccess: (data) => {
      setFormData(prev => ({ ...prev, description: data.job_description }));
      setIsGenerating(false);
      toast.success('Job description generated successfully!');
    },
    onError: (error) => {
      setIsGenerating(false);
      toast.error('Failed to generate job description. Please try again.');
    },
  });

  const createJobMutation = useMutation(createJob, {
    onSuccess: () => {
      toast.success('Job posted successfully!');
      setFormData({ role: '', requirements: [''], description: '' });
    },
    onError: (error) => {
      toast.error('Failed to post job. Please try again.');
    },
  });

  const handleRequirementChange = (index, value) => {
    const newRequirements = [...formData.requirements];
    newRequirements[index] = value;
    setFormData(prev => ({ ...prev, requirements: newRequirements }));
  };

  const addRequirement = () => {
    setFormData(prev => ({
      ...prev,
      requirements: [...prev.requirements, ''],
    }));
  };

  const removeRequirement = (index) => {
    setFormData(prev => ({
      ...prev,
      requirements: prev.requirements.filter((_, i) => i !== index),
    }));
  };

  const handleGenerateDescription = async () => {
    if (!formData.role || formData.requirements.every(req => !req)) {
      toast.error('Please fill in the role and at least one requirement');
      return;
    }

    setIsGenerating(true);
    generateDescriptionMutation.mutate({
      role: formData.role,
      requirements: formData.requirements.filter(req => req),
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.description) {
      toast.error('Please generate or enter a job description');
      return;
    }

    createJobMutation.mutate(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="role" className="block text-sm font-medium text-gray-700">
          Job Role
        </label>
        <input
          type="text"
          id="role"
          value={formData.role}
          onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value }))}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          placeholder="e.g., Senior Frontend Developer"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Requirements
        </label>
        <div className="space-y-2">
          {formData.requirements.map((requirement, index) => (
            <div key={index} className="flex space-x-2">
              <input
                type="text"
                value={requirement}
                onChange={(e) => handleRequirementChange(index, e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                placeholder="e.g., 5+ years of React experience"
              />
              {formData.requirements.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeRequirement(index)}
                  className="mt-1 inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  Remove
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={addRequirement}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Add Requirement
          </button>
        </div>
      </div>

      <div>
        <div className="flex justify-between items-center">
          <label htmlFor="description" className="block text-sm font-medium text-gray-700">
            Job Description
          </label>
          <button
            type="button"
            onClick={handleGenerateDescription}
            disabled={isGenerating}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            {isGenerating ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Generating...
              </>
            ) : (
              <>
                <SparklesIcon className="h-4 w-4 mr-2" />
                Generate with AI
              </>
            )}
          </button>
        </div>
        <textarea
          id="description"
          value={formData.description}
          onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
          rows={6}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          placeholder="Job description will be generated here..."
          required
        />
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={createJobMutation.isLoading}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          {createJobMutation.isLoading ? 'Posting...' : 'Post Job'}
        </button>
      </div>
    </form>
  );
} 