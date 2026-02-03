import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Language } from '../i18n/translations';

interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  category: string;
  complianceLevel: string;
  complianceScore: number;
  preferredLanguage: Language;
}

// Demo account email pattern - must match seed_data.py
const DEMO_EMAIL_PATTERN = /^demo\..+@example\.com$/;

function isDemoAccount(email: string): boolean {
  return DEMO_EMAIL_PATTERN.test(email);
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isDemoMode: boolean;
  language: Language;
  setUser: (user: User | null) => void;
  setTokens: (access: string, refresh: string) => void;
  setLanguage: (lang: Language) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isDemoMode: false,
      language: 'en',

      setUser: (user) =>
        set({
          user,
          isAuthenticated: !!user,
          isDemoMode: user ? isDemoAccount(user.email) : false,
          language: user?.preferredLanguage || 'en',
        }),

      setTokens: (access, refresh) =>
        set({
          accessToken: access,
          refreshToken: refresh,
          isAuthenticated: true,
        }),

      setLanguage: (language) => set({ language }),

      logout: () =>
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          isDemoMode: false,
        }),
    }),
    {
      name: 'puar-auth',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
        language: state.language,
        isAuthenticated: state.isAuthenticated,
        isDemoMode: state.isDemoMode,
      }),
    }
  )
);
