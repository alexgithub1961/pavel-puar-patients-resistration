import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Play, User, UserPlus, Sparkles } from 'lucide-react';
import { authApi, patientApi } from '../api/client';
import { useAuthStore } from '../store/authStore';
import { t } from '../i18n/translations';
import FeatureTour from '../components/FeatureTour';

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

type LoginForm = z.infer<typeof loginSchema>;

// Demo account credentials - must match seed_data.py
const _DEMO_ACCOUNTS = {
  newPatient: {
    email: 'demo.new@example.com',
    password: 'demo1234',
    label: 'New Patient Demo',
    description: 'No appointments yet',
  },
  regularPatient: {
    email: 'demo.regular@example.com',
    password: 'demo1234',
    label: 'Regular Patient Demo',
    description: 'Has appointment history',
  },
};

export default function LoginPage() {
  const navigate = useNavigate();
  const { setTokens, setUser, language } = useAuthStore();
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showTour, setShowTour] = useState(false);
  const [pendingDemoLogin, setPendingDemoLogin] = useState<'newPatient' | 'regularPatient' | null>(null);

  const {
    register,
    handleSubmit,
    // setValue,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true);
    setError('');

    try {
      // Login
      const loginResponse = await authApi.login(data.email, data.password);
      const { access_token, refresh_token } = loginResponse.data;
      setTokens(access_token, refresh_token);

      // Get user profile
      const profileResponse = await patientApi.getMe();
      setUser({
        id: profileResponse.data.id,
        email: profileResponse.data.email,
        firstName: profileResponse.data.first_name,
        lastName: profileResponse.data.last_name,
        category: profileResponse.data.category,
        complianceLevel: profileResponse.data.compliance_level,
        complianceScore: profileResponse.data.compliance_score,
        preferredLanguage: profileResponse.data.preferred_language || 'en',
      });

      navigate('/dashboard');
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosError = err as { response?: { data?: { detail?: string } } };
        setError(axiosError.response?.data?.detail || 'Login failed');
      } else {
        setError('Login failed');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = (accountType: 'newPatient' | 'regularPatient') => {
    // Show the feature tour first, then login
    setPendingDemoLogin(accountType);
    setShowTour(true);
  };

  const completeDemoLogin = async () => {
    if (pendingDemoLogin) {
      setIsLoading(true);
      setError('');

      try {
        // Use the dedicated demo login endpoint
        const role = pendingDemoLogin === 'newPatient' ? 'new_patient' : 'regular_patient';
        const loginResponse = await authApi.demoLogin(role);
        const { access_token, refresh_token } = loginResponse.data;
        setTokens(access_token, refresh_token);

        // Get user profile
        const profileResponse = await patientApi.getMe();
        setUser({
          id: profileResponse.data.id,
          email: profileResponse.data.email,
          firstName: profileResponse.data.first_name,
          lastName: profileResponse.data.last_name,
          category: profileResponse.data.category,
          complianceLevel: profileResponse.data.compliance_level,
          complianceScore: profileResponse.data.compliance_score,
          preferredLanguage: profileResponse.data.preferred_language || 'en',
        });

        navigate('/dashboard');
      } catch (err: unknown) {
        if (err && typeof err === 'object' && 'response' in err) {
          const axiosError = err as { response?: { data?: { detail?: string } } };
          setError(axiosError.response?.data?.detail || 'Demo login failed');
        } else {
          setError('Demo login failed');
        }
      } finally {
        setIsLoading(false);
        setPendingDemoLogin(null);
      }
    }
    setShowTour(false);
  };

  return (
    <>
      {showTour && <FeatureTour onClose={completeDemoLogin} />}

      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div>
            <h1 className="text-center text-3xl font-bold text-primary-600">
              {t('app.name', language)}
            </h1>
            <h2 className="mt-6 text-center text-2xl font-semibold text-gray-900">
              {t('auth.login', language)}
            </h2>
          </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-md text-sm">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                {t('auth.email', language)}
              </label>
              <input
                {...register('email')}
                type="email"
                autoComplete="email"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                {t('auth.password', language)}
              </label>
              <input
                {...register('password')}
                type="password"
                autoComplete="current-password"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              />
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
              )}
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
          >
            {isLoading ? t('loading', language) : t('auth.login', language)}
          </button>

          <p className="text-center text-sm text-gray-600">
            {t('auth.noAccount', language)}{' '}
            <Link to="/register" className="text-primary-600 hover:text-primary-500">
              {t('auth.register', language)}
            </Link>
          </p>
        </form>

        {/* Demo Mode Section */}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <div className="flex items-center gap-2 mb-4">
            <Play className="w-5 h-5 text-amber-500" />
            <h3 className="text-sm font-semibold text-gray-700">
              {t('demo.title', language)}
            </h3>
          </div>

          <p className="text-xs text-gray-500 mb-4">
            {t('demo.description', language)}
          </p>

          <div className="space-y-3">
            {/* New Patient Demo */}
            <button
              type="button"
              onClick={() => handleDemoLogin('newPatient')}
              disabled={isLoading}
              className="w-full flex items-center gap-3 px-4 py-3 border-2 border-dashed border-amber-300 rounded-lg bg-amber-50 hover:bg-amber-100 hover:border-amber-400 transition-colors disabled:opacity-50"
            >
              <div className="flex-shrink-0 w-10 h-10 bg-amber-200 rounded-full flex items-center justify-center">
                <UserPlus className="w-5 h-5 text-amber-700" />
              </div>
              <div className="text-left">
                <p className="font-medium text-amber-800">
                  {t('demo.newPatient', language)}
                </p>
                <p className="text-xs text-amber-600">
                  {t('demo.newPatientDesc', language)}
                </p>
              </div>
            </button>

            {/* Regular Patient Demo */}
            <button
              type="button"
              onClick={() => handleDemoLogin('regularPatient')}
              disabled={isLoading}
              className="w-full flex items-center gap-3 px-4 py-3 border-2 border-dashed border-emerald-300 rounded-lg bg-emerald-50 hover:bg-emerald-100 hover:border-emerald-400 transition-colors disabled:opacity-50"
            >
              <div className="flex-shrink-0 w-10 h-10 bg-emerald-200 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-emerald-700" />
              </div>
              <div className="text-left">
                <p className="font-medium text-emerald-800">
                  {t('demo.regularPatient', language)}
                </p>
                <p className="text-xs text-emerald-600">
                  {t('demo.regularPatientDesc', language)}
                </p>
              </div>
            </button>
          </div>

          {/* Feature Tour Button */}
          <button
            type="button"
            onClick={() => setShowTour(true)}
            className="w-full flex items-center justify-center gap-2 py-2 text-sm text-primary-600 hover:text-primary-700"
          >
            <Sparkles className="w-4 h-4" />
            {t('tour.showAgain', language)}
          </button>
        </div>
      </div>
    </div>
    </>
  );
}
