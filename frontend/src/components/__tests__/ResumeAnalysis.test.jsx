import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import ResumeAnalysis from '../recruiter/ResumeAnalysis';
import { analyzeResume } from '../../services/api';

// Mock the API functions
jest.mock('../../services/api', () => ({
  analyzeResume: jest.fn(),
}));

const mockAnalysisResult = {
  raw_analysis: `Key skills:
- React.js
- Node.js
- Python
Experience level: Senior
Education: Bachelor's in Computer Science
Potential job matches: Frontend Developer, Full Stack Developer
Areas for improvement: Cloud technologies`,
  model_used: 'ollama',
  score: 85.5,
};

describe('ResumeAnalysis Component', () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  const renderResumeAnalysis = (props = {}) => {
    render(
      <QueryClientProvider client={queryClient}>
        <ResumeAnalysis resumeText="Sample resume text" {...props} />
      </QueryClientProvider>
    );
  };

  it('renders resume analysis form', () => {
    renderResumeAnalysis();
    expect(screen.getByText(/Resume Analysis/i)).toBeInTheDocument();
  });

  it('handles successful resume analysis', async () => {
    analyzeResume.mockResolvedValueOnce(mockAnalysisResult);
    
    renderResumeAnalysis();

    await waitFor(() => {
      expect(analyzeResume).toHaveBeenCalledWith('Sample resume text');
      expect(screen.getByText(/85.5%/)).toBeInTheDocument();
      expect(screen.getByText(/Key skills:/i)).toBeInTheDocument();
      expect(screen.getByText(/React\.js/i)).toBeInTheDocument();
      expect(screen.getByText(/Experience level: Senior/i)).toBeInTheDocument();
    });
  });

  it('displays loading state during analysis', async () => {
    analyzeResume.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    renderResumeAnalysis();

    await waitFor(() => {
      expect(screen.getByText('Analyzing...')).toBeInTheDocument();
    });
  });

  it('handles analysis error', async () => {
    const errorMessage = 'Failed to analyze resume';
    analyzeResume.mockRejectedValueOnce(new Error(errorMessage));
    
    renderResumeAnalysis();

    await waitFor(() => {
      const errorElement = screen.getByText((content, element) => {
        return element.textContent === `Error: ${errorMessage}`;
      });
      expect(errorElement).toBeInTheDocument();
    });
  });

  it('updates analysis when new resume text is provided', async () => {
    analyzeResume.mockResolvedValueOnce(mockAnalysisResult);
    
    const { rerender } = render(
      <QueryClientProvider client={queryClient}>
        <ResumeAnalysis resumeText="Initial resume text" />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(analyzeResume).toHaveBeenCalledWith('Initial resume text');
    });

    // Update props with new resume text
    rerender(
      <QueryClientProvider client={queryClient}>
        <ResumeAnalysis resumeText="Updated resume text" />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(analyzeResume).toHaveBeenCalledWith('Updated resume text');
    });
  });

  it('displays model information', async () => {
    analyzeResume.mockResolvedValueOnce(mockAnalysisResult);
    
    renderResumeAnalysis();

    await waitFor(() => {
      expect(screen.getByText(/Model: ollama/i)).toBeInTheDocument();
    });
  });
}); 