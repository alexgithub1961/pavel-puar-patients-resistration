import { X, Lightbulb } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import { t } from '../i18n/translations';

interface DemoHintProps {
  id: string;
  titleKey: string;
  descriptionKey: string;
  className?: string;
}

export default function DemoHint({ id, titleKey, descriptionKey, className = '' }: DemoHintProps) {
  const { isDemoMode, language } = useAuthStore();
  const [isDismissed, setIsDismissed] = useState(false);

  // Check localStorage for previously dismissed hints
  useEffect(() => {
    const dismissed = localStorage.getItem(`demo-hint-dismissed-${id}`);
    if (dismissed === 'true') {
      setIsDismissed(true);
    }
  }, [id]);

  const handleDismiss = () => {
    setIsDismissed(true);
    localStorage.setItem(`demo-hint-dismissed-${id}`, 'true');
  };

  if (!isDemoMode || isDismissed) {
    return null;
  }

  return (
    <div className={`bg-amber-50 border border-amber-200 rounded-lg p-4 ${className}`}>
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <div className="w-8 h-8 bg-amber-200 rounded-full flex items-center justify-center">
            <Lightbulb className="w-4 h-4 text-amber-700" />
          </div>
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div>
              <h4 className="text-sm font-semibold text-amber-900">
                {t(titleKey, language)}
              </h4>
              <p className="text-sm text-amber-700 mt-1">
                {t(descriptionKey, language)}
              </p>
            </div>
            <button
              onClick={handleDismiss}
              className="flex-shrink-0 p-1 text-amber-500 hover:text-amber-700 hover:bg-amber-100 rounded transition-colors"
              aria-label="Dismiss hint"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
