import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Calendar, TrendingUp, AlertCircle, Plus } from 'lucide-react';
import { format } from 'date-fns';
import { useAuthStore } from '../store/authStore';
import { bookingsApi, patientApi } from '../api/client';
import { t } from '../i18n/translations';
import DemoHint from '../components/DemoHint';

export default function DashboardPage() {
  const { user, language, isDemoMode } = useAuthStore();

  const { data: bookings } = useQuery({
    queryKey: ['bookings'],
    queryFn: async () => {
      const response = await bookingsApi.getAll();
      return response.data;
    },
  });

  const { data: bookingWindow } = useQuery({
    queryKey: ['bookingWindow'],
    queryFn: async () => {
      const response = await patientApi.getBookingWindow();
      return response.data;
    },
  });

  const nextBooking = bookings?.items?.[0];

  return (
    <div className="space-y-6">
      {/* Demo Hint for new users */}
      {isDemoMode && (
        <DemoHint
          id="dashboard-welcome"
          titleKey="demo.hint.welcome.title"
          descriptionKey="demo.hint.welcome.desc"
        />
      )}

      {/* Welcome Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900">
          {t('dashboard.welcome', language)}, {user?.firstName}!
        </h1>
        <p className="text-gray-600 mt-1">{t('app.tagline', language)}</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Compliance Score */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t('dashboard.complianceScore', language)}</p>
              <p className="text-3xl font-bold text-primary-600">{user?.complianceScore || 0}</p>
            </div>
            <TrendingUp className="w-10 h-10 text-primary-200" />
          </div>
          <div className="mt-2">
            <span
              className={`inline-block px-2 py-1 text-xs rounded-full ${
                user?.complianceLevel === 'platinum'
                  ? 'bg-purple-100 text-purple-800'
                  : user?.complianceLevel === 'gold'
                  ? 'bg-yellow-100 text-yellow-800'
                  : user?.complianceLevel === 'silver'
                  ? 'bg-gray-100 text-gray-800'
                  : 'bg-orange-100 text-orange-800'
              }`}
            >
              {user?.complianceLevel}
            </span>
          </div>
        </div>

        {/* Category */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t('dashboard.category', language)}</p>
              <p className="text-xl font-semibold text-gray-900 capitalize">
                {user?.category?.replace('_', ' ') || 'Not set'}
              </p>
            </div>
            <AlertCircle className="w-10 h-10 text-primary-200" />
          </div>
        </div>

        {/* Visit Frequency */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t('dashboard.visitFrequency', language)}</p>
              <p className="text-xl font-semibold text-gray-900">
                {bookingWindow?.visit_frequency_days
                  ? `Every ${bookingWindow.visit_frequency_days} days`
                  : 'Not set'}
              </p>
            </div>
            <Calendar className="w-10 h-10 text-primary-200" />
          </div>
        </div>
      </div>

      {/* Demo Hint for booking */}
      {isDemoMode && !nextBooking && (
        <DemoHint
          id="dashboard-book"
          titleKey="demo.hint.book.title"
          descriptionKey="demo.hint.book.desc"
        />
      )}

      {/* Next Appointment */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          {t('dashboard.nextAppointment', language)}
        </h2>

        {nextBooking ? (
          <div className="flex items-center justify-between p-4 bg-primary-50 rounded-lg">
            <div>
              <p className="font-medium text-gray-900">
                {format(new Date(nextBooking.slot_start_time), 'EEEE, MMMM d, yyyy')}
              </p>
              <p className="text-gray-600">
                {format(new Date(nextBooking.slot_start_time), 'h:mm a')} -{' '}
                {format(new Date(nextBooking.slot_end_time), 'h:mm a')}
              </p>
              <p className="text-sm text-gray-500 mt-1">{nextBooking.doctor_name}</p>
            </div>
            <Link
              to="/bookings"
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              View Details
            </Link>
          </div>
        ) : (
          <div className="text-center py-8">
            <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 mb-4">{t('dashboard.noUpcoming', language)}</p>
            {bookingWindow?.can_book && (
              <Link
                to="/book"
                className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
              >
                <Plus className="w-5 h-5" />
                {t('dashboard.bookNow', language)}
              </Link>
            )}
          </div>
        )}
      </div>

      {/* Booking Window Info */}
      {bookingWindow && !bookingWindow.can_book && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
            <div>
              <p className="text-yellow-800 font-medium">Cannot book at this time</p>
              <p className="text-yellow-700 text-sm">{bookingWindow.reason}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
