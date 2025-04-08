import '@testing-library/jest-dom';
import { server } from './mocks/server';

// Mock fetch
global.fetch = jest.fn();

beforeAll(() => server.listen());
afterEach(() => {
  server.resetHandlers();
  global.fetch.mockClear();
});
afterAll(() => server.close()); 