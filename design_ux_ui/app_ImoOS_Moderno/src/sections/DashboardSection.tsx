import { useRef, useLayoutEffect, useEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  Building2, 
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

const dashboardModules = [
  { icon: BarChart3, label: 'Vendas', value: '124', trend: '+12%', color: 'neon-blue' },
  { icon: Building2, label: 'Obras', value: '8', trend: '2 novas', color: 'electric-violet' },
  { icon: Users, label: 'Leads', value: '47', trend: '+23%', color: 'hot-pink' },
  { icon: TrendingUp, label: 'Receita', value: '8.5M', trend: '+5%', color: 'neon-blue' },
];

const recentActivities = [
  { text: 'Nova reserva: Apartamento T3 - Praia', time: '2 min', type: 'success' },
  { text: 'Pagamento recebido: 450.000 CVE', time: '15 min', type: 'success' },
  { text: 'Alerta: Atraso na obra - Projeto Sol', time: '1h', type: 'warning' },
  { text: 'Novo lead qualificado', time: '2h', type: 'info' },
];

export default function DashboardSection() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const titleRef = useRef<HTMLDivElement>(null);
  const dashboardRef = useRef<HTMLDivElement>(null);
  const modulesRef = useRef<HTMLDivElement>(null);

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

      // Title entrance
      scrollTl.fromTo(
        titleRef.current,
        { opacity: 0, y: 30 },
        { opacity: 1, y: 0, ease: 'none' },
        0
      );

      // Dashboard 3D entrance
      scrollTl.fromTo(
        dashboardRef.current,
        { opacity: 0, rotateY: -30, x: -100 },
        { opacity: 1, rotateY: 0, x: 0, ease: 'none' },
        0.05
      );

      // Modules stagger
      const modules = modulesRef.current?.children;
      if (modules) {
        scrollTl.fromTo(
          modules,
          { opacity: 0, y: 20 },
          { opacity: 1, y: 0, stagger: 0.02, ease: 'none' },
          0.1
        );
      }

      // SETTLE (30-70%): Hold

      // EXIT (70-100%)
      scrollTl.fromTo(
        titleRef.current,
        { opacity: 1, y: 0 },
        { opacity: 0, y: -30, ease: 'power2.in' },
        0.7
      );

      scrollTl.fromTo(
        dashboardRef.current,
        { opacity: 1, rotateY: 0 },
        { opacity: 0, rotateY: 30, x: 100, ease: 'power2.in' },
        0.7
      );
    }, section);

    return () => ctx.revert();
  }, []);

  // Floating animation
  useEffect(() => {
    if (dashboardRef.current) {
      gsap.to(dashboardRef.current, {
        y: '-=10',
        duration: 4,
        ease: 'sine.inOut',
        yoyo: true,
        repeat: -1,
      });
    }
  }, []);

  return (
    <section
      ref={sectionRef}
      id="solutions"
      className="section-pinned bg-deep-space flex items-center justify-center"
    >
      <div className="relative z-10 w-full max-w-7xl mx-auto px-6 lg:px-10">
        {/* Title */}
        <div ref={titleRef} className="text-center mb-12">
          <span className="text-micro text-electric-violet mb-4 block">DASHBOARD INTELIGENTE</span>
          <h2 className="font-display text-h1 text-white mb-4">
            Controle <span className="gradient-text-violet">Total</span>
          </h2>
          <p className="text-body-lg text-white/60 max-w-2xl mx-auto">
            Visualize todos os seus projetos, vendas e métricas em tempo real numa única interface
          </p>
        </div>

        {/* Dashboard */}
        <div className="perspective-1000">
          <div
            ref={dashboardRef}
            className="preserve-3d"
            style={{ transform: 'rotateY(-5deg)' }}
          >
            <div className="glass-card p-6 lg:p-8">
              {/* Dashboard Header */}
              <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-neon-blue/20 to-electric-violet/20 flex items-center justify-center">
                    <BarChart3 className="w-6 h-6 text-neon-blue" />
                  </div>
                  <div>
                    <h3 className="font-display text-xl font-semibold text-white">ImoOS Dashboard</h3>
                    <p className="text-small text-white/50">Atualizado há 2 segundos</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="flex items-center gap-2 text-micro text-neon-blue">
                    <span className="w-2 h-2 rounded-full bg-neon-blue animate-pulse" />
                    AO VIVO
                  </span>
                </div>
              </div>

              {/* Modules Grid */}
              <div ref={modulesRef} className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                {dashboardModules.map((module, index) => {
                  const Icon = module.icon;
                  return (
                    <div 
                      key={index} 
                      className="glass-card p-4 hover:bg-white/[0.06] transition-all cursor-pointer group"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className={`w-10 h-10 rounded-lg bg-${module.color}/10 flex items-center justify-center`}>
                          <Icon className={`w-5 h-5 text-${module.color}`} />
                        </div>
                        <span className={`text-small text-${module.color}`}>{module.trend}</span>
                      </div>
                      <p className="text-small text-white/50 mb-1">{module.label}</p>
                      <p className="font-display text-2xl font-bold text-white group-hover:scale-105 transition-transform origin-left">
                        {module.value}
                      </p>
                    </div>
                  );
                })}
              </div>

              {/* Main Content Area */}
              <div className="grid lg:grid-cols-3 gap-6">
                {/* Chart */}
                <div className="lg:col-span-2 glass-card p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h4 className="font-display text-lg font-semibold text-white">Vendas por Projeto</h4>
                    <div className="flex gap-2">
                      <button className="px-3 py-1 rounded-lg bg-neon-blue/20 text-neon-blue text-small">Mês</button>
                      <button className="px-3 py-1 rounded-lg bg-white/5 text-white/50 text-small hover:bg-white/10 transition-colors">Ano</button>
                    </div>
                  </div>
                  <div className="h-48 flex items-end gap-3">
                    {[
                      { label: 'Jan', value: 45, color: 'neon-blue' },
                      { label: 'Fev', value: 62, color: 'electric-violet' },
                      { label: 'Mar', value: 55, color: 'neon-blue' },
                      { label: 'Abr', value: 78, color: 'electric-violet' },
                      { label: 'Mai', value: 65, color: 'neon-blue' },
                      { label: 'Jun', value: 85, color: 'hot-pink' },
                      { label: 'Jul', value: 72, color: 'neon-blue' },
                      { label: 'Ago', value: 90, color: 'hot-pink' },
                    ].map((bar, i) => (
                      <div key={i} className="flex-1 flex flex-col items-center gap-2 group cursor-pointer">
                        <div 
                          className={`w-full rounded-t-lg bg-${bar.color} opacity-80 group-hover:opacity-100 transition-all group-hover:shadow-[0_0_20px_rgba(0,212,255,0.4)]`}
                          style={{ height: `${bar.value}%` }}
                        />
                        <span className="text-micro text-white/40">{bar.label}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Activity Feed */}
                <div className="glass-card p-6">
                  <h4 className="font-display text-lg font-semibold text-white mb-4">Atividade Recente</h4>
                  <div className="space-y-4">
                    {recentActivities.map((activity, i) => (
                      <div key={i} className="flex items-start gap-3">
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                          activity.type === 'success' ? 'bg-green-500/20' : 
                          activity.type === 'warning' ? 'bg-yellow-500/20' : 'bg-neon-blue/20'
                        }`}>
                          {activity.type === 'success' ? <CheckCircle2 className="w-4 h-4 text-green-400" /> :
                           activity.type === 'warning' ? <AlertCircle className="w-4 h-4 text-yellow-400" /> :
                           <TrendingUp className="w-4 h-4 text-neon-blue" />}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-small text-white/80 truncate">{activity.text}</p>
                          <p className="text-micro text-white/40">{activity.time}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
