/**
 * Demo API Client
 * 
 * Returns mock data when DEMO_MODE is enabled.
 * Simulates API delays for realistic UX.
 */

import { demoConfig } from './config';

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const demoApi = {
  // Auth endpoints
  async getCurrentUser() {
    await delay(300);
    return { data: demoConfig.user };
  },

  async getRateLimit() {
    await delay(100);
    return {
      data: {
        limit: 1000,
        remaining: 847,
        reset: Date.now() + 3600000,
      },
    };
  },

  // Repository endpoints
  async getRepositories() {
    await delay(400);
    return { data: demoConfig.repositories };
  },

  async getRepository(id: string) {
    await delay(300);
    const repo = demoConfig.repositories.find(r => r.id === id);
    if (!repo) throw new Error('Repository not found');
    return { data: repo };
  },

  // Document endpoints
  async getDocuments(filters?: any) {
    await delay(500);
    return { data: demoConfig.documents };
  },

  async getDocument(id: string) {
    await delay(300);
    const doc = demoConfig.documents.find(d => d.id === id);
    if (!doc) throw new Error('Document not found');
    return { data: doc };
  },

  // Collection endpoints
  async getCollections() {
    await delay(400);
    return { data: demoConfig.collections };
  },

  async getCollection(id: string) {
    await delay(300);
    const collection = demoConfig.collections.find(c => c.id === id);
    if (!collection) throw new Error('Collection not found');
    return { data: collection };
  },

  // Code file endpoints
  async getCodeFile(id: string) {
    await delay(600);
    return { data: demoConfig.codeFile };
  },

  async getChunks(fileId: string) {
    await delay(400);
    return { data: demoConfig.codeFile.chunks };
  },

  async getAnnotations(fileId: string) {
    await delay(300);
    return { data: demoConfig.codeFile.annotations };
  },

  async getQuality(fileId: string) {
    await delay(300);
    return { data: demoConfig.codeFile.quality };
  },

  // Health check
  async getHealth() {
    await delay(100);
    return {
      data: {
        status: 'healthy',
        mode: 'demo',
        timestamp: new Date().toISOString(),
      },
    };
  },
};
