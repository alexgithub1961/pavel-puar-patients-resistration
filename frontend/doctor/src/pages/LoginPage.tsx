import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Play, Stethoscope, Sparkles } from 'lucide-react';
import { authApi, doctorApi } from '../api/client';
import { useAuthStore } from '../store/authStore';
import FeatureTour from '../components/FeatureTour';

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

type LoginForm = z.infer<typeof loginSchema>;

// Demo account credentials - must match seed_data.py
const DEMO_DOCTOR = {
  email: 'demo.doctor@example.com',
  password: 'demo1234',
};

export default function LoginPage() {
  const navigate = useNavigate();
  const { setTokens, setDoctor } = useAuthStore();
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showTour, setShowTour] = useState(false);
  const [pendingDemoLogin, setPendingDemoLogin] = useState(false);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true);
    setError('');

    try {
      const loginResponse = await authApi.login(data.email, data.password);
      const { access_token, refresh_token } = loginResponse.data;
      setTokens(access_token, refresh_token);

      const profileResponse = await doctorApi.getMe();
      setDoctor({
        id: profileResponse.data.id,
        email: profileResponse.data.email,
        firstName: profileResponse.data.first_name,
        lastName: profileResponse.data.last_name,
        specialisation: profileResponse.data.specialisation,
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

  const handleDemoLogin = () => {
    // Show the feature tour first, then login
    setPendingDemoLogin(true);
    setShowTour(true);
  };

  const completeDemoLogin = async () => {
    if (pendingDemoLogin) {
      setIsLoading(true);
      setError('');

      try {
        // Use the dedicated demo login endpoint
        const loginResponse = await authApi.demoLogin();
        const { access_token, refresh_token } = loginResponse.data;
        setTokens(access_token, refresh_token);

        const profileResponse = await doctorApi.getMe();
        setDoctor({
          id: profileResponse.data.id,
          email: profileResponse.data.email,
          firstName: profileResponse.data.first_name,
          lastName: profileResponse.data.last_name,
          specialisation: profileResponse.data.specialisation,
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
        setPendingDemoLogin(false);
      }
    }
    setShowTour(false);
  };

  return (
    <>
      {showTour && <FeatureTour onClose={completeDemoLogin} />}

      <div className="min-h-screen flex items-center justify-center bg-emerald-50 py-12 px-4">
        <div className="max-w-md w-full space-y-8">
          <div>
            <h1 className="text-center text-3xl font-bold text-emerald-800">
              PUAR Doctor Portal
            </h1>
            <h2 className="mt-6 text-center text-2xl font-semibold text-gray-900">
              Login
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
              <label className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                {...register('email')}
                type="email"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                {...register('password')}
                type="password"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
              />
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
              )}
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 disabled:opacity-50"
          >
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        {/* Demo Mode Section */}
        <div className="mt-8 pt-6 border-t border-emerald-200">
          <div className="flex items-center gap-2 mb-4">
            <Play className="w-5 h-5 text-amber-500" />
            <h3 className="text-sm font-semibold text-gray-700">
              Demo Mode
            </h3>
          </div>

          <p className="text-xs text-gray-500 mb-4">
            Try the doctor portal with a demo account
          </p>

          <button
            type="button"
            onClick={handleDemoLogin}
            disabled={isLoading}
            className="w-full flex items-center gap-3 px-4 py-3 border-2 border-dashed border-emerald-400 rounded-lg bg-emerald-100 hover:bg-emerald-200 hover:border-emerald-500 transition-colors disabled:opacity-50"
          >
            <div className="flex-shrink-0 w-10 h-10 bg-emerald-300 rounded-full flex items-center justify-center">
              <Stethoscope className="w-5 h-5 text-emerald-800" />
            </div>
            <div className="text-left">
              <p className="font-medium text-emerald-900">
                Dr. Demo
              </p>
              <p className="text-xs text-emerald-700">
                View patient appointments and manage slots
              </p>
            </div>
          </button>
        </div>

        {/* Feature Tour Button */}
        <button
          type="button"
          onClick={() => setShowTour(true)}
          className="w-full flex items-center justify-center gap-2 py-2 text-sm text-emerald-600 hover:text-emerald-700"
        >
          <Sparkles className="w-4 h-4" />
          Show Feature Tour
        </button>
      </div>
    </div>
    </>
  );
}
