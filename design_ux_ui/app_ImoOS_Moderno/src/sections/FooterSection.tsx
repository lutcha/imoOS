import { Linkedin, Instagram, MessageCircle, Twitter } from 'lucide-react';

const footerLinks = {
  produto: [
    { label: 'Funcionalidades', href: '#features' },
    { label: 'Dashboard', href: '#solutions' },
    { label: 'Integrações', href: '#' },
    { label: 'Preços', href: '#' },
  ],
  empresa: [
    { label: 'Sobre nós', href: '#' },
    { label: 'Carreiras', href: '#' },
    { label: 'Blog', href: '#' },
    { label: 'Contacto', href: '#contact' },
  ],
  suporte: [
    { label: 'Documentação', href: '#' },
    { label: 'API', href: '#' },
    { label: 'Status', href: '#' },
    { label: 'FAQ', href: '#' },
  ],
  legal: [
    { label: 'Termos', href: '#' },
    { label: 'Privacidade', href: '#' },
    { label: 'Cookies', href: '#' },
  ],
};

const socialLinks = [
  { icon: Linkedin, href: '#', label: 'LinkedIn', color: 'neon-blue' },
  { icon: Instagram, href: '#', label: 'Instagram', color: 'hot-pink' },
  { icon: Twitter, href: '#', label: 'Twitter', color: 'electric-violet' },
  { icon: MessageCircle, href: '#', label: 'WhatsApp', color: 'green-500' },
];

export default function FooterSection() {
  const scrollToSection = (href: string) => {
    if (href.startsWith('#')) {
      const element = document.getElementById(href.slice(1));
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
    }
  };

  return (
    <footer className="relative bg-void border-t border-white/5">
      {/* Grid background */}
      <div 
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `
            linear-gradient(rgba(0, 212, 255, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 212, 255, 0.02) 1px, transparent 1px)
          `,
          backgroundSize: '60px 60px',
        }}
      />

      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-10 py-16">
        {/* Main Footer Content */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8 mb-12">
          {/* Logo & Description */}
          <div className="col-span-2">
            <a 
              href="#" 
              onClick={(e) => {
                e.preventDefault();
                window.scrollTo({ top: 0, behavior: 'smooth' });
              }}
              className="inline-block mb-4"
            >
              <span className="font-display text-3xl font-bold text-white">
                Imo<span className="gradient-text">OS</span>
              </span>
            </a>
            <p className="text-body text-white/50 mb-6 max-w-sm">
              A primeira plataforma PropTech de Cabo Verde. 
              Transformando a gestão imobiliária com tecnologia de ponta.
            </p>

            {/* Social Links */}
            <div className="flex gap-3">
              {socialLinks.map((social, index) => {
                const Icon = social.icon;
                return (
                  <a
                    key={index}
                    href={social.href}
                    aria-label={social.label}
                    className={`w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center hover:bg-${social.color}/20 transition-all group`}
                  >
                    <Icon className={`w-5 h-5 text-white/60 group-hover:text-${social.color} transition-colors`} />
                  </a>
                );
              })}
            </div>
          </div>

          {/* Links */}
          <div>
            <h4 className="font-display text-sm font-semibold text-white mb-4">Produto</h4>
            <ul className="space-y-3">
              {footerLinks.produto.map((link, index) => (
                <li key={index}>
                  <button
                    onClick={() => scrollToSection(link.href)}
                    className="text-small text-white/50 hover:text-neon-blue transition-colors"
                  >
                    {link.label}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="font-display text-sm font-semibold text-white mb-4">Empresa</h4>
            <ul className="space-y-3">
              {footerLinks.empresa.map((link, index) => (
                <li key={index}>
                  <button
                    onClick={() => scrollToSection(link.href)}
                    className="text-small text-white/50 hover:text-electric-violet transition-colors"
                  >
                    {link.label}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="font-display text-sm font-semibold text-white mb-4">Suporte</h4>
            <ul className="space-y-3">
              {footerLinks.suporte.map((link, index) => (
                <li key={index}>
                  <button
                    onClick={() => scrollToSection(link.href)}
                    className="text-small text-white/50 hover:text-hot-pink transition-colors"
                  >
                    {link.label}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="font-display text-sm font-semibold text-white mb-4">Legal</h4>
            <ul className="space-y-3">
              {footerLinks.legal.map((link, index) => (
                <li key={index}>
                  <button
                    onClick={() => scrollToSection(link.href)}
                    className="text-small text-white/50 hover:text-white transition-colors"
                  >
                    {link.label}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-small text-white/40">
            © 2026 ImoOS. Todos os direitos reservados.
          </p>
          <p className="text-small text-white/40 flex items-center gap-2">
            Feito com <span className="text-hot-pink">♥</span> em Cabo Verde
          </p>
        </div>
      </div>

      {/* Scanline effect */}
      <div 
        className="absolute bottom-0 left-0 right-0 h-[1px] opacity-30"
        style={{
          background: 'linear-gradient(90deg, transparent, #00D4FF, transparent)',
        }}
      />
    </footer>
  );
}
