import React, { createContext, useState, useEffect, ReactNode } from 'react';
import { User, UserRole } from '../types';
import { authService } from '../services/authService';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  hasRole: (roles: UserRole[]) => boolean;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('modelforge_token'));
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('modelforge_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('modelforge_token');
      if (storedToken) {
        try {
          const currentUser = await authService.getMe();
          setUser(currentUser);
          localStorage.setItem('modelforge_user', JSON.stringify(currentUser));
        } catch (err) {
          console.warn('Session expired or invalid token:', err);
          localStorage.removeItem('modelforge_token');
          localStorage.removeItem('modelforge_user');
          setToken(null);
          setUser(null);
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = (newToken: string, newUser: User) => {
    localStorage.setItem('modelforge_token', newToken);
    localStorage.setItem('modelforge_user', JSON.stringify(newUser));
    setToken(newToken);
    setUser(newUser);
  };

  const logout = () => {
    localStorage.removeItem('modelforge_token');
    localStorage.removeItem('modelforge_user');
    setToken(null);
    setUser(null);
  };

  const hasRole = (roles: UserRole[]): boolean => {
    if (!user) return false;
    return roles.includes(user.role);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        login,
        logout,
        hasRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
