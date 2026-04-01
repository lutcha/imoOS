import { useRef, useLayoutEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { Check, ArrowRight, Bell, Download, BarChart3 } from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

const dashboardFeatures = [
  'Visão de vendas, obra e financeiro numa só tela.',
  'Alertas automáticos para atrasos e pagamentos.',
  'Exportações prontas para contabilidade.',
];

export default function DashboardPreviewSection() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const leftCardRef = useRef<HTMLDivElement>(null);
  const rightCardRef = useRef<HTMLDivElement>(null);
  const pillRef = useRef<HTMLDivElement>(null);

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

      // ENTRANCE (0-30%)
      // Left card from left
      scrollTl.fromTo(
        leftCardRef.current,
        { x: '-55vw', opacity: 0 },
        { x: 0, opacity: 1, ease: 'none' },
        0
      );

      // Right card from right
      scrollTl.fromTo(
        rightCardRef.current,
        { x: '55vw', opacity: 0 },
        { x: 0, opacity: 1, ease: 'none' },
        0
      );

      // Pill from bottom
      scrollTl.fromTo(
        pillRef.current,
        { y: '10vh', opacity: 0 },
        { y: 0, opacity: 1, ease: 'none' },
        0.1
      );

      // Text bullets stagger
      const bullets = leftCardRef.current?.querySelectorAll('.bullet-item');
      if (bullets) {
        scrollTl.fromTo(
          bullets,
          { opacity: 0, y: 12 },
          { opacity: 1, y: 0, stagger: 0.03, ease: 'none' },
          0.12
        );
      }

      // SETTLE (30-70%): Hold

      // EXIT (70-100%)
      scrollTl.fromTo(
        leftCardRef.current,
        { x: 0, opacity: 1 },
        { x: '-14vw', opacity: 0, ease: 'power2.in' },
        0.7
      );

      scrollTl.fromTo(
        rightCardRef.current,
        { x: 0, opacity: 1 },
        { x: '14vw', opacity: 0, ease: 'power2.in' },
        0.7
      );

      scrollTl.fromTo(
        pillRef.current,
        { y: 0, opacity: 1 },
        { y: '8vh', opacity: 0, ease: 'power2.in' },
        0.75
      );
    }, section);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="imos-section-pinned bg-imos-bg flex items-center justify-center"
    >
      {/* Left Text Card */}
      <div
        ref={leftCardRef}
        className="absolute left-[4vw] top-[14vh] w-[34vw] h-[72vh] bg-white rounded-3xl shadow-card p-8 flex flex-col justify-center"
      >
        <h2 className="font-heading text-h1 font-light text-imos-text mb-8">
          Dashboard unificado
        </h2>

        <div className="space-y-5 mb-8">
          {dashboardFeatures.map((feature, index) => (
            <div key={index} className="bullet-item flex items-start gap-3">
              <div className="w-5 h-5 bg-imos-accent/10 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <Check className="w-3 h-3 text-imos-accent" />
              </div>
              <p className="text-body text-imos-text-secondary leading-relaxed">
                {feature}
              </p>
            </div>
          ))}
        </div>

        <button className="flex items-center gap-2 text-imos-accent font-medium hover:gap-3 transition-all w-fit">
          Ver todos os módulos
          <ArrowRight size={18} />
        </button>
      </div>

      {/* Right Image Card - Dashboard Mockup */}
      <div
        ref={rightCardRef}
        className="absolute left-[40vw] top-[14vh] w-[56vw] h-[72vh] bg-white rounded-3xl shadow-card p-6 overflow-hidden"
      >
        {/* Dashboard UI Mockup */}
        <div className="w-full h-full bg-imos-bg rounded-2xl overflow-hidden">
          {/* Sidebar */}
          <div className="flex h-full">
            <div className="w-16 bg-white border-r border-imos-text/5 flex flex-col items-center py-4 gap-4">
              <div className="w-8 h-8 bg-imos-accent rounded-lg flex items-center justify-center">
                <BarChart3 className="w-4 h-4 text-white" />
              </div>
              <div className="w-8 h-8 bg-imos-text/5 rounded-lg" />
              <div className="w-8 h-8 bg-imos-text/5 rounded-lg" />
              <div className="w-8 h-8 bg-imos-text/5 rounded-lg" />
            </div>

            {/* Main Content */}
            <div className="flex-1 p-6 overflow-hidden">
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h4 className="font-heading text-lg font-medium text-imos-text">
                    Visão Geral
                  </h4>
                  <p className="text-small text-imos-text-secondary">
                    Resumo de todos os projetos
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center shadow-sm">
                    <Bell className="w-4 h-4 text-imos-text-secondary" />
                  </div>
                  <div className="w-10 h-10 bg-imos-accent rounded-lg flex items-center justify-center">
                    <Download className="w-4 h-4 text-white" />
                  </div>
                </div>
              </div>

              {/* Stats Row */}
              <div className="grid grid-cols-4 gap-4 mb-6">
                {[
                  { label: 'Unidades Vendidas', value: '124', change: '+12%' },
                  { label: 'Cashflow Mês', value: '8.5M', change: '+5%' },
                  { label: 'Obras Ativas', value: '8', change: '2 novas' },
                  { label: 'Leads Novos', value: '47', change: '+23%' },
                ].map((stat, i) => (
                  <div key={i} className="bg-white rounded-xl p-4 shadow-sm">
                    <p className="text-small text-imos-text-secondary mb-1">
                      {stat.label}
                    </p>
                    <div className="flex items-end gap-2">
                      <span className="font-heading text-2xl font-medium text-imos-text">
                        {stat.value}
                      </span>
                      <span className="text-small text-imos-success mb-1">
                        {stat.change}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Charts Area */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white rounded-xl p-4 shadow-sm">
                  <p className="text-small text-imos-text-secondary mb-3">
                    Vendas por Projeto
                  </p>
                  <div className="h-24 flex items-end gap-2">
                    {[40, 65, 45, 80, 55, 70, 90].map((h, i) => (
                      <div
                        key={i}
                        className="flex-1 bg-imos-accent/20 rounded-t-sm"
                        style={{ height: `${h}%` }}
                      >
                        <div
                          className="w-full bg-imos-accent rounded-t-sm"
                          style={{ height: `${h * 0.6}%` }}
                        />
                      </div>
                    ))}
                  </div>
                </div>
                <div className="bg-white rounded-xl p-4 shadow-sm">
                  <p className="text-small text-imos-text-secondary mb-3">
                    Cashflow Projetado
                  </p>
                  <div className="h-24 relative">
                    <svg className="w-full h-full" viewBox="0 0 200 80">
                      <path
                        d="M0,60 Q30,50 60,45 T120,35 T180,25"
                        fill="none"
                        stroke="#2F5AF5"
                        strokeWidth="2"
                      />
                      <path
                        d="M0,60 Q30,50 60,45 T120,35 T180,25 L180,80 L0,80 Z"
                        fill="url(#gradient)"
                        opacity="0.2"
                      />
                      <defs>
                        <linearGradient id="gradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#2F5AF5" />
                          <stop offset="100%" stopColor="#2F5AF5" stopOpacity="0" />
                        </linearGradient>
                      </defs>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Accent Pill */}
      <div
        ref={pillRef}
        className="absolute left-[36vw] top-[78vh] bg-imos-accent text-white px-4 py-2 rounded-full font-mono text-label shadow-lg"
      >
        ATUALIZAÇÕES EM TEMPO REAL
      </div>
    </section>
  );
}
