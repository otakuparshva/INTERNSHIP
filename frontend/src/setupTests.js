import '@testing-library/jest-dom';

// Mock fetch globally
global.fetch = jest.fn(() => Promise.resolve({
  ok: true,
  json: () => Promise.resolve({}),
}));

// Setup localStorage mock
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  clear: jest.fn(),
  removeItem: jest.fn(),
};
global.localStorage = localStorageMock;

// Clean up after each test
afterEach(() => {
  jest.clearAllMocks();
  localStorage.clear();
}); 