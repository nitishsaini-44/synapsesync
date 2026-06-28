import React, { useEffect } from 'react';
import LandingNavbar from '../components/landing/LandingNavbar';
import Hero from '../components/landing/Hero';
import Features from '../components/landing/Features';
import HowItWorks from '../components/landing/HowItWorks';
import Pricing from '../components/landing/Pricing';
import FAQ from '../components/landing/FAQ';
import CTA from '../components/landing/CTA';
import Footer from '../components/landing/Footer';

const Landing = () => {
  useEffect(() => {
    // Scroll to top on mount
    window.scrollTo({ top: 0, behavior: 'instant' });
  }, []);

  return (
    <div className="min-h-screen bg-surface-bg font-sans antialiased">
      {/* SEO meta managed here via document.title */}

      <LandingNavbar />

      <main>
        <Hero />

        {/* Subtle divider */}
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <div className="h-px bg-border" />
        </div>

        <Features />

        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <div className="h-px bg-border" />
        </div>

        <HowItWorks />

        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <div className="h-px bg-border" />
        </div>

        <Pricing />

        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <div className="h-px bg-border" />
        </div>

        <FAQ />

        <CTA />
      </main>

      <Footer />
    </div>
  );
};

export default Landing;
