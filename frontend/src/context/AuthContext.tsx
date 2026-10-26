import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, AuthResponse } from '../types';
import { authService } from '../services/domainServices';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string, role?: string) => Promise<void>;
  quickDemoLogin: (role: 'admin' | 'treasury_manager' | 'payment_ops' | 'auditor') => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('kaizen_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('kaizen_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('kaizen_token');
      if (storedToken) {
        try {
          const me = await authService.getMe();
          setUser(me);
          localStorage.setItem('kaizen_user', JSON.stringify(me));
        } catch {
          try {
            const data = await authService.login('treasury@kaizen.dev', 'Demo1234!');
            handleAuthSuccess(data);
          } catch {
            localStorage.removeItem('kaizen_token');
            localStorage.removeItem('kaizen_user');
            setToken(null);
            setUser(null);
          }
        }
      } else if (window.location.pathname.startsWith('/app')) {
        try {
          const data = await authService.login('treasury@kaizen.dev', 'Demo1234!');
          handleAuthSuccess(data);
        } catch (e) {
          console.warn('Demo session auto-login failed:', e);
        }
      }
      setIsLoading(false);
    };
    initAuth();
  }, []);

  const handleAuthSuccess = (data: AuthResponse) => {
    localStorage.setItem('kaizen_token', data.access_token);
    localStorage.setItem('kaizen_user', JSON.stringify(data.user));
    setToken(data.access_token);
    setUser(data.user);
  };

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const data = await authService.login(email, password);
      handleAuthSuccess(data);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string, fullName: string, role = 'payment_ops') => {
    setIsLoading(true);
    try {
      const data = await authService.register(email, password, fullName, role);
      handleAuthSuccess(data);
    } finally {
      setIsLoading(false);
    }
  };

  const quickDemoLogin = async (role: 'admin' | 'treasury_manager' | 'payment_ops' | 'auditor') => {
    const roleEmailMap = {
      admin: 'admin@kaizen.dev',
      treasury_manager: 'treasury@kaizen.dev',
      payment_ops: 'ops@kaizen.dev',
      auditor: 'auditor@kaizen.dev',
    };
    await login(roleEmailMap[role], 'Demo1234!');
  };

  const logout = () => {
    authService.logout().catch(() => {});
    localStorage.removeItem('kaizen_token');
    localStorage.removeItem('kaizen_user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        isAuthenticated: !!token && !!user,
        login,
        register,
        quickDemoLogin,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
