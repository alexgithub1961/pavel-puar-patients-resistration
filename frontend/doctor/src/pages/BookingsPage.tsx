import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import { CheckCircle, XCircle } from 'lucide-react';
import { doctorApi } from '../api/client';

export default function BookingsPage() {
  const queryClient = useQueryClient();

  const { data: bookings, isLoading } = useQuery({
    queryKey: ['doctorBookings'],
    queryFn: async () => {
      const response = await doctorApi.getBookings({ page_size: 100 });
      return response.data;
    },
  });

  const completeMutation = useMutation({
    mutationFn: async (bookingId: string) => {
      return doctorApi.markComplete(bookingId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['doctorBookings'] });
    },
  });

  const noShowMutation = useMutation({
    mutationFn: async (bookingId: string) => {
      return doctorApi.markNoShow(bookingId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['doctorBookings'] });
    },
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      case 'no_show':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Appointments</h1>

      {isLoading ? (
        <p className="text-gray-500 py-8 text-center">Loading...</p>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Date & Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Patient
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Reason
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {bookings?.items?.map((booking: {
                id: string;
                slot_start_time: string;
                slot_end_time: string;
                patient_id: string;
                reason: string | null;
                status: string;
              }) => (
                <tr key={booking.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <p className="font-medium">
                      {format(new Date(booking.slot_start_time), 'MMM d, yyyy')}
                    </p>
                    <p className="text-sm text-gray-500">
                      {format(new Date(booking.slot_start_time), 'h:mm a')} -{' '}
                      {format(new Date(booking.slot_end_time), 'h:mm a')}
                    </p>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {booking.patient_id.slice(0, 8)}...
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                    {booking.reason || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(
                        booking.status
                      )}`}
                    >
                      {booking.status.replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {booking.status === 'confirmed' && (
                      <div className="flex gap-2">
                        <button
                          onClick={() => completeMutation.mutate(booking.id)}
                          className="p-1 text-green-600 hover:bg-green-50 rounded"
                          title="Mark complete"
                        >
                          <CheckCircle className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => noShowMutation.mutate(booking.id)}
                          className="p-1 text-red-600 hover:bg-red-50 rounded"
                          title="Mark no-show"
                        >
                          <XCircle className="w-5 h-5" />
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {(!bookings?.items || bookings.items.length === 0) && (
            <p className="text-gray-500 py-8 text-center">No appointments found</p>
          )}
        </div>
      )}
    </div>
  );
}
