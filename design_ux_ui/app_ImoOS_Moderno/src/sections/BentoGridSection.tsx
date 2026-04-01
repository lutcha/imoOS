import { useRef, useLayoutEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import {
  Users,
  Calendar,
  FileSignature,
  CreditCard,
  HardHat,
  BarChart3,
  ArrowRight,
} from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

const bentoItems = [
  {
    icon: Users,
    title: 'Gestão de leads',
    description: 'Capture, qualifique e distribua leads pela equipa comercial.',
    accent: false,
  },
  {
    icon: Calendar,
    title: 'Agenda de visitas',
    description: 'Marcações sincronizadas com disponibilidade de unidades.',
    accent: false,
  },
  {
    icon: FileSignature,
    title: 'Contratos digitais',
    description: 'Modele, gere versões e colete assinaturas online.',
    accent: false,
  },
  {
    icon: CreditCard,
    title: 'Plano de pagamentos',
    description: 'Prestações automáticas com alertas e recibos.',
    accent: false,
  },
  {
    icon: HardHat,
    title: 'Diário de obra',
    description: 'Registos diários, fotos e não conformidades.',
    accent: false,
  },
  {
    icon: BarChart3,
    title: 'Analytics',
    description: 'Métricas de conversão, cash flow e previsões.',
    accent: true,
  },
];

export default function BentoGridSection() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<(HTMLDivElement | null)[]>([]);

  useLayoutEffect(() => {
    const section = sectionRef.current;
    if (!section) return;

    const ctx = gsap.context(() => {
      cardsRef.current.forEach((card, index) => {
        if (!card) return;

        gsap.fromTo(
          card,
          { y: '8vh', opacity: 0 },
          {
            y: 0,
            opacity: 1,
            ease: 'power2.out',
            scrollTrigger: {
              trigger: section,
              start: `top ${80 - index * 5}%`,
              end: `top ${40 - index * 5}%`,
              scrub: 0.5,
            },
          }
        );
      });
    }, section);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="imos-section bg-imos-bg py-[10vh] px-[4vw]"
    >
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-12">
          <h2 className="font-heading text-h1 font-light text-imos-text mb-4">
            Tudo o que precisa.
          </h2>
          <p className="text-body-lg text-imos-text-secondary max-w-2xl mx-auto">
            Um sistema completo que acompanha todo o ciclo de vida do seu
            projeto imobiliário.
          </p>
        </div>

        {/* Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {bentoItems.map((item, index) => {
            const Icon = item.icon;
            return (
              <div
                key={index}
                ref={(el) => { cardsRef.current[index] = el; }}
                className={`${
                  item.accent
                    ? 'bg-imos-accent text-white'
                    : 'bg-white text-imos-text'
                } rounded-3xl shadow-card p-6 flex flex-col justify-between min-h-[240px] transition-transform duration-300 hover:-translate-y-1`}
              >
                <div>
                  <div
                    className={`w-10 h-10 ${
                      item.accent ? 'bg-white/20' : 'bg-imos-accent/10'
                    } rounded-xl flex items-center justify-center mb-4`}
                  >
                    <Icon
                      className={`w-5 h-5 ${
                        item.accent ? 'text-white' : 'text-imos-accent'
                      }`}
                    />
                  </div>

                  <h3
                    className={`font-heading text-h2 ${
                      item.accent ? 'text-white' : 'text-imos-text'
                    } mb-2`}
                  >
                    {item.title}
                  </h3>

                  <p
                    className={`text-body leading-relaxed ${
                      item.accent ? 'text-white/80' : 'text-imos-text-secondary'
                    }`}
                  >
                    {item.description}
                  </p>
                </div>

                <button
                  className={`flex items-center gap-2 mt-4 font-medium hover:gap-3 transition-all ${
                    item.accent ? 'text-white' : 'text-imos-accent'
                  }`}
                >
                  Saber mais
                  <ArrowRight size={16} />
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
