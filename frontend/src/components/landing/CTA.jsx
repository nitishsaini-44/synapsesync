import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, Zap } from 'lucide-react';

const CTA = () => {
  return (
    <section className="py-20 md:py-28">
      <div className="max-w-4xl mx-auto px-4 sm:px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.55 }}
          className="relative overflow-hidden bg-primary rounded-card p-10 md:p-16 text-center"
        >
          {/* Background decoration */}
          <div className="absolute -top-20 -right-20 w-64 h-64 rounded-full bg-white/5 blur-3xl pointer-events-none" />
          <div className="absolute -bottom-16 -left-16 w-48 h-48 rounded-full bg-white/5 blur-2xl pointer-events-none" />

          <div className="relative">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-white/15 rounded-full text-white text-xs font-semibold mb-5">
              <Zap size={12} />
              Start for Free — No credit card required
            </div>

            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white leading-tight tracking-tight">
              Ready to Transform<br className="hidden sm:block" /> Your Inbox?
            </h2>

            <p className="mt-4 text-white/70 text-lg max-w-xl mx-auto">
              Join hundreds of professionals using SynapseSync to manage email smarter with AI.
            </p>

            <div className="mt-8 flex flex-col sm:flex-row gap-3 justify-center">
              <Link
                to="/register"
                className="flex items-center justify-center gap-2 px-7 py-3.5 bg-white text-primary font-bold rounded-button hover:bg-white/95 transition-all shadow-modal active:scale-95 text-[15px]"
              >
                Get Started Free
                <ArrowRight size={16} />
              </Link>
              <Link
                to="/login"
                className="flex items-center justify-center gap-2 px-7 py-3.5 bg-white/10 text-white font-semibold rounded-button border border-white/20 hover:bg-white/20 transition-all text-[15px]"
              >
                Sign In
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default CTA;
