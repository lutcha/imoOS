import { useRef, useLayoutEffect, useState, useEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { Building2, Users, Clock, TrendingUp } from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

const stats = [
  { 
    icon: Building2, 
    value: 2000, 
    suffix: '+', 
    label: 'Unidades Geridas',
    description: 'Apartamentos, moradias e lotes',
    color: 'neon-blue',
  },
  { 
    icon: Users, 
    value: 120, 
    suffix: '+', 
    label: 'Projetos Ativos',
    description: 'Em todas as ilhas de Cabo Verde',
    color: 'electric-violet',
  },
  { 
    icon: TrendingUp, 
    value: 98, 
    suffix: '%', 
    label: 'Satisfação',
    description: 'Baseado em avaliações de clientes',
    color: 'hot-pink',
  },
  { 
    icon: Clock, 
    value: 24, 
    suffix: 'h', 
    label: 'Suporte',
    description: 'Resposta em horas úteis',
    color: 'neon-blue',
  },
];

function AnimatedCounter({ value, suffix }: { value: number; suffix: string }) {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);
  const hasAnimated = useRef(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !hasAnimated.current) {
            hasAnimated.current = true;
            const duration = 2500;
            const startTime = Date.now();

            const animate = () => {
              const elapsed = Date.now() - startTime;
              const progress = Math.min(elapsed / duration, 1);
              const easeProgress = 1 - Math.pow(1 - progress, 4);
              const currentValue = Math.floor(value * easeProgress);
              setCount(currentValue);

              if (progress < 1) {
                requestAnimationFrame(animate);
              }
            };

            requestAnimationFrame(animate);
          }
        });
      },
      { threshold: 0.5 }
    );

    observer.observe(element);
    return () => observer.disconnect();
  }, [value]);

  return (
    <span ref={ref} className="font-display text-5xl lg:text-6xl font-bold text-white">
      {count.toLocaleString()}{suffix}
    </span>
  );
}

export default function StatsSection() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<(HTMLDivElement | null)[]>([]);

  useLayoutEffect(() => {
    const section = sectionRef.current;
    if (!section) return;

    const ctx = gsap.context(() => {
      // Entrance animation
      cardsRef.current.forEach((card, index) => {
        if (!card) return;

        gsap.fromTo(
          card,
          { opacity: 0, y: 60, rotateX: 20 },
          {
            opacity: 1,
            y: 0,
            rotateX: 0,
            duration: 0.8,
            delay: index * 0.15,
            ease: 'power3.out',
            scrollTrigger: {
              trigger: section,
              start: 'top 80%',
              toggleActions: 'play none none reverse',
            },
          }
        );
      });
    }, section);

    return () => ctx.revert();
  }, []);

  // Independent floating animation for each card
  useEffect(() => {
    cardsRef.current.forEach((card, index) => {
      if (!card) return;

      gsap.to(card, {
        y: `-=${10 + index * 3}`,
        duration: 3 + index * 0.5,
        ease: 'sine.inOut',
        yoyo: true,
        repeat: -1,
        delay: index * 0.3,
      });
    });
  }, []);

  return (
    <section
      ref={sectionRef}
      className="relative bg-deep-space py-24 overflow-hidden"
    >
      {/* Background glow */}
      <div 
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full pointer-events-none"
        style={{
          background: 'radial-gradient(circle, rgba(0, 212, 255, 0.1) 0%, transparent 60%)',
          filter: 'blur(60px)',
        }}
      />

      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-10">
        {/* Header */}
        <div className="text-center mb-16">
          <span className="text-micro text-hot-pink mb-4 block">RESULTADOS REAIS</span>
          <h2 className="font-display text-h1 text-white mb-4">
            Números que <span className="gradient-text">Falam</span>
          </h2>
          <p className="text-body-lg text-white/60 max-w-2xl mx-auto">
            A confiança de dezenas de promotoras e construtoras em todo o arquipélago
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 perspective-1000">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            
            return (
              <div
                key={index}
                ref={(el) => { cardsRef.current[index] = el; }}
                className="preserve-3d"
              >
                <div className="glass-card glass-card-hover p-8 text-center h-full relative overflow-hidden group">
                  {/* Glow on hover */}
                  <div 
                    className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                    style={{
                      background: `radial-gradient(circle at 50% 0%, rgba(${stat.color === 'neon-blue' ? '0, 212, 255' : stat.color === 'electric-violet' ? '124, 58, 237' : '236, 72, 153'}, 0.15), transparent 70%)`,
                    }}
                  />

                  <div className="relative">
                    {/* Icon */}
                    <div className={`w-16 h-16 mx-auto rounded-2xl bg-${stat.color}/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                      <Icon className={`w-8 h-8 text-${stat.color}`} />
                    </div>

                    {/* Value */}
                    <div className="mb-2">
                      <AnimatedCounter value={stat.value} suffix={stat.suffix} />
                    </div>

                    {/* Label */}
                    <h3 className="font-display text-lg font-semibold text-white mb-2">
                      {stat.label}
                    </h3>

                    {/* Description */}
                    <p className="text-small text-white/50">
                      {stat.description}
                    </p>
                  </div>

                  {/* Corner accent */}
                  <div 
                    className="absolute bottom-0 right-0 w-16 h-16 opacity-10"
                    style={{
                      background: `linear-gradient(315deg, transparent 50%, rgba(${stat.color === 'neon-blue' ? '0, 212, 255' : stat.color === 'electric-violet' ? '124, 58, 237' : '236, 72, 153'}, 0.5) 50%)`,
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
