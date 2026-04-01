import { useRef, useLayoutEffect, useState } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { ChevronDown, HelpCircle } from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

const faqs = [
  {
    question: 'O ImoOS funciona offline na obra?',
    answer: 'Sim! O ImoOS tem modo offline que permite registar atividades, tirar fotos e preencher checklists mesmo sem internet. Assim que a conexão voltar, tudo sincroniza automaticamente com a nuvem.',
    category: 'Funcionalidades',
  },
  {
    question: 'Integra com o portal imo.cv?',
    answer: 'Sim, temos integração nativa com o imo.cv. Pode publicar e atualizar anúncios diretamente do ImoOS, sincronizar leads recebidos e gerenciar todo o pipeline de vendas num só lugar.',
    category: 'Integrações',
  },
  {
    question: 'Funciona em todas as ilhas de Cabo Verde?',
    answer: 'Absolutamente! O ImoOS é 100% cloud-based e funciona em qualquer lugar com internet. Temos clientes em Santiago, São Vicente, Sal, Boa Vista e todas as outras ilhas.',
    category: 'Suporte',
  },
  {
    question: 'Qual o tempo de implementação?',
    answer: 'O setup básico é feito em 24-48 horas. A importação de dados existentes e treinamento da equipa leva entre 3-5 dias úteis. Oferecemos acompanhamento completo durante todo o processo.',
    category: 'Implementação',
  },
  {
    question: 'O suporte é em português ou crioulo?',
    answer: 'Nosso suporte é em português, mas a nossa equipa local entende e pode comunicar em crioulo cabo-verdiano quando necessário. Estamos disponíveis por telefone, WhatsApp e email em horário comercial.',
    category: 'Suporte',
  },
  {
    question: 'Posso experimentar antes de comprar?',
    answer: 'Sim! Oferecemos 14 dias de teste gratuito em qualquer plano, sem necessidade de cartão de crédito. Durante o trial terá acesso a todas as funcionalidades do plano escolhido.',
    category: 'Planos',
  },
  {
    question: 'Os dados estão seguros?',
    answer: 'Totalmente. Usamos encriptação SSL em todas as transmissões, backups automáticos diários, e servidores com certificação ISO 27001. Seus dados nunca são partilhados com terceiros.',
    category: 'Segurança',
  },
  {
    question: 'Funciona com bancos cabo-verdianos?',
    answer: 'Sim, temos integração com os principais bancos de Cabo Verde para conciliação automática de pagamentos e geração de recibos. Suportamos transferências, depósitos e pagamentos via POS.',
    category: 'Integrações',
  },
];

export default function FAQSection() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const titleRef = useRef<HTMLDivElement>(null);
  const faqsRef = useRef<HTMLDivElement>(null);
  const [openIndex, setOpenIndex] = useState<number | null>(0);

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

      // FAQs entrance
      const faqItems = faqsRef.current?.children;
      if (faqItems) {
        gsap.fromTo(
          faqItems,
          { opacity: 0, y: 20 },
          {
            opacity: 1,
            y: 0,
            duration: 0.5,
            stagger: 0.08,
            ease: 'power3.out',
            scrollTrigger: {
              trigger: section,
              start: 'top 70%',
              toggleActions: 'play none none reverse',
            },
          }
        );
      }
    }, section);

    return () => ctx.revert();
  }, []);

  const toggleFaq = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section
      ref={sectionRef}
      id="faq"
      className="relative bg-deep-space py-20 lg:py-28 overflow-hidden"
    >
      {/* Background glow */}
      <div 
        className="absolute top-1/3 right-0 w-[500px] h-[500px] rounded-full pointer-events-none"
        style={{
          background: 'radial-gradient(circle, rgba(0, 212, 255, 0.08) 0%, transparent 60%)',
          filter: 'blur(60px)',
        }}
      />

      <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-10">
        {/* Title */}
        <div ref={titleRef} className="text-center mb-10 lg:mb-14">
          <span className="text-micro text-neon-blue mb-3 lg:mb-4 block uppercase tracking-wider">Dúvidas Frequentes</span>
          <h2 className="font-display text-3xl sm:text-4xl lg:text-h1 text-white mb-3 lg:mb-4">
            Perguntas <span className="gradient-text">Comuns</span>
          </h2>
          <p className="text-base lg:text-body-lg text-white/60">
            Tudo o que precisa saber sobre o ImoOS
          </p>
        </div>

        {/* FAQ List */}
        <div ref={faqsRef} className="space-y-3 lg:space-y-4">
          {faqs.map((faq, index) => {
            const isOpen = openIndex === index;
            
            return (
              <div
                key={index}
                className={`glass-card overflow-hidden transition-all duration-300 ${
                  isOpen ? 'border-neon-blue/30' : ''
                }`}
              >
                <button
                  onClick={() => toggleFaq(index)}
                  className="w-full px-4 py-4 lg:px-6 lg:py-5 flex items-center justify-between text-left"
                  aria-expanded={isOpen}
                >
                  <div className="flex items-center gap-3 pr-4">
                    <HelpCircle className="w-5 h-5 text-neon-blue flex-shrink-0" />
                    <span className="font-medium text-white text-sm lg:text-base">{faq.question}</span>
                  </div>
                  <ChevronDown 
                    className={`w-5 h-5 text-white/50 flex-shrink-0 transition-transform duration-300 ${
                      isOpen ? 'rotate-180' : ''
                    }`} 
                  />
                </button>
                
                <div 
                  className={`overflow-hidden transition-all duration-300 ${
                    isOpen ? 'max-h-96' : 'max-h-0'
                  }`}
                >
                  <div className="px-4 pb-4 lg:px-6 lg:pb-5 pt-0">
                    <div className="pl-8 border-l-2 border-neon-blue/20">
                      <p className="text-small lg:text-body text-white/70 leading-relaxed">
                        {faq.answer}
                      </p>
                      <span className="inline-block mt-3 px-2 py-1 rounded bg-white/5 text-[10px] lg:text-micro text-white/40 uppercase tracking-wider">
                        {faq.category}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Contact CTA */}
        <div className="mt-10 lg:mt-12 text-center">
          <p className="text-small lg:text-body text-white/60 mb-4">
            Ainda tem dúvidas? Estamos aqui para ajudar.
          </p>
          <a 
            href="#contact"
            onClick={(e) => {
              e.preventDefault();
              document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' });
            }}
            className="inline-flex items-center gap-2 text-neon-blue hover:text-white transition-colors font-medium"
          >
            Falar com a equipa
            <ChevronDown className="w-4 h-4 rotate-[-90deg]" />
          </a>
        </div>
      </div>
    </section>
  );
}
