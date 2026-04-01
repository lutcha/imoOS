import { useEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { Toaster } from 'sonner';
import Navigation from './components/Navigation';
import ParticleBackground from './components/ParticleBackground';
import AnimatedGradient from './components/AnimatedGradient';
import HeroSection from './sections/HeroSection';
import TrustSection from './sections/TrustSection';
import FeaturesSection from './sections/FeaturesSection';
import DashboardSection from './sections/DashboardSection';
import StatsSection from './sections/StatsSection';
import PricingSection from './sections/PricingSection';
import IntegrationsSection from './sections/IntegrationsSection';
import TestimonialsSection from './sections/TestimonialsSection';
import FAQSection from './sections/FAQSection';
import ContactSection from './sections/ContactSection';
import FooterSection from './sections/FooterSection';
import './App.css';

gsap.registerPlugin(ScrollTrigger);

function App() {
  const [navScrolled, setNavScrolled] = useState(false);
  const mainRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleScroll = () => {
      setNavScrolled(window.scrollY > 100);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    // Global snap configuration for pinned sections
    const setupGlobalSnap = () => {
      const pinned = ScrollTrigger.getAll()
        .filter(st => st.vars.pin)
        .sort((a, b) => a.start - b.start);
      
      const maxScroll = ScrollTrigger.maxScroll(window);
      if (!maxScroll || pinned.length === 0) return;

      const pinnedRanges = pinned.map(st => ({
        start: st.start / maxScroll,
        end: (st.end ?? st.start) / maxScroll,
        center: (st.start + ((st.end ?? st.start) - st.start) * 0.5) / maxScroll,
      }));

      ScrollTrigger.create({
        snap: {
          snapTo: (value: number) => {
            const inPinned = pinnedRanges.some(
              r => value >= r.start - 0.02 && value <= r.end + 0.02
            );
            if (!inPinned) return value;

            const target = pinnedRanges.reduce(
              (closest, r) =>
                Math.abs(r.center - value) < Math.abs(closest - value)
                  ? r.center
                  : closest,
              pinnedRanges[0]?.center ?? 0
            );
            return target;
          },
          duration: { min: 0.15, max: 0.35 },
          delay: 0,
          ease: 'power2.out',
        },
      });
    };

    const timer = setTimeout(setupGlobalSnap, 500);

    return () => {
      clearTimeout(timer);
      ScrollTrigger.getAll().forEach(st => st.kill());
    };
  }, []);

  return (
    <div className="relative min-h-screen bg-deep-space">
      {/* Toast notifications */}
      <Toaster 
        position="top-right" 
        theme="dark"
        toastOptions={{
          style: {
            background: 'rgba(17, 17, 24, 0.95)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            color: '#fff',
          },
        }}
      />

      {/* Background effects */}
      <AnimatedGradient />
      <ParticleBackground />

      {/* Noise overlay */}
      <div className="noise-overlay" aria-hidden="true" />

      {/* Navigation */}
      <Navigation scrolled={navScrolled} />

      {/* Main content */}
      <main ref={mainRef} className="relative">
        {/* Section 1: Hero - z-10 */}
        <div className="relative z-10">
          <HeroSection />
        </div>

        {/* Section 2: Trust Signals - z-20 */}
        <div className="relative z-20">
          <TrustSection />
        </div>

        {/* Section 3: Features - z-30 */}
        <div className="relative z-30">
          <FeaturesSection />
        </div>

        {/* Section 4: Dashboard - z-40 */}
        <div className="relative z-40">
          <DashboardSection />
        </div>

        {/* Section 5: Stats - z-50 */}
        <div className="relative z-50">
          <StatsSection />
        </div>

        {/* Section 6: Pricing - z-[60] */}
        <div className="relative z-[60]">
          <PricingSection />
        </div>

        {/* Section 7: Integrations - z-[70] */}
        <div className="relative z-[70]">
          <IntegrationsSection />
        </div>

        {/* Section 8: Testimonials - z-[80] */}
        <div className="relative z-[80]">
          <TestimonialsSection />
        </div>

        {/* Section 9: FAQ - z-[90] */}
        <div className="relative z-[90]">
          <FAQSection />
        </div>

        {/* Section 10: Contact - z-[100] */}
        <div className="relative z-[100]">
          <ContactSection />
        </div>

        {/* Section 11: Footer - z-[110] */}
        <div className="relative z-[110]">
          <FooterSection />
        </div>
      </main>
    </div>
  );
}

export default App;
