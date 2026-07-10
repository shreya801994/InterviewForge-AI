import { Link } from 'react-router-dom';
import { Cpu, Home } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gray-950 flex flex-col items-center justify-center p-4 text-center">
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-900/20 via-gray-950 to-violet-900/20 pointer-events-none" />
      <div className="relative">
        <div className="p-3 bg-indigo-600 rounded-xl mb-6 inline-flex shadow-lg shadow-indigo-500/30">
          <Cpu className="w-7 h-7 text-white" />
        </div>
        <h1 className="text-8xl font-black text-white mb-3 bg-gradient-to-br from-indigo-400 to-violet-400 bg-clip-text text-transparent">
          404
        </h1>
        <h2 className="text-2xl font-bold text-white mb-2">Page Not Found</h2>
        <p className="text-gray-400 mb-8 max-w-sm">
          The page you&apos;re looking for doesn&apos;t exist or has been moved.
        </p>
        <Link to="/dashboard" className="btn-primary">
          <Home className="w-4 h-4" />
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
}
