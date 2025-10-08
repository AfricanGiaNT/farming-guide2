import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, Cloud, Sprout, Search, Database, Shield } from 'lucide-react';

const Navigation: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: Home, label: 'Home' },
    { path: '/weather', icon: Cloud, label: 'Weather' },
    { path: '/crops', icon: Sprout, label: 'Crops' },
    { path: '/varieties', icon: Database, label: 'Varieties' },
    { path: '/search', icon: Search, label: 'Search' },
    { path: '/admin/varieties', icon: Shield, label: 'Admin' }
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <>
      {/* Mobile Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 md:hidden z-50">
        <div className="flex justify-around py-2">
          {navItems.map(({ path, icon: Icon, label }) => (
            <Link
              key={path}
              to={path}
              className={`flex flex-col items-center py-2 px-3 min-w-[60px] transition-colors ${
                isActive(path)
                  ? 'text-green-600'
                  : 'text-gray-500 hover:text-green-500'
              }`}
            >
              <Icon size={20} />
              <span className="text-xs mt-1 font-medium">{label}</span>
            </Link>
          ))}
        </div>
      </nav>

      {/* Desktop Sidebar */}
      <nav className="hidden md:flex md:flex-col md:w-64 md:min-h-screen md:bg-white md:border-r md:border-gray-200 md:fixed md:left-0 md:top-0 z-40">
        <div className="p-6">
          <h1 className="text-xl font-bold text-green-600 flex items-center gap-2">
            <Sprout size={24} />
            Mlangizi wa Ulimi
          </h1>
          <p className="text-sm text-gray-600 mt-1">Agricultural Advisory</p>
        </div>
        
        <div className="flex-1 px-4">
          {navItems.map(({ path, icon: Icon, label }) => (
            <Link
              key={path}
              to={path}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg mb-1 transition-colors ${
                isActive(path)
                  ? 'bg-green-50 text-green-700 font-medium'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <Icon size={20} />
              <span>{label}</span>
            </Link>
          ))}
        </div>
      </nav>
    </>
  );
};

export default Navigation;
