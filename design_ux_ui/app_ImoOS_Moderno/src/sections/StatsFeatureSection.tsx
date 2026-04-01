import { useRef, useLayoutEffect, useState, useEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { Link2, MessageCircle, FileSpreadsheet } from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

const stats = [
  { value: 2000, suffix: '', label: 'Unidades geridas' },
  { value: 120, suffix: '', label: 'Projetos ativos' },
  { value: 98, suffix: '%', label: 'Satisfação no suporte' },
];

const integrations = [
  { name: 'imo.cv', icon: Link2 },
  { name: 'WhatsApp Business', icon: MessageCircle },
  { name: 'Exportação contabilística', icon: FileSpreadsheet },
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
            const duration = 2000;
            const startTime = Date.now();
            const startValue = 0;

            const animate = () => {
              const elapsed = Date.now() - startTime;
              const progress = Math.min(elapsed / duration, 1);
              const easeProgress = 1 - Math.pow(1 - progress, 3);
              const currentValue = Math.floor(
                startValue + (value - startValue) * easeProgress
              );
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
    <span ref={ref}>
      +{count.toLocaleString()}
      {suffix}
    </span>
  );
}

export default function StatsFeatureSection() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const statsRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLDivElement>(null);
  const cardRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const section = sectionRef.current;
    if (!section) return;

    const ctx = gsap.context(() => {
      // Stats reveal
      gsap.fromTo(
        statsRef.current,
        { y: 12, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: section,
            start: 'top 80%',
            end: 'top 50%',
            scrub: 0.5,
          },
        }
      );

      // Image from left
      gsap.fromTo(
        imageRef.current,
        { x: '-10vw', opacity: 0 },
        {
          x: 0,
          opacity: 1,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: section,
            start: 'top 70%',
            end: 'top 30%',
            scrub: 0.5,
          },
        }
      );

      // Card from right
      gsap.fromTo(
        cardRef.current,
        { x: '10vw', opacity: 0 },
        {
          x: 0,
          opacity: 1,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: section,
            start: 'top 65%',
            end: 'top 35%',
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
      id="pricing"
      className="imos-section bg-imos-bg py-[10vh] px-[4vw]"
    >
      <div className="max-w-7xl mx-auto">
        {/* Stats Row */}
        <div
          ref={statsRef}
          className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16"
        >
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <p className="font-heading text-display font-light text-imos-text mb-2">
                <AnimatedCounter value={stat.value} suffix={stat.suffix} />
              </p>
              <p className="font-mono text-label text-imos-text-secondary">
                {stat.label.toUpperCase()}
              </p>
            </div>
          ))}
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Image */}
          <div ref={imageRef}>
            <div className="rounded-3xl overflow-hidden shadow-card aspect-[16/10]">
              <img
                src="https://images.unsplash.com/photo-1590644365607-1c5a519e7b37?w=1200&h=750&fit=crop"
                alt="Construction site overview"
                className="w-full h-full object-cover"
              />
            </div>
          </div>

          {/* Right Feature Card */}
          <div
            ref={cardRef}
            className="bg-imos-accent rounded-3xl shadow-card p-8 flex flex-col justify-center"
          >
            <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center mb-6">
              <Link2 className="w-6 h-6 text-white" />
            </div>

            <h3 className="font-heading text-h1 font-light text-white mb-6">
              Integração nativa
            </h3>

            <div className="space-y-4">
              {integrations.map((integration, index) => {
                const Icon = integration.icon;
                return (
                  <div
                    key={index}
                    className="flex items-center gap-3 text-white/90"
                  >
                    <Icon className="w-5 h-5 text-white/60" />
                    <span className="text-body">{integration.name}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
