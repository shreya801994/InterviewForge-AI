import { useState, useRef, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { BellRing } from 'lucide-react';

export default function Navbar({ title }) {
  const { user } = useAuth();
  const [showNotifications, setShowNotifications] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowNotifications(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <header className="h-16 bg-gray-900 border-b border-gray-800 flex items-center justify-between px-6 flex-shrink-0">
      <h2 className="text-white font-semibold text-lg">{title}</h2>
      <div className="flex items-center gap-4">
        <div className="relative" ref={dropdownRef}>
          <button 
            onClick={() => setShowNotifications(!showNotifications)}
            className={`p-2 rounded-lg transition-colors ${showNotifications ? 'bg-gray-800 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800'}`}
          >
            <BellRing className="w-4 h-4" />
          </button>
          
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-64 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50 animate-slide-up origin-top-right">
              <div className="px-4 py-3 border-b border-gray-700">
                <h3 className="text-sm font-semibold text-white">Notifications</h3>
              </div>
              <div className="p-6 text-center">
                <p className="text-sm text-gray-400">No notifications yet</p>
              </div>
            </div>
          )}
        </div>
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-white text-xs font-bold">
            {user?.name?.[0]?.toUpperCase() ?? 'U'}
          </div>
          <span className="text-gray-300 text-sm font-medium hidden sm:block">{user?.name}</span>
        </div>
      </div>
    </header>
  );
}
