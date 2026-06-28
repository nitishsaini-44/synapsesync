import React, { useState } from 'react';
import { MessageSquare, Tags, Sparkles, Copy, RefreshCw, Check } from 'lucide-react';
import { summarizeEmail, classifyLead, generateReply } from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';
import UrgencyBadge from '../components/UrgencyBadge';

const AIAssistant = () => {
  const [input, setInput] = useState('');
  const [loadingAction, setLoadingAction] = useState(null); // 'summarize', 'classify', 'reply'
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  const handleAction = async (actionType) => {
    if (!input.trim()) {
      setError("Please enter a message first.");
      return;
    }
    setError(null);
    setLoadingAction(actionType);
    setResult(null);

    try {
      let res;
      if (actionType === 'summarize') {
        res = await summarizeEmail(input);
      } else if (actionType === 'classify') {
        res = await classifyLead(input);
      } else if (actionType === 'reply') {
        res = await generateReply(input);
      }
      
      setResult({
        type: actionType,
        data: res.data
      });
    } catch (err) {
      setError(`Failed to ${actionType} message. Ensure backend is running.`);
    } finally {
      setLoadingAction(null);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 md:space-y-8 animate-fade-in">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl md:text-[32px] font-bold text-heading leading-tight">AI Assistant</h1>
        <p className="text-sm md:text-[15px] text-muted mt-1">Process emails and messages with AI.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 md:gap-8">
        {/* Input Section */}
        <div className="space-y-4">
          <div className="bg-surface-card rounded-card border border-border shadow-card overflow-hidden focus-within:border-primary/40 focus-within:shadow-input-focus transition-all duration-200">
            <div className="px-5 py-3 border-b border-divider">
              <span className="text-sm font-medium text-heading">Input Message</span>
            </div>
            <textarea
              className="w-full h-40 md:h-64 bg-transparent text-heading p-4 md:p-5 outline-none resize-none placeholder-muted/60 text-[15px] leading-relaxed"
              placeholder="Paste an email, customer query, or message here..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
          </div>

          {error && (
            <div className="flex items-center gap-2 p-3 bg-error-light border border-error/15 rounded-button text-error text-sm">
              <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
              </svg>
              <span>{error}</span>
            </div>
          )}

          <div className="grid grid-cols-3 gap-3">
            <button
              onClick={() => handleAction('summarize')}
              disabled={loadingAction !== null}
              className="flex flex-col items-center justify-center p-3 md:p-4 rounded-card bg-surface-card border border-border hover:border-primary/30 hover:shadow-card-hover transition-all duration-200 group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="w-10 h-10 rounded-2xl bg-primary-light flex items-center justify-center mb-2 group-hover:bg-primary/10 transition-colors">
                <MessageSquare className="text-primary" size={18} />
              </div>
              <span className="text-xs md:text-sm font-medium text-body group-hover:text-primary transition-colors">Summarize</span>
            </button>
            <button
              onClick={() => handleAction('classify')}
              disabled={loadingAction !== null}
              className="flex flex-col items-center justify-center p-3 md:p-4 rounded-card bg-surface-card border border-border hover:border-primary/30 hover:shadow-card-hover transition-all duration-200 group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="w-10 h-10 rounded-2xl bg-primary-light flex items-center justify-center mb-2 group-hover:bg-primary/10 transition-colors">
                <Tags className="text-primary" size={18} />
              </div>
              <span className="text-xs md:text-sm font-medium text-body group-hover:text-primary transition-colors">Classify</span>
            </button>
            <button
              onClick={() => handleAction('reply')}
              disabled={loadingAction !== null}
              className="flex flex-col items-center justify-center p-3 md:p-4 rounded-card bg-surface-card border border-border hover:border-primary/30 hover:shadow-card-hover transition-all duration-200 group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="w-10 h-10 rounded-2xl bg-primary-light flex items-center justify-center mb-2 group-hover:bg-primary/10 transition-colors">
                <Sparkles className="text-primary" size={18} />
              </div>
              <span className="text-xs md:text-sm font-medium text-body group-hover:text-primary transition-colors">Ai-Reply</span>
            </button>
          </div>
        </div>

        {/* Results Section */}
        <div className="bg-surface-card rounded-card border border-border shadow-card p-5 md:p-6 flex flex-col min-h-[300px] md:min-h-[400px]">
          <h3 className="text-base font-semibold text-heading mb-5 pb-4 border-b border-divider">AI Output</h3>
          
          <div className="flex-1">
            {loadingAction ? (
              <div className="h-full flex items-center justify-center">
                <LoadingSpinner text={`AI is thinking...`} />
              </div>
            ) : result ? (
              <div className="space-y-5 animate-fade-in">
                {/* Status Badges for Summarize/Classify */}
                {(result.type === 'summarize' || result.type === 'classify') && result.data && (
                  <div className="flex flex-wrap gap-2.5">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-body border border-border capitalize">
                      {result.data.category || 'Uncategorized'}
                    </span>
                    <UrgencyBadge level={result.data.urgency || result.data.priority} />
                  </div>
                )}

                {/* Summary Text */}
                {(result.type === 'summarize' || result.type === 'classify') && result.data?.summary && (
                  <div>
                    <h4 className="text-xs font-semibold text-muted uppercase tracking-wider mb-2.5">Summary</h4>
                    <p className="text-heading leading-relaxed bg-surface-bg p-4 rounded-2xl border border-border text-[15px]">
                      {result.data.summary}
                    </p>
                  </div>
                )}

                {/* Reply Text */}
                {result.type === 'reply' && result.data?.reply && (
                  <div className="space-y-4">
                    <h4 className="text-xs font-semibold text-muted uppercase tracking-wider">Drafted Reply</h4>
                    <div className="relative group">
                      <p className="text-heading leading-relaxed bg-primary-light/50 p-4 rounded-2xl border border-primary/10 whitespace-pre-wrap text-[15px]">
                        {result.data.reply}
                      </p>
                      <button 
                        onClick={() => copyToClipboard(result.data.reply)}
                        className="absolute top-3 right-3 p-2 rounded-xl bg-surface-card text-muted opacity-0 group-hover:opacity-100 transition-all duration-200 hover:text-heading hover:shadow-card border border-border"
                        title="Copy to clipboard"
                      >
                        {copied ? <Check size={16} className="text-success" /> : <Copy size={16} />}
                      </button>
                    </div>
                    <div className="flex justify-end">
                      <button 
                        onClick={() => handleAction('reply')}
                        className="flex items-center gap-2 text-sm text-primary hover:text-primary-hover transition-colors font-medium"
                      >
                        <RefreshCw size={14} />
                        <span>Regenerate</span>
                      </button>
                    </div>
                  </div>
                )}

              </div>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-muted space-y-3">
                <div className="w-16 h-16 rounded-2xl bg-surface-bg flex items-center justify-center">
                  <Sparkles size={28} className="text-gray-300" />
                </div>
                <p className="text-sm">Waiting for input...</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;
