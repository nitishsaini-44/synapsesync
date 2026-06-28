import React from 'react';
import { Link } from 'react-router-dom';
import { Mail, ExternalLink } from 'lucide-react';

import { openMail } from '../../utils/mailHelper';

const handleEmailClick = () => {
  openMail({
    to: 'nitishsaini044@gmail.com',
    subject: 'SynapseSync General Inquiry',
    body: `Hello Nitish,

I am reaching out regarding SynapseSync.

How can you help me today? 
[Type your message here...]

Thank you.`,
  });
};

const Footer = () => {
  const year = new Date().getFullYear();

  return (
    <footer className="bg-surface-card border-t border-border">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-12">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-10 mb-10">
          {/* Brand */}
          <div className="sm:col-span-2 lg:col-span-1">
            <div className="flex items-center gap-2.5 mb-3">
              <div className="w-9 h-9 rounded-2xl bg-primary flex items-center justify-center">
                <span className="text-white font-bold text-base">S</span>
              </div>
              <span className="text-lg font-bold text-heading">SynapseSync</span>
            </div>
            <p className="text-sm text-muted leading-relaxed max-w-xs">
              AI-powered email intelligence that classifies, summarizes, and automates your inbox workflows.
            </p>
            <div className="flex items-center gap-3 mt-5">
              <button
                onClick={handleEmailClick}
                className="w-9 h-9 rounded-full bg-surface-bg border border-border flex items-center justify-center text-muted hover:text-heading hover:border-primary/30 transition-all"
                aria-label="Email"
              >
                <Mail size={16} />
              </button>
              <a
                href="https://facebook.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-9 h-9 rounded-full bg-surface-bg border border-border flex items-center justify-center text-muted hover:text-heading hover:border-primary/30 transition-all"
                aria-label="Facebook"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"></path>
                </svg>
              </a>
              <a
                href="https://instagram.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-9 h-9 rounded-full bg-surface-bg border border-border flex items-center justify-center text-muted hover:text-heading hover:border-primary/30 transition-all"
                aria-label="Instagram"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect>
                  <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path>
                  <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line>
                </svg>
              </a>
            </div>
          </div>

          {/* Product */}
          <div>
            <h4 className="text-sm font-semibold text-heading mb-4">Product</h4>
            <ul className="space-y-2.5">
              {[
                { label: 'Features', href: '#features' },
                { label: 'How It Works', href: '#how-it-works' },
                { label: 'Pricing', href: '#pricing' },
                { label: 'FAQ', href: '#faq' },
              ].map((l) => (
                <li key={l.label}>
                  <a
                    href={l.href}
                    onClick={(e) => {
                      e.preventDefault();
                      document.querySelector(l.href)?.scrollIntoView({ behavior: 'smooth' });
                    }}
                    className="text-sm text-muted hover:text-primary transition-colors"
                  >
                    {l.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Platform */}
          <div>
            <h4 className="text-sm font-semibold text-heading mb-4">Platform</h4>
            <ul className="space-y-2.5">
              {[
                { label: 'Dashboard', to: '/' },
                { label: 'AI Assistant', to: '/assistant' },
                { label: 'Lead Management', to: '/leads' },
                { label: 'Integrations', to: '/integrations' },
              ].map((l) => (
                <li key={l.label}>
                  <Link
                    to={l.to}
                    className="text-sm text-muted hover:text-primary transition-colors"
                  >
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="text-sm font-semibold text-heading mb-4">Resources</h4>
            <ul className="space-y-2.5">
              {[
                { label: 'Quick Start Guide', href: '#' },
                { label: 'Help Center', href: '#' },
                { label: 'Video Tutorials', href: '#' },
                { label: 'Community Forum', href: '#' }
              ].map((l) => (
                <li key={l.label}>
                  <a href={l.href} className="text-sm text-muted hover:text-primary transition-colors">
                    {l.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-6 border-t border-divider flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-muted">
          <span>© {year} SynapseSync. All rights reserved.</span>
          <div className="flex items-center gap-5">
            <a href="#" className="hover:text-primary transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-primary transition-colors">Terms of Service</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
