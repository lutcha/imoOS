---
name: seo-multi-tenant
description: Dynamic SEO metadata per tenant and page for ImoOS — Next.js metadata API, sitemap, canonical URLs with subdomain. Auto-load when building public-facing pages.
argument-hint: [page-type] [tenant]
allowed-tools: Read, Write
---

# SEO for Multi-Tenant ImoOS

## Dynamic Metadata per Tenant
```typescript
// app/layout.tsx
import type { Metadata } from 'next';
import { getCurrentTenant } from '@/lib/tenant';

export async function generateMetadata(): Promise<Metadata> {
  const tenant = await getCurrentTenant();
  return {
    metadataBase: new URL(`https://${tenant.subdomain}.imos.cv`),
    title: { default: tenant.name, template: `%s | ${tenant.name}` },
    description: `${tenant.name} — Imóveis em Cabo Verde`,
    openGraph: {
      type: 'website',
      locale: 'pt_PT',
      siteName: tenant.name,
      images: [{ url: tenant.settings.logo_url }],
    },
  };
}
```

## Project/Unit Page SEO
```typescript
// app/projects/[slug]/page.tsx
export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  const project = await getProject(params.slug);
  return {
    title: project.name,
    description: `${project.unit_count} unidades disponíveis. A partir de ${formatCVE(project.min_price)}.`,
    openGraph: {
      images: [{ url: project.cover_image_url, width: 1200, height: 630 }],
    },
    alternates: {
      canonical: `/projects/${project.slug}`,
    },
  };
}
```

## Sitemap per Tenant
```typescript
// app/sitemap.ts
export default async function sitemap() {
  const projects = await getPublicProjects();
  return [
    { url: '/', lastModified: new Date(), changeFrequency: 'daily', priority: 1 },
    ...projects.map(p => ({
      url: `/projects/${p.slug}`,
      lastModified: p.updated_at,
      changeFrequency: 'weekly' as const,
      priority: 0.8,
    })),
  ];
}
```

## Key Rules
- Canonical URL must use subdomain (`empresa-a.imos.cv/projects/...`)
- `metadataBase` must be set to tenant subdomain — affects all relative URLs
- Only public/published content in sitemap — never draft or reserved units
- Open Graph images must be 1200x630px for best social sharing
