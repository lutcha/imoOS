---
name: tailwind-design-tokens
description: ImoOS Tailwind CSS design tokens — colors, spacing, typography, tenant dynamic theming. Auto-load when building UI components or configuring Tailwind.
argument-hint: [component] [theme]
allowed-tools: Read, Write
---

# Tailwind Design Tokens — ImoOS

## tailwind.config.ts
```typescript
import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // ImoOS brand (default — can be overridden per tenant)
        primary: {
          50: '#eff6ff', 100: '#dbeafe', 500: '#3b82f6',
          600: '#2563eb', 700: '#1d4ed8', 800: '#1e40af', 900: '#1e3a8a',
        },
        // Status colors
        status: {
          available: '#22c55e',   // green-500
          reserved: '#f59e0b',    // amber-500
          contract: '#8b5cf6',    // violet-500
          sold: '#ef4444',        // red-500
        },
        // CV-specific
        ocean: { DEFAULT: '#0ea5e9', dark: '#0284c7' },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
    },
  },
};
export default config;
```

## Dynamic Tenant Theming
```typescript
// app/layout.tsx — inject tenant primary color as CSS variable
export default async function Layout({ children }: { children: React.ReactNode }) {
  const tenant = await getCurrentTenant();
  return (
    <html style={{ '--color-primary': tenant.primary_color } as React.CSSProperties}>
      <body>{children}</body>
    </html>
  );
}

// Component usage with tenant color
<Button className="bg-[var(--color-primary)] hover:bg-[var(--color-primary)]/90">
  Reservar Unidade
</Button>
```

## Component Class Conventions
```typescript
// Use clsx for conditional classes
import clsx from 'clsx';

const statusClass = clsx({
  'bg-status-available text-white': status === 'AVAILABLE',
  'bg-status-reserved text-white': status === 'RESERVED',
  'bg-status-sold text-white': status === 'SOLD',
});
```

## Key Rules
- Never hardcode colors — use design tokens or `var(--color-primary)`
- Mobile-first: all components start with mobile styles, then `md:` and `lg:`
- Touch targets minimum `h-11` (44px) for mobile app use cases
- Use `text-gray-900` for body text, `text-gray-500` for muted — never pure black
