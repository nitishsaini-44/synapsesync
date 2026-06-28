import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Check, Zap, Star } from 'lucide-react';

const plans = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    description: 'Perfect for personal use and getting started.',
    cta: 'Get Started Free',
    ctaLink: '/register',
    highlighted: false,
    features: [
      'Up to 100 emails/month',
      'AI classification',
      'Basic dashboard',
      'Gmail integration',
      'Community support',
    ],
  },
  {
    name: 'Pro',
    price: '$19',
    period: 'per month',
    description: 'For professionals who need full AI power.',
    cta: 'Start Pro Free',
    ctaLink: '/register',
    highlighted: true,
    badge: 'Most Popular',
    features: [
      'Unlimited emails',
      'Advanced AI classification',
      'Lead detection & scoring',
      'Discord webhook alerts',
      'AI-suggested replies',
      'Smart summaries',
      'Priority support',
      'Analytics export',
    ],
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: 'contact us',
    description: 'For teams needing scale and custom integrations.',
    cta: 'Contact Sales',
    ctaLink: 'mailto:nitishsaini044@gmail.com?subject=SynapseSync Enterprise',
    highlighted: false,
    features: [
      'Everything in Pro',
      'Custom integrations',
      'SSO & team accounts',
      'SLA guarantees',
      'Dedicated support',
      'On-premise option',
    ],
  },
];

const Pricing = () => {
  return (
    <section id="pricing" className="py-20 md:py-28">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.5 }}
          className="text-center mb-14"
        >
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-primary-light border border-primary/20 rounded-full text-primary text-xs font-semibold mb-4">
            <Zap size={11} />
            Simple Pricing
          </span>
          <h2 className="text-3xl sm:text-4xl font-bold text-heading tracking-tight">
            Start Free, Scale as You Grow
          </h2>
          <p className="mt-3 text-muted text-lg max-w-xl mx-auto">
            No hidden fees. Cancel anytime.
          </p>
        </motion.div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
          {plans.map((plan, i) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-60px' }}
              transition={{ duration: 0.45, delay: i * 0.1 }}
              className={`relative flex flex-col rounded-card p-7 border transition-all duration-300 ${
                plan.highlighted
                  ? 'bg-primary border-primary shadow-modal scale-[1.02]'
                  : 'bg-surface-card border-border shadow-card hover:shadow-card-hover hover:border-primary/20'
              }`}
            >
              {/* Badge */}
              {plan.badge && (
                <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
                  <span className="inline-flex items-center gap-1 px-3 py-1 bg-surface-card border border-primary/30 rounded-full text-primary text-xs font-bold shadow-card">
                    <Star size={10} className="fill-primary" />
                    {plan.badge}
                  </span>
                </div>
              )}

              {/* Plan Info */}
              <div className="mb-6">
                <h3 className={`text-lg font-bold mb-1 ${plan.highlighted ? 'text-white' : 'text-heading'}`}>
                  {plan.name}
                </h3>
                <p className={`text-sm mb-4 ${plan.highlighted ? 'text-white/70' : 'text-muted'}`}>
                  {plan.description}
                </p>
                <div className="flex items-end gap-1.5">
                  <span className={`text-4xl font-bold ${plan.highlighted ? 'text-white' : 'text-heading'}`}>
                    {plan.price}
                  </span>
                  <span className={`text-sm pb-1 ${plan.highlighted ? 'text-white/60' : 'text-muted'}`}>
                    / {plan.period}
                  </span>
                </div>
              </div>

              {/* CTA */}
              {plan.name === 'Enterprise' ? (
                <a
                  href={plan.ctaLink}
                  className={`w-full flex items-center justify-center py-2.5 px-4 rounded-button font-semibold text-sm transition-all mb-6 ${
                    plan.highlighted
                      ? 'bg-white text-primary hover:bg-white/90'
                      : 'bg-surface-bg text-heading border border-border hover:border-primary/30 hover:bg-surface-card'
                  }`}
                >
                  {plan.cta}
                </a>
              ) : (
                <Link
                  to={plan.ctaLink}
                  className={`w-full flex items-center justify-center py-2.5 px-4 rounded-button font-semibold text-sm transition-all mb-6 ${
                    plan.highlighted
                      ? 'bg-white text-primary hover:bg-white/90'
                      : 'bg-primary text-white hover:bg-primary-hover'
                  }`}
                >
                  {plan.cta}
                </Link>
              )}

              {/* Features */}
              <ul className="space-y-2.5">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-2.5 text-sm">
                    <Check
                      size={15}
                      className={`flex-shrink-0 mt-0.5 ${plan.highlighted ? 'text-white/80' : 'text-success'}`}
                    />
                    <span className={plan.highlighted ? 'text-white/80' : 'text-body'}>{f}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Pricing;
