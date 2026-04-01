import { useRef, useLayoutEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { Link2, MessageCircle, Landmark, Calculator, Calendar, FileText } from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

const integrations = [
  { icon: Link2, name: 'imo.cv', description: 'Portal imobiliário', color: 'neon-blue' },
  { icon: MessageCircle, name: 'WhatsApp', description: 'Comunicação direta', color: 'green-500' },
  { icon: Landmark, name: 'Bancos', description: 'Integração bancária', color: 'electric-violet' },
  { icon: Calculator, name: 'Contabilidade', description: 'Exportação fiscal', color: 'hot-pink' },
  { icon: Calendar, name: 'Google Calendar', description: 'Sincronização', color: 'blue-500' },
  { icon: FileText, name: 'Documentos', description: 'Gestão documental', color: 'orange-500' },
];

export default function IntegrationsSection() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const titleRef = useRef<HTMLDivElement>(null);
  const orbitRef = useRef<HTMLDivElement>(null);

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

      // Orbit entrance
      gsap.fromTo(
        orbitRef.current,
        { opacity: 0, scale: 0.8 },
        {
          opacity: 1,
          scale: 1,
          duration: 1,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: section,
            start: 'top 70%',
            toggleActions: 'play none none reverse',
          },
        }
      );

      // Continuous rotation for orbit
      gsap.to(orbitRef.current, {
        rotation: 360,
        duration: 60,
        ease: 'none',
        repeat: -1,
      });
    }, section);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="relative bg-deep-space py-24 overflow-hidden"
    >
      {/* Background glow */}
      <div 
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full pointer-events-none"
        style={{
          background: 'radial-gradient(circle, rgba(124, 58, 237, 0.1) 0%, transparent 50%)',
          filter: 'blur(80px)',
        }}
      />

      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-10">
        {/* Title */}
        <div ref={titleRef} className="text-center mb-20">
          <span className="text-micro text-electric-violet mb-4 block">INTEGRAÇÕES</span>
          <h2 className="font-display text-h1 text-white mb-4">
            Conectado ao <span className="gradient-text-violet">Ecossistema</span>
          </h2>
          <p className="text-body-lg text-white/60 max-w-2xl mx-auto">
            Integre com as ferramentas que já utiliza para uma experiência fluida
          </p>
        </div>

        {/* Orbit Visualization */}
        <div className="relative h-[500px] flex items-center justify-center">
          {/* Center - ImoOS */}
          <div className="absolute z-20">
            <div className="glass-card p-8 rounded-full glow-violet">
              <span className="font-display text-3xl font-bold gradient-text-violet">ImoOS</span>
            </div>
          </div>

          {/* Orbit rings */}
          <div className="absolute w-[300px] h-[300px] rounded-full border border-white/5" />
          <div className="absolute w-[450px] h-[450px] rounded-full border border-white/5" />

          {/* Orbiting integrations */}
          <div ref={orbitRef} className="absolute w-[450px] h-[450px]">
            {integrations.map((integration, index) => {
              const Icon = integration.icon;
              const angle = (index / integrations.length) * 360;
              const radius = 175;
              const x = Math.cos((angle * Math.PI) / 180) * radius;
              const y = Math.sin((angle * Math.PI) / 180) * radius;

              return (
                <div
                  key={index}
                  className="absolute"
                  style={{
                    left: `calc(50% + ${x}px)`,
                    top: `calc(50% + ${y}px)`,
                    transform: 'translate(-50%, -50%)',
                  }}
                >
                  <div 
                    className="glass-card p-4 hover:scale-110 transition-transform cursor-pointer group"
                    style={{ animation: `orbit-counter 60s linear infinite` }}
                  >
                    <div className={`w-12 h-12 rounded-xl bg-${integration.color}/10 flex items-center justify-center mb-2`}>
                      <Icon className={`w-6 h-6 text-${integration.color}`} />
                    </div>
                    <p className="text-small text-white font-medium text-center">{integration.name}</p>
                    <p className="text-micro text-white/50 text-center">{integration.description}</p>
                  </div>

                  {/* Connection line */}
                  <div 
                    className="absolute top-1/2 left-1/2 w-[175px] h-[1px] bg-gradient-to-r from-white/10 to-transparent origin-left -z-10"
                    style={{ transform: `rotate(${-angle}deg)` }}
                  />
                </div>
              );
            })}
          </div>

          {/* Pulsing dots on orbit */}
          {[0, 90, 180, 270].map((angle, i) => (
            <div
              key={i}
              className="absolute w-2 h-2 rounded-full bg-neon-blue/50 animate-pulse"
              style={{
                left: `calc(50% + ${Math.cos((angle * Math.PI) / 180) * 150}px)`,
                top: `calc(50% + ${Math.sin((angle * Math.PI) / 180) * 150}px)`,
                transform: 'translate(-50%, -50%)',
              }}
            />
          ))}
        </div>

        {/* Integration list (mobile) */}
        <div className="md:hidden grid grid-cols-2 gap-4 mt-12">
          {integrations.map((integration, index) => {
            const Icon = integration.icon;
            return (
              <div key={index} className="glass-card p-4 flex items-center gap-3">
                <div className={`w-10 h-10 rounded-lg bg-${integration.color}/10 flex items-center justify-center flex-shrink-0`}>
                  <Icon className={`w-5 h-5 text-${integration.color}`} />
                </div>
                <div>
                  <p className="text-small text-white font-medium">{integration.name}</p>
                  <p className="text-micro text-white/50">{integration.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <style>{`
        @keyframes orbit-counter {
          from { transform: rotate(0deg); }
          to { transform: rotate(-360deg); }
        }
      `}</style>
    </section>
  );
}
