import { Play, X } from 'lucide-react';
import { useState } from 'react';
import { useAuthStore } from '../store/authStore';

export default function DemoBanner() {
  const { isDemoMode } = useAuthStore();
  const [isDismissed, setIsDismissed] = useState(false);

  if (!isDemoMode || isDismissed) {
    return null;
  }

  return (
    <div className="bg-gradient-to-r from-amber-500 to-orange-500 text-white px-4 py-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Play className="w-4 h-4" />
          <span className="text-sm font-medium">
            DEMO MODE
          </span>
          <span className="text-xs opacity-80 hidden sm:inline">
            — Explore all features with sample data
          </span>
        </div>
        <button
          onClick={() => setIsDismissed(true)}
          className="p-1 hover:bg-white/20 rounded transition-colors"
          aria-label="Dismiss demo banner"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
