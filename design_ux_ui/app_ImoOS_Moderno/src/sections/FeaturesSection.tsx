import { useRef, useLayoutEffect, useState } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { Building2, TrendingUp, Wallet, ArrowRight } from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

const features = [
  {
    icon: Building2,
    title: 'ConstruTech',
    subtitle: 'Gestão de Obra',
    description: 'Controle total do ciclo de construção. Cronogramas, diário de obra, qualidade e segurança em uma plataforma.',
    color: 'neon-blue',
    gradient: 'from-neon-blue/20 to-electric-violet/20',
  },
  {
    icon: TrendingUp,
    title: 'PropTech',
    subtitle: 'Vendas & CRM',
    description: 'Pipeline inteligente de vendas, gestão de leads, reservas digitais e acompanhamento de propostas.',
    color: 'electric-violet',
    gradient: 'from-electric-violet/20 to-hot-pink/20',
  },
  {
    icon: Wallet,
    title: 'FinTech',
    subtitle: 'Financeiro',
    description: 'Cashflow em tempo real, planos de pagamento automatizados, integração bancária e relatórios.',
    color: 'hot-pink',
    gradient: 'from-hot-pink/20 to-neon-blue/20',
  },
];

export default function FeaturesSection() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const titleRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<(HTMLDivElement | null)[]>([]);
  const [hoveredCard, setHoveredCard] = useState<number | null>(null);

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

      // Title entrance
      scrollTl.fromTo(
        titleRef.current,
        { opacity: 0, y: 50 },
        { opacity: 1, y: 0, ease: 'none' },
        0
      );

      // Cards entrance from different directions
      cardsRef.current.forEach((card, index) => {
        if (!card) return;
        const directions = [
          { x: -100, y: 50 },
          { x: 0, y: -100 },
          { x: 100, y: 50 },
        ];
        
        scrollTl.fromTo(
          card,
          { opacity: 0, x: directions[index].x, y: directions[index].y },
          { opacity: 1, x: 0, y: 0, ease: 'none' },
          0.05 * index
        );
      });

      // SETTLE (30-70%): Hold

      // EXIT (70-100%)
      scrollTl.fromTo(
        titleRef.current,
        { opacity: 1, y: 0 },
        { opacity: 0, y: -30, ease: 'power2.in' },
        0.7
      );

      cardsRef.current.forEach((card, index) => {
        if (!card) return;
        scrollTl.fromTo(
          card,
          { opacity: 1, y: 0 },
          { opacity: 0, y: 50, ease: 'power2.in' },
          0.7 + index * 0.02
        );
      });
    }, section);

    return () => ctx.revert();
  }, []);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>, index: number) => {
    const card = cardsRef.current[index];
    if (!card) return;

    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    const rotateX = (y - centerY) / 20;
    const rotateY = (centerX - x) / 20;

    gsap.to(card, {
      rotateX: -rotateX,
      rotateY: rotateY,
      duration: 0.3,
      ease: 'power2.out',
    });
  };

  const handleMouseLeave = (index: number) => {
    const card = cardsRef.current[index];
    if (!card) return;

    gsap.to(card, {
      rotateX: 0,
      rotateY: 0,
      duration: 0.5,
      ease: 'power2.out',
    });
    setHoveredCard(null);
  };

  return (
    <section
      ref={sectionRef}
      id="features"
      className="section-pinned bg-deep-space flex items-center justify-center"
    >
      <div className="relative z-10 w-full max-w-7xl mx-auto px-6 lg:px-10">
        {/* Title */}
        <div ref={titleRef} className="text-center mb-16">
          <span className="text-micro text-neon-blue mb-4 block">ECOSSISTEMA INTEGRADO</span>
          <h2 className="font-display text-h1 text-white mb-4">
            A Revolução <span className="gradient-text">PropTech</span>
          </h2>
          <p className="text-body-lg text-white/60 max-w-2xl mx-auto">
            Três pilares tecnológicos transformando o setor imobiliário em Cabo Verde
          </p>
        </div>

        {/* Cards Grid */}
        <div className="grid md:grid-cols-3 gap-6 perspective-1000">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            const isHovered = hoveredCard === index;
            
            return (
              <div
                key={index}
                ref={(el) => { cardsRef.current[index] = el; }}
                onMouseMove={(e) => handleMouseMove(e, index)}
                onMouseEnter={() => setHoveredCard(index)}
                onMouseLeave={() => handleMouseLeave(index)}
                className="preserve-3d cursor-pointer"
                style={{ transformStyle: 'preserve-3d' }}
              >
                <div 
                  className={`glass-card glass-card-hover p-8 h-full relative overflow-hidden transition-all duration-500 ${
                    isHovered ? 'scale-[1.02]' : ''
                  }`}
                >
                  {/* Glow effect on hover */}
                  <div 
                    className={`absolute inset-0 rounded-3xl transition-opacity duration-500 ${
                      isHovered ? 'opacity-100' : 'opacity-0'
                    }`}
                    style={{
                      background: `radial-gradient(circle at 50% 0%, rgba(${feature.color === 'neon-blue' ? '0, 212, 255' : feature.color === 'electric-violet' ? '124, 58, 237' : '236, 72, 153'}, 0.2), transparent 70%)`,
                    }}
                  />

                  {/* Content */}
                  <div className="relative">
                    {/* Icon */}
                    <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-6`}>
                      <Icon className={`w-8 h-8 text-${feature.color}`} />
                    </div>

                    {/* Label */}
                    <span className={`text-micro text-${feature.color} mb-2 block`}>
                      {feature.subtitle.toUpperCase()}
                    </span>

                    {/* Title */}
                    <h3 className="font-display text-h3 text-white mb-4">
                      {feature.title}
                    </h3>

                    {/* Description */}
                    <p className="text-body text-white/60 leading-relaxed mb-6">
                      {feature.description}
                    </p>

                    {/* Link */}
                    <button className={`flex items-center gap-2 text-${feature.color} font-medium group`}>
                      Explorar
                      <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </button>
                  </div>

                  {/* Corner accent */}
                  <div 
                    className={`absolute top-0 right-0 w-20 h-20 opacity-20`}
                    style={{
                      background: `linear-gradient(135deg, transparent 50%, rgba(${feature.color === 'neon-blue' ? '0, 212, 255' : feature.color === 'electric-violet' ? '124, 58, 237' : '236, 72, 153'}, 0.3) 50%)`,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
