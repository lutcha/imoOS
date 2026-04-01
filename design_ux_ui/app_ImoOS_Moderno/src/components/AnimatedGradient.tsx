export default function AnimatedGradient() {
  return (
    <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
      {/* Base gradient */}
      <div 
        className="absolute inset-0"
        style={{
          background: 'radial-gradient(ellipse at 20% 20%, rgba(124, 58, 237, 0.15) 0%, transparent 50%)',
        }}
      />
      <div 
        className="absolute inset-0"
        style={{
          background: 'radial-gradient(ellipse at 80% 80%, rgba(0, 212, 255, 0.1) 0%, transparent 50%)',
        }}
      />
      <div 
        className="absolute inset-0"
        style={{
          background: 'radial-gradient(ellipse at 50% 50%, rgba(236, 72, 153, 0.05) 0%, transparent 60%)',
        }}
      />
      
      {/* Animated orbs */}
      <div 
        className="absolute w-[600px] h-[600px] rounded-full animate-float-slow"
        style={{
          background: 'radial-gradient(circle, rgba(124, 58, 237, 0.2) 0%, transparent 70%)',
          filter: 'blur(60px)',
          top: '10%',
          left: '-10%',
        }}
      />
      <div 
        className="absolute w-[500px] h-[500px] rounded-full animate-float"
        style={{
          background: 'radial-gradient(circle, rgba(0, 212, 255, 0.15) 0%, transparent 70%)',
          filter: 'blur(80px)',
          top: '50%',
          right: '-5%',
          animationDelay: '2s',
        }}
      />
      <div 
        className="absolute w-[400px] h-[400px] rounded-full animate-float-slow"
        style={{
          background: 'radial-gradient(circle, rgba(236, 72, 153, 0.1) 0%, transparent 70%)',
          filter: 'blur(50px)',
          bottom: '10%',
          left: '30%',
          animationDelay: '4s',
        }}
      />

      {/* Grid overlay */}
      <div 
        className="absolute inset-0 opacity-30"
        style={{
          backgroundImage: `
            linear-gradient(rgba(0, 212, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 212, 255, 0.03) 1px, transparent 1px)
          `,
          backgroundSize: '80px 80px',
        }}
      />
    </div>
  );
}
