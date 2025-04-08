import React, { useState } from 'react';
import { useMutation } from 'react-query';
import { generateJobDescription } from '../../services/api';
import { SparklesIcon } from '@heroicons/react/24/outline';

export default function JobDescriptionGenerator({ onGenerate }) {
  const [title, setTitle] = useState('');
  const [error, setError] = useState('');

  const { mutate: generate, isLoading } = useMutation(generateJobDescription, {
    onSuccess: (data) => {
      if (onGenerate) {
        onGenerate(data);
      }
      setError('');
    },
    onError: (err) => {
      setError(err.message || 'Failed to generate job description');
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title) {
      setError('Job title is required');
      return;
    }
    generate({ title });
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Job Description Generator</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700">
            Job Title
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            placeholder="e.g. Senior Frontend Developer"
          />
        </div>

        {error && (
          <div className="text-red-600 text-sm">
            Error: {error}
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          {isLoading ? (
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
      </form>
    </div>
  );
} 