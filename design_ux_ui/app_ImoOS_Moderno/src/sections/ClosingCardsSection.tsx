import { useRef, useLayoutEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { ArrowRight, GraduationCap, HeadphonesIcon } from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

export default function ClosingCardsSection() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const leftCardRef = useRef<HTMLDivElement>(null);
  const topRightCardRef = useRef<HTMLDivElement>(null);
  const bottomRightCardRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const section = sectionRef.current;
    if (!section) return;

    const ctx = gsap.context(() => {
      const scrollTl = gsap.timeline({
        scrollTrigger: {
          trigger: section,
          start: 'top top',
          end: '+=130%',
          pin: true,
          scrub: 0.6,
        },
      });

      // ENTRANCE (0-30%)
      scrollTl.fromTo(
        leftCardRef.current,
        { x: '-55vw', opacity: 0 },
        { x: 0, opacity: 1, ease: 'none' },
        0
      );

      scrollTl.fromTo(
        topRightCardRef.current,
        { x: '55vw', y: '-35vh', opacity: 0 },
        { x: 0, y: 0, opacity: 1, ease: 'none' },
        0
      );

      scrollTl.fromTo(
        bottomRightCardRef.current,
        { x: '55vw', y: '35vh', opacity: 0 },
        { x: 0, y: 0, opacity: 1, ease: 'none' },
        0
      );

      // CTA button scale
      const ctaButton = leftCardRef.current?.querySelector('.cta-button');
      if (ctaButton) {
        scrollTl.fromTo(
          ctaButton,
          { scale: 0.96, opacity: 0 },
          { scale: 1, opacity: 1, ease: 'none' },
          0.18
        );
      }

      // SETTLE (30-70%): Hold

      // EXIT (70-100%)
      scrollTl.fromTo(
        leftCardRef.current,
        { x: 0, opacity: 1 },
        { x: '-18vw', opacity: 0, ease: 'power2.in' },
        0.7
      );

      scrollTl.fromTo(
        topRightCardRef.current,
        { x: 0, y: 0, opacity: 1 },
        { x: '18vw', y: '-12vh', opacity: 0, ease: 'power2.in' },
        0.7
      );

      scrollTl.fromTo(
        bottomRightCardRef.current,
        { x: 0, y: 0, opacity: 1 },
        { x: '18vw', y: '12vh', opacity: 0, ease: 'power2.in' },
        0.7
      );
    }, section);

    return () => ctx.revert();
  }, []);

  const scrollToContact = () => {
    const element = document.getElementById('contact');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section
      ref={sectionRef}
      className="imos-section-pinned bg-imos-bg flex items-center justify-center"
    >
      {/* Left Card (Accent) */}
      <div
        ref={leftCardRef}
        className="absolute left-[4vw] top-[14vh] w-[44vw] h-[72vh] bg-imos-accent rounded-3xl shadow-card p-8 flex flex-col justify-center"
      >
        <h2 className="font-heading text-h1 font-light text-white mb-6">
          Pronto para escalar?
        </h2>

        <p className="text-body-lg text-white/80 leading-relaxed mb-8">
          Implementação em dias, não meses. Suporte local em Cabo Verde.
        </p>

        <button
          onClick={scrollToContact}
          className="cta-button bg-white text-imos-accent px-6 py-3 rounded-full font-medium flex items-center gap-2 w-fit hover:gap-3 transition-all"
        >
          Falar com a equipa
          <ArrowRight size={18} />
        </button>
      </div>

      {/* Top-Right Card */}
      <div
        ref={topRightCardRef}
        className="absolute left-[52vw] top-[14vh] w-[44vw] h-[34vh] bg-white rounded-3xl shadow-card p-8 flex flex-col justify-center"
      >
        <div className="w-12 h-12 bg-imos-accent/10 rounded-xl flex items-center justify-center mb-4">
          <GraduationCap className="w-6 h-6 text-imos-accent" />
        </div>

        <h3 className="font-heading text-h2 font-light text-imos-text mb-3">
          Onboarding guiado
        </h3>

        <p className="text-body text-imos-text-secondary leading-relaxed">
          Importação de dados + formação da equipa.
        </p>
      </div>

      {/* Bottom-Right Card */}
      <div
        ref={bottomRightCardRef}
        className="absolute left-[52vw] top-[52vh] w-[44vw] h-[34vh] bg-white rounded-3xl shadow-card p-8 flex flex-col justify-center"
      >
        <div className="w-12 h-12 bg-imos-accent/10 rounded-xl flex items-center justify-center mb-4">
          <HeadphonesIcon className="w-6 h-6 text-imos-accent" />
        </div>

        <h3 className="font-heading text-h2 font-light text-imos-text mb-3">
          Suporte humano
        </h3>

        <p className="text-body text-imos-text-secondary leading-relaxed">
          Resposta em horas úteis, em português.
        </p>
      </div>
    </section>
  );
}
