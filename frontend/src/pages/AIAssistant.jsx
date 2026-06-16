import React, { useState } from 'react';
import { MessageSquare, Tags, Sparkles, Copy, RefreshCw } from 'lucide-react';
import { summarizeEmail, classifyLead, generateReply } from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';
import UrgencyBadge from '../components/UrgencyBadge';

const AIAssistant = () => {
  const [input, setInput] = useState('');
  const [loadingAction, setLoadingAction] = useState(null); // 'summarize', 'classify', 'reply'
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

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
        data: actionType === 'reply' ? res.data : res.data // Use nested data object
      });
    } catch (err) {
      setError(`Failed to ${actionType} message. Ensure backend is running.`);
    } finally {
      setLoadingAction(null);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    // Simple toast could be added here
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 md:space-y-8 animate-in fade-in duration-500">
      <div>
        <h2 className="text-xl md:text-2xl font-bold text-slate-100">AI Assistant</h2>
        <p className="text-sm md:text-base text-slate-400">Process emails and messages with AI.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-8">
        {/* Input Section */}
        <div className="space-y-4">
          <div className="bg-dark-surface rounded-xl border border-slate-700/50 shadow-sm overflow-hidden focus-within:border-primary/50 focus-within:ring-1 focus-within:ring-primary/50 transition-all">
            <div className="bg-slate-800/50 px-4 py-2 border-b border-slate-700/50 text-sm font-medium text-slate-300">
              Input Message
            </div>
            <textarea
              className="w-full h-40 md:h-64 bg-transparent text-slate-200 p-3 md:p-4 outline-none resize-none placeholder-slate-500 text-sm md:text-base"
              placeholder="Paste an email, customer query, or message here..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
          </div>

          {error && <div className="text-danger text-sm">{error}</div>}

          <div className="grid grid-cols-1 gap-3">
            <div className="grid grid-cols-3 gap-2 md:gap-3">
              <button
                onClick={() => handleAction('summarize')}
                disabled={loadingAction !== null}
                className="flex flex-col items-center justify-center p-2.5 md:p-3 rounded-xl bg-dark-surface border border-slate-700 hover:border-primary/50 hover:bg-primary/10 transition-all group disabled:opacity-50"
              >
                <MessageSquare className="text-slate-400 group-hover:text-primary mb-1 md:mb-2" size={18} />
                <span className="text-xs md:text-sm font-medium text-slate-300 group-hover:text-primary">Summarize</span>
              </button>
              <button
                onClick={() => handleAction('classify')}
                disabled={loadingAction !== null}
                className="flex flex-col items-center justify-center p-2.5 md:p-3 rounded-xl bg-dark-surface border border-slate-700 hover:border-primary/50 hover:bg-primary/10 transition-all group disabled:opacity-50"
              >
                <Tags className="text-slate-400 group-hover:text-primary mb-1 md:mb-2" size={18} />
                <span className="text-xs md:text-sm font-medium text-slate-300 group-hover:text-primary">Classify</span>
              </button>
              <button
                onClick={() => handleAction('reply')}
                disabled={loadingAction !== null}
                className="flex flex-col items-center justify-center p-2.5 md:p-3 rounded-xl bg-dark-surface border border-slate-700 hover:border-primary/50 hover:bg-primary/10 transition-all group disabled:opacity-50"
              >
                <Sparkles className="text-slate-400 group-hover:text-primary mb-1 md:mb-2" size={18} />
                <span className="text-xs md:text-sm font-medium text-slate-300 group-hover:text-primary">Auto-Reply</span>
              </button>
            </div>
          </div>
        </div>

        {/* Results Section */}
        <div className="bg-dark-surface rounded-xl border border-slate-700/50 shadow-sm p-4 md:p-6 flex flex-col min-h-[300px] md:min-h-[400px]">
          <h3 className="text-lg font-semibold text-slate-200 mb-6 border-b border-slate-700/50 pb-4">AI Output</h3>
          
          <div className="flex-1">
            {loadingAction ? (
              <div className="h-full flex items-center justify-center">
                <LoadingSpinner text={`AI is thinking...`} />
              </div>
            ) : result ? (
              <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-300">
                {/* Status Badges for Summarize/Classify */}
                {(result.type === 'summarize' || result.type === 'classify') && result.data && (
                  <div className="flex flex-wrap gap-3">
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700 capitalize">
                      {result.data.category || 'Uncategorized'}
                    </span>
                    <UrgencyBadge level={result.data.urgency || result.data.priority} />
                  </div>
                )}

                {/* Summary Text */}
                {(result.type === 'summarize' || result.type === 'classify') && result.data?.summary && (
                  <div>
                    <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Summary</h4>
                    <p className="text-slate-200 leading-relaxed bg-slate-800/30 p-4 rounded-lg border border-slate-700/30">
                      {result.data.summary}
                    </p>
                  </div>
                )}

                {/* Reply Text */}
                {result.type === 'reply' && result.data?.reply && (
                  <div className="space-y-4">
                    <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Drafted Reply</h4>
                    <div className="relative group">
                      <p className="text-slate-200 leading-relaxed bg-primary/5 p-4 rounded-lg border border-primary/20 whitespace-pre-wrap">
                        {result.data.reply}
                      </p>
                      <button 
                        onClick={() => copyToClipboard(result.data.reply)}
                        className="absolute top-2 right-2 p-2 rounded-md bg-dark-surface/80 text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity hover:text-white"
                        title="Copy to clipboard"
                      >
                        <Copy size={16} />
                      </button>
                    </div>
                    <div className="flex justify-end">
                      <button 
                        onClick={() => handleAction('reply')}
                        className="flex items-center space-x-2 text-sm text-primary hover:text-primary/80 transition-colors"
                      >
                        <RefreshCw size={14} />
                        <span>Regenerate</span>
                      </button>
                    </div>
                  </div>
                )}


              </div>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-4 opacity-50">
                <Sparkles size={48} className="text-slate-600" />
                <p>Waiting for input...</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;
