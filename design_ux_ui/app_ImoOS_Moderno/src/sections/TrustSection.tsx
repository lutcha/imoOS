import { useRef, useLayoutEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { Building2, Home, Landmark, Hotel, Castle } from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

// Client logos represented as icons with names (would be replaced with actual logos)
const clients = [
  { name: 'Construtora Horizonte', icon: Building2 },
  { name: 'Promotora Sol', icon: Home },
  { name: 'Imobiliária PraiaMar', icon: Landmark },
  { name: 'Grupo Santiago', icon: Hotel },
  { name: 'Villas do Sal', icon: Castle },
  { name: 'Obras CV', icon: Building2 },
];

export default function TrustSection() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const logosRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const section = sectionRef.current;
    if (!section) return;

    const ctx = gsap.context(() => {
      // Content entrance
      gsap.fromTo(
        contentRef.current,
        { opacity: 0, y: 20 },
        {
          opacity: 1,
          y: 0,
          duration: 0.6,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: section,
            start: 'top 85%',
            toggleActions: 'play none none reverse',
          },
        }
      );

      // Logos entrance with stagger
      const logos = logosRef.current?.children;
      if (logos) {
        gsap.fromTo(
          logos,
          { opacity: 0, y: 20, scale: 0.9 },
          {
            opacity: 1,
            y: 0,
            scale: 1,
            duration: 0.5,
            stagger: 0.1,
            ease: 'power3.out',
            scrollTrigger: {
              trigger: section,
              start: 'top 80%',
              toggleActions: 'play none none reverse',
            },
          }
        );
      }
    }, section);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="relative bg-deep-space py-12 lg:py-16 overflow-hidden border-y border-white/5"
    >
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-10">
        <div ref={contentRef} className="text-center mb-8 lg:mb-10">
          <p className="text-small lg:text-body text-white/50">
            Empresas que já transformaram a sua gestão com o <span className="text-neon-blue font-medium">ImoOS</span>
          </p>
        </div>

        {/* Client Logos Grid */}
        <div 
          ref={logosRef}
          className="grid grid-cols-3 md:grid-cols-6 gap-4 lg:gap-8"
        >
          {clients.map((client, index) => {
            const Icon = client.icon;
            return (
              <div 
                key={index}
                className="group flex flex-col items-center justify-center p-4 lg:p-6 rounded-xl bg-white/[0.02] hover:bg-white/[0.05] border border-white/5 hover:border-white/10 transition-all duration-300"
              >
                <div className="w-10 h-10 lg:w-12 lg:h-12 rounded-lg bg-gradient-to-br from-neon-blue/10 to-electric-violet/10 flex items-center justify-center mb-2 group-hover:scale-110 transition-transform">
                  <Icon className="w-5 h-5 lg:w-6 lg:h-6 text-white/40 group-hover:text-neon-blue transition-colors" />
                </div>
                <span className="text-[10px] lg:text-small text-white/40 group-hover:text-white/60 transition-colors text-center">
                  {client.name}
                </span>
              </div>
            );
          })}
        </div>

        {/* Stats row */}
        <div className="mt-8 lg:mt-10 flex flex-wrap justify-center gap-6 lg:gap-12">
          {[
            { value: '50+', label: 'Empresas' },
            { value: '9', label: 'Ilhas' },
            { value: '4.9/5', label: 'Avaliação' },
          ].map((stat, index) => (
            <div key={index} className="text-center">
              <span className="font-display text-xl lg:text-2xl font-bold text-white">{stat.value}</span>
              <span className="block text-[10px] lg:text-micro text-white/40 uppercase tracking-wider mt-1">{stat.label}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
