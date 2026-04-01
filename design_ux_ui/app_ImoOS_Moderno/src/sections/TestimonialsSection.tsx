import { useRef, useLayoutEffect, useState } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { Quote, ChevronLeft, ChevronRight, Star } from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

const testimonials = [
  {
    name: 'Ana Lopes',
    role: 'Diretora Comercial',
    company: 'Construtora Horizonte',
    image: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&h=400&fit=crop',
    quote: 'ImoOS eliminou as planilhas. Hoje, a equipa comercial e a obra falam a mesma língua. A produtividade aumentou 40%.',
    rating: 5,
  },
  {
    name: 'Carlos Mendes',
    role: 'Gestor de Projetos',
    company: 'Promotora Sol',
    image: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop',
    quote: 'O controle financeiro em tempo real mudou completamente a forma como gerimos os projetos. Decisões mais rápidas e assertivas.',
    rating: 5,
  },
  {
    name: 'Maria Santos',
    role: 'CEO',
    company: 'Imobiliária PraiaMar',
    image: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&h=400&fit=crop',
    quote: 'Finalmente uma solução pensada para o mercado cabo-verdiano. O suporte local faz toda a diferença.',
    rating: 5,
  },
];

export default function TestimonialsSection() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const titleRef = useRef<HTMLDivElement>(null);
  const carouselRef = useRef<HTMLDivElement>(null);
  const [currentIndex, setCurrentIndex] = useState(0);

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

      // Carousel entrance
      scrollTl.fromTo(
        carouselRef.current,
        { opacity: 0, y: 50 },
        { opacity: 1, y: 0, ease: 'none' },
        0.05
      );

      // SETTLE (30-70%): Hold

      // EXIT (70-100%)
      scrollTl.fromTo(
        titleRef.current,
        { opacity: 1, y: 0 },
        { opacity: 0, y: -30, ease: 'power2.in' },
        0.7
      );

      scrollTl.fromTo(
        carouselRef.current,
        { opacity: 1, y: 0 },
        { opacity: 0, y: 50, ease: 'power2.in' },
        0.72
      );
    }, section);

    return () => ctx.revert();
  }, []);

  const nextSlide = () => {
    setCurrentIndex((prev) => (prev + 1) % testimonials.length);
  };

  const prevSlide = () => {
    setCurrentIndex((prev) => (prev - 1 + testimonials.length) % testimonials.length);
  };

  return (
    <section
      ref={sectionRef}
      className="section-pinned bg-deep-space flex items-center justify-center"
    >
      <div className="relative z-10 w-full max-w-6xl mx-auto px-6 lg:px-10">
        {/* Title */}
        <div ref={titleRef} className="text-center mb-12">
          <span className="text-micro text-neon-blue mb-4 block">TESTEMUNHOS</span>
          <h2 className="font-display text-h1 text-white mb-4">
            O que dizem os <span className="gradient-text">Nossos Clientes</span>
          </h2>
        </div>

        {/* Carousel */}
        <div ref={carouselRef} className="relative">
          {/* Cards Container */}
          <div className="relative h-[400px] perspective-1000">
            {testimonials.map((testimonial, index) => {
              const offset = index - currentIndex;
              const isActive = index === currentIndex;
              
              return (
                <div
                  key={index}
                  className="absolute inset-0 flex items-center justify-center transition-all duration-500"
                  style={{
                    transform: `translateX(${offset * 60}%) translateZ(${isActive ? 0 : -200}px) rotateY(${offset * -15}deg)`,
                    opacity: Math.abs(offset) > 1 ? 0 : 1 - Math.abs(offset) * 0.4,
                    zIndex: isActive ? 10 : 5 - Math.abs(offset),
                  }}
                >
                  <div className={`glass-card p-8 max-w-2xl w-full transition-all duration-500 ${isActive ? 'scale-100' : 'scale-90'}`}>
                    {/* Quote icon */}
                    <Quote className="w-10 h-10 text-neon-blue/30 mb-6" />

                    {/* Quote text */}
                    <p className="font-display text-xl lg:text-2xl text-white leading-relaxed mb-8">
                      "{testimonial.quote}"
                    </p>

                    {/* Author */}
                    <div className="flex items-center gap-4">
                      <img
                        src={testimonial.image}
                        alt={testimonial.name}
                        className="w-14 h-14 rounded-full object-cover border-2 border-neon-blue/30"
                      />
                      <div className="flex-1">
                        <p className="font-display text-lg font-semibold text-white">{testimonial.name}</p>
                        <p className="text-small text-white/60">{testimonial.role}, {testimonial.company}</p>
                      </div>
                      {/* Rating */}
                      <div className="flex gap-1">
                        {[...Array(testimonial.rating)].map((_, i) => (
                          <Star key={i} className="w-5 h-5 text-yellow-400 fill-yellow-400" />
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Navigation */}
          <div className="flex items-center justify-center gap-4 mt-8">
            <button
              onClick={prevSlide}
              className="w-12 h-12 rounded-full glass-card flex items-center justify-center hover:bg-white/10 transition-colors"
            >
              <ChevronLeft className="w-6 h-6 text-white" />
            </button>

            {/* Dots */}
            <div className="flex gap-2">
              {testimonials.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentIndex(index)}
                  className={`w-2 h-2 rounded-full transition-all duration-300 ${
                    index === currentIndex 
                      ? 'w-8 bg-neon-blue' 
                      : 'bg-white/30 hover:bg-white/50'
                  }`}
                />
              ))}
            </div>

            <button
              onClick={nextSlide}
              className="w-12 h-12 rounded-full glass-card flex items-center justify-center hover:bg-white/10 transition-colors"
            >
              <ChevronRight className="w-6 h-6 text-white" />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
