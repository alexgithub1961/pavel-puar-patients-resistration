import { useState } from 'react';
import { X, ChevronRight, Calendar, TrendingUp, FileQuestion, Clock, AlertTriangle, Sparkles } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { t } from '../i18n/translations';

interface FeatureTourProps {
  onClose: () => void;
}

interface Feature {
  icon: React.ReactNode;
  titleKey: string;
  descKey: string;
  tryItKey: string;
  path?: string;
}

const features: Feature[] = [
  {
    icon: <Calendar className="w-6 h-6" />,
    titleKey: 'tour.feature.booking.title',
    descKey: 'tour.feature.booking.desc',
    tryItKey: 'tour.feature.booking.try',
    path: '/book',
  },
  {
    icon: <TrendingUp className="w-6 h-6" />,
    titleKey: 'tour.feature.compliance.title',
    descKey: 'tour.feature.compliance.desc',
    tryItKey: 'tour.feature.compliance.try',
    path: '/compliance',
  },
  {
    icon: <FileQuestion className="w-6 h-6" />,
    titleKey: 'tour.feature.triage.title',
    descKey: 'tour.feature.triage.desc',
    tryItKey: 'tour.feature.triage.try',
  },
  {
    icon: <Clock className="w-6 h-6" />,
    titleKey: 'tour.feature.frequency.title',
    descKey: 'tour.feature.frequency.desc',
    tryItKey: 'tour.feature.frequency.try',
    path: '/dashboard',
  },
  {
    icon: <AlertTriangle className="w-6 h-6" />,
    titleKey: 'tour.feature.priority.title',
    descKey: 'tour.feature.priority.desc',
    tryItKey: 'tour.feature.priority.try',
  },
];

export default function FeatureTour({ onClose }: FeatureTourProps) {
  const { language } = useAuthStore();
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
        <div className="bg-gradient-to-r from-primary-600 to-primary-700 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-white">
              <Sparkles className="w-5 h-5" />
              <h2 className="text-lg font-semibold">{t('tour.title', language)}</h2>
            </div>
            <button
              onClick={onClose}
              className="text-white/80 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          <p className="text-primary-100 text-sm mt-1">
            {t('tour.subtitle', language)}
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
                  ? 'bg-primary-600'
                  : idx < currentFeature
                  ? 'bg-primary-300'
                  : 'bg-gray-200'
              }`}
            />
          ))}
        </div>

        {/* Feature Content */}
        <div className="p-6">
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center text-primary-600">
              {feature.icon}
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900">
                {t(feature.titleKey, language)}
              </h3>
              <p className="text-gray-600 mt-2 text-sm leading-relaxed">
                {t(feature.descKey, language)}
              </p>
              <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                <p className="text-amber-800 text-sm font-medium">
                  {t('tour.tryIt', language)}
                </p>
                <p className="text-amber-700 text-sm">
                  {t(feature.tryItKey, language)}
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
              {t('tour.skip', language)}
            </button>
            <button
              onClick={handleNext}
              className="flex items-center gap-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-sm font-medium"
            >
              {currentFeature < features.length - 1 ? (
                <>
                  {t('tour.next', language)}
                  <ChevronRight className="w-4 h-4" />
                </>
              ) : (
                t('tour.start', language)
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
