import { useRef, useLayoutEffect, useState } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { Mail, Phone, MapPin, Send, Sparkles, CheckCircle2 } from 'lucide-react';
import { toast } from 'sonner';

gsap.registerPlugin(ScrollTrigger);

export default function ContactSection() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const formRef = useRef<HTMLDivElement>(null);

  const [formData, setFormData] = useState({
    nome: '',
    empresa: '',
    email: '',
    telefone: '',
    mensagem: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  useLayoutEffect(() => {
    const section = sectionRef.current;
    if (!section) return;

    const ctx = gsap.context(() => {
      // Content entrance
      gsap.fromTo(
        contentRef.current,
        { opacity: 0, x: -50 },
        {
          opacity: 1,
          x: 0,
          duration: 0.8,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: section,
            start: 'top 80%',
            toggleActions: 'play none none reverse',
          },
        }
      );

      // Form entrance
      gsap.fromTo(
        formRef.current,
        { opacity: 0, x: 50 },
        {
          opacity: 1,
          x: 0,
          duration: 0.8,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: section,
            start: 'top 75%',
            toggleActions: 'play none none reverse',
          },
        }
      );
    }, section);

    return () => ctx.revert();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    await new Promise((resolve) => setTimeout(resolve, 1500));

    toast.success('Mensagem enviada!', {
      description: 'Entraremos em contacto em breve.',
      icon: <CheckCircle2 className="w-5 h-5 text-green-400" />,
    });

    setFormData({
      nome: '',
      empresa: '',
      email: '',
      telefone: '',
      mensagem: '',
    });
    setIsSubmitting(false);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  return (
    <section
      ref={sectionRef}
      id="contact"
      className="relative bg-deep-space py-24 overflow-hidden"
    >
      {/* Animated background */}
      <div className="absolute inset-0">
        <div 
          className="absolute top-0 left-1/4 w-[600px] h-[600px] rounded-full animate-float-slow"
          style={{
            background: 'radial-gradient(circle, rgba(0, 212, 255, 0.1) 0%, transparent 60%)',
            filter: 'blur(80px)',
          }}
        />
        <div 
          className="absolute bottom-0 right-1/4 w-[500px] h-[500px] rounded-full animate-float"
          style={{
            background: 'radial-gradient(circle, rgba(124, 58, 237, 0.1) 0%, transparent 60%)',
            filter: 'blur(60px)',
            animationDelay: '2s',
          }}
        />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-10">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Left Content */}
          <div ref={contentRef}>
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card mb-6">
              <Sparkles className="w-4 h-4 text-hot-pink" />
              <span className="text-micro text-white/70">COMECE A SUA TRANSFORMAÇÃO</span>
            </div>

            <h2 className="font-display text-h1 text-white mb-6">
              Pronto para o <span className="gradient-text">Futuro</span>?
            </h2>

            <p className="text-body-lg text-white/60 leading-relaxed mb-10">
              Junte-se às dezenas de promotoras e construtoras que já transformaram 
              a gestão dos seus projetos com o ImoOS.
            </p>

            {/* Contact Info */}
            <div className="space-y-6">
              <div className="flex items-center gap-4 group">
                <div className="w-14 h-14 rounded-xl bg-neon-blue/10 flex items-center justify-center group-hover:bg-neon-blue/20 transition-colors">
                  <Mail className="w-6 h-6 text-neon-blue" />
                </div>
                <div>
                  <p className="text-micro text-white/50 mb-1">EMAIL</p>
                  <p className="text-body text-white">geral@imoos.cv</p>
                </div>
              </div>

              <div className="flex items-center gap-4 group">
                <div className="w-14 h-14 rounded-xl bg-electric-violet/10 flex items-center justify-center group-hover:bg-electric-violet/20 transition-colors">
                  <Phone className="w-6 h-6 text-electric-violet" />
                </div>
                <div>
                  <p className="text-micro text-white/50 mb-1">TELEFONE</p>
                  <p className="text-body text-white">+238 000 00 00</p>
                </div>
              </div>

              <div className="flex items-center gap-4 group">
                <div className="w-14 h-14 rounded-xl bg-hot-pink/10 flex items-center justify-center group-hover:bg-hot-pink/20 transition-colors">
                  <MapPin className="w-6 h-6 text-hot-pink" />
                </div>
                <div>
                  <p className="text-micro text-white/50 mb-1">LOCALIZAÇÃO</p>
                  <p className="text-body text-white">Praia, Cabo Verde</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Form */}
          <div ref={formRef}>
            <form onSubmit={handleSubmit} className="glass-card p-8 relative overflow-hidden">
              {/* Glow effect */}
              <div 
                className="absolute inset-0 opacity-30"
                style={{
                  background: 'radial-gradient(circle at 50% 0%, rgba(0, 212, 255, 0.2), transparent 70%)',
                }}
              />

              <div className="relative">
                <h3 className="font-display text-2xl font-semibold text-white mb-6">
                  Fale Connosco
                </h3>

                <div className="grid md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-micro text-white/50 mb-2">NOME</label>
                    <input
                      type="text"
                      name="nome"
                      value={formData.nome}
                      onChange={handleChange}
                      required
                      className="futuristic-input"
                      placeholder="Seu nome"
                    />
                  </div>
                  <div>
                    <label className="block text-micro text-white/50 mb-2">EMPRESA</label>
                    <input
                      type="text"
                      name="empresa"
                      value={formData.empresa}
                      onChange={handleChange}
                      className="futuristic-input"
                      placeholder="Nome da empresa"
                    />
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-micro text-white/50 mb-2">EMAIL</label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      className="futuristic-input"
                      placeholder="seu@email.com"
                    />
                  </div>
                  <div>
                    <label className="block text-micro text-white/50 mb-2">TELEFONE</label>
                    <input
                      type="tel"
                      name="telefone"
                      value={formData.telefone}
                      onChange={handleChange}
                      className="futuristic-input"
                      placeholder="+238 xxx xx xx"
                    />
                  </div>
                </div>

                <div className="mb-6">
                  <label className="block text-micro text-white/50 mb-2">MENSAGEM</label>
                  <textarea
                    name="mensagem"
                    value={formData.mensagem}
                    onChange={handleChange}
                    required
                    rows={4}
                    className="futuristic-input resize-none"
                    placeholder="Como podemos ajudar?"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="neon-btn w-full flex items-center justify-center gap-2 disabled:opacity-70"
                >
                  {isSubmitting ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      A enviar...
                    </>
                  ) : (
                    <>
                      Enviar Mensagem
                      <Send className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </section>
  );
}
