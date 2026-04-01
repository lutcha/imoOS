import { useRef, useLayoutEffect, useState } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { Check, Sparkles, Building2, Rocket } from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

const plans = [
  {
    name: 'Starter',
    description: 'Para pequenas promotoras',
    price: '29.900',
    priceUnit: 'CVE/mês',
    icon: Building2,
    features: [
      'Até 3 projetos',
      'Até 50 unidades',
      'Gestão de leads básica',
      'Dashboard padrão',
      'Suporte por email',
      'Exportação de relatórios',
    ],
    cta: 'Começar Grátis',
    highlighted: false,
    color: 'neon-blue',
  },
  {
    name: 'Professional',
    description: 'Para promotoras em crescimento',
    price: '79.900',
    priceUnit: 'CVE/mês',
    icon: Sparkles,
    features: [
      'Projetos ilimitados',
      'Até 500 unidades',
      'CRM completo',
      'Dashboard avançado',
      'Integração imo.cv',
      'WhatsApp Business',
      'Suporte prioritário',
      'API de integração',
    ],
    cta: 'Experimentar 14 Dias',
    highlighted: true,
    color: 'electric-violet',
    badge: 'MAIS POPULAR',
  },
  {
    name: 'Enterprise',
    description: 'Para grandes construtoras',
    price: 'Sob consulta',
    priceUnit: '',
    icon: Rocket,
    features: [
      'Tudo do Professional',
      'Unidades ilimitadas',
      'White label',
      'Integrações customizadas',
      'Treinamento presencial',
      'Gerente de conta dedicado',
      'SLA garantido',
      'Desenvolvimento sob demanda',
    ],
    cta: 'Falar com Vendas',
    highlighted: false,
    color: 'hot-pink',
  },
];

export default function PricingSection() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const titleRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<(HTMLDivElement | null)[]>([]);
  const [hoveredCard, setHoveredCard] = useState<number | null>(null);

  useLayoutEffect(() => {
    const section = sectionRef.current;
    if (!section) return;

    const ctx = gsap.context(() => {
      // Title entrance
      gsap.fromTo(
        titleRef.current,
        { opacity: 0, y: 30 },
        {
          opacity: 1,
          y: 0,
          duration: 0.8,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: section,
            start: 'top 80%',
            toggleActions: 'play none none reverse',
          },
        }
      );

      // Cards entrance
      cardsRef.current.forEach((card, index) => {
        if (!card) return;
        gsap.fromTo(
          card,
          { opacity: 0, y: 50 },
          {
            opacity: 1,
            y: 0,
            duration: 0.6,
            delay: index * 0.15,
            ease: 'power3.out',
            scrollTrigger: {
              trigger: section,
              start: 'top 70%',
              toggleActions: 'play none none reverse',
            },
          }
        );
      });
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
      id="pricing"
      className="relative bg-deep-space py-20 lg:py-28 overflow-hidden"
    >
      {/* Background glow */}
      <div 
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full pointer-events-none"
        style={{
          background: 'radial-gradient(circle, rgba(236, 72, 153, 0.1) 0%, transparent 60%)',
          filter: 'blur(80px)',
        }}
      />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-10">
        {/* Title */}
        <div ref={titleRef} className="text-center mb-12 lg:mb-16">
          <span className="text-micro text-hot-pink mb-3 lg:mb-4 block uppercase tracking-wider">Planos Flexíveis</span>
          <h2 className="font-display text-3xl sm:text-4xl lg:text-h1 text-white mb-3 lg:mb-4">
            Escolha o Seu <span className="gradient-text">Plano</span>
          </h2>
          <p className="text-base lg:text-body-lg text-white/60 max-w-2xl mx-auto">
            Planos que crescem com o seu negócio. Todos incluem setup gratuito e suporte em português.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-6 lg:gap-8">
          {plans.map((plan, index) => {
            const Icon = plan.icon;
            const isHovered = hoveredCard === index;
            
            return (
              <div
                key={index}
                ref={(el) => { cardsRef.current[index] = el; }}
                onMouseEnter={() => setHoveredCard(index)}
                onMouseLeave={() => setHoveredCard(null)}
                className={`relative ${plan.highlighted ? 'md:-mt-4 md:mb-4' : ''}`}
              >
                {/* Popular badge */}
                {plan.badge && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 z-10">
                    <span className="px-4 py-1 rounded-full bg-gradient-to-r from-electric-violet to-hot-pink text-white text-xs font-semibold uppercase tracking-wider">
                      {plan.badge}
                    </span>
                  </div>
                )}

                <div 
                  className={`glass-card h-full p-6 lg:p-8 transition-all duration-500 ${
                    plan.highlighted ? 'border-electric-violet/30' : ''
                  } ${isHovered ? 'scale-[1.02]' : ''}`}
                >
                  {/* Glow effect on hover */}
                  <div 
                    className={`absolute inset-0 rounded-3xl transition-opacity duration-500 pointer-events-none ${
                      isHovered ? 'opacity-100' : 'opacity-0'
                    }`}
                    style={{
                      background: `radial-gradient(circle at 50% 0%, rgba(${plan.color === 'neon-blue' ? '0, 212, 255' : plan.color === 'electric-violet' ? '124, 58, 237' : '236, 72, 153'}, 0.15), transparent 70%)`,
                    }}
                  />

                  <div className="relative">
                    {/* Icon & Name */}
                    <div className="flex items-center gap-3 mb-4">
                      <div className={`w-12 h-12 rounded-xl bg-${plan.color}/10 flex items-center justify-center`}>
                        <Icon className={`w-6 h-6 text-${plan.color}`} />
                      </div>
                      <div>
                        <h3 className="font-display text-xl font-semibold text-white">{plan.name}</h3>
                        <p className="text-small text-white/50">{plan.description}</p>
                      </div>
                    </div>

                    {/* Price */}
                    <div className="mb-6">
                      <div className="flex items-baseline gap-1">
                        <span className="font-display text-3xl lg:text-4xl font-bold text-white">
                          {plan.price.startsWith('Sob') ? plan.price : `${plan.price} CVE`}
                        </span>
                      </div>
                      {plan.priceUnit && (
                        <span className="text-small text-white/50">{plan.priceUnit}</span>
                      )}
                    </div>

                    {/* Features */}
                    <ul className="space-y-3 mb-8">
                      {plan.features.map((feature, i) => (
                        <li key={i} className="flex items-start gap-3">
                          <div className={`w-5 h-5 rounded-full bg-${plan.color}/20 flex items-center justify-center flex-shrink-0 mt-0.5`}>
                            <Check className={`w-3 h-3 text-${plan.color}`} />
                          </div>
                          <span className="text-small text-white/80">{feature}</span>
                        </li>
                      ))}
                    </ul>

                    {/* CTA */}
                    <button
                      onClick={scrollToContact}
                      className={`w-full py-3 px-4 rounded-xl font-semibold text-sm transition-all ${
                        plan.highlighted
                          ? 'bg-gradient-to-r from-electric-violet to-hot-pink text-white hover:shadow-lg hover:shadow-electric-violet/25'
                          : 'bg-white/5 text-white hover:bg-white/10 border border-white/10'
                      }`}
                    >
                      {plan.cta}
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Trust note */}
        <div className="mt-10 lg:mt-12 text-center">
          <p className="text-small text-white/40">
            Todos os planos incluem: Setup gratuito • Suporte em português • Cancelamento a qualquer momento
          </p>
        </div>
      </div>
    </section>
  );
}
