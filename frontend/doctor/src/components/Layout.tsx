import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { Home, Calendar, Clock, Users, LogOut } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import DemoBanner from './DemoBanner';

export default function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { doctor, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/dashboard', icon: Home, label: 'Dashboard' },
    { path: '/slots', icon: Clock, label: 'Manage Slots' },
    { path: '/bookings', icon: Calendar, label: 'Appointments' },
    { path: '/patients', icon: Users, label: 'Patients' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 w-64 bg-emerald-800 text-white hidden md:block">
        <div className="p-6">
          <h1 className="text-xl font-bold">PUAR Doctor</h1>
          <p className="text-emerald-200 text-sm mt-1">Management Portal</p>
        </div>

        <nav className="mt-6">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-6 py-3 ${
                  isActive
                    ? 'bg-emerald-900 border-l-4 border-white'
                    : 'hover:bg-emerald-700'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-6 border-t border-emerald-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">{doctor?.firstName} {doctor?.lastName}</p>
              <p className="text-sm text-emerald-200">{doctor?.specialisation || 'Doctor'}</p>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 hover:bg-emerald-700 rounded"
              title="Logout"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="md:ml-64 min-h-screen">
        {/* Demo Mode Banner */}
        <DemoBanner />

        <header className="bg-white shadow-sm sticky top-0 z-10">
          <div className="px-6 py-4">
            <h2 className="text-lg font-semibold text-gray-900">
              {navItems.find((item) => item.path === location.pathname)?.label || 'Dashboard'}
            </h2>
          </div>
        </header>

        <div className="p-6">
          <Outlet />
        </div>
      </main>

      {/* Mobile Navigation */}
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
                  isActive ? 'text-emerald-600' : 'text-gray-600'
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
