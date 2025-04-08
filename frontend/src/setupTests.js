import '@testing-library/jest-dom';
import { server } from './mocks/server';

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

beforeAll(() => server.listen());
afterEach(() => {
  server.resetHandlers();
  mockFetch.mockReset();
});
afterAll(() => server.close()); 