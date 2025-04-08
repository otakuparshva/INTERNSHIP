import React, { useState, useEffect } from 'react';
import { useMutation } from 'react-query';
import { analyzeResume } from '../../services/api';
import { ChartBarIcon } from '@heroicons/react/24/outline';

export default function ResumeAnalysis({ resumeText }) {
  const [error, setError] = useState('');
  const [analysis, setAnalysis] = useState(null);

  const { mutate: analyze, isLoading } = useMutation(analyzeResume, {
    onSuccess: (data) => {
      setAnalysis(data);
      setError('');
    },
    onError: (err) => {
      console.error('Analysis error:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to analyze resume');
    },
  });

  useEffect(() => {
    if (resumeText) {
      analyze(resumeText);
    }
  }, [resumeText, analyze]);

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Resume Analysis</h2>

      {error && (
        <div className="text-red-600 text-sm mb-4">
          Error: {error}
        </div>
      )}

      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <svg className="animate-spin h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="ml-2 text-gray-600">Analyzing...</span>
        </div>
      )}

      {analysis && !isLoading && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <ChartBarIcon className="h-5 w-5 text-blue-600 mr-2" />
              <span className="text-lg font-medium text-gray-900">{analysis.score}%</span>
            </div>
            <div className="text-sm text-gray-500">
              Model: {analysis.model_used}
            </div>
          </div>

          {analysis.summary && (
            <div className="bg-blue-50 p-4 rounded-md">
              <h3 className="text-md font-medium text-blue-800 mb-2">Summary</h3>
              <p className="text-blue-700">{analysis.summary}</p>
            </div>
          )}

          <div className="prose max-w-none">
            <h3 className="text-md font-medium text-gray-800 mb-2">Detailed Analysis</h3>
            <div className="whitespace-pre-wrap text-gray-700">
              {analysis.raw_analysis}
            </div>
          </div>
        </div>
      )}

      {!resumeText && (
        <div className="text-gray-500 text-center py-8">
          Upload a resume to begin analysis
        </div>
      )}
    </div>
  );
} 