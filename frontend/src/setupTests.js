import '@testing-library/jest-dom';
import { server } from './mocks/server';

// Mock fetch globally
global.fetch = jest.fn();

// Setup localStorage mock
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  clear: jest.fn(),
  removeItem: jest.fn(),
};
global.localStorage = localStorageMock;

beforeAll(() => server.listen());
afterEach(() => {
  server.resetHandlers();
  mockFetch.mockReset();
  jest.clearAllMocks();
  localStorage.clear();
});
afterAll(() => server.close()); 