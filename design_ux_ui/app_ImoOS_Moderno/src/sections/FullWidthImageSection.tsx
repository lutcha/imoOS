import { useRef, useLayoutEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { DollarSign } from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

export default function FullWidthImageSection() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLDivElement>(null);
  const textRef = useRef<HTMLDivElement>(null);
  const pillRef = useRef<HTMLDivElement>(null);

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
      // Image from bottom
      scrollTl.fromTo(
        imageRef.current,
        { y: '100vh', opacity: 0 },
        { y: 0, opacity: 1, ease: 'none' },
        0
      );

      // Text overlay
      scrollTl.fromTo(
        textRef.current,
        { y: '6vh', opacity: 0 },
        { y: 0, opacity: 1, ease: 'none' },
        0.12
      );

      // Pill
      scrollTl.fromTo(
        pillRef.current,
        { x: '6vw', opacity: 0 },
        { x: 0, opacity: 1, ease: 'none' },
        0.16
      );

      // SETTLE (30-70%): Hold

      // EXIT (70-100%)
      scrollTl.fromTo(
        imageRef.current,
        { scale: 1, opacity: 1 },
        { scale: 1.06, opacity: 0, ease: 'power2.in' },
        0.7
      );

      scrollTl.fromTo(
        textRef.current,
        { y: 0, opacity: 1 },
        { y: '-6vh', opacity: 0, ease: 'power2.in' },
        0.72
      );

      scrollTl.fromTo(
        pillRef.current,
        { opacity: 1 },
        { opacity: 0, ease: 'power2.in' },
        0.75
      );
    }, section);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="imos-section-pinned bg-imos-bg flex items-center justify-center"
    >
      {/* Full-bleed image card */}
      <div
        ref={imageRef}
        className="absolute left-[4vw] top-[10vh] w-[92vw] h-[80vh] rounded-3xl overflow-hidden shadow-card"
      >
        <img
          src="https://images.unsplash.com/photo-1503387762-592deb58ef4e?w=1600&h=900&fit=crop"
          alt="Blueprints and planning"
          className="w-full h-full object-cover"
        />

        {/* Dark gradient overlay for text readability */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />

        {/* Text overlay */}
        <div
          ref={textRef}
          className="absolute left-[4vw] bottom-[12vh] max-w-lg"
        >
          <h2 className="font-heading text-h1 font-light text-white mb-4">
            Orçamento sob controlo.
          </h2>
          <p className="text-body-lg text-white/80 leading-relaxed">
            Acompanhe custos por lote, por fase e por categoria—em tempo real.
          </p>
        </div>

        {/* Accent Pill */}
        <div
          ref={pillRef}
          className="absolute right-[4vw] bottom-[8vh] bg-white/90 backdrop-blur-sm px-4 py-2 rounded-full flex items-center gap-2"
        >
          <div className="w-8 h-8 bg-imos-accent/10 rounded-full flex items-center justify-center">
            <DollarSign className="w-4 h-4 text-imos-accent" />
          </div>
          <span className="font-mono text-label text-imos-text">
            CONTROLO DE CUSTOS
          </span>
        </div>
      </div>
    </section>
  );
}
