"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Building2,
  TrendingUp,
  Users,
  CheckCircle2,
  ArrowRight,
  Menu,
  X,
  Play,
  Star,
  Lock,
  Globe,
  FileText,
  Calculator,
  ChevronRight,
} from "lucide-react";
import Link from "next/link";

const fadeInUp = {
  initial: { opacity: 0, y: 40 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] },
};

const staggerContainer = {
  animate: { transition: { staggerChildren: 0.1 } },
};

function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 50);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const navLinks = [
    { name: "Funcionalidades", href: "#features" },
    { name: "Preços", href: "#pricing" },
    { name: "Testemunhos", href: "#testimonials" },
    { name: "FAQ", href: "#faq" },
  ];

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6 }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled ? "bg-white/90 backdrop-blur-xl shadow-lg shadow-slate-200/20" : "bg-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          <Link href="/landing" className="flex items-center gap-3">
            <div className="relative">
              <div className="absolute inset-0 bg-blue-600 rounded-xl blur-lg opacity-50" />
              <div className="relative bg-gradient-to-br from-blue-600 to-blue-700 w-10 h-10 rounded-xl flex items-center justify-center">
                <Building2 className="w-6 h-6 text-white" />
              </div>
            </div>
            <span className={`text-2xl font-bold ${isScrolled ? "text-slate-900" : "text-white"}`}>
              ImoOS
            </span>
          </Link>

          <div className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <a key={link.name} href={link.href} className={`text-sm font-medium transition-colors hover:text-blue-500 ${isScrolled ? "text-slate-600" : "text-white/90"}`}>
                {link.name}
              </a>
            ))}
          </div>

          <div className="hidden md:flex items-center gap-4">
            <Link href="/login" className={`text-sm font-medium transition-colors ${isScrolled ? "text-slate-600 hover:text-slate-900" : "text-white/90 hover:text-white"}`}>
              Entrar
            </Link>
            <Link href="/register" className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-full text-sm font-semibold transition-all hover:shadow-lg hover:shadow-blue-600/25">
              Começar Grátis
            </Link>
          </div>

          <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="md:hidden p-2">
            {isMobileMenuOpen ? (
              <X className={`w-6 h-6 ${isScrolled ? "text-slate-900" : "text-white"}`} />
            ) : (
              <Menu className={`w-6 h-6 ${isScrolled ? "text-slate-900" : "text-white"}`} />
            )}
          </button>
        </div>
      </div>

      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} className="md:hidden bg-white border-t border-slate-100">
            <div className="px-4 py-6 space-y-4">
              {navLinks.map((link) => (
                <a key={link.name} href={link.href} onClick={() => setIsMobileMenuOpen(false)} className="block text-slate-600 hover:text-blue-600 font-medium">
                  {link.name}
                </a>
              ))}
              <div className="pt-4 space-y-3">
                <Link href="/login" className="block w-full text-center py-3 text-slate-600 font-medium border border-slate-200 rounded-xl">Entrar</Link>
                <Link href="/register" className="block w-full text-center py-3 bg-blue-600 text-white font-semibold rounded-xl">Começar Grátis</Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
}

