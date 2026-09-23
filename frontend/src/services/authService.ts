import { apiClient } from './apiClient';
import { User } from '../types';

export const authService = {
  login: async (_formData: FormData): Promise<{ access_token: string; user: User }> => {
    throw new Error('authService.login not yet implemented');
  },
  register: async (_userData: Record<string, any>): Promise<User> => {
    throw new Error('authService.register not yet implemented');
  },
  getMe: async (): Promise<User> => {
    throw new Error('authService.getMe not yet implemented');
  },
};
