import { useQuery } from '@tanstack/react-query';
import { User } from 'lucide-react';
import { doctorApi } from '../api/client';

export default function PatientsPage() {
  const { data: patients, isLoading } = useQuery({
    queryKey: ['patients'],
    queryFn: async () => {
      const response = await doctorApi.getPatients({ page_size: 100 });
      return response.data;
    },
  });

  const getComplianceColor = (level: string) => {
    switch (level) {
      case 'platinum':
        return 'bg-purple-100 text-purple-800';
      case 'gold':
        return 'bg-yellow-100 text-yellow-800';
      case 'silver':
        return 'bg-gray-100 text-gray-800';
      case 'bronze':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-red-100 text-red-800';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'critical':
        return 'text-red-600';
      case 'high_risk':
        return 'text-orange-600';
      case 'moderate':
        return 'text-yellow-600';
      default:
        return 'text-green-600';
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Patients</h1>

      {isLoading ? (
        <p className="text-gray-500 py-8 text-center">Loading...</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {patients?.items?.map((patient: {
            id: string;
            first_name: string;
            last_name: string;
            category: string;
            compliance_level: string;
            compliance_score: number;
            total_appointments: number;
            no_shows: number;
            late_cancellations: number;
          }) => (
            <div key={patient.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center">
                  <User className="w-6 h-6 text-emerald-600" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">
                    {patient.first_name} {patient.last_name}
                  </h3>
                  <p className={`text-sm capitalize ${getCategoryColor(patient.category)}`}>
                    {patient.category.replace('_', ' ')}
                  </p>
                </div>
                <span
                  className={`px-2 py-1 rounded-full text-xs font-medium ${getComplianceColor(
                    patient.compliance_level
                  )}`}
                >
                  {patient.compliance_level}
                </span>
              </div>

              <div className="mt-4 grid grid-cols-3 gap-4 text-center border-t pt-4">
                <div>
                  <p className="text-2xl font-bold text-gray-900">
                    {patient.compliance_score}
                  </p>
                  <p className="text-xs text-gray-500">Score</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">
                    {patient.total_appointments}
                  </p>
                  <p className="text-xs text-gray-500">Visits</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-red-600">
                    {patient.no_shows}
                  </p>
                  <p className="text-xs text-gray-500">No-shows</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {(!patients?.items || patients.items.length === 0) && !isLoading && (
        <div className="text-center py-12">
          <User className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">No patients found</p>
        </div>
      )}
    </div>
  );
}
