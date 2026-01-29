/**
 * Phase 5: Implementation Planner - Demo Data
 */

import type { Plan } from '@/types/planner';

export const demoPlan: Plan = {
  id: 'demo-plan-1',
  name: 'Payment Service Implementation',
  description: 'Build a payment service with Stripe integration',
  createdAt: new Date('2024-01-20'),
  updatedAt: new Date('2024-01-25'),
  tasks: [
    {
      id: 'task-1',
      planId: 'demo-plan-1',
      title: 'Set up Stripe SDK',
      description: 'Install and configure Stripe SDK in the project',
      completed: true,
      order: 1,
      links: [
        {
          id: 'link-1',
          taskId: 'task-1',
          label: 'Stripe Docs',
          url: 'https://stripe.com/docs',
          type: 'external',
        },
      ],
      details: [
        {
          id: 'detail-1',
          taskId: 'task-1',
          type: 'command',
          content: 'npm install stripe',
          order: 1,
        },
        {
          id: 'detail-2',
          taskId: 'task-1',
          type: 'code',
          content: `import Stripe from 'stripe';
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);`,
          language: 'typescript',
          order: 2,
        },
      ],
      createdAt: new Date('2024-01-20'),
      updatedAt: new Date('2024-01-21'),
    },
    {
      id: 'task-2',
      planId: 'demo-plan-1',
      title: 'Create payment endpoint',
      description: 'Implement POST /api/payment endpoint',
      completed: true,
      order: 2,
      links: [
        {
          id: 'link-2',
          taskId: 'task-2',
          label: 'Sample Code',
          url: '#',
          type: 'code',
        },
      ],
      details: [
        {
          id: 'detail-3',
          taskId: 'task-2',
          type: 'code',
          content: `app.post('/api/payment', async (req, res) => {
  const { amount, currency } = req.body;
  
  const paymentIntent = await stripe.paymentIntents.create({
    amount,
    currency,
  });
  
  res.json({ clientSecret: paymentIntent.client_secret });
});`,
          language: 'typescript',
          order: 1,
        },
      ],
      createdAt: new Date('2024-01-21'),
      updatedAt: new Date('2024-01-22'),
    },
    {
      id: 'task-3',
      planId: 'demo-plan-1',
      title: 'Add webhook handler',
      description: 'Handle Stripe webhook events for payment confirmation',
      completed: true,
      order: 3,
      links: [
        {
          id: 'link-3',
          taskId: 'task-3',
          label: 'Webhook Guide',
          url: 'https://stripe.com/docs/webhooks',
          type: 'external',
        },
      ],
      details: [
        {
          id: 'detail-4',
          taskId: 'task-3',
          type: 'text',
          content: 'Set up webhook endpoint to receive payment events from Stripe',
          order: 1,
        },
        {
          id: 'detail-5',
          taskId: 'task-3',
          type: 'code',
          content: `app.post('/api/webhooks/stripe', async (req, res) => {
  const sig = req.headers['stripe-signature'];
  const event = stripe.webhooks.constructEvent(req.body, sig, webhookSecret);
  
  if (event.type === 'payment_intent.succeeded') {
    // Handle successful payment
  }
  
  res.json({ received: true });
});`,
          language: 'typescript',
          order: 2,
        },
      ],
      createdAt: new Date('2024-01-22'),
      updatedAt: new Date('2024-01-23'),
    },
    {
      id: 'task-4',
      planId: 'demo-plan-1',
      title: 'Implement error handling',
      description: 'Add comprehensive error handling for payment failures',
      completed: false,
      order: 4,
      links: [],
      details: [
        {
          id: 'detail-6',
          taskId: 'task-4',
          type: 'text',
          content: 'Add try-catch blocks and return appropriate error responses',
          order: 1,
        },
      ],
      createdAt: new Date('2024-01-23'),
      updatedAt: new Date('2024-01-23'),
    },
    {
      id: 'task-5',
      planId: 'demo-plan-1',
      title: 'Add payment validation',
      description: 'Validate payment amounts and currency codes',
      completed: false,
      order: 5,
      links: [],
      details: [
        {
          id: 'detail-7',
          taskId: 'task-5',
          type: 'command',
          content: 'npm install zod',
          order: 1,
        },
        {
          id: 'detail-8',
          taskId: 'task-5',
          type: 'code',
          content: `const PaymentSchema = z.object({
  amount: z.number().positive(),
  currency: z.enum(['USD', 'EUR', 'GBP']),
});`,
          language: 'typescript',
          order: 2,
        },
      ],
      createdAt: new Date('2024-01-24'),
      updatedAt: new Date('2024-01-24'),
    },
    {
      id: 'task-6',
      planId: 'demo-plan-1',
      title: 'Write unit tests',
      description: 'Test payment endpoint with mocked Stripe calls',
      completed: false,
      order: 6,
      links: [],
      details: [],
      createdAt: new Date('2024-01-24'),
      updatedAt: new Date('2024-01-24'),
    },
    {
      id: 'task-7',
      planId: 'demo-plan-1',
      title: 'Add integration tests',
      description: 'Test full payment flow with Stripe test mode',
      completed: false,
      order: 7,
      links: [],
      details: [],
      createdAt: new Date('2024-01-24'),
      updatedAt: new Date('2024-01-24'),
    },
    {
      id: 'task-8',
      planId: 'demo-plan-1',
      title: 'Update API documentation',
      description: 'Document payment endpoints in OpenAPI spec',
      completed: false,
      order: 8,
      links: [],
      details: [],
      createdAt: new Date('2024-01-24'),
      updatedAt: new Date('2024-01-24'),
    },
    {
      id: 'task-9',
      planId: 'demo-plan-1',
      title: 'Deploy to staging',
      description: 'Deploy payment service to staging environment',
      completed: false,
      order: 9,
      links: [],
      details: [],
      createdAt: new Date('2024-01-25'),
      updatedAt: new Date('2024-01-25'),
    },
    {
      id: 'task-10',
      planId: 'demo-plan-1',
      title: 'Monitor production metrics',
      description: 'Set up monitoring for payment success/failure rates',
      completed: false,
      order: 10,
      links: [],
      details: [],
      createdAt: new Date('2024-01-25'),
      updatedAt: new Date('2024-01-25'),
    },
  ],
  metadata: {
    totalTasks: 10,
    completedTasks: 3,
    progress: 30,
  },
};
