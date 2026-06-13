"use client";

import { useState } from "react";
import { Upload, Briefcase, Search, MapPin, DollarSign, Building, AlertCircle } from "lucide-react";

type Job = {
  id: string;
  title: string;
  company: string;
  location: string;
  salary?: string;
  description?: string;
  apply_url: string;
  source: string;
  posted_date?: string;
  match_score?: number;
};

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const pollResults = async (taskId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/results/${taskId}`);
      if (!res.ok) throw new Error("Failed to fetch results");
      
      const data = await res.json();
      if (data.status === "done") {
        setJobs(data.jobs);
        setLoading(false);
        setTaskId(null);
      } else if (data.status === "error") {
        setError(data.detail || "An error occurred during search.");
        setLoading(false);
        setTaskId(null);
      } else {
        // Still processing, poll again in 3 seconds
        setTimeout(() => pollResults(taskId), 3000);
      }
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
      setTaskId(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    
    setLoading(true);
    setError(null);
    setJobs([]);
    
    const formData = new FormData();
    formData.append("file", file);
    
    try {
      const res = await fetch("http://localhost:8000/search", {
        method: "POST",
        body: formData,
      });
      
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Upload failed");
      }
      
      const data = await res.json();
      setTaskId(data.task_id);
      
      // Start polling
      pollResults(data.task_id);
      
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-white font-sans selection:bg-indigo-500/30">
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#4f4f4f2e_1px,transparent_1px),linear-gradient(to_bottom,#4f4f4f2e_1px,transparent_1px)] bg-[size:14px_24px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none"></div>
      
      <main className="relative z-10 max-w-6xl mx-auto px-6 py-16 flex flex-col items-center">
        
        <header className="text-center mb-16 space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-sm text-indigo-400 font-medium mb-4">
            <Search className="w-4 h-4" />
            <span>AI-Powered Job Search</span>
          </div>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-br from-white to-white/50">
            Find your next role.
          </h1>
          <p className="text-neutral-400 max-w-xl mx-auto text-lg">
            Upload your resume and our AI will search across LinkedIn, Naukri, Indeed, and more to find your perfect match.
          </p>
        </header>

        {/* Upload Section */}
        <div className="w-full max-w-xl p-1 rounded-2xl bg-gradient-to-b from-white/10 to-transparent">
          <div className="bg-neutral-900/80 backdrop-blur-xl border border-white/5 rounded-xl p-8 flex flex-col items-center text-center gap-6 shadow-2xl">
            
            <div className="w-20 h-20 rounded-full bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20">
              <Upload className="w-8 h-8 text-indigo-400" />
            </div>
            
            <div className="space-y-1">
              <h3 className="text-xl font-semibold">Upload Resume</h3>
              <p className="text-sm text-neutral-500">PDF, DOCX, or TXT up to 5MB</p>
            </div>

            <label className="w-full cursor-pointer group">
              <input type="file" className="hidden" accept=".pdf,.docx,.txt" onChange={handleFileChange} />
              <div className="w-full border-2 border-dashed border-white/10 group-hover:border-indigo-500/50 rounded-lg p-4 transition-all bg-white/5 group-hover:bg-indigo-500/5">
                {file ? (
                  <span className="text-indigo-400 font-medium">{file.name}</span>
                ) : (
                  <span className="text-neutral-400">Click to browse or drag and drop</span>
                )}
              </div>
            </label>

            <button
              onClick={handleUpload}
              disabled={!file || loading}
              className="w-full bg-white text-black hover:bg-neutral-200 disabled:opacity-50 disabled:cursor-not-allowed font-semibold py-3 px-6 rounded-lg transition-all shadow-[0_0_40px_-10px_rgba(255,255,255,0.3)] hover:shadow-[0_0_60px_-15px_rgba(255,255,255,0.5)]"
            >
              {loading ? "Searching the web..." : "Find Matches"}
            </button>
            
            {error && (
              <div className="flex items-center gap-2 text-red-400 bg-red-400/10 px-4 py-2 rounded-lg w-full text-sm">
                <AlertCircle className="w-4 h-4" />
                <span>{error}</span>
              </div>
            )}
          </div>
        </div>

        {/* Results Section */}
        {loading && (
          <div className="mt-20 w-full max-w-4xl space-y-4">
            <h2 className="text-2xl font-semibold mb-6 flex items-center gap-3">
              <div className="w-5 h-5 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin"></div>
              Aggregating jobs & ranking...
            </h2>
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-32 bg-white/5 rounded-xl animate-pulse border border-white/5"></div>
            ))}
          </div>
        )}

        {!loading && jobs.length > 0 && (
          <div className="mt-20 w-full max-w-4xl animate-in fade-in slide-in-from-bottom-10 duration-700">
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-2xl font-semibold">Matched Roles <span className="text-neutral-500 text-lg">({jobs.length})</span></h2>
            </div>
            
            <div className="space-y-4">
              {jobs.map((job) => (
                <a 
                  key={job.id} 
                  href={job.apply_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="block group relative p-1 rounded-xl bg-gradient-to-b from-white/5 to-transparent hover:from-indigo-500/20 transition-all"
                >
                  <div className="bg-neutral-900 border border-white/5 rounded-lg p-6 hover:bg-neutral-800/80 transition-colors flex flex-col md:flex-row md:items-center justify-between gap-6">
                    
                    <div className="space-y-3 flex-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="text-xl font-bold group-hover:text-indigo-400 transition-colors">{job.title}</h3>
                          <div className="flex flex-wrap items-center gap-4 mt-2 text-sm text-neutral-400">
                            <div className="flex items-center gap-1.5 text-neutral-300">
                              <Building className="w-4 h-4" />
                              <span>{job.company}</span>
                            </div>
                            <div className="flex items-center gap-1.5">
                              <MapPin className="w-4 h-4" />
                              <span>{job.location || "Remote / Undefined"}</span>
                            </div>
                            {job.salary && (
                              <div className="flex items-center gap-1.5 text-emerald-400/80">
                                <DollarSign className="w-4 h-4" />
                                <span>{job.salary}</span>
                              </div>
                            )}
                          </div>
                        </div>
                        {job.match_score !== undefined && (
                          <div className="shrink-0 ml-4 flex flex-col items-end">
                            <span className="text-xs text-neutral-500 mb-1 uppercase tracking-wider font-semibold">Match Score</span>
                            <div className={`px-3 py-1 rounded-md font-mono font-bold text-lg ${
                              job.match_score >= 80 ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 
                              job.match_score >= 60 ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : 
                              'bg-neutral-500/10 text-neutral-400 border border-neutral-500/20'
                            }`}>
                              {job.match_score}%
                            </div>
                          </div>
                        )}
                      </div>
                      
                      {job.description && (
                        <p className="text-sm text-neutral-500 line-clamp-2">
                          {job.description}
                        </p>
                      )}
                      
                      <div className="flex items-center gap-2 pt-2">
                        <span className="text-xs px-2.5 py-1 bg-white/5 rounded-md text-neutral-400 border border-white/5 uppercase tracking-wider font-medium">
                          {job.source}
                        </span>
                        {job.posted_date && (
                          <span className="text-xs text-neutral-500">
                            Posted {job.posted_date}
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <div className="shrink-0 flex items-center justify-center bg-white text-black p-3 rounded-full opacity-0 -translate-x-4 group-hover:opacity-100 group-hover:translate-x-0 transition-all">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>
                    </div>
                  </div>
                </a>
              ))}
            </div>
          </div>
        )}

      </main>
    </div>
  );
}
