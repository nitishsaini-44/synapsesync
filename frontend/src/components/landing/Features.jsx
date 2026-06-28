import React from 'react';
import { motion } from 'framer-motion';
import {
  Brain, Zap, Mail, Users, BarChart2, MessageSquare,
  Search, Shield, Sparkles, Clock, Bell, Filter
} from 'lucide-react';

const features = [
  {
    icon: Brain,
    title: 'AI Email Classification',
    description: 'Groq Llama 3.1 automatically categorizes every incoming email into Sales, Urgent, Support, or Spam in real time.',
  },
  {
    icon: Users,
    title: 'Lead Detection',
    description: 'Automatically identifies sales opportunities hidden in your inbox and surfaces them instantly on your dashboard.',
  },
  {
    icon: Zap,
    title: 'Workflow Automation',
    description: 'Set up intelligent rules that trigger actions automatically — reply, tag, route, or notify without lifting a finger.',
  },
  {
    icon: MessageSquare,
    title: 'Discord Alerts',
    description: 'Get instant webhook notifications in your Discord server whenever a high-priority email or lead is detected.',
  },
  {
    icon: BarChart2,
    title: 'Live Analytics Dashboard',
    description: 'Track email volume, category distribution, lead counts, and automation performance with real-time charts.',
  },
  {
    icon: Sparkles,
    title: 'AI-Suggested Replies',
    description: 'Generate context-aware email replies with one click, powered by Groq Llama 3.1 for natural language quality.',
  },
  {
    icon: Mail,
    title: 'Smart Summaries',
    description: 'Get crisp AI-generated summaries of long email threads so you can understand context in seconds.',
  },
  {
    icon: Shield,
    title: 'Spam Detection',
    description: 'Intelligent spam filtering keeps your inbox clean. Every flagged email is logged for your review.',
  },
  {
    icon: Bell,
    title: 'Real-time Notifications',
    description: 'Socket.io powered live updates push new email events to your dashboard instantly without page refresh.',
  },
];

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.07 } },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.45, ease: 'easeOut' } },
};

const Features = () => {
  return (
    <section id="features" className="py-20 md:py-28">
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
            <Zap size={11} />
            Everything You Need
          </span>
          <h2 className="text-3xl sm:text-4xl font-bold text-heading tracking-tight">
            Built for the Modern Inbox
          </h2>
          <p className="mt-3 text-muted text-lg max-w-xl mx-auto">
            SynapseSync handles the cognitive load of email management — so you can focus on what matters.
          </p>
        </motion.div>

        {/* Feature Grid */}
        <motion.div
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: '-60px' }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5"
        >
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={feature.title}
                variants={item}
                className="group bg-surface-card border border-border rounded-card p-6 shadow-card hover:shadow-card-hover hover:border-primary/20 transition-all duration-300 cursor-default"
              >
                <div className="w-11 h-11 bg-primary-light rounded-2xl flex items-center justify-center text-primary mb-4 group-hover:bg-primary group-hover:text-white transition-all duration-300">
                  <Icon size={20} />
                </div>
                <h3 className="text-base font-semibold text-heading mb-2">{feature.title}</h3>
                <p className="text-sm text-muted leading-relaxed">{feature.description}</p>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
};

export default Features;
