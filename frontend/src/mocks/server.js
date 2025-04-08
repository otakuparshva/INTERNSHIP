import { setupServer } from 'msw/node';
import { rest } from 'msw';

export const handlers = [
  rest.post('/api/auth/login', (req, res, ctx) => {
    return res(
      ctx.json({
        access_token: 'fake-token',
        token_type: 'bearer'
      })
    );
  }),
  
  rest.post('/api/auth/register', (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({
        id: '123',
        email: req.body.email,
        full_name: req.body.full_name
      })
    );
  }),
  
  rest.get('/api/auth/me', (req, res, ctx) => {
    return res(
      ctx.json({
        id: '123',
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'candidate'
      })
    );
  })
];

export const server = setupServer(...handlers); 