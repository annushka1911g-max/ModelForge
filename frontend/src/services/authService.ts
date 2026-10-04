import { apiClient } from './apiClient';
import { User } from '../types';

export const authService = {
  login: async (email: string, password: string): Promise<{ access_token: string; user: User }> => {
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);

    const response = await apiClient.post<{ access_token: string; token_type: string }>(
      '/auth/login',
      params,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );

    const token = response.data.access_token;
    localStorage.setItem('modelforge_token', token);

    const userResponse = await apiClient.get<User>('/auth/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    return {
      access_token: token,
      user: userResponse.data,
    };
  },

  register: async (userData: {
    email: string;
    password: string;
    full_name: string;
    role?: string;
  }): Promise<User> => {
    const response = await apiClient.post<User>('/auth/register', userData);
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },

  getUsers: async (skip: number = 0, limit: number = 100): Promise<User[]> => {
    const response = await apiClient.get<User[]>('/users', {
      params: { skip, limit },
    });
    return response.data;
  },

  updateUser: async (
    userId: number,
    data: { role?: string; is_active?: boolean; full_name?: string }
  ): Promise<User> => {
    const response = await apiClient.patch<User>(`/users/${userId}`, data);
    return response.data;
  },
};
