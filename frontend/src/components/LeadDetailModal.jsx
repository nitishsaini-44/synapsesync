import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { X, Mail, Sparkles, MessageSquare, Copy, Check, Loader2, RefreshCw } from 'lucide-react';
import UrgencyBadge from './UrgencyBadge';
import { generateReply } from '../api/client';

// Strips HTML tags, collapses long URLs, and normalises whitespace for display only.
// The raw lead.message is still used unchanged for AI reply generation.
const cleanMessageForDisplay = (raw) => {
  if (!raw) return '';

  let text = raw;

  // Remove <style>…</style> and <script>…</script> blocks entirely
  text = text.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, ' ');
  text = text.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, ' ');

  // Strip all remaining HTML tags
  text = text.replace(/<[^>]+>/g, ' ');

  // Decode common HTML entities
  text = text
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, ' ');

  // Replace long URLs (> 60 chars) with a short [link] placeholder
  text = text.replace(/https?:\/\/\S{60,}/g, '[link]');

  // Collapse multiple spaces / tabs to one space
  text = text.replace(/[ \t]+/g, ' ');

  // Collapse 3+ consecutive newlines to two
  text = text.replace(/\n{3,}/g, '\n\n');

  // Trim leading/trailing whitespace from each line, then overall
  text = text
    .split('\n')
    .map((line) => line.trim())
    .filter((line, i, arr) => !(line === '' && arr[i - 1] === ''))  // remove duplicate blank lines
    .join('\n')
    .trim();

  return text || raw; // fallback to raw if cleaning wiped everything
};

const LeadDetailModal = ({ lead, onClose }) => {
  const [copied, setCopied] = useState(null); // 'message' | 'summary' | 'reply'
  const [aiReply, setAiReply] = useState(lead?.ai_reply || null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);

  const handleRegenerate = async () => {
    setIsGenerating(true);
    setError(null);
    try {
      const res = await generateReply(lead.message, lead.category || 'general');
      const text = res.data?.reply || res.data;
      setAiReply(text);
      lead.ai_reply = text; // Cache locally
    } catch (err) {
      console.error("Failed to generate reply", err);
      setError("Failed to generate reply.");
    } finally {
      setIsGenerating(false);
    }
  };

  // Generate reply if missing on mount
  useEffect(() => {
    if (lead && !aiReply && !isGenerating && !error) {
      handleRegenerate();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lead]);

  // Close on Escape key
  useEffect(() => {
    const handleEsc = (e) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handleEsc);
    return () => document.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  // Prevent body scroll
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = ''; };
  }, []);

  if (!lead) return null;

  const copyText = (text, type) => {
    navigator.clipboard.writeText(text);
    setCopied(type);
    setTimeout(() => setCopied(null), 2000);
  };

  const modalContent = (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4" onClick={onClose}>
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/25 backdrop-blur-sm" />

      {/* Modal */}
      <div
        className="relative w-full max-w-2xl max-h-[85vh] bg-surface-card rounded-modal border border-border shadow-modal overflow-hidden flex flex-col animate-fade-in"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-divider flex-shrink-0">
          <div className="flex items-center gap-3 flex-wrap">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-body border border-border capitalize">
              {lead.category || 'Uncategorized'}
            </span>
            <UrgencyBadge level={lead.urgency} />
            {lead.created_at && (
              <span className="text-xs text-muted">
                {new Date(lead.created_at).toLocaleString()}
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className="w-9 h-9 flex items-center justify-center rounded-xl text-muted hover:text-heading hover:bg-gray-100 transition-colors flex-shrink-0 ml-3"
            aria-label="Close"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content — scrollable */}
        <div className="flex-1 overflow-y-auto px-6 py-5 space-y-6">

          {/* Original Message */}
          <section>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-gray-100 flex items-center justify-center">
                  <Mail size={14} className="text-body" />
                </div>
                <h3 className="text-sm font-semibold text-heading">Original Message</h3>
              </div>
              {lead.message && (
                <button
                  onClick={() => copyText(lead.message, 'message')}
                  className="p-1.5 rounded-lg text-muted hover:text-heading hover:bg-gray-100 transition-colors"
                  title="Copy message"
                >
                  {copied === 'message' ? <Check size={14} className="text-success" /> : <Copy size={14} />}
                </button>
              )}
            </div>
            <div className="bg-surface-bg rounded-2xl border border-border p-4">
              <p className="text-heading text-[15px] leading-relaxed whitespace-pre-wrap">
                {cleanMessageForDisplay(lead.message) || 'No message available.'}
              </p>
            </div>
          </section>

          {/* AI Summary */}
          <section>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-primary-light flex items-center justify-center">
                  <Sparkles size={14} className="text-primary" />
                </div>
                <h3 className="text-sm font-semibold text-heading">AI Summary</h3>
              </div>
              {lead.summary && (
                <button
                  onClick={() => copyText(lead.summary, 'summary')}
                  className="p-1.5 rounded-lg text-muted hover:text-heading hover:bg-gray-100 transition-colors"
                  title="Copy summary"
                >
                  {copied === 'summary' ? <Check size={14} className="text-success" /> : <Copy size={14} />}
                </button>
              )}
            </div>
            <div className="bg-surface-bg rounded-2xl border border-border p-4">
              <p className="text-heading text-[15px] leading-relaxed">
                {lead.summary || 'No AI summary generated for this message.'}
              </p>
            </div>
          </section>

          {/* AI Reply */}
          <section>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-success-light flex items-center justify-center">
                  <MessageSquare size={14} className="text-success" />
                </div>
                <h3 className="text-sm font-semibold text-heading">AI Generated Reply</h3>
              </div>
              <div className="flex items-center gap-1.5">
                {aiReply && (
                  <button
                    onClick={handleRegenerate}
                    disabled={isGenerating}
                    className="p-1.5 rounded-lg text-muted hover:text-heading hover:bg-gray-100 transition-colors disabled:opacity-50"
                    title="Regenerate reply"
                  >
                    <RefreshCw size={14} className={isGenerating ? "animate-spin" : ""} />
                  </button>
                )}
                {aiReply && (
                  <button
                    onClick={() => copyText(aiReply, 'reply')}
                    className="p-1.5 rounded-lg text-muted hover:text-heading hover:bg-gray-100 transition-colors"
                    title="Copy reply"
                  >
                    {copied === 'reply' ? <Check size={14} className="text-success" /> : <Copy size={14} />}
                  </button>
                )}
              </div>
            </div>
            <div className={`rounded-2xl border p-4 ${aiReply ? 'bg-success-light/50 border-success/10' : 'bg-surface-bg border-border'}`}>
              {isGenerating ? (
                <div className="flex items-center gap-3 text-muted">
                  <Loader2 size={16} className="animate-spin text-success" />
                  <span className="text-[15px]">Generating intelligent reply...</span>
                </div>
              ) : error ? (
                <p className="text-error text-[15px]">{error}</p>
              ) : (
                <p className="text-heading text-[15px] leading-relaxed whitespace-pre-wrap">
                  {aiReply || 'No AI reply has been generated for this message.'}
                </p>
              )}
            </div>
          </section>

        </div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};

export default LeadDetailModal;
