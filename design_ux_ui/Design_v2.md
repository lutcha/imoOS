# ImoOS 2.0 — Design Futurista PropTech

## Conceito Visual: "O Futuro da Construção"

### Identidade Visual
- **Estilo**: Neo-futurismo, Glassmorphism, Cyber-elegance
- **Sensação**: Inovação, tecnologia de ponta, liderança digital
- **Inspiração**: Interfaces de sci-fi, fintech premium, arquitetura paramétrica

### Paleta de Cores

**Cores Primárias:**
- `--neon-blue`: #00D4FF (Ciano elétrico - energia, inovação)
- `--electric-violet`: #7C3AED (Roxo elétrico - tecnologia, premium)
- `--hot-pink`: #EC4899 (Rosa choque - destaque, ação)

**Cores de Fundo:**
- `--deep-space`: #0A0A0F (Quase preto com tom azulado)
- `--midnight`: #111118 (Azul muito escuro)
- `--void`: #07070A (Preto absoluto)

**Cores de Superfície:**
- `--glass`: rgba(255, 255, 255, 0.03) (Glassmorphism base)
- `--glass-border`: rgba(255, 255, 255, 0.08) (Bordas sutis)
- `--glass-highlight`: rgba(255, 255, 255, 0.12) (Hover states)

**Gradientes:**
- Hero gradient: linear-gradient(135deg, #7C3AED 0%, #00D4FF 50%, #EC4899 100%)
- Card glow: radial-gradient(circle at 50% 0%, rgba(0, 212, 255, 0.15), transparent 70%)
- Accent line: linear-gradient(90deg, #00D4FF, #EC4899)

### Tipografia

**Font Family:**
- Display/Headings: "Clash Display" ou "Satoshi" (geometric, bold)
- Body: "Inter" (clean, modern)
- Mono: "JetBrains Mono" (tech feel)

**Hierarchy:**
- Hero: 80-120px, weight 700, letter-spacing -0.03em
- H1: 56-72px, weight 600
- H2: 36-48px, weight 600
- Body: 16-18px, weight 400, line-height 1.6
- Micro: 12px, uppercase, letter-spacing 0.2em

### Efeitos Visuais

**Glassmorphism:**
- backdrop-filter: blur(20px)
- background: rgba(255, 255, 255, 0.03)
- border: 1px solid rgba(255, 255, 255, 0.08)
- border-radius: 24px

**Glow Effects:**
- box-shadow: 0 0 60px rgba(0, 212, 255, 0.3)
- text-shadow: 0 0 40px rgba(0, 212, 255, 0.5)

**3D Transforms:**
- perspective: 1000px
- transform-style: preserve-3d
- rotateX, rotateY para cards

**Background Animado:**
- Mesh gradient animado
- Partículas flutuantes
- Grid tecnológico sutil

---

## Estrutura de Seções (13 Seções)

### Section 1: Hero Immersivo
**pin**: true

**Composição:**
- Background: Mesh gradient animado (roxo → ciano → rosa)
- Partículas flutuantes conectadas por linhas (efeito rede)
- Grid tecnológico sutil no fundo

**Elementos:**
- Logo animado com glow
- Headline massivo com gradiente de texto
- Subheadline com efeito de digitação
- CTAs com glow pulsante
- Dashboard 3D flutuante (mockup com perspective)
- Stats flutuantes em cards glass

**Animações:**
- Headline: revela letra por letra com stagger
- Dashboard: flutuação suave (y: -20px ↔ 20px)
- Partículas: movimento orgânico contínuo
- CTAs: glow pulsante infinito

---

### Section 2: PropTech Revolution
**pin**: true

**Composição:**
- Título central: "A Revolução PropTech Chegou a Cabo Verde"
- 3 cards em formato de triângulo/pirâmide
- Cards com efeito 3D tilt on hover

**Cards:**
1. 🏗️ ConstruTech (ícone animado)
2. 🏠 PropTech (ícone animado)
3. 💰 FinTech (ícone animado)

**Animações:**
- Cards voam de direções diferentes
- Efeito 3D no hover (rotateX/Y baseado em mouse position)
- Glow intensificado no hover

---

### Section 3: Dashboard Holográfico
**pin**: true

**Composição:**
- Dashboard em perspective (3D)
- Elementos do dashboard com glow individual
- Dados animados (contadores, gráficos)

**Elementos:**
- Gráfico de vendas animado (barras crescendo)
- Mapa de calor de projetos
- Cards de métricas com números contando
- Linha do tempo de obras

**Animações:**
- Dashboard rotaciona suavemente no scroll
- Gráficos animam entrada
- Números contagem progressiva

---

### Section 4: Features Orbitais
**pin**: false (flowing)

**Composição:**
- Central element: Círculo central com ícone
- Features em órbita ao redor
- Linhas conectando ao centro

**Features:**
- Gestão de Projetos
- CRM & Vendas
- Controle Financeiro
- Diário de Obra
- Documentação
- Analytics

**Animações:**
- Órbita lenta contínua
- Features pulsam no hover
- Linhas traçam ao scroll

---

### Section 5: Timeline Interativa
**pin**: false

**Composição:**
- Linha do tempo vertical com nodes
- Cada node expande on hover
- Conexões animadas entre nodes

**Etapas:**
1. Lead → 2. Visita → 3. Proposta → 4. Reserva → 5. Contrato → 6. Entrega

**Animações:**
- Linha desenha ao scroll
- Nodes aparecem sequencialmente
- Expansão suave no hover

---

### Section 6: Estatísticas em 3D
**pin**: true

**Composição:**
- 4 grandes números em cards glass
- Cards flutuantes em diferentes alturas
- Background com partículas

**Stats:**
- +2.000 Unidades
- +120 Projetos
- 98% Satisfação
- 24h Suporte

**Animações:**
- Contagem animada
- Cards flutuam independentemente
- Glow sincronizado

---

### Section 7: Integrações Galaxy
**pin**: false

**Composição:**
- Central: Logo ImoOS
- Satélites: Logos de integrações
- Orbitas visuais

**Integrações:**
- imo.cv
- WhatsApp
- Bancos
- Contabilidade
- Google Calendar

**Animações:**
- Satélites orbitam
- Conexões pulsantes
- Hover expande satélite

---

### Section 8: Testemunhos Cards 3D
**pin**: true

**Composição:**
- Cards em carrossel 3D
- Cada card com foto e quote
- Efeito de profundidade

**Animações:**
- Carrossel rotaciona
- Cards têm depth individual
- Transições suaves

---

### Section 9: Mapa de Cabo Verde
**pin**: false

**Composição:**
- Mapa estilizado de Cabo Verde
- Pontos de projeto pulsantes
- Conexões entre ilhas

**Animações:**
- Pontos pulsam
- Linhas traçam rotas
- Hover mostra info do projeto

---

### Section 10: Pricing Cards Flutuantes
**pin**: false

**Composição:**
- 3 cards de preço em glassmorphism
- Card do meio destacado (popular)
- Efeito de flutuação

**Planos:**
- Starter
- Professional (destacado)
- Enterprise

**Animações:**
- Cards flutuam em onda
- Hover: card sobe e brilha
- Botão com glow intenso

---

### Section 11: Demo Interativa
**pin**: true

**Composição:**
- Tela de demo central
- Controles ao redor
- Preview ao vivo

**Animações:**
- Demo screen flutua
- Controles pulsam
- CTA glow intenso

---

### Section 12: CTA Final
**pin**: true

**Composição:**
- Background: Gradiente intenso animado
- Headline massivo
- Formulário minimalista
- Efeito de partículas aceleradas

**Animações:**
- Gradiente shift contínuo
- Partículas convergem para centro
- Formulário aparece com efeito

---

### Section 13: Footer Futurista
**pin**: false

**Composição:**
- Grid tecnológico no fundo
- Links organizados
- Social icons com glow
- Copyright com efeito de scanline

---

## Animações Especiais

### Efeito de Partículas
- 50-100 partículas
- Movimento orgânico (Perlin noise)
- Conexões quando próximas
- Cor: ciano com baixa opacidade

### Efeito de Grid
- Grid de linhas finas
- Efeito de perspectiva (mais denso ao fundo)
- Pulso sutil

### Efeito de Glow
- Todos os elementos interativos têm glow
- Glow intensifica no hover
- Glow pulsante em CTAs importantes

### Efeito 3D Cards
- Perspective: 1000px
- RotateX/Y no hover (max 10deg)
- Transform-style: preserve-3d
- Shadow dinâmica baseada na rotação

### Efeito de Texto
- Gradient text (clip background)
- Glitch effect sutil em headlines
- Typewriter effect em subtítulos

---

## Componentes Especiais

### GlassCard
```
- backdrop-filter: blur(20px)
- background: rgba(255, 255, 255, 0.03)
- border: 1px solid rgba(255, 255, 255, 0.08)
- border-radius: 24px
- box-shadow: 
  0 4px 30px rgba(0, 0, 0, 0.1),
  0 0 0 1px rgba(255, 255, 255, 0.05) inset
```

### NeonButton
```
- background: linear-gradient(135deg, #00D4FF, #7C3AED)
- border-radius: 12px
- box-shadow: 
  0 0 20px rgba(0, 212, 255, 0.4),
  0 0 40px rgba(0, 212, 255, 0.2)
- animation: pulse-glow 2s infinite
```

### GradientText
```
- background: linear-gradient(135deg, #00D4FF, #EC4899)
- -webkit-background-clip: text
- -webkit-text-fill-color: transparent
```

---

## Responsividade

### Desktop (1440px+)
- Todas as animações ativas
- Efeitos 3D completos
- Partículas visíveis

### Tablet (768px - 1439px)
- Animações simplificadas
- Efeitos 3D reduzidos
- Grid ajustado

### Mobile (< 768px)
- Animações essenciais apenas
- Sem efeitos 3D complexos
- Layout single column
- Partículas desativadas

---

## Performance

- Usar `will-change` em elementos animados
- Lazy load de imagens
- Partículas em canvas (não DOM)
- RequestAnimationFrame para animações
- Reduzir partículas em dispositivos menos potentes
