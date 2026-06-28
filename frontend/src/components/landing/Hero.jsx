import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, Zap, Mail, Brain, BarChart2, Shield } from 'lucide-react';

const floatingCards = [
  {
    icon: <Brain size={16} className="text-primary" />,
    label: 'AI Classification',
    value: 'Sales Lead',
    bg: 'bg-primary-light',
    delay: 0,
  },
  {
    icon: <Mail size={16} className="text-success" />,
    label: 'New Email',
    value: 'Priority: Urgent',
    bg: 'bg-success-light',
    delay: 0.15,
  },
  {
    icon: <BarChart2 size={16} className="text-primary" />,
    label: 'Processed Today',
    value: '247 emails',
    bg: 'bg-primary-light',
    delay: 0.3,
  },
  {
    icon: <Shield size={16} className="text-warning" />,
    label: 'Spam Blocked',
    value: '18 filtered',
    bg: 'bg-warning-light',
    delay: 0.45,
  },
];

const features = [
  { icon: <Brain size={15} />, text: 'AI Email Classification' },
  { icon: <Zap size={15} />, text: 'Discord Alerts' },
  { icon: <BarChart2 size={15} />, text: 'Live Analytics' },
];

const Hero = () => {
  return (
    <section className="relative min-h-screen flex items-center overflow-hidden pt-16">
      {/* Background blobs */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-40 -right-40 w-[600px] h-[600px] rounded-full bg-primary/5 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-[500px] h-[500px] rounded-full bg-primary/4 blur-3xl" />
        {/* Subtle grid */}
        <div
          className="absolute inset-0 opacity-[0.025]"
          style={{
            backgroundImage:
              'linear-gradient(#D72660 1px, transparent 1px), linear-gradient(90deg, #D72660 1px, transparent 1px)',
            backgroundSize: '40px 40px',
          }}
        />
      </div>

      <div className="relative max-w-6xl mx-auto px-4 sm:px-6 py-16 md:py-24 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Left — Copy */}
          <div className="text-center lg:text-left">
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-primary-light border border-primary/20 rounded-full text-primary text-xs font-semibold mb-6"
            >
              <Zap size={12} />
              Powered by Groq Llama 3.1
            </motion.div>

            {/* Headline */}
            <motion.h1
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.55, delay: 0.1 }}
              className="text-4xl sm:text-5xl lg:text-[56px] font-bold text-heading leading-tight tracking-tight"
            >
              Your AI Employee{' '}
              <span className="text-primary">for Email</span>{' '}
              Management
            </motion.h1>

            {/* Subheadline */}
            <motion.p
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.55, delay: 0.2 }}
              className="mt-5 text-lg text-muted leading-relaxed max-w-lg mx-auto lg:mx-0"
            >
              SynapseSync automatically classifies emails, detects leads, and
              triggers smart workflows — so you never miss what matters.
            </motion.p>

            {/* Feature pills */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.28 }}
              className="mt-6 flex flex-wrap gap-2 justify-center lg:justify-start"
            >
              {features.map((f) => (
                <span
                  key={f.text}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-surface-card border border-border rounded-full text-xs text-body font-medium shadow-card"
                >
                  <span className="text-primary">{f.icon}</span>
                  {f.text}
                </span>
              ))}
            </motion.div>

            {/* CTA Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.35 }}
              className="mt-8 flex flex-col sm:flex-row gap-3 justify-center lg:justify-start"
            >
              <Link
                to="/register"
                className="flex items-center justify-center gap-2 px-6 py-3 bg-primary text-white font-semibold rounded-button hover:bg-primary-hover transition-all shadow-card hover:shadow-card-hover active:scale-95 text-[15px]"
              >
                Start Free Today
                <ArrowRight size={16} />
              </Link>
              <Link
                to="/login"
                className="flex items-center justify-center gap-2 px-6 py-3 bg-surface-card text-body font-medium rounded-button border border-border hover:border-primary/30 hover:text-heading transition-all text-[15px]"
              >
                Sign In
              </Link>
            </motion.div>

            {/* Trust note */}
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.55 }}
              className="mt-5 text-xs text-muted"
            >
              No credit card required · Gmail OAuth · Privacy first
            </motion.p>
          </div>

          {/* Right — Floating UI Cards */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="relative hidden lg:flex flex-col items-center justify-center min-h-[420px]"
          >
            {/* Main dashboard preview card */}
            <div className="w-full max-w-sm bg-surface-card border border-border rounded-card shadow-modal p-5">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-semibold text-heading">Inbox Overview</span>
                <span className="text-xs px-2.5 py-1 bg-success-light text-success rounded-full font-medium">● Live</span>
              </div>
              <div className="space-y-2.5">
                {[
                  { label: 'Sales Leads', val: 34, color: 'bg-primary', pct: '68%' },
                  { label: 'Urgent', val: 8, color: 'bg-error', pct: '16%' },
                  { label: 'Support', val: 10, color: 'bg-success', pct: '20%' },
                  { label: 'Spam', val: 6, color: 'bg-muted/40', pct: '12%' },
                ].map((row) => (
                  <div key={row.label}>
                    <div className="flex justify-between text-xs text-muted mb-1">
                      <span>{row.label}</span><span>{row.val}</span>
                    </div>
                    <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: row.pct }}
                        transition={{ duration: 1, delay: 0.6 }}
                        className={`h-full rounded-full ${row.color}`}
                      />
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-4 pt-3 border-t border-divider flex items-center justify-between text-xs text-muted">
                <span>Total processed today</span>
                <span className="font-semibold text-heading">247</span>
              </div>
            </div>

            {/* Floating mini cards */}
            {floatingCards.map((card, i) => (
              <motion.div
                key={card.label}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: [0, -6, 0] }}
                transition={{
                  opacity: { duration: 0.4, delay: 0.5 + card.delay },
                  y: { duration: 3, delay: 1 + card.delay, repeat: Infinity, ease: 'easeInOut' },
                }}
                className={`absolute flex items-center gap-2 px-3.5 py-2.5 bg-surface-card border border-border rounded-card shadow-modal text-xs font-medium text-heading ${
                  i === 0 ? '-top-4 -left-10' :
                  i === 1 ? 'top-16 -right-10' :
                  i === 2 ? '-bottom-4 -left-6' :
                  '-bottom-10 right-4'
                }`}
              >
                <div className={`w-7 h-7 rounded-xl ${card.bg} flex items-center justify-center`}>
                  {card.icon}
                </div>
                <div>
                  <div className="text-muted text-[10px] leading-none mb-0.5">{card.label}</div>
                  <div className="text-heading font-semibold">{card.value}</div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
