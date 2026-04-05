import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',

  // Ensure CDN/reverse-proxy (DO App Platform) caches RSC navigation responses
  // separately from full HTML responses. Without this, the proxy may serve a
  // cached `text/x-component` RSC payload to a plain browser request, causing
  // the page to display raw RSC flight data instead of HTML.
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Vary',
            value: 'RSC, Next-Router-State-Tree, Next-Router-Prefetch',
          },
        ],
      },
    ];
  },
};

export default nextConfig;