function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-slate-900">
      <div className="absolute inset-0">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-blue-600/30 rounded-full blur-[120px] animate-pulse" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-purple-600/20 rounded-full blur-[100px] animate-pulse" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-blue-500/10 rounded-full blur-[150px]" />
        <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`, backgroundSize: "60px 60px" }} />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-32">
        <motion.div variants={staggerContainer} initial="initial" animate="animate" className="text-center">
          <motion.div variants={fadeInUp} className="mb-8">
            <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 text-white/90 text-sm font-medium">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              Novo: Integração com imo.cv
            </span>
          </motion.div>

          <motion.h1 variants={fadeInUp} className="text-5xl sm:text-6xl lg:text-7xl font-bold text-white mb-8 leading-tight">
            Gestão Imobiliária
            <br />
            <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-blue-400 bg-clip-text text-transparent">Inteligente & Completa</span>
          </motion.h1>

          <motion.p variants={fadeInUp} className="text-xl text-slate-400 max-w-3xl mx-auto mb-12 leading-relaxed">
            A plataforma tudo-em-um para promotoras e construtoras em Cabo Verde. Gerencie projetos, vendas, obras e clientes num só lugar.
          </motion.p>

          <motion.div variants={fadeInUp} className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
            <Link href="/register" className="group relative px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-full font-semibold text-lg transition-all hover:shadow-2xl hover:shadow-blue-600/30 overflow-hidden">
              <span className="relative z-10 flex items-center gap-2">
                Começar Gratuitamente
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </span>
            </Link>
            <button className="group flex items-center gap-3 px-8 py-4 bg-white/10 hover:bg-white/20 backdrop-blur-sm text-white rounded-full font-semibold text-lg transition-all border border-white/20">
              <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                <Play className="w-4 h-4 ml-0.5" />
              </div>
              Ver Demonstração
            </button>
          </motion.div>

          <motion.div variants={fadeInUp} className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
            {[
              { value: "500+", label: "Empresas" },
              { value: "50K+", label: "Unidades Geridas" },
              { value: "2B+", label: "Em Projetos" },
              { value: "99.9%", label: "Uptime" },
            ].map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl sm:text-4xl font-bold text-white mb-1">{stat.value}</div>
                <div className="text-slate-400 text-sm">{stat.label}</div>
              </div>
            ))}
          </motion.div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 100 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.4 }} className="mt-20 relative">
          <div className="absolute -inset-4 bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-3xl blur-2xl" />
          <div className="relative bg-slate-800/50 backdrop-blur-xl rounded-2xl border border-white/10 p-2 shadow-2xl">
            <div className="bg-slate-900 rounded-xl overflow-hidden">
              <div className="flex items-center gap-2 px-4 py-3 bg-slate-800 border-b border-slate-700">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500" />
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                </div>
                <div className="flex-1 flex justify-center">
                  <div className="bg-slate-900 px-4 py-1.5 rounded-lg text-slate-400 text-sm flex items-center gap-2">
                    <Lock className="w-3 h-3" />
                    app.imoos.cv/dashboard
                  </div>
                </div>
              </div>
              <div className="p-6 grid grid-cols-1 lg:grid-cols-3 gap-4">
                <div className="lg:col-span-2 space-y-4">
                  <div className="grid grid-cols-3 gap-4">
                    {[
                      { label: "Vendas", value: "1.2M", change: "+12%" },
                      { label: "Obras", value: "85%", change: "+5%" },
                      { label: "Leads", value: "234", change: "+28%" },
                    ].map((item, i) => (
                      <div key={i} className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
                        <div className="text-slate-400 text-xs mb-1">{item.label}</div>
                        <div className="flex items-end justify-between">
                          <div className="text-xl lg:text-2xl font-bold text-white">{item.value}</div>
                          <div className="text-green-400 text-xs">{item.change}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700 h-48">
                    <div className="flex items-center justify-between mb-4">
                      <div className="text-slate-300 text-sm font-medium">Pipeline de Vendas</div>
                      <div className="flex gap-2">
                        <div className="w-2 h-2 rounded-full bg-blue-500" />
                        <div className="w-2 h-2 rounded-full bg-purple-500" />
                      </div>
                    </div>
                    <div className="space-y-3">
                      {[75, 50, 85, 60].map((width, i) => (
                        <div key={i} className="flex items-center gap-3">
                          <div className="w-16 text-xs text-slate-500">Mês {i + 1}</div>
                          <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                            <div className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full" style={{ width: `${width}%` }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="space-y-4">
                  <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
                    <div className="text-slate-300 text-sm font-medium mb-3">Atividades Recentes</div>
                    <div className="space-y-3">
                      {["Nova reserva #2341", "Pagamento recebido", "Lead qualificado", "Tarefa concluída"].map((item, i) => (
                        <div key={i} className="flex items-center gap-3 text-xs">
                          <div className="w-2 h-2 rounded-full bg-blue-500" />
                          <span className="text-slate-400">{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl p-4">
                    <div className="text-white text-sm font-medium mb-2">Próximo Pagamento</div>
                    <div className="text-2xl font-bold text-white mb-1">45,000</div>
                    <div className="text-white/70 text-xs">Em 5 dias</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

function Features() {
  const features = [
    { icon: Building2, title: "Gestão de Projetos", description: "Acompanhe todos os seus empreendimentos em tempo real. Controle fases, unidades disponíveis e estatísticas de vendas.", color: "blue" },
    { icon: Users, title: "CRM Integrado", description: "Gerencie leads, clientes e reservas num só lugar. Automação de follow-ups e notificações personalizadas.", color: "purple" },
    { icon: TrendingUp, title: "Obras & Construção", description: "Cronogramas, gestão de tarefas, progresso fotográfico e controle de qualidade da obra.", color: "green" },
    { icon: Calculator, title: "Orçamentos & Custos", description: "Controle financeiro completo com mapas de custos, análise de rentabilidade e gestão de pagamentos.", color: "orange" },
    { icon: FileText, title: "Contratos Digitais", description: "Geração automática de contratos, assinatura digital integrada e gestão de documentos.", color: "pink" },
    { icon: Globe, title: "Integração imo.cv", description: "Publique automaticamente no maior portal imobiliário de Cabo Verde. Sincronização em tempo real.", color: "cyan" },
  ];

  const colorClasses: Record<string, string> = {
    blue: "from-blue-500 to-blue-600",
    purple: "from-purple-500 to-purple-600",
    green: "from-green-500 to-green-600",
    orange: "from-orange-500 to-orange-600",
    pink: "from-pink-500 to-pink-600",
    cyan: "from-cyan-500 to-cyan-600",
  };

  return (
    <section id="features" className="py-32 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }} className="text-center mb-20">
          <span className="inline-block px-4 py-2 bg-blue-50 text-blue-600 rounded-full text-sm font-semibold mb-6">Funcionalidades</span>
          <h2 className="text-4xl sm:text-5xl font-bold text-slate-900 mb-6">
            Tudo o que precisa para
            <br />
            <span className="text-blue-600">gerir o seu negócio</span>
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Do primeiro contacto com o cliente à entrega das chaves, o ImoOS acompanha todo o ciclo de vida do seu projeto imobiliário.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="group relative"
            >
              <div className="relative bg-slate-50 hover:bg-white rounded-2xl p-8 transition-all duration-300 hover:shadow-2xl hover:shadow-slate-200/50 border border-slate-100 hover:border-slate-200">
                <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${colorClasses[feature.color]} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                  <feature.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">{feature.title}</h3>
                <p className="text-slate-600 leading-relaxed">{feature.description}</p>
                <div className="mt-6 flex items-center text-blue-600 font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                  Saber mais
                  <ChevronRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function HowItWorks() {
  const steps = [
    { number: "01", title: "Crie a sua conta", description: "Registo simples em menos de 2 minutos. Sem cartão de crédito necessário.", icon: CheckCircle2 },
    { number: "02", title: "Configure o projeto", description: "Adicione os seus empreendimentos, unidades e personalize as definições.", icon: Building2 },
    { number: "03", title: "Comece a vender", description: "Importe leads, faça reservas e acompanhe todo o processo de vendas.", icon: TrendingUp },
  ];

  return (
    <section className="py-32 bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="text-center mb-20">
          <span className="inline-block px-4 py-2 bg-green-50 text-green-600 rounded-full text-sm font-semibold mb-6">Como Funciona</span>
          <h2 className="text-4xl sm:text-5xl font-bold text-slate-900 mb-6">
            Comece em minutos,
            <br />
            <span className="text-blue-600">não em meses</span>
          </h2>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="relative"
            >
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-12 left-full w-full h-0.5 bg-gradient-to-r from-blue-200 to-transparent" />
              )}
              <div className="bg-white rounded-2xl p-8 shadow-lg shadow-slate-200/50 border border-slate-100">
                <div className="text-6xl font-bold text-blue-100 mb-6">{step.number}</div>
                <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center mb-6">
                  <step.icon className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">{step.title}</h3>
                <p className="text-slate-600">{step.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Testimonials() {
  const testimonials = [
    { quote: "O ImoOS transformou completamente a nossa gestão. Conseguimos reduzir o tempo de resposta aos clientes em 60%.", author: "Carlos Silva", role: "Diretor Comercial, Promocasa", rating: 5 },
    { quote: "Finalmente uma plataforma que entende as necessidades específicas do mercado imobiliário cabo-verdiano.", author: "Ana Ferreira", role: "CEO, Imoplus", rating: 5 },
    { quote: "A integração com o imo.cv vale o investimento sozinha. As vendas aumentaram 40% no primeiro trimestre.", author: "Jose Mendes", role: "Gerente de Vendas, Construcoes CV", rating: 5 },
  ];

  return (
    <section id="testimonials" className="py-32 bg-slate-900 overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="text-center mb-20">
          <span className="inline-block px-4 py-2 bg-white/10 text-white rounded-full text-sm font-semibold mb-6">Testemunhos</span>
          <h2 className="text-4xl sm:text-5xl font-bold text-white mb-6">
            O que os nossos
            <br />
            <span className="text-blue-400">clientes dizem</span>
          </h2>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="relative group"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 to-purple-600/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="relative bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8 hover:bg-white/10 transition-colors">
                <div className="flex gap-1 mb-6">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-yellow-400" />
                  ))}
                </div>
                <p className="text-white/90 text-lg mb-8 leading-relaxed">&ldquo;{testimonial.quote}&rdquo;</p>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold">
                    {testimonial.author[0]}
                  </div>
                  <div>
                    <div className="text-white font-semibold">{testimonial.author}</div>
                    <div className="text-white/60 text-sm">{testimonial.role}</div>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Pricing() {
  const plans = [
    { name: "Starter", price: "Grátis", period: "para sempre", description: "Perfeito para começar", features: ["1 projeto ativo", "Até 150 unidades", "10 utilizadores", "CRM básico", "Suporte por email"], cta: "Começar Grátis", popular: false },
    { name: "Pro", price: "49", period: "/mês", description: "Para empresas em crescimento", features: ["20 projetos ativos", "Até 1,000 unidades", "50 utilizadores", "CRM avançado", "Gestão de obras", "Relatórios avançados", "Integração imo.cv", "Suporte prioritário"], cta: "Experimentar 14 dias", popular: true },
    { name: "Enterprise", price: "Personalizado", period: "", description: "Para grandes promotoras", features: ["Projetos ilimitados", "Unidades ilimitadas", "Utilizadores ilimitados", "API dedicada", "Onboarding personalizado", "Suporte 24/7", "SLA garantido", "Infraestrutura dedicada"], cta: "Contactar Vendas", popular: false },
  ];

  return (
    <section id="pricing" className="py-32 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="text-center mb-20">
          <span className="inline-block px-4 py-2 bg-purple-50 text-purple-600 rounded-full text-sm font-semibold mb-6">Preços</span>
          <h2 className="text-4xl sm:text-5xl font-bold text-slate-900 mb-6">
            Planos para todos os
            <br />
            <span className="text-blue-600">tamanhos de negócio</span>
          </h2>
          <p className="text-xl text-slate-600">Comece gratuitamente e escale conforme cresce</p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8 items-stretch">
          {plans.map((plan, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className={`relative rounded-2xl flex flex-col ${plan.popular ? "bg-slate-900 text-white shadow-2xl shadow-slate-900/20 md:-mt-4 md:mb-4" : "bg-slate-50 text-slate-900 border border-slate-200"}`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <span className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-1 rounded-full text-sm font-semibold">Mais Popular</span>
                </div>
              )}

              <div className="p-8 flex flex-col flex-1">
                <div className="mb-6">
                  <h3 className="text-xl font-bold mb-2">{plan.name}</h3>
                  <p className={`text-sm ${plan.popular ? "text-slate-400" : "text-slate-600"}`}>{plan.description}</p>
                </div>

                <div className="mb-8">
                  <span className="text-4xl font-bold">{plan.price === "49" ? "€" + plan.price : plan.price}</span>
                  <span className={plan.popular ? "text-slate-400" : "text-slate-600"}>{plan.period}</span>
                </div>

                <ul className="space-y-4 mb-8 flex-1">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-3">
                      <CheckCircle2 className={`w-5 h-5 flex-shrink-0 ${plan.popular ? "text-blue-400" : "text-blue-600"}`} />
                      <span className={`text-sm ${plan.popular ? "text-slate-300" : "text-slate-600"}`}>{feature}</span>
                    </li>
                  ))}
                </ul>

                <Link href={plan.name === "Enterprise" ? "#" : "/register"} className={`block w-full text-center py-3 rounded-xl font-semibold transition-all ${plan.popular ? "bg-white text-slate-900 hover:bg-slate-100" : "bg-slate-900 text-white hover:bg-slate-800"}`}>
                  {plan.cta}
                </Link>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function FAQ() {
  const faqs = [
    { question: "Quanto tempo leva a implementação?", answer: "A implementação básica pode ser feita em menos de 1 hora. Para projetos maiores com migração de dados, o processo típico leva entre 1-2 semanas, incluindo formação da equipa." },
    { question: "Posso migrar dados do meu sistema atual?", answer: "Sim! Oferecemos ferramentas de importação para Excel/CSV e APIs para integração com sistemas existentes. A nossa equipa de suporte pode ajudar na migração." },
    { question: "O ImoOS funciona em mobile?", answer: "Sim, a plataforma é totalmente responsiva e funciona em qualquer dispositivo. Além disso, temos uma app mobile nativa para iOS e Android com funcionalidades específicas para obra." },
    { question: "Qual é o suporte disponível?", answer: "Todos os planos incluem suporte por email. Planos Pro têm suporte prioritário com resposta em 4 horas. Enterprise inclui suporte 24/7 com gestor de conta dedicado." },
    { question: "Os meus dados estão seguros?", answer: "Absolutamente. Usamos encriptação AES-256, backups diários automáticos, e estamos em conformidade com o RGPD. A infraestrutura está alojada na DigitalOcean com certificações SOC 2." },
  ];

  return (
    <section id="faq" className="py-32 bg-slate-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="text-center mb-20">
          <span className="inline-block px-4 py-2 bg-orange-50 text-orange-600 rounded-full text-sm font-semibold mb-6">FAQ</span>
          <h2 className="text-4xl sm:text-5xl font-bold text-slate-900 mb-6">
            Perguntas
            <span className="text-blue-600"> Frequentes</span>
          </h2>
        </motion.div>

        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="bg-white rounded-xl border border-slate-200 overflow-hidden"
            >
              <details className="group">
                <summary className="flex items-center justify-between p-6 cursor-pointer list-none">
                  <span className="text-lg font-semibold text-slate-900">{faq.question}</span>
                  <ChevronRight className="w-5 h-5 text-slate-400 group-open:rotate-90 transition-transform" />
                </summary>
                <div className="px-6 pb-6 text-slate-600 leading-relaxed">{faq.answer}</div>
              </details>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function CTA() {
  return (
    <section className="py-32 bg-slate-900 relative overflow-hidden">
      <div className="absolute inset-0">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-blue-600/20 rounded-full blur-[120px]" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[100px]" />
      </div>

      <div className="relative max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <motion.div initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-8">
            Pronto para transformar
            <br />
            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">o seu negócio imobiliário?</span>
          </h2>
          <p className="text-xl text-slate-400 mb-12 max-w-3xl mx-auto">
            Junte-se a mais de 500 empresas que já revolucionaram a sua gestão imobiliária com o ImoOS.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/register" className="px-8 py-4 bg-white text-slate-900 rounded-full font-semibold text-lg hover:bg-slate-100 transition-all hover:shadow-2xl hover:shadow-white/10">
              Começar Gratuitamente
            </Link>
            <Link href="/login" className="px-8 py-4 bg-white/10 text-white rounded-full font-semibold text-lg hover:bg-white/20 transition-all border border-white/20">
              Já tenho conta
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

function Footer() {
  const links = {
    Produto: ["Funcionalidades", "Preços", "Integrações", "Mobile App", "API"],
    Empresa: ["Sobre nós", "Carreiras", "Blog", "Contactos", "Parceiros"],
    Recursos: ["Documentação", "Tutoriais", "Webinars", "Comunidade", "Status"],
    Legal: ["Privacidade", "Termos", "Cookies", "RGPD", "SLA"],
  };

  return (
    <footer className="bg-slate-950 py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-12 mb-12">
          <div className="lg:col-span-2">
            <Link href="/landing" className="flex items-center gap-3 mb-6">
              <div className="bg-gradient-to-br from-blue-600 to-blue-700 w-10 h-10 rounded-xl flex items-center justify-center">
                <Building2 className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold text-white">ImoOS</span>
            </Link>
            <p className="text-slate-400 mb-6 max-w-sm">
              A plataforma líder em gestão imobiliária para Cabo Verde. Simplificamos o complexo para que você possa focar no que realmente importa.
            </p>
            <div className="flex gap-4">
              {["twitter", "linkedin", "facebook", "instagram"].map((social) => (
                <a key={social} href="#" className="w-10 h-10 bg-slate-900 rounded-lg flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-800 transition-colors">
                  <Globe className="w-5 h-5" />
                </a>
              ))}
            </div>
          </div>

          {Object.entries(links).map(([category, items]) => (
            <div key={category}>
              <h4 className="text-white font-semibold mb-4">{category}</h4>
              <ul className="space-y-3">
                {items.map((item) => (
                  <li key={item}>
                    <a href="#" className="text-slate-400 hover:text-white transition-colors text-sm">{item}</a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="border-t border-slate-900 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-slate-500 text-sm">
            © 2026 ImoOS. Todos os direitos reservados.
          </p>
          <div className="flex items-center gap-6">
            <a href="#" className="text-slate-500 hover:text-white text-sm transition-colors">Termos de Serviço</a>
            <a href="#" className="text-slate-500 hover:text-white text-sm transition-colors">Política de Privacidade</a>
            <a href="#" className="text-slate-500 hover:text-white text-sm transition-colors">Cookies</a>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-white">
      <Navbar />
      <Hero />
      <Features />
      <HowItWorks />
      <Testimonials />
      <Pricing />
      <FAQ />
      <CTA />
      <Footer />
    </main>
  );
}
