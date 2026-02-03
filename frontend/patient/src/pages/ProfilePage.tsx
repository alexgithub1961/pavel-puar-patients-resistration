import { useAuthStore } from '../store/authStore';
import { t } from '../i18n/translations';

export default function ProfilePage() {
  const { user, language } = useAuthStore();

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">{t('profile.title', language)}</h1>

      {/* Personal Information */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          {t('profile.personalInfo', language)}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-gray-600">
              {t('auth.firstName', language)}
            </label>
            <p className="font-medium">{user?.firstName}</p>
          </div>
          <div>
            <label className="block text-sm text-gray-600">
              {t('auth.lastName', language)}
            </label>
            <p className="font-medium">{user?.lastName}</p>
          </div>
          <div>
            <label className="block text-sm text-gray-600">
              {t('auth.email', language)}
            </label>
            <p className="font-medium">{user?.email}</p>
          </div>
        </div>
      </div>

      {/* Medical Information */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          {t('profile.medicalInfo', language)}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-gray-600">
              {t('dashboard.category', language)}
            </label>
            <p className="font-medium capitalize">{user?.category?.replace('_', ' ')}</p>
          </div>
        </div>
      </div>

      {/* Compliance Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          {t('profile.compliance', language)}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-gray-600">
              {t('dashboard.complianceScore', language)}
            </label>
            <div className="flex items-center gap-2">
              <div className="w-24 h-3 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary-600 rounded-full"
                  style={{ width: `${user?.complianceScore || 0}%` }}
                />
              </div>
              <span className="font-medium">{user?.complianceScore || 0}/100</span>
            </div>
          </div>
          <div>
            <label className="block text-sm text-gray-600">Level</label>
            <span
              className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
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
      </div>
    </div>
  );
}
