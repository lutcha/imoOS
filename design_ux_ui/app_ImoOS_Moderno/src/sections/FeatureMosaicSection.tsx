import { useRef, useLayoutEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { Building2, TrendingUp, FileCheck, ArrowRight } from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

const features = [
  {
    icon: Building2,
    title: 'Gestão de projetos',
    description:
      'Cronogramas, tarefas e equipas num só lugar—com visibilidade real do progresso.',
    link: 'Explorar',
    accent: false,
  },
  {
    icon: TrendingUp,
    title: 'Vendas & reservas',
    description:
      'Pipeline claro, propostas rápidas e reservas com assinatura digital.',
    link: 'Explorar',
    accent: true,
  },
  {
    icon: FileCheck,
    title: 'Relatórios & compliance',
    description:
      'Métricas de vendas, cash flow e documentação sempre atualizados.',
    link: 'Explorar',
    accent: false,
  },
];

export default function FeatureMosaicSection() {
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
      // Left card from left
      scrollTl.fromTo(
        leftCardRef.current,
        { x: '-55vw', opacity: 0 },
        { x: 0, opacity: 1, ease: 'none' },
        0
      );

      // Top-right card from top-right
      scrollTl.fromTo(
        topRightCardRef.current,
        { x: '55vw', y: '-35vh', opacity: 0 },
        { x: 0, y: 0, opacity: 1, ease: 'none' },
        0
      );

      // Bottom-right card from bottom-right
      scrollTl.fromTo(
        bottomRightCardRef.current,
        { x: '55vw', y: '35vh', opacity: 0 },
        { x: 0, y: 0, opacity: 1, ease: 'none' },
        0
      );

      // Card content stagger
      const allCards = [leftCardRef, topRightCardRef, bottomRightCardRef];
      allCards.forEach((cardRef, index) => {
        const card = cardRef.current;
        if (card) {
          const content = card.querySelectorAll('.card-content');
          scrollTl.fromTo(
            content,
            { opacity: 0, y: 16 },
            { opacity: 1, y: 0, stagger: 0.03, ease: 'none' },
            0.05 + index * 0.02
          );
        }
      });

      // SETTLE (30-70%): Hold - no animation

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
      id="features"
      className="imos-section-pinned bg-imos-bg flex items-center justify-center"
    >
      {/* Left Feature Card */}
      <div
        ref={leftCardRef}
        className="absolute left-[4vw] top-[14vh] w-[44vw] h-[72vh] bg-white rounded-3xl shadow-card p-8 flex flex-col justify-between"
      >
        <div className="card-content">
          <div className="w-12 h-12 bg-imos-accent/10 rounded-xl flex items-center justify-center mb-6">
            <Building2 className="w-6 h-6 text-imos-accent" />
          </div>
        </div>
        <div className="card-content">
          <h3 className="font-heading text-h1 font-light text-imos-text mb-4">
            {features[0].title}
          </h3>
        </div>
        <div className="card-content">
          <p className="text-body text-imos-text-secondary leading-relaxed mb-6">
            {features[0].description}
          </p>
        </div>
        <div className="card-content">
          <button className="flex items-center gap-2 text-imos-accent font-medium hover:gap-3 transition-all">
            {features[0].link}
            <ArrowRight size={18} />
          </button>
        </div>
      </div>

      {/* Top-Right Feature Card (Accent) */}
      <div
        ref={topRightCardRef}
        className="absolute left-[52vw] top-[14vh] w-[44vw] h-[34vh] bg-imos-accent rounded-3xl shadow-card p-8 flex flex-col justify-between"
      >
        <div className="card-content">
          <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center mb-4">
            <TrendingUp className="w-6 h-6 text-white" />
          </div>
        </div>
        <div className="card-content">
          <h3 className="font-heading text-h2 font-light text-white mb-3">
            {features[1].title}
          </h3>
        </div>
        <div className="card-content">
          <p className="text-body text-white/80 leading-relaxed mb-4">
            {features[1].description}
          </p>
        </div>
        <div className="card-content">
          <button className="flex items-center gap-2 text-white font-medium hover:gap-3 transition-all">
            {features[1].link}
            <ArrowRight size={18} />
          </button>
        </div>
      </div>

      {/* Bottom-Right Feature Card */}
      <div
        ref={bottomRightCardRef}
        className="absolute left-[52vw] top-[52vh] w-[44vw] h-[34vh] bg-white rounded-3xl shadow-card p-8 flex flex-col justify-between"
      >
        <div className="card-content">
          <div className="w-12 h-12 bg-imos-accent/10 rounded-xl flex items-center justify-center mb-4">
            <FileCheck className="w-6 h-6 text-imos-accent" />
          </div>
        </div>
        <div className="card-content">
          <h3 className="font-heading text-h2 font-light text-imos-text mb-3">
            {features[2].title}
          </h3>
        </div>
        <div className="card-content">
          <p className="text-body text-imos-text-secondary leading-relaxed mb-4">
            {features[2].description}
          </p>
        </div>
        <div className="card-content">
          <button className="flex items-center gap-2 text-imos-accent font-medium hover:gap-3 transition-all">
            {features[2].link}
            <ArrowRight size={18} />
          </button>
        </div>
      </div>
    </section>
  );
}
