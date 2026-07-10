export default function MetricCard({ title, value, icon: Icon, subtitle, accent = 'indigo' }) {
  const accentMap = {
    indigo: 'from-indigo-500/20 to-indigo-600/10 border-indigo-500/30 text-indigo-400',
    violet: 'from-violet-500/20 to-violet-600/10 border-violet-500/30 text-violet-400',
    emerald: 'from-emerald-500/20 to-emerald-600/10 border-emerald-500/30 text-emerald-400',
    amber: 'from-amber-500/20 to-amber-600/10 border-amber-500/30 text-amber-400',
    rose: 'from-rose-500/20 to-rose-600/10 border-rose-500/30 text-rose-400',
  };
  const accentClass = accentMap[accent] || accentMap.indigo;

  return (
    <div className={`relative bg-gradient-to-br ${accentClass} border rounded-xl p-5 overflow-hidden group hover:scale-[1.02] transition-transform duration-200`}>
      <div className="flex items-start justify-between mb-3">
        <span className="text-gray-400 text-sm font-medium">{title}</span>
        {Icon && (
          <div className={`p-2 rounded-lg bg-gray-800/50 ${accentClass} border`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>
      <p className="text-3xl font-bold text-white mb-1">{value}</p>
      {subtitle && <p className="text-gray-500 text-xs">{subtitle}</p>}
    </div>
  );
}
