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
    apiClient.post('/auth/doctors/login', { email, password }),

  register: (data: Record<string, unknown>) =>
    apiClient.post('/auth/doctors/register', data),

  demoLogin: () =>
    apiClient.post('/auth/demo', { role: 'doctor' }),
};

// Doctor API
export const doctorApi = {
  getMe: () => apiClient.get('/doctors/me'),
  updateMe: (data: Record<string, unknown>) => apiClient.patch('/doctors/me', data),
  getBookings: (params?: Record<string, unknown>) =>
    apiClient.get('/doctors/me/bookings', { params }),
  getScarcity: (daysAhead = 7) =>
    apiClient.get('/doctors/me/scarcity', { params: { days_ahead: daysAhead } }),
  getPatients: (params?: Record<string, unknown>) =>
    apiClient.get('/doctors/me/patients', { params }),
  markComplete: (bookingId: string) =>
    apiClient.post(`/doctors/me/bookings/${bookingId}/complete`),
  markNoShow: (bookingId: string) =>
    apiClient.post(`/doctors/me/bookings/${bookingId}/no-show`),
  reserveUrgentSlots: (percentage: number) =>
    apiClient.post('/doctors/me/reserve-urgent-slots', null, { params: { percentage } }),
  releaseReservedSlots: (hoursBefore: number) =>
    apiClient.post('/doctors/me/release-reserved-slots', null, { params: { hours_before: hoursBefore } }),
};

// Slots API
export const slotsApi = {
  getAll: (params?: Record<string, unknown>) =>
    apiClient.get('/slots/doctor', { params }),
  create: (data: Record<string, unknown>) =>
    apiClient.post('/slots/', data),
  createBulk: (data: Record<string, unknown>) =>
    apiClient.post('/slots/bulk', data),
  autoGenerate: (data: Record<string, unknown>) =>
    apiClient.post('/slots/auto-generate', data),
  update: (slotId: string, data: Record<string, unknown>) =>
    apiClient.patch(`/slots/${slotId}`, data),
  block: (slotId: string) =>
    apiClient.post(`/slots/${slotId}/block`),
  deleteRecurring: (recurrenceGroupId: string) =>
    apiClient.delete(`/slots/recurring/${recurrenceGroupId}`),
};
