import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Cpu, 
  Eye, 
  EyeOff, 
  AlertCircle, 
  Sparkles, 
  TrendingUp, 
  Brain, 
  Check, 
  Activity, 
  ShieldCheck, 
  Award,
  ArrowRight
} from 'lucide-react';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPwd, setShowPwd] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.email || !form.password) {
      setError('Please fill in all fields.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await login(form.email, form.password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0F] text-slate-100 flex flex-col lg:flex-row relative overflow-hidden font-sans">
      {/* Inject custom CSS keyframes for premium animations */}
      <style>{`
        @keyframes float-slow {
          0%, 100% { transform: translate3d(0, 0, 0) scale(1); }
          50% { transform: translate3d(20px, -30px, 0) scale(1.05); }
        }
        @keyframes float-medium {
          0%, 100% { transform: translate3d(0, 0, 0) scale(1.05); }
          50% { transform: translate3d(-30px, 20px, 0) scale(0.95); }
        }
        @keyframes core-pulse {
          0%, 100% { transform: scale(1); filter: drop-shadow(0 0 15px rgba(124, 58, 237, 0.3)); }
          50% { transform: scale(1.05); filter: drop-shadow(0 0 30px rgba(139, 92, 246, 0.6)); }
        }
        @keyframes orbital-spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .animate-float-slow {
          animation: float-slow 8s ease-in-out infinite;
        }
        .animate-float-medium {
          animation: float-medium 10s ease-in-out infinite;
        }
        .animate-core-pulse {
          animation: core-pulse 4s ease-in-out infinite;
        }
        .animate-orbital-spin {
          animation: orbital-spin 20s linear infinite;
        }
        .animate-orbital-spin-reverse {
          animation: orbital-spin 15s linear infinite reverse;
        }
      `}</style>

      {/* Background Layer: Grid and Gradient Orbs */}
      <div className="absolute inset-0 pointer-events-none z-0">
        {/* Visual grid backdrop */}
        <div 
          className="absolute inset-0 opacity-[0.03]" 
          style={{
            backgroundImage: `radial-gradient(circle at 1px 1px, white 1px, transparent 0)`,
            backgroundSize: '24px 24px'
          }}
        />
        {/* Soft Indigo Gradient Glow */}
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-indigo-600/10 blur-[120px] animate-float-slow" />
        {/* Soft Violet Gradient Glow */}
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-violet-600/10 blur-[120px] animate-float-medium" />
        {/* Subtle Blue Accent in Center */}
        <div className="absolute top-[35%] left-[30%] w-[40%] h-[40%] rounded-full bg-blue-500/5 blur-[100px]" />
      </div>

      {/* Left Column: Branding / Marketing (60% width) - Hidden on Mobile, shown on Large Screens */}
      <div className="hidden lg:flex lg:w-[60%] flex-col justify-between p-12 relative z-10 border-r border-white/5 bg-gradient-to-b from-transparent via-white/[0.01] to-transparent">


        {/* Hero & Centerpiece Section */}
        <div className="my-auto py-12 flex flex-col items-start gap-8">
          <div className="space-y-4">
            <h1 className="text-6xl md:text-7xl xl:text-8xl font-extrabold text-white tracking-tight leading-none">
              InterviewForge
              <span className="block bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">AI</span>
            </h1>
            <h2 className="text-2xl md:text-3xl font-semibold text-slate-300 mt-6 leading-tight max-w-lg">
              Prepare Smarter. Interview Better. Get Hired Faster.
            </h2>
            <p className="text-slate-400 text-base max-w-lg mt-4 leading-relaxed">
              Adaptive technical interviews powered by Gemini AI. Practice with resume-aware questioning, receive detailed grading, and master your weak areas.
            </p>
          </div>

          {/* Interactive Preview Cards Grid (2x2) */}
          <div className="grid grid-cols-2 gap-4 w-full max-w-xl">
            {/* Card 1: Interview Score */}
            <div className="p-4 rounded-2xl bg-white/5 border border-white/10 hover:border-white/20 transition-all hover:scale-[1.02] flex items-start gap-3 backdrop-blur-md">
              <div className="p-2 bg-emerald-500/10 rounded-lg text-emerald-400">
                <Award className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Interview Score</h4>
                <div className="flex items-baseline gap-1.5 mt-1">
                  <span className="text-xl font-bold text-white">8.4</span>
                  <span className="text-xs text-slate-400">/ 10</span>
                </div>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 mt-1 inline-block">
                  Strong Communication
                </span>
              </div>
            </div>

            {/* Card 2: Weak Topic Detection */}
            <div className="p-4 rounded-2xl bg-white/5 border border-white/10 hover:border-white/20 transition-all hover:scale-[1.02] flex items-start gap-3 backdrop-blur-md">
              <div className="p-2 bg-amber-500/10 rounded-lg text-amber-400">
                <Brain className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Weak Topic Focus</h4>
                <p className="text-sm font-bold text-white mt-1">DBMS Indexing</p>
                <div className="w-24 bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
                  <div className="bg-amber-500 h-full w-[42%]" />
                </div>
                <span className="text-[9px] text-slate-400 mt-1 block">42% average accuracy</span>
              </div>
            </div>

            {/* Card 3: Recent Performance */}
            <div className="p-4 rounded-2xl bg-white/5 border border-white/10 hover:border-white/20 transition-all hover:scale-[1.02] flex items-start gap-3 backdrop-blur-md">
              <div className="p-2 bg-blue-500/10 rounded-lg text-blue-400">
                <Activity className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Score Progression</h4>
                <p className="text-sm font-bold text-white mt-1">Steady Growth</p>
                <div className="flex items-center gap-1.5 mt-1.5 text-xs">
                  <span className="text-slate-500">6.2</span>
                  <ArrowRight className="w-3 h-3 text-slate-600" />
                  <span className="text-slate-400">7.5</span>
                  <ArrowRight className="w-3 h-3 text-slate-400" />
                  <span className="text-emerald-400 font-semibold">8.4</span>
                </div>
              </div>
            </div>

            {/* Card 4: AI Feedback Preview */}
            <div className="p-4 rounded-2xl bg-white/5 border border-white/10 hover:border-white/20 transition-all hover:scale-[1.02] flex items-start gap-3 backdrop-blur-md">
              <div className="p-2 bg-violet-500/10 rounded-lg text-violet-400">
                <Sparkles className="w-4 h-4" />
              </div>
              <div className="flex-1">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">AI feedback excerpt</h4>
                <p className="text-[10px] text-slate-300 italic mt-1.5 leading-snug">
                  "Explain indexing logic well. Expand on B-Tree structures."
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Miniature Dashboard Preview Widget */}
        <div className="w-full max-w-xl p-5 rounded-2xl bg-white/5 border border-white/10 flex flex-col gap-4 backdrop-blur-md">
          <div className="flex justify-between items-center">
            <span className="text-xs font-bold text-slate-300 tracking-wide uppercase">Performance Metrics</span>
            <div className="flex items-center gap-1 text-[10px] text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
              <TrendingUp className="w-3 h-3" />
              <span>+18% Overall</span>
            </div>
          </div>
          
          <div className="grid grid-cols-3 gap-3">
            <div className="p-3 bg-white/[0.02] border border-white/5 rounded-xl text-center">
              <span className="text-[10px] text-slate-400">Technical</span>
              <p className="text-lg font-extrabold text-white mt-0.5">88%</p>
            </div>
            <div className="p-3 bg-white/[0.02] border border-white/5 rounded-xl text-center">
              <span className="text-[10px] text-slate-400">Communication</span>
              <p className="text-lg font-extrabold text-white mt-0.5">92%</p>
            </div>
            <div className="p-3 bg-white/[0.02] border border-white/5 rounded-xl text-center">
              <span className="text-[10px] text-slate-400">Depth</span>
              <p className="text-lg font-extrabold text-white mt-0.5">79%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Floating Animated AI Core Visual (Visual bridge between panels, visible on lg) */}
      <div className="hidden lg:block absolute left-[58%] top-1/2 -translate-y-1/2 w-24 h-24 pointer-events-none z-20">
        <div className="relative w-full h-full flex items-center justify-center">
          {/* Outer Ring */}
          <div className="absolute inset-0 rounded-full border border-dashed border-violet-500/30 animate-orbital-spin" />
          {/* Middle Ring */}
          <div className="absolute inset-2 rounded-full border border-violet-400/20 animate-orbital-spin-reverse" />
          {/* Inner Glowing Core */}
          <div className="absolute inset-6 rounded-full bg-gradient-to-tr from-violet-600 to-indigo-600 opacity-80 blur-[2px] animate-core-pulse flex items-center justify-center shadow-lg shadow-violet-500/50">
            <Sparkles className="w-4 h-4 text-white animate-pulse" />
          </div>
        </div>
      </div>

      {/* Right Column: Authentication Panel (40% width on desktop, 100% on mobile) */}
      <div className="flex-1 lg:w-[40%] flex flex-col justify-center items-center p-6 sm:p-12 relative z-10">
        {/* Mobile Header (Hidden on large screens) */}
        <div className="flex lg:hidden flex-col items-center mb-6 w-full max-w-md text-center">
          <div className="flex items-center gap-2 mb-2">
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              InterviewForge <span className="bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">AI</span>
            </h1>
          </div>
          <h2 className="text-xl sm:text-2xl font-semibold text-slate-300 leading-tight">
            Prepare Smarter. Interview Better. Get Hired Faster.
          </h2>
          <p className="text-slate-400 text-xs mt-2 leading-relaxed">
            Adaptive AI technical preparation engine.
          </p>

          {/* Show exactly ONE interactive product-preview card above the form on Mobile */}
          <div className="mt-5 p-3 rounded-xl bg-white/5 border border-white/10 flex items-center gap-3 w-full text-left max-w-sm backdrop-blur-md">
            <div className="p-2 bg-violet-500/10 rounded-lg text-violet-400 flex-shrink-0">
              <Sparkles className="w-4 h-4" />
            </div>
            <div className="min-w-0 flex-1">
              <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">AI Feedback preview</h4>
              <p className="text-[11px] text-slate-200 italic leading-snug truncate">
                "Excellent database indexes description. Deepen algorithm explainers."
              </p>
            </div>
          </div>
        </div>

        {/* Premium Authentication Card */}
        <div className="w-full max-w-md backdrop-blur-xl bg-white/[0.03] border border-white/10 shadow-2xl rounded-3xl p-6 sm:p-8 flex flex-col gap-6 relative overflow-hidden group">
          {/* Soft inner glow card accent */}
          <div className="absolute -top-24 -left-24 w-48 h-48 rounded-full bg-violet-500/10 blur-[60px] pointer-events-none group-hover:bg-violet-500/15 transition-colors duration-500" />
          
          <div className="text-center sm:text-left">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Welcome Back</h1>
            <p className="text-slate-400 text-sm mt-1.5 leading-relaxed">
              Continue your interview preparation journey.
            </p>
          </div>

          {/* Error Message Display */}
          {error && (
            <div className="flex items-start gap-2.5 p-3.5 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm animate-shake">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span className="leading-snug">{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            {/* Email Field */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider" htmlFor="email">
                Email Address
              </label>
              <div className="relative group/input">
                <input
                  id="email"
                  type="email"
                  name="email"
                  value={form.email}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-white/[0.02] border border-white/10 rounded-xl text-white text-sm placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500 transition-all duration-300 hover:bg-white/[0.04] hover:border-white/20"
                  placeholder="name@domain.com"
                  autoComplete="email"
                  required
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="flex flex-col gap-1.5">
              <div className="flex justify-between items-center">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider" htmlFor="password">
                  Password
                </label>
                <a href="#forgot" className="text-xs text-violet-400 hover:text-violet-300 transition-colors">
                  Forgot?
                </a>
              </div>
              <div className="relative group/input">
                <input
                  id="password"
                  type={showPwd ? 'text' : 'password'}
                  name="password"
                  value={form.password}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-white/[0.02] border border-white/10 rounded-xl text-white text-sm placeholder-slate-600 pr-11 focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500 transition-all duration-300 hover:bg-white/[0.04] hover:border-white/20"
                  placeholder="••••••••"
                  autoComplete="current-password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPwd(!showPwd)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors p-1"
                  aria-label={showPwd ? "Hide password" : "Show password"}
                >
                  {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Remember me Checkbox */}
            <div className="flex items-center gap-2 mt-1">
              <input
                id="remember"
                type="checkbox"
                className="w-4 h-4 bg-white/5 border border-white/10 rounded text-violet-600 focus:ring-violet-500 focus:ring-offset-[#0A0A0F]"
              />
              <label htmlFor="remember" className="text-xs text-slate-400 select-none cursor-pointer hover:text-slate-300 transition-colors">
                Remember my session on this device
              </label>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full mt-4 py-3.5 px-4 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 active:from-violet-700 active:to-indigo-700 text-white text-sm font-semibold rounded-xl transition-all duration-300 shadow-lg shadow-violet-500/25 hover:shadow-violet-500/35 hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed disabled:scale-100 flex items-center justify-center gap-2"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Signing in...
                </span>
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                </>
              )}
            </button>
          </form>

          <div className="border-t border-white/5 pt-5 text-center">
            <p className="text-slate-500 text-sm">
              Don&apos;t have an account?{' '}
              <Link to="/register" className="text-violet-400 hover:text-violet-300 font-semibold transition-colors">
                Create one
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

