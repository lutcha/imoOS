import { useRef, useLayoutEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { Quote } from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

export default function TestimonialSection() {
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

      // Portrait scale
      const portrait = leftCardRef.current?.querySelector('.portrait');
      if (portrait) {
        scrollTl.fromTo(
          portrait,
          { scale: 1.04, opacity: 0 },
          { scale: 1, opacity: 1, ease: 'none' },
          0.1
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

  return (
    <section
      ref={sectionRef}
      className="imos-section-pinned bg-imos-bg flex items-center justify-center"
    >
      {/* Left Testimonial Card */}
      <div
        ref={leftCardRef}
        className="absolute left-[4vw] top-[14vh] w-[44vw] h-[72vh] bg-white rounded-3xl shadow-card overflow-hidden"
      >
        {/* Portrait Image */}
        <div className="portrait h-[45%] w-full overflow-hidden">
          <img
            src="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=800&h=600&fit=crop"
            alt="Ana Lopes"
            className="w-full h-full object-cover"
          />
        </div>

        {/* Quote Content */}
        <div className="p-8 flex flex-col justify-between h-[55%]">
          <div>
            <Quote className="w-8 h-8 text-imos-accent/30 mb-4" />
            <p className="font-heading text-h2 font-light text-imos-text leading-snug mb-6">
              "ImoOS eliminou as planilhas. Hoje, a equipa comercial e a obra
              falam a mesma língua."
            </p>
          </div>

          <div>
            <p className="font-medium text-imos-text">Ana Lopes</p>
            <p className="text-small text-imos-text-secondary">
              Diretora Comercial, Construtora Horizonte
            </p>
          </div>
        </div>
      </div>

      {/* Top-Right Card (Accent) */}
      <div
        ref={topRightCardRef}
        className="absolute left-[52vw] top-[14vh] w-[44vw] h-[34vh] bg-imos-accent rounded-3xl shadow-card p-8 flex flex-col justify-center"
      >
        <Quote className="w-8 h-8 text-white/30 mb-4" />
        <p className="font-heading text-h1 font-light text-white leading-tight">
          "Reservas em minutos, não em dias."
        </p>
      </div>

      {/* Bottom-Right Card */}
      <div
        ref={bottomRightCardRef}
        className="absolute left-[52vw] top-[52vh] w-[44vw] h-[34vh] bg-white rounded-3xl shadow-card p-8 flex flex-col justify-center"
      >
        <Quote className="w-8 h-8 text-imos-accent/30 mb-4" />
        <p className="font-heading text-h2 font-light text-imos-text leading-snug mb-4">
          "A documentação do projeto finalmente está num só sítio—e acessível ao
          investidor."
        </p>
        <p className="text-small text-imos-text-secondary">
          — Gestor de projeto, Praia
        </p>
      </div>
    </section>
  );
}
