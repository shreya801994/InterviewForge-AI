import { useState, useEffect } from 'react';
import { AlertCircle, X } from 'lucide-react';

export default function GlobalNetworkBanner() {
  const [show, setShow] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const handleNetworkError = (e) => {
      setMessage(e.detail || 'AI is currently busy or has reached its usage limit — please try again in a moment.');
      setShow(true);
      // Auto-hide after 8 seconds
      setTimeout(() => setShow(false), 8000);
    };

    window.addEventListener('network-quota-error', handleNetworkError);
    return () => window.removeEventListener('network-quota-error', handleNetworkError);
  }, []);

  if (!show) return null;

  return (
    <div className="fixed top-4 left-1/2 -translate-x-1/2 z-[9999] animate-slide-down w-full max-w-md px-4">
      <div className="bg-amber-500/10 border border-amber-500/30 backdrop-blur-xl rounded-2xl p-4 shadow-2xl shadow-amber-500/10 flex items-start gap-3">
        <div className="p-2 bg-amber-500/20 rounded-lg shrink-0 mt-0.5">
          <AlertCircle className="w-5 h-5 text-amber-400" />
        </div>
        <div className="flex-1">
          <h4 className="text-amber-400 font-bold text-sm">Service Temporarily Unavailable</h4>
          <p className="text-amber-200/80 text-xs mt-1 leading-relaxed">
            {message}
          </p>
        </div>
        <button 
          onClick={() => setShow(false)}
          className="p-1.5 hover:bg-white/5 rounded-lg text-amber-400/70 hover:text-amber-400 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
