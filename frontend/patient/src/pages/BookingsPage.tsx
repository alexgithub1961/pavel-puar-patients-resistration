import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { format } from 'date-fns';
import { Calendar, Clock, User, XCircle, RefreshCw } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { bookingsApi } from '../api/client';
import { t } from '../i18n/translations';

type TabType = 'upcoming' | 'past';

export default function BookingsPage() {
  const { language } = useAuthStore();
  const [activeTab, setActiveTab] = useState<TabType>('upcoming');

  const { data, isLoading } = useQuery({
    queryKey: ['bookings', activeTab],
    queryFn: async () => {
      const response = await bookingsApi.getAll(activeTab === 'past');
      return response.data;
    },
  });

  const bookings = data?.items || [];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'cancelled_by_patient':
      case 'cancelled_by_doctor':
        return 'bg-red-100 text-red-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      case 'no_show':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">{t('bookings.title', language)}</h1>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex gap-8">
          <button
            onClick={() => setActiveTab('upcoming')}
            className={`py-2 border-b-2 font-medium text-sm ${
              activeTab === 'upcoming'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {t('bookings.upcoming', language)}
          </button>
          <button
            onClick={() => setActiveTab('past')}
            className={`py-2 border-b-2 font-medium text-sm ${
              activeTab === 'past'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {t('bookings.past', language)}
          </button>
        </nav>
      </div>

      {/* Bookings List */}
      {isLoading ? (
        <div className="text-center py-12">
          <p className="text-gray-500">{t('loading', language)}</p>
        </div>
      ) : bookings.length === 0 ? (
        <div className="text-center py-12">
          <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">{t('bookings.noBookings', language)}</p>
        </div>
      ) : (
        <div className="space-y-4">
          {bookings.map((booking: {
            id: string;
            status: string;
            slot_start_time: string;
            slot_end_time: string;
            doctor_name: string;
            reason?: string;
          }) => (
            <div
              key={booking.id}
              className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-primary-600" />
                    <span className="font-medium">
                      {format(new Date(booking.slot_start_time), 'EEEE, MMMM d, yyyy')}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-600">
                    <Clock className="w-5 h-5" />
                    <span>
                      {format(new Date(booking.slot_start_time), 'h:mm a')} -{' '}
                      {format(new Date(booking.slot_end_time), 'h:mm a')}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-600">
                    <User className="w-5 h-5" />
                    <span>{booking.doctor_name}</span>
                  </div>
                  {booking.reason && (
                    <p className="text-sm text-gray-500">Reason: {booking.reason}</p>
                  )}
                </div>

                <div className="flex flex-col items-end gap-2">
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(
                      booking.status
                    )}`}
                  >
                    {booking.status.replace(/_/g, ' ')}
                  </span>

                  {activeTab === 'upcoming' && booking.status !== 'cancelled_by_patient' && (
                    <div className="flex gap-2">
                      <button className="flex items-center gap-1 text-sm text-orange-600 hover:text-orange-700">
                        <RefreshCw className="w-4 h-4" />
                        {t('bookings.reschedule', language)}
                      </button>
                      <button className="flex items-center gap-1 text-sm text-red-600 hover:text-red-700">
                        <XCircle className="w-4 h-4" />
                        {t('bookings.cancel', language)}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
