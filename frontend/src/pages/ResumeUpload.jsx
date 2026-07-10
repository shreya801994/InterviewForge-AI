import { useState, useEffect, useRef } from 'react';
import client from '../api/client';
import {
  Upload, FileText, CheckCircle, AlertCircle, Loader2, Code2, Briefcase, Lightbulb, Target
} from 'lucide-react';

const AnalysisSection = ({ icon: Icon, title, items, color }) => {
  if (!items?.length) return null;
  const colorsMap = {
    indigo: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20',
    violet: 'text-violet-400 bg-violet-500/10 border-violet-500/20',
    emerald: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    amber: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
  };
  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <Icon className={`w-4 h-4 ${colorsMap[color].split(' ')[0]}`} />
        <h3 className="text-white font-semibold">{title}</h3>
        <span className="ml-auto text-gray-500 text-xs">{items.length} items</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {items.map((item, i) => (
          <span
            key={i}
            className={`px-2.5 py-1 rounded-lg text-xs font-medium border ${colorsMap[color]}`}
          >
            {item}
          </span>
        ))}
      </div>
    </div>
  );
};

const ATSScoreCard = ({ score, breakdown, suggestions }) => {
  if (score === null || score === undefined) return null;
  
  let colorClass = 'text-red-400 border-red-500/30 bg-red-500/10';
  if (score >= 80) colorClass = 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
  else if (score >= 60) colorClass = 'text-amber-400 border-amber-500/30 bg-amber-500/10';

  return (
    <div className="card md:col-span-2">
      <div className="flex items-center gap-4 mb-4">
        <div className={`w-16 h-16 rounded-full flex items-center justify-center border-4 ${colorClass}`}>
          <span className="text-xl font-bold">{score}</span>
        </div>
        <div>
          <h3 className="text-white font-semibold text-lg">ATS Readiness Score</h3>
          <p className="text-gray-400 text-sm mt-1">{breakdown}</p>
        </div>
      </div>
      {suggestions?.length > 0 && (
        <div className="mt-4 p-3 rounded-lg bg-gray-800/50 border border-gray-700">
          <h4 className="text-gray-300 text-sm font-medium mb-2 flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-amber-400" />
            Suggestions to Improve:
          </h4>
          <ul className="list-disc pl-5 space-y-1">
            {suggestions.map((s, i) => (
              <li key={i} className="text-gray-400 text-sm">{s}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default function ResumeUpload() {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState('');
  const [latestLoading, setLatestLoading] = useState(true);
  const fileRef = useRef(null);

  // Load existing resume analysis
  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await client.get('/api/resume/latest');
        setAnalysis(data);
      } catch {
        // No existing resume
      } finally {
        setLatestLoading(false);
      }
    };
    load();
  }, []);

  const handleFile = async (file) => {
    if (!file) return;
    if (file.type !== 'application/pdf') {
      setError('Please upload a PDF file.');
      return;
    }
    setError('');
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const { data } = await client.post('/api/resume/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setAnalysis(data.analysis);
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    handleFile(file);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-slide-up">
      <div>
        <h2 className="text-xl font-bold text-white">Resume Analysis</h2>
        <p className="text-gray-400 text-sm mt-1">Upload your resume to personalize your interview questions.</p>
      </div>

      {/* Drop zone */}
      <div
        onDragEnter={() => setDragging(true)}
        onDragLeave={() => setDragging(false)}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        onClick={() => fileRef.current?.click()}
        className={`relative border-2 border-dashed rounded-xl p-12 flex flex-col items-center justify-center cursor-pointer transition-all duration-200 ${
          dragging
            ? 'border-indigo-500 bg-indigo-500/10 scale-[1.01]'
            : 'border-gray-700 bg-gray-900 hover:border-indigo-500/50 hover:bg-gray-800/50'
        }`}
      >
        <input
          type="file"
          ref={fileRef}
          accept=".pdf"
          className="hidden"
          onChange={(e) => handleFile(e.target.files[0])}
        />
        {uploading ? (
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="w-10 h-10 text-indigo-400 animate-spin" />
            <p className="text-white font-medium">Analyzing your resume with AI...</p>
            <p className="text-gray-400 text-sm">This may take a few seconds</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3 text-center">
            <div className={`p-4 rounded-full transition-colors ${dragging ? 'bg-indigo-600/20' : 'bg-gray-800'}`}>
              <Upload className={`w-8 h-8 ${dragging ? 'text-indigo-400' : 'text-gray-400'}`} />
            </div>
            <div>
              <p className="text-white font-medium">Drop your PDF resume here</p>
              <p className="text-gray-500 text-sm mt-1">or click to browse files</p>
            </div>
            <p className="text-gray-600 text-xs">Supported format: PDF only</p>
          </div>
        )}
      </div>

      {error && (
        <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
      )}

      {/* Analysis Results */}
      {/* Analysis Results */}
      {latestLoading ? (
        <div className="flex items-center gap-2 text-gray-500 text-sm">
          <Loader2 className="w-4 h-4 animate-spin" />
          Loading previous analysis...
        </div>
      ) : uploading ? (
        <div className="space-y-4 animate-pulse">
          <div className="flex items-center gap-2 text-indigo-400/50">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span className="font-medium">Analyzing with Gemini AI...</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Skeleton ATS Score Card (md:col-span-2) */}
            <div className="card md:col-span-2 min-h-[140px] flex flex-col justify-center gap-4">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-full bg-gray-800 shrink-0" />
                <div className="space-y-2 flex-1">
                  <div className="h-5 bg-gray-800 rounded w-1/3" />
                  <div className="h-4 bg-gray-800/50 rounded w-2/3" />
                </div>
              </div>
              <div className="h-16 bg-gray-800/50 rounded-lg w-full mt-2" />
            </div>
            
            {/* Skeleton Analysis Sections (4 cards) */}
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="card min-h-[120px]">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-4 h-4 rounded bg-gray-800" />
                  <div className="h-5 bg-gray-800 rounded w-24" />
                </div>
                <div className="flex flex-wrap gap-2">
                  <div className="h-6 w-16 bg-gray-800 rounded-lg" />
                  <div className="h-6 w-24 bg-gray-800 rounded-lg" />
                  <div className="h-6 w-20 bg-gray-800 rounded-lg" />
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : analysis ? (
        <div className="space-y-4 animate-slide-up">
          <div className="flex items-center gap-2 text-emerald-400">
            <CheckCircle className="w-5 h-5" />
            <span className="font-medium">Resume analyzed successfully</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <ATSScoreCard 
              score={analysis.ats_score} 
              breakdown={analysis.ats_breakdown} 
              suggestions={analysis.ats_suggestions} 
            />
            <AnalysisSection icon={Code2} title="Skills" items={analysis.skills} color="indigo" />
            <AnalysisSection icon={Briefcase} title="Projects" items={analysis.projects} color="violet" />
            <AnalysisSection icon={CheckCircle} title="Strengths" items={analysis.strengths} color="emerald" />
            <AnalysisSection icon={Target} title="Focus Areas" items={analysis.focus_areas} color="amber" />
          </div>
        </div>
      ) : (
        <div className="card text-center py-8">
          <FileText className="w-10 h-10 text-gray-600 mx-auto mb-3" />
          <p className="text-gray-400 text-sm">No resume uploaded yet.</p>
        </div>
      )}
    </div>
  );
}
