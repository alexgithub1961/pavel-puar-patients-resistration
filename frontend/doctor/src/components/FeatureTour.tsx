import { useState } from 'react';
import { X, ChevronRight, Calendar, Users, Clock, AlertTriangle, BarChart3, Sparkles } from 'lucide-react';

interface FeatureTourProps {
  onClose: () => void;
}

interface Feature {
  icon: React.ReactNode;
  title: string;
  description: string;
  tryIt: string;
  path?: string;
}

const features: Feature[] = [
  {
    icon: <Clock className="w-6 h-6" />,
    title: 'Slot Management',
    description: 'Create and manage appointment slots. Define your availability and let patients self-book into your schedule.',
    tryIt: 'Go to "Manage Slots" to create individual slots or use bulk creation for recurring schedules.',
    path: '/slots',
  },
  {
    icon: <Calendar className="w-6 h-6" />,
    title: 'Appointment Overview',
    description: 'View all bookings in one place. See today\'s schedule, upcoming appointments, and booking history.',
    tryIt: 'Check "Appointments" to see your daily schedule and patient details.',
    path: '/bookings',
  },
  {
    icon: <Users className="w-6 h-6" />,
    title: 'Patient Categories',
    description: 'Patients are categorised by health status: Critical, High Risk, Moderate, Stable, Maintenance, and Healthy.',
    tryIt: 'View "Patients" to see categories and how they affect booking frequency.',
    path: '/patients',
  },
  {
    icon: <BarChart3 className="w-6 h-6" />,
    title: 'Compliance Tracking',
    description: 'Monitor patient compliance scores (Platinum to Probation). Higher compliance means better slot access.',
    tryIt: 'In the Patients list, check compliance levels to understand patient discipline.',
  },
  {
    icon: <AlertTriangle className="w-6 h-6" />,
    title: 'Scarcity Management',
    description: 'When slots are scarce, the system fairly prioritises patients. Monitor scarcity levels on your dashboard.',
    tryIt: 'Check the dashboard for scarcity alerts and consider adding more slots when needed.',
    path: '/dashboard',
  },
];

export default function FeatureTour({ onClose }: FeatureTourProps) {
  const [currentFeature, setCurrentFeature] = useState(0);

  const handleNext = () => {
    if (currentFeature < features.length - 1) {
      setCurrentFeature(currentFeature + 1);
    } else {
      onClose();
    }
  };

  const feature = features[currentFeature];

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-emerald-600 to-emerald-700 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-white">
              <Sparkles className="w-5 h-5" />
              <h2 className="text-lg font-semibold">Doctor Portal Tour</h2>
            </div>
            <button
              onClick={onClose}
              className="text-white/80 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          <p className="text-emerald-100 text-sm mt-1">
            Discover what you can do in the doctor portal
          </p>
        </div>

        {/* Progress */}
        <div className="flex gap-1 px-6 pt-4">
          {features.map((_, idx) => (
            <button
              key={idx}
              onClick={() => setCurrentFeature(idx)}
              className={`h-1.5 flex-1 rounded-full transition-colors ${
                idx === currentFeature
                  ? 'bg-emerald-600'
                  : idx < currentFeature
                  ? 'bg-emerald-300'
                  : 'bg-gray-200'
              }`}
            />
          ))}
        </div>

        {/* Feature Content */}
        <div className="p-6">
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center text-emerald-600">
              {feature.icon}
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900">
                {feature.title}
              </h3>
              <p className="text-gray-600 mt-2 text-sm leading-relaxed">
                {feature.description}
              </p>
              <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                <p className="text-amber-800 text-sm font-medium">
                  Try it:
                </p>
                <p className="text-amber-700 text-sm">
                  {feature.tryIt}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 flex items-center justify-between">
          <span className="text-sm text-gray-500">
            {currentFeature + 1} / {features.length}
          </span>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 text-sm font-medium"
            >
              Skip
            </button>
            <button
              onClick={handleNext}
              className="flex items-center gap-1 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 text-sm font-medium"
            >
              {currentFeature < features.length - 1 ? (
                <>
                  Next
                  <ChevronRight className="w-4 h-4" />
                </>
              ) : (
                'Start Exploring'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
