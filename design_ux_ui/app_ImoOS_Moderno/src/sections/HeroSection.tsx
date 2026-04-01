import { useEffect, useRef, useLayoutEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { ArrowRight, Play, Zap, TrendingUp, Building2 } from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

export default function HeroSection() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const headlineRef = useRef<HTMLHeadingElement>(null);
  const subheadlineRef = useRef<HTMLParagraphElement>(null);
  const ctaRef = useRef<HTMLDivElement>(null);
  const dashboardRef = useRef<HTMLDivElement>(null);
  const statsRef = useRef<HTMLDivElement>(null);
  const glowRef = useRef<HTMLDivElement>(null);

  // Check for reduced motion preference
  const prefersReducedMotion = typeof window !== 'undefined' 
    ? window.matchMedia('(prefers-reduced-motion: reduce)').matches 
    : false;

  // Entrance animation
  useEffect(() => {
    if (prefersReducedMotion) return;

    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

      // Glow effect
      tl.fromTo(
        glowRef.current,
        { opacity: 0, scale: 0.8 },
        { opacity: 1, scale: 1, duration: 1.5 }
      );

      // Headline animation (word by word instead of character)
      if (headlineRef.current) {
        const words = headlineRef.current.querySelectorAll('.word');
        tl.fromTo(
          words,
          { opacity: 0, y: 50 },
          { 
            opacity: 1, 
            y: 0,
            duration: 0.6, 
            stagger: 0.1,
          },
          '-=1'
        );
      }

      // Subheadline
      tl.fromTo(
        subheadlineRef.current,
        { opacity: 0, y: 30 },
        { opacity: 1, y: 0, duration: 0.8 },
        '-=0.4'
      );

      // CTAs
      tl.fromTo(
        ctaRef.current,
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.6 },
        '-=0.4'
      );

      // Dashboard 3D entrance
      tl.fromTo(
        dashboardRef.current,
        { opacity: 0, y: 80, rotateX: 30 },
        { 
          opacity: 1, 
          y: 0, 
          rotateX: 10,
          duration: 1,
          ease: 'power2.out'
        },
        '-=0.6'
      );

      // Stats
      tl.fromTo(
        statsRef.current?.children || [],
        { opacity: 0, x: -20 },
        { opacity: 1, x: 0, duration: 0.4, stagger: 0.08 },
        '-=0.4'
      );
    }, sectionRef);

    return () => ctx.revert();
  }, [prefersReducedMotion]);

  // Scroll-driven exit animation
  useLayoutEffect(() => {
    if (prefersReducedMotion) return;
    
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
          onLeaveBack: () => {
            const words = headlineRef.current?.querySelectorAll('.word');
            if (words && words.length > 0) {
              gsap.set(words, { opacity: 1, y: 0 });
            }
            gsap.set(subheadlineRef.current, { opacity: 1, y: 0 });
            gsap.set(ctaRef.current, { opacity: 1, y: 0 });
            gsap.set(dashboardRef.current, { opacity: 1, y: 0, rotateX: 10 });
          },
        },
      });

      // EXIT (70-100%)
      scrollTl.fromTo(
        headlineRef.current?.querySelectorAll('.word') || [],
        { opacity: 1, y: 0 },
        { opacity: 0, y: -30, stagger: 0.02, ease: 'power2.in' },
        0.7
      );

      scrollTl.fromTo(
        subheadlineRef.current,
        { opacity: 1, y: 0 },
        { opacity: 0, y: -20, ease: 'power2.in' },
        0.72
      );

      scrollTl.fromTo(
        ctaRef.current,
        { opacity: 1, y: 0 },
        { opacity: 0, y: -15, ease: 'power2.in' },
        0.74
      );

      scrollTl.fromTo(
        dashboardRef.current,
        { opacity: 1, y: 0, rotateX: 10 },
        { opacity: 0, y: -60, rotateX: 30, ease: 'power2.in' },
        0.7
      );

      scrollTl.fromTo(
        statsRef.current,
        { opacity: 1 },
        { opacity: 0, ease: 'power2.in' },
        0.75
      );
    }, section);

    return () => ctx.revert();
  }, [prefersReducedMotion]);

  // Floating animation for dashboard (only if not reduced motion)
  useEffect(() => {
    if (prefersReducedMotion || !dashboardRef.current) return;
    
    gsap.to(dashboardRef.current, {
      y: '-=12',
      duration: 4,
      ease: 'sine.inOut',
      yoyo: true,
      repeat: -1,
    });
  }, [prefersReducedMotion]);

  const scrollToContact = () => {
    const element = document.getElementById('contact');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const scrollToFeatures = () => {
    const element = document.getElementById('features');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section
      ref={sectionRef}
      className="section-pinned bg-deep-space flex items-center justify-center overflow-hidden"
    >
      {/* Background glow */}
      <div 
        ref={glowRef}
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] lg:w-[800px] lg:h-[800px] rounded-full pointer-events-none"
        style={{
          background: 'radial-gradient(circle, rgba(124, 58, 237, 0.2) 0%, rgba(0, 212, 255, 0.1) 40%, transparent 70%)',
          filter: 'blur(80px)',
        }}
      />

      {/* Content */}
      <div className="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-10 pt-20 lg:pt-24">
        <div className="grid lg:grid-cols-2 gap-8 lg:gap-12 items-center">
          {/* Left Content */}
          <div className="text-center lg:text-left order-2 lg:order-1">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-3 py-1.5 lg:px-4 lg:py-2 rounded-full glass-card mb-4 lg:mb-6">
              <Zap className="w-3 h-3 lg:w-4 lg:h-4 text-neon-blue" aria-hidden="true" />
              <span className="text-[10px] lg:text-micro text-white/70 uppercase tracking-wider">PropTech • ConstruTech • FinTech</span>
            </div>

            {/* Headline - Simplified, no character splitting */}
            <h1
              ref={headlineRef}
              className="font-display text-4xl sm:text-5xl md:text-6xl lg:text-hero text-white leading-[0.95] mb-3 lg:mb-4"
            >
              <span className="word block">O Futuro da</span>
              <span className="word block gradient-text">Construção</span>
            </h1>

            {/* Subheadline */}
            <p
              ref={subheadlineRef}
              className="text-base sm:text-lg lg:text-body-lg text-white/70 leading-relaxed mb-6 lg:mb-8 max-w-lg mx-auto lg:mx-0"
            >
              A primeira plataforma <span className="text-neon-blue font-medium">PropTech</span> de{' '}
              <span className="text-electric-violet font-medium">Cabo Verde</span>. Unindo vendas, obra e 
              financiamentos num ecossistema digital.
            </p>

            {/* CTAs */}
            <div ref={ctaRef} className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center lg:justify-start">
              <button 
                onClick={scrollToContact} 
                className="neon-btn text-sm"
                aria-label="Pedir demonstração do ImoOS"
              >
                <span className="flex items-center justify-center gap-2">
                  Pedir Demonstração
                  <ArrowRight className="w-4 h-4" aria-hidden="true" />
                </span>
              </button>
              <button 
                onClick={scrollToFeatures} 
                className="glass-btn text-sm flex items-center justify-center gap-2"
                aria-label="Ver funcionalidades do ImoOS"
              >
                <Play className="w-4 h-4" aria-hidden="true" />
                Ver Funcionalidades
              </button>
            </div>

            {/* Trust text */}
            <p className="text-xs lg:text-small text-white/40 mt-4 lg:mt-6">
              Setup em 24h • Sem cartão de crédito • 14 dias grátis
            </p>

            {/* Stats */}
            <div ref={statsRef} className="flex flex-wrap gap-3 lg:gap-6 mt-6 lg:mt-10 justify-center lg:justify-start">
              {[
                { icon: Building2, value: '+120', label: 'Projetos' },
                { icon: TrendingUp, value: '+2K', label: 'Unidades' },
                { icon: Zap, value: '24h', label: 'Suporte' },
              ].map((stat, index) => (
                <div key={index} className="glass-card px-3 py-2 lg:px-4 lg:py-3 flex items-center gap-2 lg:gap-3">
                  <div className="w-8 h-8 lg:w-10 lg:h-10 rounded-lg bg-gradient-to-br from-neon-blue/20 to-electric-violet/20 flex items-center justify-center flex-shrink-0">
                    <stat.icon className="w-4 h-4 lg:w-5 lg:h-5 text-neon-blue" aria-hidden="true" />
                  </div>
                  <div>
                    <p className="font-display text-lg lg:text-xl font-bold text-white">{stat.value}</p>
                    <p className="text-[10px] lg:text-micro text-white/50 uppercase tracking-wider">{stat.label}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right Content - 3D Dashboard */}
          <div className="relative perspective-1000 order-1 lg:order-2 hidden sm:block">
            <div
              ref={dashboardRef}
              className="relative preserve-3d mx-auto max-w-md lg:max-w-none"
              style={{ transform: 'rotateX(10deg) rotateY(-3deg)' }}
            >
              {/* Dashboard Card */}
              <div className="glass-card p-4 lg:p-6 relative overflow-hidden">
                {/* Glow border */}
                <div className="absolute inset-0 rounded-3xl opacity-50 pointer-events-none" style={{
                  background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(124, 58, 237, 0.15))',
                }} />
                
                {/* Dashboard Content */}
                <div className="relative">
                  {/* Header */}
                  <div className="flex items-center justify-between mb-4 lg:mb-6">
                    <div>
                      <h3 className="font-display text-base lg:text-lg font-semibold text-white">Dashboard</h3>
                      <p className="text-xs lg:text-small text-white/50">Visão geral em tempo real</p>
                    </div>
                    <div className="flex gap-1.5 lg:gap-2">
                      <div className="w-2.5 h-2.5 lg:w-3 lg:h-3 rounded-full bg-hot-pink" aria-hidden="true" />
                      <div className="w-2.5 h-2.5 lg:w-3 lg:h-3 rounded-full bg-electric-violet" aria-hidden="true" />
                      <div className="w-2.5 h-2.5 lg:w-3 lg:h-3 rounded-full bg-neon-blue" aria-hidden="true" />
                    </div>
                  </div>

                  {/* Stats Grid */}
                  <div className="grid grid-cols-2 gap-2 lg:gap-4 mb-4 lg:mb-6">
                    {[
                      { label: 'Vendas', value: '124', change: '+12%', color: 'text-neon-blue' },
                      { label: 'Obras', value: '8', change: '2 novas', color: 'text-electric-violet' },
                      { label: 'Leads', value: '47', change: '+23%', color: 'text-hot-pink' },
                      { label: 'Receita', value: '8.5M', change: '+5%', color: 'text-neon-blue' },
                    ].map((item, i) => (
                      <div key={i} className="glass-card p-2.5 lg:p-4 hover:bg-white/[0.06] transition-colors">
                        <p className="text-xs lg:text-small text-white/50 mb-0.5 lg:mb-1">{item.label}</p>
                        <div className="flex items-end gap-1.5 lg:gap-2">
                          <span className="font-display text-lg lg:text-2xl font-bold text-white">{item.value}</span>
                          <span className={`text-xs lg:text-small ${item.color}`}>{item.change}</span>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Chart */}
                  <div className="glass-card p-3 lg:p-4">
                    <p className="text-xs lg:text-small text-white/50 mb-2 lg:mb-3">Vendas por Projeto</p>
                    <div className="h-16 lg:h-24 flex items-end gap-1 lg:gap-2">
                      {[35, 55, 40, 70, 50, 65, 85, 60, 75, 90].map((h, i) => (
                        <div key={i} className="flex-1 flex flex-col justify-end group cursor-pointer">
                          <div 
                            className="w-full rounded-t-sm bg-gradient-to-t from-electric-violet to-neon-blue opacity-80 group-hover:opacity-100 transition-all"
                            style={{ height: `${h}%` }}
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Floating elements */}
              <div className="absolute -top-3 -right-3 lg:-top-4 lg:-right-4 glass-card px-2.5 py-1 lg:px-4 lg:py-2 animate-float">
                <span className="text-[10px] lg:text-micro text-neon-blue uppercase tracking-wider">● Ao Vivo</span>
              </div>
              <div className="absolute -bottom-3 -left-3 lg:-bottom-4 lg:-left-4 glass-card px-2.5 py-1 lg:px-4 lg:py-2 animate-float-slow">
                <span className="text-[10px] lg:text-micro text-hot-pink uppercase tracking-wider">98% Satisfação</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
