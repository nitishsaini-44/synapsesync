import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown } from 'lucide-react';

const faqs = [
  {
    q: 'How does SynapseSync connect to Gmail?',
    a: 'We use Google’s official, secure login system to connect to your inbox. You sign in directly through Google, so we never see or store your Gmail password. You stay in full control and can safely disconnect your account at any time with a single click.',
  },
  {
    q: 'Which AI model powers the classification?',
    a: 'SynapseSync uses Groq-hosted Llama 3.1 for email classification, summarization, and AI-reply generation. Groq provides ultra-fast inference so emails are processed in milliseconds.',
  },
  {
    q: 'How do Discord notifications work?',
    a: 'You paste a Discord Webhook URL in the Integrations page. Whenever SynapseSync detects a sales lead or urgent email, it sends a beautifully formatted message to your chosen Discord channel instantly.',
  },
  {
    q: 'Is my email data private and secure?',
    a: 'Absolutely. While we do store your emails and sensitive information to provide our features, everything is kept strictly in an encrypted format using industry-standard security. We never sell or share your data with third parties, ensuring your privacy is always protected.',
  },
  {
    q: 'How do I get started with SynapseSync?',
    a: 'Getting started is easy! Simply create a free account, click Connect Gmail on your integrations page, and our AI will immediately begin analyzing and organizing your incoming emails.',
  },
  {
    q: 'What happens if an email is misclassified?',
    a: 'We use the highly advanced Llama 3.1 model to analyze your emails, and we are constantly refining our prompts to make the AI smarter and more accurate every single day. So don\'t worry!.',
  },
];

const FAQ = () => {
  const [openIndex, setOpenIndex] = useState(null);

  const toggle = (i) => setOpenIndex(openIndex === i ? null : i);

  return (
    <section id="faq" className="py-20 md:py-28 bg-surface-bg">
      <div className="max-w-3xl mx-auto px-4 sm:px-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl sm:text-4xl font-bold text-heading tracking-tight">
            Frequently Asked Questions
          </h2>
          <p className="mt-3 text-muted text-lg">
            Everything you need to know about SynapseSync.
          </p>
        </motion.div>

        {/* Accordion */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true, margin: '-60px' }}
          transition={{ duration: 0.4 }}
          className="space-y-3"
        >
          {faqs.map((faq, i) => (
            <div
              key={i}
              className={`bg-surface-card border rounded-card overflow-hidden transition-all duration-200 ${
                openIndex === i ? 'border-primary/20 shadow-card' : 'border-border shadow-card'
              }`}
            >
              <button
                onClick={() => toggle(i)}
                className="w-full flex items-center justify-between gap-4 p-5 text-left"
                aria-expanded={openIndex === i}
              >
                <span className="font-semibold text-heading text-[15px]">{faq.q}</span>
                <motion.div
                  animate={{ rotate: openIndex === i ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                  className="flex-shrink-0 text-muted"
                >
                  <ChevronDown size={18} />
                </motion.div>
              </button>

              <AnimatePresence initial={false}>
                {openIndex === i && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.25, ease: 'easeInOut' }}
                  >
                    <div className="px-5 pb-5 text-sm text-muted leading-relaxed border-t border-divider pt-3">
                      {faq.a}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default FAQ;
