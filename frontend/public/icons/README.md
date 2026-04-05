# PWA Icons

Colocar aqui os ícones necessários para o PWA:

## Tamanhos necessários

- `icon-72x72.png`
- `icon-96x96.png`
- `icon-128x128.png`
- `icon-144x144.png`
- `icon-152x152.png`
- `icon-192x192.png` (obrigatório)
- `icon-384x384.png`
- `icon-512x512.png` (obrigatório)

## Especificações

- Formato: PNG
- Fundo: transparente ou cor da marca
- Cor principal: `#1e40af` (azul ImoOS)
- Ícone sugerido: 🏗️ ou 🔨 (construção)

## Gerar ícones

Pode usar ferramentas como:
- [PWA Asset Generator](https://github.com/onderceylan/pwa-asset-generator)
- [Figma](https://figma.com)
- [Icon Kitchen](https://icon.kitchen)

Exemplo com PWA Asset Generator:

```bash
npx pwa-asset-generator logo.png icons/ \
  --scrape false \
  --manifest manifest.json \
  --index ""
```
