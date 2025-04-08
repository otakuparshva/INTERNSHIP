import React, { useState } from 'react';
import { useQuery, useMutation } from 'react-query';
import { motion } from 'framer-motion';
import { generateInterviewQuestions, submitInterviewAnswers } from '../../services/api';

export default function InterviewBot() {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [interviewStarted, setInterviewStarted] = useState(false);
  const [interviewCompleted, setInterviewCompleted] = useState(false);
  const [error, setError] = useState('');

  const { data: questions, isLoading } = useQuery(
    'interviewQuestions',
    () => generateInterviewQuestions(localStorage.getItem('currentJobId'), 5),
    {
      enabled: interviewStarted,
      onSuccess: (data) => {
        setAnswers(
          data.questions.reduce((acc, q) => ({ ...acc, [q.id]: '' }), {})
        );
      },
    }
  );

  const submitMutation = useMutation(submitInterviewAnswers, {
    onSuccess: () => {
      setInterviewCompleted(true);
      setError('');
    },
    onError: () => {
      setError('Failed to submit interview. Please try again.');
    },
  });

  const handleStartInterview = () => {
    setInterviewStarted(true);
  };

  const handleAnswerSelect = (questionId, answer) => {
    setAnswers(prev => ({ ...prev, [questionId]: answer }));
  };

  const handleNext = () => {
    if (currentQuestion < questions.questions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1);
    }
  };

  const handleSubmit = () => {
    const unansweredQuestions = questions.questions.filter(
      q => !answers[q.id]
    );

    if (unansweredQuestions.length > 0) {
      setError('Please answer all questions before submitting.');
      return;
    }

    submitMutation.mutate({
      interviewId: localStorage.getItem('currentInterviewId'),
      answers,
    });
  };

  if (!interviewStarted) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Ready for your interview?
        </h2>
        <p className="text-gray-600 mb-8">
          This interview consists of 5 multiple-choice questions based on the job requirements.
          Take your time and answer carefully.
        </p>
        <button
          onClick={handleStartInterview}
          className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Start Interview
        </button>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        Loading...
      </div>
    );
  }

  if (interviewCompleted) {
    return (
      <div className="text-center py-12">
        <motion.div
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Interview Completed!
          </h2>
          <p className="text-gray-600">
            Thank you for completing the interview. We will review your answers and get back to you soon.
          </p>
        </motion.div>
      </div>
    );
  }

  const question = questions.questions[currentQuestion];
  const progress = ((currentQuestion + 1) / questions.questions.length) * 100;

  return (
    <div className="max-w-3xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="mb-8">
          <div className="flex justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              Question {currentQuestion + 1} of {questions.questions.length}
            </span>
            <span className="text-sm font-medium text-gray-700">
              {Math.round(progress)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
        >
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            {question.text}
          </h3>
          <div className="space-y-3">
            {question.options.map((option) => (
              <label
                key={option}
                className="flex items-center p-4 border rounded-lg cursor-pointer transition-colors duration-200 border-gray-200 hover:border-blue-300"
              >
                <input
                  type="radio"
                  name={`question-${currentQuestion + 1}`}
                  value={option}
                  checked={answers[question.id] === option}
                  onChange={() => handleAnswerSelect(question.id, option)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-3 text-gray-700">{option}</span>
              </label>
            ))}
          </div>
        </motion.div>

        {error && (
          <div className="mt-4 text-red-600 text-sm">
            {error}
          </div>
        )}

        <div className="mt-8 flex justify-between">
          <button
            onClick={handlePrevious}
            disabled={currentQuestion === 0}
            className={`inline-flex items-center px-4 py-2 border ${
              currentQuestion === 0
                ? 'border-gray-300 text-gray-400 cursor-not-allowed'
                : 'border-gray-300 text-gray-700 hover:bg-gray-50'
            } text-sm font-medium rounded-md`}
          >
            Previous
          </button>
          {currentQuestion === questions.questions.length - 1 ? (
            <button
              onClick={handleSubmit}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Submit
            </button>
          ) : (
            <button
              onClick={handleNext}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Next
            </button>
          )}
        </div>
      </div>
    </div>
  );
} 