import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import InterviewBot from '../candidate/InterviewBot';
import { generateInterviewQuestions, submitInterviewAnswers } from '../../services/api';

// Mock the API functions
jest.mock('../../services/api', () => ({
  generateInterviewQuestions: jest.fn(),
  submitInterviewAnswers: jest.fn(),
}));

const mockQuestions = {
  questions: [
    {
      id: '1',
      text: 'What is your greatest strength?',
      type: 'multiple_choice',
      options: ['Problem-solving', 'Communication', 'Leadership', 'Technical skills'],
    },
    {
      id: '2',
      text: 'Describe a challenging project you worked on.',
      type: 'multiple_choice',
      options: ['Project A', 'Project B', 'Project C', 'Project D'],
    },
  ],
};

describe('InterviewBot Component', () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    localStorage.setItem('currentJobId', '123');
    localStorage.setItem('currentInterviewId', '456');
  });

  const renderInterviewBot = () => {
    render(
      <QueryClientProvider client={queryClient}>
        <InterviewBot />
      </QueryClientProvider>
    );
  };

  it('renders initial start screen', () => {
    renderInterviewBot();
    expect(screen.getByText(/Ready for your interview?/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Start Interview/i })).toBeInTheDocument();
  });

  it('starts interview when clicking start button', async () => {
    generateInterviewQuestions.mockResolvedValueOnce(mockQuestions);
    
    renderInterviewBot();
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /Start Interview/i }));
    });
    
    await waitFor(() => {
      expect(generateInterviewQuestions).toHaveBeenCalledWith('123', 5);
    });
  });

  it('displays questions and handles navigation', async () => {
    generateInterviewQuestions.mockResolvedValueOnce(mockQuestions);
    
    renderInterviewBot();
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /Start Interview/i }));
    });
    
    await waitFor(() => {
      expect(screen.getByText(mockQuestions.questions[0].text)).toBeInTheDocument();
    });

    // Test answer selection
    fireEvent.click(screen.getByText('Problem-solving'));
    
    // Test navigation
    fireEvent.click(screen.getByRole('button', { name: /Next/i }));
    expect(screen.getByText(mockQuestions.questions[1].text)).toBeInTheDocument();
    
    fireEvent.click(screen.getByRole('button', { name: /Previous/i }));
    expect(screen.getByText(mockQuestions.questions[0].text)).toBeInTheDocument();
  });

  it('handles interview submission', async () => {
    generateInterviewQuestions.mockResolvedValueOnce(mockQuestions);
    submitInterviewAnswers.mockResolvedValueOnce({ success: true });
    
    renderInterviewBot();
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /Start Interview/i }));
    });
    
    await waitFor(() => {
      expect(screen.getByText(mockQuestions.questions[0].text)).toBeInTheDocument();
    });

    // Answer all questions
    fireEvent.click(screen.getByText('Problem-solving'));
    fireEvent.click(screen.getByRole('button', { name: /Next/i }));
    fireEvent.click(screen.getByText('Project A'));

    // Submit interview
    fireEvent.click(screen.getByRole('button', { name: /Submit/i }));

    await waitFor(() => {
      expect(submitInterviewAnswers).toHaveBeenCalledWith({
        interviewId: '456',
        answers: {
          '1': 'Problem-solving',
          '2': 'Project A',
        },
      });
      expect(screen.getByText(/Interview Completed!/i)).toBeInTheDocument();
    });
  });

  it('shows error when submitting without answering all questions', async () => {
    generateInterviewQuestions.mockResolvedValueOnce(mockQuestions);
    
    renderInterviewBot();
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /Start Interview/i }));
    });
    
    await waitFor(() => {
      expect(screen.getByText(mockQuestions.questions[0].text)).toBeInTheDocument();
    });

    // Navigate to the end without answering
    fireEvent.click(screen.getByRole('button', { name: /Next/i }));
    fireEvent.click(screen.getByRole('button', { name: /Submit/i }));

    expect(screen.getByText(/Please answer all questions before submitting/i)).toBeInTheDocument();
    expect(submitInterviewAnswers).not.toHaveBeenCalled();
  });

  it('displays loading state', async () => {
    generateInterviewQuestions.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    renderInterviewBot();
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /Start Interview/i }));
    });
    
    expect(screen.getByText(/Loading questions/i)).toBeInTheDocument();
  });
}); 