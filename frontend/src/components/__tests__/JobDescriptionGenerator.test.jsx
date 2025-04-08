import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import JobDescriptionGenerator from '../recruiter/JobDescriptionGenerator';
import { generateJobDescription } from '../../services/api';

// Mock the API functions
jest.mock('../../services/api', () => ({
  generateJobDescription: jest.fn(),
}));

const mockGeneratedDescription = {
  description: `We are seeking a talented Senior Frontend Developer to join our team.

Key responsibilities:
- Develop and maintain modern web applications using React.js
- Lead frontend architecture decisions
- Mentor junior developers
- Collaborate with backend team

Required qualifications:
- 5+ years of experience with React.js
- Strong TypeScript skills
- Experience with modern frontend tools
- Excellent problem-solving abilities`,
  requirements: [
    'React.js expertise',
    'TypeScript proficiency',
    'Frontend architecture experience',
    'Team leadership skills',
  ],
};

describe('JobDescriptionGenerator Component', () => {
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

  const renderGenerator = (props = {}) => {
    render(
      <QueryClientProvider client={queryClient}>
        <JobDescriptionGenerator {...props} />
      </QueryClientProvider>
    );
  };

  it('renders job description generator form', () => {
    renderGenerator();
    expect(screen.getByText(/Job Description Generator/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Generate with AI/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/Job Title/i)).toBeInTheDocument();
  });

  it('handles successful job description generation', async () => {
    const onGenerateMock = jest.fn();
    generateJobDescription.mockResolvedValueOnce(mockGeneratedDescription);
    
    renderGenerator({ onGenerate: onGenerateMock });
    
    fireEvent.change(screen.getByLabelText(/Job Title/i), {
      target: { value: 'Senior Frontend Developer' },
    });
    
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /Generate with AI/i }));
    });

    await waitFor(() => {
      expect(generateJobDescription).toHaveBeenCalledWith({
        title: 'Senior Frontend Developer',
      });
      expect(onGenerateMock).toHaveBeenCalledWith(mockGeneratedDescription);
    });
  });

  it('displays loading state during generation', async () => {
    generateJobDescription.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    renderGenerator();
    
    fireEvent.change(screen.getByLabelText(/Job Title/i), {
      target: { value: 'Senior Frontend Developer' },
    });
    
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /Generate with AI/i }));
    });

    await waitFor(() => {
      expect(screen.getByText('Generating...')).toBeInTheDocument();
    });
  });

  it('handles generation error', async () => {
    const errorMessage = 'Failed to generate job description';
    generateJobDescription.mockRejectedValueOnce(new Error(errorMessage));
    
    renderGenerator();
    
    fireEvent.change(screen.getByLabelText(/Job Title/i), {
      target: { value: 'Senior Frontend Developer' },
    });
    
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /Generate with AI/i }));
    });

    await waitFor(() => {
      const errorElement = screen.getByText((content, element) => {
        return element.textContent === `Error: ${errorMessage}`;
      });
      expect(errorElement).toBeInTheDocument();
    });
  });

  it('validates required fields before generation', async () => {
    renderGenerator();
    
    // Try to generate without entering a job title
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /Generate with AI/i }));
    });

    expect(screen.getByText(/Job title is required/i)).toBeInTheDocument();
    expect(generateJobDescription).not.toHaveBeenCalled();
  });
}); 