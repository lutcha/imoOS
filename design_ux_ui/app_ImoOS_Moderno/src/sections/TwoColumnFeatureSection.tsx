import { useRef, useLayoutEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { Check, Workflow } from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

const features = [
  'Comentários por unidade e por tarefa',
  'Aprovações com assinatura digital',
  'Relatórios automáticos para investidores',
];

export default function TwoColumnFeatureSection() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const textRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLDivElement>(null);
  const pillRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const section = sectionRef.current;
    if (!section) return;

    const ctx = gsap.context(() => {
      // Text from left
      gsap.fromTo(
        textRef.current,
        { x: '-10vw', opacity: 0 },
        {
          x: 0,
          opacity: 1,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: section,
            start: 'top 80%',
            end: 'top 30%',
            scrub: 0.5,
          },
        }
      );

      // Image from right
      gsap.fromTo(
        imageRef.current,
        { x: '10vw', opacity: 0 },
        {
          x: 0,
          opacity: 1,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: section,
            start: 'top 75%',
            end: 'top 35%',
            scrub: 0.5,
          },
        }
      );

      // Pill from bottom
      gsap.fromTo(
        pillRef.current,
        { y: '6vh', opacity: 0 },
        {
          y: 0,
          opacity: 1,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: section,
            start: 'top 60%',
            end: 'top 40%',
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
      className="imos-section bg-imos-bg py-[10vh] px-[4vw]"
    >
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left Text */}
          <div ref={textRef} className="lg:pr-8 order-2 lg:order-1">
            <h2 className="font-heading text-h1 font-light text-imos-text mb-6">
              Menos reuniões, mais clareza.
            </h2>

            <p className="text-body-lg text-imos-text-secondary leading-relaxed mb-8">
              Comentários ligados a unidades, documentos versionados e
              aprovações com rastro—tudo visível para quem precisa.
            </p>

            <div className="space-y-4">
              {features.map((feature, index) => (
                <div key={index} className="flex items-start gap-3">
                  <div className="w-5 h-5 bg-imos-accent/10 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Check className="w-3 h-3 text-imos-accent" />
                  </div>
                  <p className="text-body text-imos-text">{feature}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Right Image */}
          <div ref={imageRef} className="relative order-1 lg:order-2">
            <div className="relative rounded-3xl overflow-hidden shadow-card aspect-[4/3]">
              <img
                src="https://images.unsplash.com/photo-1503387762-592deb58ef4e?w=1000&h=750&fit=crop"
                alt="Architect working on laptop"
                className="w-full h-full object-cover"
              />
              {/* Gradient overlay */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />
            </div>

            {/* Accent Pill */}
            <div
              ref={pillRef}
              className="absolute -bottom-4 -left-4 bg-white shadow-card px-4 py-2 rounded-full flex items-center gap-2"
            >
              <div className="w-8 h-8 bg-imos-accent/10 rounded-full flex items-center justify-center">
                <Workflow className="w-4 h-4 text-imos-accent" />
              </div>
              <span className="font-mono text-label text-imos-text">
                FLUXO DE TRABALHO
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
