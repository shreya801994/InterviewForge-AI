import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer
} from 'recharts';
import client from '../api/client';
import {
  Trophy, TrendingUp, AlertTriangle, MapPin, Loader2, AlertCircle, ChevronLeft
} from 'lucide-react';

const ScoreMeter = ({ score }) => {
  const pct = Math.min(Math.max(score, 0), 100);
  const color = pct >= 70 ? '#10b981' : pct >= 50 ? '#f59e0b' : '#ef4444';
  const dashLen = 220;
  const dashOffset = dashLen - (dashLen * pct) / 100;

  return (
    <div className="flex flex-col items-center">
      <svg width="140" height="80" viewBox="0 0 140 80">
        <path
          d="M 10 70 A 60 60 0 0 1 130 70"
          fill="none" stroke="#1f2937" strokeWidth="12" strokeLinecap="round"
        />
        <path
          d="M 10 70 A 60 60 0 0 1 130 70"
          fill="none" stroke={color} strokeWidth="12" strokeLinecap="round"
          strokeDasharray={dashLen}
          strokeDashoffset={dashOffset}
          style={{ transition: 'stroke-dashoffset 1s ease-out' }}
        />
      </svg>
      <div className="-mt-6 text-center">
        <p className="text-4xl font-black text-white">{pct.toFixed(1)}</p>
        <p className="text-gray-500 text-xs">out of 100</p>
      </div>
    </div>
  );
};

export default function ReportDetails() {
  const { sessionId } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await client.get(`/api/dashboard/report/${sessionId}`);
        setReport(data);
      } catch {
        setError('Report not found or not yet generated.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [sessionId]);

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
    </div>
  );

  if (error) return (
    <div className="text-center py-16">
      <AlertCircle className="w-10 h-10 text-red-400 mx-auto mb-3" />
      <p className="text-red-400 mb-4">{error}</p>
      <Link to="/dashboard" className="btn-secondary">Back to Dashboard</Link>
    </div>
  );

  const radarData = [
    { subject: 'Technical', value: report.overall_score ?? 0 },
    { subject: 'Depth', value: (report.overall_score ?? 0) * 0.9 },
    { subject: 'Communication', value: (report.overall_score ?? 0) * 0.95 },
    { subject: 'Problem Solving', value: (report.overall_score ?? 0) * 0.85 },
    { subject: 'Completeness', value: (report.overall_score ?? 0) * 0.92 },
  ];

  return (
    <div className="max-w-5xl mx-auto animate-slide-up space-y-6">
      {/* Back + header */}
      <div className="flex items-center gap-3">
        <Link to="/dashboard" className="text-gray-400 hover:text-white transition-colors">
          <ChevronLeft className="w-5 h-5" />
        </Link>
        <div>
          <h2 className="text-xl font-bold text-white">{report.role}</h2>
          <p className="text-gray-400 text-sm">{report.difficulty} Interview Report</p>
        </div>
      </div>

      {/* Score + Radar */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card flex flex-col items-center justify-center py-6">
          <p className="text-gray-400 text-sm mb-4">Overall Score</p>
          <ScoreMeter score={report.overall_score} />
        </div>

        <div className="card">
          <p className="text-gray-400 text-sm mb-2 font-medium">Performance Breakdown</p>
          <ResponsiveContainer width="100%" height={180}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#1f2937" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: '#9ca3af', fontSize: 11 }} />
              <Radar
                name="Score"
                dataKey="value"
                stroke="#6366f1"
                fill="#6366f1"
                fillOpacity={0.25}
                strokeWidth={2}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Summary */}
      <div className="card">
        <div className="flex items-center gap-2 mb-3">
          <Trophy className="w-4 h-4 text-amber-400" />
          <h3 className="text-white font-semibold">Interview Summary</h3>
        </div>
        <p className="text-gray-300 text-sm leading-relaxed">{report.summary || 'No summary available.'}</p>
      </div>

      {/* ATS & Consistency Analysis */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* ATS Score Card */}
        {(report.ats_readiness_score !== null && report.ats_readiness_score !== undefined) && (
          <div className="card relative overflow-hidden bg-gradient-to-br from-gray-900 to-indigo-900/10 border-indigo-500/20">
            <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full blur-[40px]" />
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-4 h-4 text-indigo-400" />
              <h3 className="text-white font-semibold">ATS Readiness Score</h3>
            </div>
            <div className="flex items-end gap-3 mt-4">
              <span className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-violet-400">
                {report.ats_readiness_score}
              </span>
              <span className="text-gray-500 text-sm mb-1.5">/ 100</span>
            </div>
            <p className="text-indigo-200/60 text-[10px] mt-4 uppercase tracking-wider font-semibold border-t border-indigo-500/10 pt-3">
              Note: This is a heuristic estimate based on keyword density and formatting, not a guarantee of ATS parsing success.
            </p>
          </div>
        )}

        {/* Consistency Feedback */}
        {report.consistency_feedback && (
          <div className="card relative overflow-hidden bg-gradient-to-br from-gray-900 to-violet-900/10 border-violet-500/20">
            <div className="absolute top-0 right-0 w-32 h-32 bg-violet-500/10 rounded-full blur-[40px]" />
            <div className="flex items-center gap-2 mb-3">
              <AlertCircle className="w-4 h-4 text-violet-400" />
              <h3 className="text-white font-semibold">Resume Consistency Analysis</h3>
            </div>
            <p className="text-gray-300 text-sm leading-relaxed relative z-10">{report.consistency_feedback}</p>
            <p className="text-violet-200/60 text-[10px] mt-4 uppercase tracking-wider font-semibold border-t border-violet-500/10 pt-3 relative z-10">
              Evaluates alignment between interview answers and stated resume experience.
            </p>
          </div>
        )}
      </div>

      {/* Strengths + Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-4 h-4 text-emerald-400" />
            <h3 className="text-white font-semibold">Strengths</h3>
          </div>
          {report.strengths?.length > 0 ? (
            <ul className="space-y-2">
              {report.strengths.map((s, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 flex-shrink-0" />
                  {s}
                </li>
              ))}
            </ul>
          ) : <p className="text-gray-600 text-sm">None recorded.</p>}
        </div>

        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="w-4 h-4 text-rose-400" />
            <h3 className="text-white font-semibold">Areas to Improve</h3>
          </div>
          {report.weaknesses?.length > 0 ? (
            <ul className="space-y-2">
              {report.weaknesses.map((w, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-400 mt-1.5 flex-shrink-0" />
                  {w}
                </li>
              ))}
            </ul>
          ) : <p className="text-gray-600 text-sm">None recorded.</p>}
        </div>
      </div>

      {/* Roadmap */}
      {report.roadmap?.length > 0 && (
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <MapPin className="w-4 h-4 text-indigo-400" />
            <h3 className="text-white font-semibold">Learning Roadmap</h3>
          </div>
          <ol className="space-y-3">
            {report.roadmap.map((item, i) => (
              <li key={i} className="flex items-start gap-3">
                <span className="w-6 h-6 rounded-full bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400 text-xs font-bold flex-shrink-0 mt-0.5">
                  {i + 1}
                </span>
                <p className="text-gray-300 text-sm leading-relaxed">{item}</p>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}
