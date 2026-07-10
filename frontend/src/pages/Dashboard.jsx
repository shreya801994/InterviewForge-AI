import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import client from '../api/client';
import MetricCard from '../components/MetricCard';
import {
  BarChart3, Play, TrendingUp, TrendingDown, Trophy, Target, Calendar, ChevronRight
} from 'lucide-react';

const TopicBadge = ({ topic, score, type }) => {
  const colors = type === 'strong'
    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
    : 'bg-rose-500/10 border-rose-500/30 text-rose-400';
  return (
    <div className={`flex items-center justify-between px-3 py-2 rounded-lg border ${colors} text-sm`}>
      <span className="font-medium">{topic}</span>
      <span className="font-bold">{typeof score === 'number' ? score.toFixed(1) : score}%</span>
    </div>
  );
};

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm shadow-xl">
      <p className="text-gray-400 mb-1">Attempt {label}</p>
      <p className="text-indigo-400 font-semibold">{payload[0].value.toFixed(1)}%</p>
    </div>
  );
};

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const [statsRes, histRes] = await Promise.all([
          client.get('/api/dashboard/stats'),
          client.get('/api/dashboard/history'),
        ]);
        setStats(statsRes.data);
        setHistory(histRes.data);
      } catch {
        setError('Failed to load dashboard data.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-16">
        <p className="text-red-400">{error}</p>
      </div>
    );
  }

  const hasData = stats?.total_interviews > 0;

  return (
    <div className="space-y-6 animate-slide-up max-w-7xl mx-auto">
      {/* Metrics row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Interviews"
          value={stats?.total_interviews ?? 0}
          icon={BarChart3}
          subtitle="Completed sessions"
          accent="indigo"
        />
        <MetricCard
          title="Average Score"
          value={`${stats?.average_score?.toFixed(1) ?? '0.0'}%`}
          icon={Target}
          subtitle="Across all sessions"
          accent="violet"
        />
        <MetricCard
          title="Latest Score"
          value={`${stats?.latest_score?.toFixed(1) ?? '0.0'}%`}
          icon={TrendingUp}
          subtitle="Most recent interview"
          accent="emerald"
        />
        <MetricCard
          title="Topics Tracked"
          value={(stats?.strong_topics?.length ?? 0) + (stats?.weak_topics?.length ?? 0)}
          icon={Trophy}
          subtitle="Skill categories"
          accent="amber"
        />
      </div>

      {hasData ? (
        <>
          {/* Score trend + Topics */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Score Trend */}
            <div className="lg:col-span-2 card">
              <div className="flex items-center justify-between mb-5">
                <h3 className="text-white font-semibold">Score Trend</h3>
                <span className="text-xs text-gray-500">{stats.score_trend.length} attempts</span>
              </div>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={stats.score_trend}>
                  <defs>
                    <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                  <XAxis dataKey="attempt" stroke="#4b5563" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                  <YAxis domain={[0, 100]} stroke="#4b5563" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Line
                    type="monotone"
                    dataKey="score"
                    stroke="#6366f1"
                    strokeWidth={2.5}
                    dot={{ fill: '#6366f1', r: 4, strokeWidth: 0 }}
                    activeDot={{ r: 6, fill: '#818cf8' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Topics */}
            <div className="card space-y-4">
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <TrendingUp className="w-4 h-4 text-emerald-400" />
                  <h3 className="text-white font-semibold text-sm">Strong Topics</h3>
                </div>
                <div className="space-y-2">
                  {stats.strong_topics?.slice(0, 3).map(({ topic, score }) => (
                    <TopicBadge key={topic} topic={topic} score={score} type="strong" />
                  ))}
                  {(!stats.strong_topics?.length) && <p className="text-gray-600 text-xs">None yet</p>}
                </div>
              </div>
              <hr className="border-gray-800" />
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <TrendingDown className="w-4 h-4 text-rose-400" />
                  <h3 className="text-white font-semibold text-sm">Weak Topics</h3>
                </div>
                <div className="space-y-2">
                  {stats.weak_topics?.slice(0, 3).map(({ topic, score }) => (
                    <TopicBadge key={topic} topic={topic} score={score} type="weak" />
                  ))}
                  {(!stats.weak_topics?.length) && <p className="text-gray-600 text-xs">None yet</p>}
                </div>
              </div>
            </div>
          </div>

          {/* Interview History */}
          <div className="card">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-white font-semibold">Interview History</h3>
              <Link to="/interview/setup" className="btn-secondary text-xs">
                <Play className="w-3 h-3" /> New Interview
              </Link>
            </div>
            <div className="space-y-2">
              {history.slice(0, 5).map((session) => (
                <Link
                  key={session.id}
                  to={`/report/${session.id}`}
                  className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition-colors group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-indigo-600/20 flex items-center justify-center flex-shrink-0">
                      <Calendar className="w-4 h-4 text-indigo-400" />
                    </div>
                    <div>
                      <p className="text-white text-sm font-medium">{session.role}</p>
                      <p className="text-gray-500 text-xs">{session.difficulty} · {session.date ? new Date(session.date).toLocaleDateString() : '—'}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-sm font-bold ${session.score >= 70 ? 'text-emerald-400' : session.score >= 50 ? 'text-amber-400' : 'text-rose-400'}`}>
                      {session.score?.toFixed(1)}%
                    </span>
                    <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-gray-400 transition-colors" />
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </>
      ) : (
        /* Empty state */
        <div className="card text-center py-16">
          <div className="w-16 h-16 rounded-2xl bg-indigo-600/10 flex items-center justify-center mx-auto mb-4">
            <Play className="w-7 h-7 text-indigo-400" />
          </div>
          <h3 className="text-white font-semibold text-lg mb-2">No interviews yet</h3>
          <p className="text-gray-400 text-sm mb-6">Complete your first interview to start tracking your progress.</p>
          <Link to="/interview/setup" className="btn-primary inline-flex">
            Start Your First Interview
          </Link>
        </div>
      )}
    </div>
  );
}
