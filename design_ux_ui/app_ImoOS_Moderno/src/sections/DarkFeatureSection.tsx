import { useRef, useLayoutEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { Check, Shield } from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

const securityFeatures = [
  'Autenticação com 2FA',
  'Permissões por projeto e por ação',
  'Histórico de auditoria',
];

export default function DarkFeatureSection() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const textRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLDivElement>(null);
  const pillRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const section = sectionRef.current;
    if (!section) return;

    const ctx = gsap.context(() => {
      // Section fade in
      gsap.fromTo(
        section,
        { opacity: 0 },
        {
          opacity: 1,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: section,
            start: 'top 90%',
            end: 'top 60%',
            scrub: 0.5,
          },
        }
      );

      // Text from left
      gsap.fromTo(
        textRef.current,
        { x: '-8vw', opacity: 0 },
        {
          x: 0,
          opacity: 1,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: section,
            start: 'top 80%',
            end: 'top 40%',
            scrub: 0.5,
          },
        }
      );

      // Image from right
      gsap.fromTo(
        imageRef.current,
        { x: '8vw', opacity: 0 },
        {
          x: 0,
          opacity: 1,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: section,
            start: 'top 75%',
            end: 'top 45%',
            scrub: 0.5,
          },
        }
      );

      // Pill from bottom
      gsap.fromTo(
        pillRef.current,
        { y: '4vh', opacity: 0 },
        {
          y: 0,
          opacity: 1,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: section,
            start: 'top 60%',
            end: 'top 50%',
            scrub: 0.5,
          },
        }
      );
    }, section);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="imos-section bg-imos-dark py-[12vh] px-[4vw]"
    >
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left Text */}
          <div ref={textRef}>
            <h2 className="font-heading text-h1 font-light text-white mb-6">
              Dados protegidos.
            </h2>

            <p className="text-body-lg text-white/70 leading-relaxed mb-8">
              Encriptação em trânsito e em repouso, backups automáticos e
              permissões granulares por utilizador.
            </p>

            <div className="space-y-4">
              {securityFeatures.map((feature, index) => (
                <div key={index} className="flex items-start gap-3">
                  <div className="w-5 h-5 bg-imos-accent/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Check className="w-3 h-3 text-imos-accent" />
                  </div>
                  <p className="text-body text-white/90">{feature}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Right Image */}
          <div ref={imageRef} className="relative">
            <div className="rounded-3xl overflow-hidden shadow-card aspect-[4/3]">
              <img
                src="https://images.unsplash.com/photo-1563986768609-322da13575f3?w=1000&h=750&fit=crop"
                alt="Security and data protection"
                className="w-full h-full object-cover"
              />
              {/* Gradient overlay */}
              <div className="absolute inset-0 bg-gradient-to-t from-imos-dark/40 to-transparent" />
            </div>

            {/* Accent Pill */}
            <div
              ref={pillRef}
              className="absolute -bottom-4 -left-4 bg-white shadow-card px-4 py-2 rounded-full flex items-center gap-2"
            >
              <div className="w-8 h-8 bg-imos-accent/10 rounded-full flex items-center justify-center">
                <Shield className="w-4 h-4 text-imos-accent" />
              </div>
              <span className="font-mono text-label text-imos-text">
                SEGURANÇA
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
