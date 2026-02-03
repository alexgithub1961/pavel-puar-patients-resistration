import { useQuery } from '@tanstack/react-query';
import { Calendar, Users, AlertTriangle, Clock } from 'lucide-react';
import { format, startOfDay, endOfDay } from 'date-fns';
import { useAuthStore } from '../store/authStore';
import { doctorApi } from '../api/client';
import DemoHint from '../components/DemoHint';

export default function DashboardPage() {
  const { doctor, isDemoMode } = useAuthStore();

  const { data: todayBookings } = useQuery({
    queryKey: ['todayBookings'],
    queryFn: async () => {
      const today = new Date();
      const response = await doctorApi.getBookings({
        start_date: startOfDay(today).toISOString(),
        end_date: endOfDay(today).toISOString(),
      });
      return response.data;
    },
  });

  const { data: scarcity } = useQuery({
    queryKey: ['scarcity'],
    queryFn: async () => {
      const response = await doctorApi.getScarcity(7);
      return response.data;
    },
  });

  const { data: patients } = useQuery({
    queryKey: ['patientCount'],
    queryFn: async () => {
      const response = await doctorApi.getPatients({ page_size: 1 });
      return response.data;
    },
  });

  const todayCount = todayBookings?.items?.length || 0;
  const patientCount = patients?.total || 0;

  return (
    <div className="space-y-6">
      {/* Demo Hint for doctors */}
      {isDemoMode && (
        <DemoHint
          id="doctor-dashboard-welcome"
          title="Welcome to Demo Mode!"
          description="Explore the doctor portal with sample patient data. Try managing slots and viewing appointments."
        />
      )}

      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome, Dr. {doctor?.lastName}
        </h1>
        <p className="text-gray-600 mt-1">
          {format(new Date(), 'EEEE, MMMM d, yyyy')}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Today's Appointments</p>
              <p className="text-3xl font-bold text-emerald-600">{todayCount}</p>
            </div>
            <Calendar className="w-10 h-10 text-emerald-200" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Patients</p>
              <p className="text-3xl font-bold text-blue-600">{patientCount}</p>
            </div>
            <Users className="w-10 h-10 text-blue-200" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Available Slots (7 days)</p>
              <p className="text-3xl font-bold text-purple-600">
                {scarcity?.available_slots || 0}
              </p>
            </div>
            <Clock className="w-10 h-10 text-purple-200" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Scarcity Level</p>
              <p
                className={`text-xl font-bold capitalize ${
                  scarcity?.level === 'critical'
                    ? 'text-red-600'
                    : scarcity?.level === 'high'
                    ? 'text-orange-600'
                    : scarcity?.level === 'moderate'
                    ? 'text-yellow-600'
                    : 'text-green-600'
                }`}
              >
                {scarcity?.level || 'Unknown'}
              </p>
            </div>
            <AlertTriangle
              className={`w-10 h-10 ${
                scarcity?.level === 'critical' || scarcity?.level === 'high'
                  ? 'text-red-200'
                  : 'text-green-200'
              }`}
            />
          </div>
        </div>
      </div>

      {/* Demo Hint for slot management */}
      {isDemoMode && (
        <DemoHint
          id="doctor-slots-hint"
          title="Manage Your Schedule"
          description="Go to 'Manage Slots' to create appointment slots. Patients can only book available slots."
        />
      )}

      {/* Today's Schedule */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Today's Schedule
        </h2>

        {todayCount === 0 ? (
          <p className="text-gray-500 py-8 text-center">No appointments today</p>
        ) : (
          <div className="space-y-3">
            {todayBookings?.items?.map((booking: {
              id: string;
              slot_start_time: string;
              slot_end_time: string;
              status: string;
              patient_id: string;
            }) => (
              <div
                key={booking.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
              >
                <div>
                  <p className="font-medium">
                    {format(new Date(booking.slot_start_time), 'h:mm a')} -{' '}
                    {format(new Date(booking.slot_end_time), 'h:mm a')}
                  </p>
                  <p className="text-sm text-gray-600">
                    Patient ID: {booking.patient_id.slice(0, 8)}...
                  </p>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-sm ${
                    booking.status === 'confirmed'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}
                >
                  {booking.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Scarcity Alert */}
      {scarcity && (scarcity.level === 'critical' || scarcity.level === 'high') && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-800">High Slot Scarcity</h3>
              <p className="text-red-700 text-sm">
                Only {scarcity.availability_percentage}% of slots available for the next 7 days.
                Consider adding more slots or releasing reserved ones.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
