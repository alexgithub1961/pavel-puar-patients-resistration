import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Doctor {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  specialisation: string | null;
}

// Demo account email pattern - must match seed_data.py
const DEMO_EMAIL_PATTERN = /^demo\..+@example\.com$/;

function isDemoAccount(email: string): boolean {
  return DEMO_EMAIL_PATTERN.test(email);
}

interface AuthState {
  doctor: Doctor | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isDemoMode: boolean;
  setDoctor: (doctor: Doctor | null) => void;
  setTokens: (access: string, refresh: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      doctor: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isDemoMode: false,

      setDoctor: (doctor) =>
        set({
          doctor,
          isAuthenticated: !!doctor,
          isDemoMode: doctor ? isDemoAccount(doctor.email) : false,
        }),

      setTokens: (access, refresh) =>
        set({
          accessToken: access,
          refreshToken: refresh,
          isAuthenticated: true,
        }),

      logout: () =>
        set({
          doctor: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          isDemoMode: false,
        }),
    }),
    {
      name: 'puar-doctor-auth',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        doctor: state.doctor,
        isAuthenticated: state.isAuthenticated,
        isDemoMode: state.isDemoMode,
      }),
    }
  )
);
