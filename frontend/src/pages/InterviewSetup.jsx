import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../api/client';
import { Play, Loader2, AlertCircle, Plus, X } from 'lucide-react';

const ROLES = [
  'Software Engineer', 'Frontend Developer', 'Backend Developer',
  'Full Stack Developer', 'DevOps Engineer', 'Data Scientist',
  'Machine Learning Engineer', 'Mobile Developer', 'QA Engineer',
  'Software Engineer Intern'
];

const FOCUS_TOPIC_OPTIONS = ['DSA', 'DBMS', 'OS', 'OOP', 'Graphs', 'Trees', 'Arrays', 'System Design'];

export default function InterviewSetup() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    role: '',
    difficulty: 'Medium',
    question_count: 10,
    focus_topics: [],
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: name === 'question_count' ? Number(value) : value });
  };

  const toggleTopic = (topic) => {
    setForm((prev) => ({
      ...prev,
      focus_topics: prev.focus_topics.includes(topic)
        ? prev.focus_topics.filter((t) => t !== topic)
        : [...prev.focus_topics, topic],
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.role) { setError('Please select or enter a role.'); return; }
    setLoading(true);
    setError('');
    try {
      const { data } = await client.post('/api/interview/start', form);
      navigate(`/interview/${data.session_id}`);
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Failed to start interview. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto animate-slide-up">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-white">Configure Interview</h2>
        <p className="text-gray-400 text-sm mt-1">Set up your AI-powered interview session.</p>
      </div>

      <div className="card">
        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg mb-5 text-red-400 text-sm">
            <AlertCircle className="w-4 h-4" /> {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Role */}
          <div>
            <label className="label" htmlFor="role">Job Role</label>
            <div className="flex gap-2 flex-wrap mb-2">
              {ROLES.slice(0, 5).map((r) => (
                <button
                  type="button"
                  key={r}
                  onClick={() => setForm({ ...form, role: r })}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                    form.role === r
                      ? 'bg-indigo-600 border-indigo-500 text-white'
                      : 'bg-gray-800 border-gray-700 text-gray-400 hover:border-gray-600 hover:text-white'
                  }`}
                >
                  {r}
                </button>
              ))}
            </div>
            <input
              id="role"
              type="text"
              name="role"
              value={form.role}
              onChange={handleChange}
              className="input-field"
              placeholder="Or type a custom role..."
            />
          </div>

          {/* Job Description (Optional) */}
          <div>
            <label className="label" htmlFor="job_description">
              Job Description <span className="text-gray-600 font-normal">(optional)</span>
            </label>
            <textarea
              id="job_description"
              name="job_description"
              value={form.job_description || ''}
              onChange={handleChange}
              className="input-field min-h-[100px] resize-y"
              placeholder="Paste the job description here for highly tailored AI questions..."
            />
          </div>

          {/* Difficulty */}
          <div>
            <label className="label">Difficulty</label>
            <div className="flex gap-3">
              {['Easy', 'Medium', 'Hard'].map((d) => (
                <button
                  type="button"
                  key={d}
                  onClick={() => setForm({ ...form, difficulty: d })}
                  className={`flex-1 py-2.5 rounded-lg text-sm font-medium border transition-all ${
                    form.difficulty === d
                      ? d === 'Easy' ? 'bg-emerald-600/20 border-emerald-500 text-emerald-400'
                        : d === 'Medium' ? 'bg-amber-600/20 border-amber-500 text-amber-400'
                        : 'bg-rose-600/20 border-rose-500 text-rose-400'
                      : 'bg-gray-800 border-gray-700 text-gray-400 hover:border-gray-600'
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          {/* Question Count */}
          <div>
            <label className="label" htmlFor="question_count">
              Number of Questions
              <span className="ml-2 text-indigo-400 font-bold">{form.question_count}</span>
            </label>
            <input
              id="question_count"
              type="range"
              name="question_count"
              min={3}
              max={20}
              value={form.question_count}
              onChange={handleChange}
              className="w-full accent-indigo-500"
            />
            <div className="flex justify-between text-xs text-gray-600 mt-1">
              <span>3</span>
              <span>20</span>
            </div>
          </div>

          {/* Focus Topics */}
          <div>
            <label className="label">Focus Topics <span className="text-gray-600 font-normal">(optional)</span></label>
            <div className="flex flex-wrap gap-2">
              {FOCUS_TOPIC_OPTIONS.map((topic) => (
                <button
                  type="button"
                  key={topic}
                  onClick={() => toggleTopic(topic)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                    form.focus_topics.includes(topic)
                      ? 'bg-indigo-600/20 border-indigo-500 text-indigo-300'
                      : 'bg-gray-800 border-gray-700 text-gray-400 hover:border-gray-600 hover:text-white'
                  }`}
                >
                  {form.focus_topics.includes(topic) && <span className="mr-1">✓</span>}
                  {topic}
                </button>
              ))}
            </div>
            {form.focus_topics.length > 0 && (
              <p className="text-indigo-400 text-xs mt-2">
                Selected: {form.focus_topics.join(', ')}
              </p>
            )}
          </div>

          <button type="submit" disabled={loading} className="btn-primary w-full mt-2">
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                Starting Interview...
              </span>
            ) : (
              <span className="flex items-center justify-center gap-2">
                <Play className="w-4 h-4" />
                Start Interview
              </span>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
