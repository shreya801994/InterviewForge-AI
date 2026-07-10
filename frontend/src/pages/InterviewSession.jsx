import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import client from '../api/client';
import {
  Send, Bot, User, CheckCircle, AlertCircle, Loader2, BarChart2, TrendingUp
} from 'lucide-react';

const EvalBadge = ({ label, value, color }) => {
  const colors = {
    indigo: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30',
    violet: 'bg-violet-500/10 text-violet-400 border-violet-500/30',
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  };
  return (
    <div className={`flex flex-col items-center p-2 rounded-lg border ${colors[color]}`}>
      <span className="text-xs text-gray-500 mb-0.5">{label}</span>
      <span className="font-bold text-sm">{value?.toFixed(1)}</span>
    </div>
  );
};

export default function InterviewSession() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [answer, setAnswer] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [lastEval, setLastEval] = useState(null);
  const [completed, setCompleted] = useState(false);
  const [error, setError] = useState('');
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  const [timeLeft, setTimeLeft] = useState(null);
  const [tabSwitchCount, setTabSwitchCount] = useState(0);

  // Load session details
  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await client.get(`/api/interview/${sessionId}`);
        setSession(data);
        if (data.status === 'COMPLETED') setCompleted(true);
      } catch {
        setError('Could not load interview session.');
      }
    };
    load();
  }, [sessionId]);

  const questions = session?.messages?.filter((m) => m.message_type === 'QUESTION') ?? [];
  const activeQuestion = questions.length > 0 ? questions[questions.length - 1] : null;

  // Timer logic
  useEffect(() => {
    if (!activeQuestion || completed || submitting) return;
    
    // Default 5 mins for coding, 2 mins for conceptual
    const defaultTime = activeQuestion.question_type === 'coding' ? 300 : 120;
    
    if (activeQuestion.time_limit_seconds) {
      setTimeLeft(activeQuestion.time_limit_seconds);
    } else {
      setTimeLeft(defaultTime);
    }
  }, [activeQuestion, completed, submitting]);

  useEffect(() => {
    if (timeLeft === null || timeLeft <= 0 || completed || submitting) return;
    
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          // Auto submit
          handleSubmit(new Event('submit'));
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    
    return () => clearInterval(timer);
  }, [timeLeft, completed, submitting]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [session?.messages, lastEval]);

  // Tab switch detection
  const lastViolationTime = useRef(0);
  useEffect(() => {
    if (completed || !session || session.status !== 'ACTIVE') return;

    const handleVisibilityChange = async () => {
      const isHidden = document.visibilityState === 'hidden' || !document.hasFocus();
      if (!isHidden) return;
      
      const now = Date.now();
      // Debounce: don't count multiple events within 1 second as separate violations
      if (now - lastViolationTime.current < 1000) return;
      lastViolationTime.current = now;

      setTabSwitchCount((prev) => {
        const newCount = prev + 1;
        if (newCount === 1) {
          alert('WARNING: Switching tabs or minimizing the window during an interview is not permitted. Another violation will terminate the session.');
        } else if (newCount >= 2) {
          client.post(`/api/interview/${sessionId}/terminate`).then(() => {
            setCompleted(true);
            setError('Session terminated due to anti-cheat violation (multiple tab switches).');
          }).catch(console.error);
        }
        return newCount;
      });
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('blur', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('blur', handleVisibilityChange);
    };
  }, [sessionId, completed, session]);

  const handleSubmit = async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    const finalAnswer = answer.trim() || "(Time expired, no answer provided)";
    setSubmitting(true);
    setError('');
    setTimeLeft(null); // Stop timer while evaluating
    
    try {
      const { data } = await client.post(`/api/interview/${sessionId}/answer`, {
        answer_text: finalAnswer
      });

      setSession((prev) => ({
        ...prev,
        questions_answered: (prev.questions_answered ?? 0) + 1,
        completion_percentage: data.is_completed ? 100 : prev.completion_percentage,
        messages: [
          ...(prev.messages || []),
          { id: Date.now(), message_type: 'ANSWER', content: finalAnswer },
          ...(data.next_question ? [{
            id: Date.now() + 1, 
            message_type: 'QUESTION', 
            content: data.next_question,
            question_type: data.next_question_type,
            time_limit_seconds: data.next_question_time_limit
          }] : [])
        ]
      }));

      setLastEval(data.evaluation);
      setAnswer('');

      if (data.is_completed) {
        setCompleted(true);
      }
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Failed to submit answer.');
    } finally {
      setSubmitting(false);
      textareaRef.current?.focus();
    }
  };

  const questionCount = session?.question_count ?? 0;
  const answered = session?.questions_answered ?? 0;
  const progress = questionCount > 0 ? Math.min((answered / questionCount) * 100, 100) : 0;

  if (!session && !error) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-16">
        <AlertCircle className="w-10 h-10 text-red-400 mx-auto mb-3" />
        <p className="text-red-400">{error}</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto animate-slide-up flex flex-col gap-4">
      {/* Header */}
      <div className="card">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="w-full sm:w-auto">
            <h2 className="text-white font-semibold flex flex-wrap items-center gap-2">
              {session.role}
              {activeQuestion?.question_type === 'coding' && (
                <span className="bg-indigo-600/20 text-indigo-400 text-xs px-2 py-0.5 rounded border border-indigo-500/30">
                  Coding Challenge
                </span>
              )}
            </h2>
            <p className="text-gray-400 text-sm mt-1">
              {session.difficulty} · {answered}/{questionCount} questions
            </p>
          </div>
          <div className="flex items-center justify-between sm:justify-end gap-6 w-full sm:w-auto border-t border-gray-700/50 sm:border-0 pt-3 sm:pt-0">
            {timeLeft !== null && !completed && (
              <div className="text-left sm:text-right">
                <p className="text-xs text-gray-500 mb-1">Time Remaining</p>
                <p className={`font-mono font-bold text-sm ${timeLeft <= 30 ? 'text-red-400 animate-pulse' : 'text-amber-400'}`}>
                  {Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, '0')}
                </p>
              </div>
            )}
            <div>
              <div className="text-right">
                <p className="text-xs text-gray-500 mb-1">Progress</p>
                <p className="text-white font-bold text-sm">{progress.toFixed(0)}%</p>
              </div>
              <div className="w-24 sm:w-32 h-2 bg-gray-800 rounded-full overflow-hidden mt-1">
                <div
                  className="h-full bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full transition-all duration-500"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Chat */}
      <div className="card flex-1 min-h-0">
        <div className="space-y-4 max-h-[420px] overflow-y-auto pr-2">
          {session.messages?.map((msg, idx) => (
            <div
              key={msg.id ?? idx}
              className={`flex gap-3 ${msg.message_type === 'ANSWER' ? 'justify-end' : 'justify-start'} animate-slide-up`}
            >
              {msg.message_type === 'QUESTION' && (
                <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Bot className="w-4 h-4 text-white" />
                </div>
              )}
              <div
                className={`max-w-[80%] rounded-xl px-4 py-3 text-sm ${
                  msg.message_type === 'ANSWER'
                    ? 'bg-indigo-600 text-white rounded-br-sm'
                    : 'bg-gray-800 text-gray-100 rounded-bl-sm'
                }`}
              >
                {msg.content}
              </div>
              {msg.message_type === 'ANSWER' && (
                <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <User className="w-4 h-4 text-gray-300" />
                </div>
              )}
            </div>
          ))}

          {/* Live Eval Card */}
          {lastEval && (
            <div className="border border-gray-700 bg-gray-800/50 rounded-xl p-4 animate-slide-up">
              <div className="flex items-center gap-2 mb-3">
                <BarChart2 className="w-4 h-4 text-indigo-400" />
                <span className="text-sm font-medium text-white">Evaluation</span>
              </div>
              <div className="grid grid-cols-3 gap-2 mb-3">
                <EvalBadge label="Technical" value={lastEval.technical_accuracy} color="indigo" />
                <EvalBadge label="Communication" value={lastEval.communication} color="violet" />
                <EvalBadge label="Depth" value={lastEval.depth} color="emerald" />
              </div>
              <p className="text-gray-400 text-xs leading-relaxed">{lastEval.feedback}</p>
            </div>
          )}

          {/* Completion state */}
          {completed && (
            <div className="text-center py-6 animate-slide-up">
              <div className="w-14 h-14 rounded-full bg-emerald-500/10 flex items-center justify-center mx-auto mb-3">
                <CheckCircle className="w-7 h-7 text-emerald-400" />
              </div>
              <h3 className="text-white font-semibold mb-1">Interview Complete!</h3>
              <p className="text-gray-400 text-sm mb-4">Your report is being generated.</p>
              <button
                onClick={() => navigate(`/report/${sessionId}`)}
                className="btn-primary"
              >
                <TrendingUp className="w-4 h-4" />
                View Report
              </button>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      {/* Input */}
      {!completed && (
        <form onSubmit={handleSubmit} className="card">
          {activeQuestion?.question_type === 'coding' && (
            <div className="flex items-center gap-2 mb-2 p-2 bg-indigo-500/10 border border-indigo-500/20 rounded text-xs text-indigo-300">
              <AlertCircle className="w-3.5 h-3.5" />
              <span>AI-reviewed, not executed. Focus on logic, structure, and algorithmic correctness.</span>
            </div>
          )}
          <textarea
            ref={textareaRef}
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) handleSubmit(e);
            }}
            placeholder={activeQuestion?.question_type === 'coding' ? "Write your code here... (Ctrl+Enter to submit)" : "Type your answer... (Ctrl+Enter to submit)"}
            rows={activeQuestion?.question_type === 'coding' ? 10 : 3}
            className={`input-field resize-y mb-3 ${activeQuestion?.question_type === 'coding' ? 'font-mono text-sm bg-gray-900 border-gray-700 text-gray-300' : ''}`}
            disabled={submitting}
          />
          <div className="flex items-center justify-between">
            <p className="text-gray-600 text-xs">Ctrl+Enter to send</p>
            <button type="submit" disabled={submitting || !answer.trim()} className="btn-primary">
              {submitting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
              {submitting ? 'Evaluating...' : 'Submit Answer'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
