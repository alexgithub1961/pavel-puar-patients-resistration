import axios from 'axios';
import { useAuthStore } from '../store/authStore';

// Use environment variable for API URL in production, fallback to relative path for dev
const API_BASE_URL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api/v1`
  : '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = useAuthStore.getState().refreshToken;
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token } = response.data;
          useAuthStore.getState().setTokens(access_token, refresh_token);

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        } catch {
          useAuthStore.getState().logout();
        }
      } else {
        useAuthStore.getState().logout();
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: (email: string, password: string) =>
    apiClient.post('/auth/patients/login', { email, password }),

  register: (data: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    phone?: string;
    date_of_birth?: string;
    preferred_language?: string;
  }) => apiClient.post('/auth/patients/register', data),

  refresh: (refreshToken: string) =>
    apiClient.post('/auth/refresh', { refresh_token: refreshToken }),

  demoLogin: (role: 'new_patient' | 'regular_patient') =>
    apiClient.post('/auth/demo', { role }),
};

// Patient API
export const patientApi = {
  getMe: () => apiClient.get('/patients/me'),
  updateMe: (data: Record<string, unknown>) => apiClient.patch('/patients/me', data),
  getBookingWindow: () => apiClient.get('/patients/me/next-booking-window'),
  getComplianceQuestionnaire: () => apiClient.get('/patients/me/compliance-questionnaire'),
  submitComplianceQuestionnaire: (data: Record<string, unknown>) =>
    apiClient.post('/patients/me/compliance-questionnaire', data),
};

// Slots API
export const slotsApi = {
  getAvailable: (doctorId: string, startDate?: string, endDate?: string) =>
    apiClient.get('/slots/available', {
      params: { doctor_id: doctorId, start_date: startDate, end_date: endDate },
    }),

  getAvailableDates: (doctorId: string, slotType?: string) =>
    apiClient.get('/slots/available-dates', {
      params: { doctor_id: doctorId, slot_type: slotType },
    }),

  getEmergencySlots: (doctorId: string) =>
    apiClient.get('/slots/available/emergency', {
      params: { doctor_id: doctorId },
    }),
};

// Bookings API
export const bookingsApi = {
  getAll: (includePast = false) =>
    apiClient.get('/bookings/', { params: { include_past: includePast } }),

  getById: (id: string) => apiClient.get(`/bookings/${id}`),

  create: (slotId: string, doctorId: string, reason?: string, isEmergency?: boolean, urgencyReason?: string) =>
    apiClient.post('/bookings/', {
      slot_id: slotId,
      reason,
      is_emergency: isEmergency,
      urgency_reason: urgencyReason,
    }, { params: { doctor_id: doctorId } }),

  submitTriage: (bookingId: string, data: Record<string, unknown>) =>
    apiClient.post(`/bookings/${bookingId}/triage`, data),

  cancel: (bookingId: string, triageId: string) =>
    apiClient.post(`/bookings/${bookingId}/cancel`, { triage_questionnaire_id: triageId }),

  reschedule: (bookingId: string, newSlotId: string, triageId: string) =>
    apiClient.post(`/bookings/${bookingId}/reschedule`, {
      new_slot_id: newSlotId,
      triage_questionnaire_id: triageId,
    }),
};
