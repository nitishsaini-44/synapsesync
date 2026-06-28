import React from 'react';
import { motion } from 'framer-motion';
import { Mail, Brain, Filter, LayoutDashboard } from 'lucide-react';

const steps = [
  {
    number: '01',
    icon: Mail,
    title: 'Connect Gmail',
    description: 'Authorize SynapseSync with your Gmail account via OAuth 2.0. We use Gmail Push API and Google Pub/Sub for real-time email events.',
    color: 'text-primary',
    bg: 'bg-primary-light',
    border: 'border-primary/20',
  },
  {
    number: '02',
    icon: Brain,
    title: 'AI Reads Your Emails',
    description: 'Groq Llama 3.1 processes every incoming email in milliseconds, extracting context, intent, and identifying key signals.',
    color: 'text-success',
    bg: 'bg-success-light',
    border: 'border-success/20',
  },
  {
    number: '03',
    icon: Filter,
    title: 'Smart Classification',
    description: 'Each email is categorized as Sales Lead, Urgent, Support, or Spam. Leads are scored and added to your pipeline automatically.',
    color: 'text-warning',
    bg: 'bg-warning-light',
    border: 'border-warning/20',
  },
  {
    number: '04',
    icon: LayoutDashboard,
    title: 'Dashboard Updates',
    description: 'Your dashboard and Discord channel update in real time via Socket.io — giving you full visibility and instant notifications.',
    color: 'text-primary',
    bg: 'bg-primary-light',
    border: 'border-primary/20',
  },
];

const HowItWorks = () => {
  return (
    <section id="how-it-works" className="py-20 md:py-28 bg-surface-bg">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.5 }}
          className="text-center mb-14"
        >
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-primary-light border border-primary/20 rounded-full text-primary text-xs font-semibold mb-4">
            Simple Process
          </span>
          <h2 className="text-3xl sm:text-4xl font-bold text-heading tracking-tight">
            Set Up in Minutes
          </h2>
          <p className="mt-3 text-muted text-lg max-w-xl mx-auto">
            Connect once. SynapseSync handles everything else automatically from there.
          </p>
        </motion.div>

        {/* Steps */}
        <div className="relative">
          {/* Connecting line — desktop */}
          <div className="hidden lg:block absolute top-[52px] left-[calc(12.5%+24px)] right-[calc(12.5%+24px)] h-px bg-border" />

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-6">
            {steps.map((step, i) => {
              const Icon = step.icon;
              return (
                <motion.div
                  key={step.number}
                  initial={{ opacity: 0, y: 24 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: '-60px' }}
                  transition={{ duration: 0.45, delay: i * 0.1 }}
                  className="flex flex-col items-center text-center lg:items-center"
                >
                  {/* Icon circle */}
                  <div className={`relative w-14 h-14 ${step.bg} border-2 ${step.border} rounded-full flex items-center justify-center mb-5 shadow-card`}>
                    <Icon size={22} className={step.color} />
                    {/* Step number badge */}
                    <span className="absolute -top-2 -right-2 w-5 h-5 bg-primary text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                      {i + 1}
                    </span>
                  </div>

                  <h3 className="text-base font-semibold text-heading mb-2">{step.title}</h3>
                  <p className="text-sm text-muted leading-relaxed">{step.description}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
