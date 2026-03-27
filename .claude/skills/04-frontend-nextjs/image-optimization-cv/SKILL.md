---
name: image-optimization-cv
description: Image loading optimized for Cabo Verde low-bandwidth conditions — next/image with S3 loader, WebP, lazy loading. Auto-load when adding images or media galleries.
argument-hint: [image-type] [context]
allowed-tools: Read, Write
---

# Image Optimization for Cabo Verde — ImoOS

## next/image with S3 Loader
```typescript
// next.config.ts
const config = {
  images: {
    loader: 'custom',
    loaderFile: './lib/s3-image-loader.ts',
    formats: ['image/webp'],  // Always serve WebP
    deviceSizes: [640, 750, 828, 1080],
    imageSizes: [16, 32, 64, 128, 256],
  },
};

// lib/s3-image-loader.ts
export default function s3Loader({ src, width, quality }: ImageLoaderProps) {
  const q = quality || 75;
  return `${process.env.NEXT_PUBLIC_CDN_URL}/${src}?w=${width}&q=${q}&fmt=webp`;
}
```

## Unit Photo Gallery (Bandwidth-Aware)
```typescript
// components/UnitGallery.tsx
import Image from 'next/image';

export function UnitGallery({ photos }: { photos: string[] }) {
  return (
    <div className="grid grid-cols-2 gap-2">
      {photos.map((src, i) => (
        <Image
          key={src}
          src={src}
          alt={`Foto ${i + 1}`}
          width={400}
          height={300}
          quality={70}           // Reduce quality for gallery thumbs
          loading={i === 0 ? 'eager' : 'lazy'}  // First image eager, rest lazy
          placeholder="blur"
          blurDataURL="data:image/webp;base64,..."  // Tiny placeholder
          className="rounded-lg object-cover"
        />
      ))}
    </div>
  );
}
```

## S3 Upload with Compression
```typescript
// lib/upload.ts
export async function uploadUnitPhoto(file: File, tenantSlug: string) {
  // Compress before upload to save storage and bandwidth
  const compressed = await compressImage(file, { maxWidth: 1920, quality: 0.8 });

  // Get presigned URL from Django
  const { presigned_url, cdn_url } = await apiClient.post('/api/v1/media/presign/', {
    content_type: 'image/webp',
    tenant_prefix: `tenants/${tenantSlug}/units/`,
  });

  await fetch(presigned_url, { method: 'PUT', body: compressed });
  return cdn_url;
}
```

## Key Rules
- Always serve WebP — 25-35% smaller than JPEG for same quality
- Compress before S3 upload — max 1920px wide, 80% quality
- Lazy load all images except first in view (LCP optimization)
- Target < 200KB per gallery thumbnail, < 500KB for full-view image
