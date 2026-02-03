import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { Home, Calendar, Plus, User, LogOut, Globe } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { t, isRTL, type Language } from '../i18n/translations';
import DemoBanner from './DemoBanner';

export default function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, language, setLanguage, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleLanguageChange = (lang: Language) => {
    setLanguage(lang);
    document.documentElement.dir = isRTL(lang) ? 'rtl' : 'ltr';
  };

  const navItems = [
    { path: '/dashboard', icon: Home, label: t('nav.home', language) },
    { path: '/bookings', icon: Calendar, label: t('nav.bookings', language) },
    { path: '/book', icon: Plus, label: t('nav.book', language) },
    { path: '/profile', icon: User, label: t('nav.profile', language) },
  ];

  return (
    <div className="min-h-screen bg-gray-50" dir={isRTL(language) ? 'rtl' : 'ltr'}>
      {/* Demo Mode Banner */}
      <DemoBanner />

      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold text-primary-600">
                {t('app.name', language)}
              </span>
            </div>

            <div className="flex items-center gap-4">
              {/* Language Selector */}
              <div className="relative group">
                <button className="flex items-center gap-1 text-gray-600 hover:text-gray-900">
                  <Globe className="w-5 h-5" />
                </button>
                <div className="absolute right-0 mt-2 w-24 bg-white rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                  {(['en', 'he', 'ru'] as Language[]).map((lang) => (
                    <button
                      key={lang}
                      onClick={() => handleLanguageChange(lang)}
                      className={`block w-full px-4 py-2 text-sm text-left hover:bg-gray-100 ${
                        language === lang ? 'bg-primary-50 text-primary-600' : ''
                      }`}
                    >
                      {lang === 'en' ? 'English' : lang === 'he' ? 'עברית' : 'Русский'}
                    </button>
                  ))}
                </div>
              </div>

              {/* User Info */}
              <span className="text-sm text-gray-600">
                {user?.firstName} {user?.lastName}
              </span>

              {/* Logout */}
              <button
                onClick={handleLogout}
                className="text-gray-600 hover:text-gray-900"
                title={t('nav.logout', language)}
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>

      {/* Bottom Navigation (Mobile) */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t md:hidden">
        <div className="flex justify-around">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex flex-col items-center py-2 px-4 ${
                  isActive ? 'text-primary-600' : 'text-gray-600'
                }`}
              >
                <Icon className="w-6 h-6" />
                <span className="text-xs mt-1">{item.label}</span>
              </Link>
            );
          })}
        </div>
      </nav>
    </div>
  );
}
