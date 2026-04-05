/**
 * Service Worker — ImoOS Field App
 * Offline-first strategy para redes 3G
 * 
 * Estratégias:
 * - Cache First para assets estáticos
 * - Network First para API calls (com fallback)
 * - Background Sync para updates pendentes
 */

const CACHE_NAME = "imos-mobile-v1";
const STATIC_ASSETS = [
  "/",
  "/mobile/obra",
  "/mobile/globals.css",
  "/icons/icon-192x192.png",
  "/icons/icon-512x512.png",
];

const API_CACHE_NAME = "imos-api-cache-v1";
const API_ROUTES = ["/api/v1/construction/tasks/"];

// Install: Cache static assets
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activate: Clean old caches
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((cacheNames) =>
        Promise.all(
          cacheNames
            .filter((name) => name !== CACHE_NAME && name !== API_CACHE_NAME)
            .map((name) => caches.delete(name))
        )
      )
      .then(() => self.clients.claim())
  );
});

// Fetch: Route-specific strategies
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests (let app handle them)
  if (request.method !== "GET") {
    return;
  }

  // API calls: Network First with cache fallback
  if (isApiCall(url.pathname)) {
    event.respondWith(networkFirstWithCache(request));
    return;
  }

  // Static assets: Cache First
  if (isStaticAsset(url.pathname)) {
    event.respondWith(cacheFirstWithNetwork(request));
    return;
  }

  // Navigation requests (pages): Stale While Revalidate
  if (request.mode === "navigate") {
    event.respondWith(staleWhileRevalidate(request));
    return;
  }

  // Default: Network with cache fallback
  event.respondWith(networkWithCacheFallback(request));
});

// Background Sync: Process pending syncs
self.addEventListener("sync", (event) => {
  if (event.tag === "imos-sync") {
    event.waitUntil(processBackgroundSync());
  }
});

// Helper functions
function isApiCall(pathname) {
  return API_ROUTES.some((route) => pathname.includes(route));
}

function isStaticAsset(pathname) {
  return (
    pathname.match(/\.(js|css|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf)$/) !== null
  );
}

// Strategy: Cache First, fallback to Network
async function cacheFirstWithNetwork(request) {
  const cached = await caches.match(request);
  if (cached) {
    return cached;
  }

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    console.error("[SW] Cache first failed:", error);
    return new Response("Offline", { status: 503 });
  }
}

// Strategy: Network First, fallback to Cache
async function networkFirstWithCache(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(API_CACHE_NAME);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }
    throw new Error("Network response not OK");
  } catch (error) {
    const cached = await caches.match(request);
    if (cached) {
      console.log("[SW] Serving cached API response");
      return cached;
    }
    console.error("[SW] Network first failed:", error);
    return new Response(
      JSON.stringify({ error: "Offline", cached: false }),
      {
        status: 503,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
}

// Strategy: Stale While Revalidate
async function staleWhileRevalidate(request) {
  const cached = await caches.match(request);

  const fetchPromise = fetch(request)
    .then((networkResponse) => {
      if (networkResponse.ok) {
        const cache = await caches.open(CACHE_NAME);
        cache.put(request, networkResponse.clone());
      }
      return networkResponse;
    })
    .catch((error) => {
      console.log("[SW] Stale while revalidate fetch failed:", error);
      return cached;
    });

  return cached || fetchPromise;
}

// Strategy: Network with cache fallback
async function networkWithCacheFallback(request) {
  try {
    return await fetch(request);
  } catch (error) {
    const cached = await caches.match(request);
    if (cached) {
      return cached;
    }
    throw error;
  }
}

// Background sync processing
async function processBackgroundSync() {
  // This will be handled by the app's useOfflineSync hook
  // We just notify all clients that sync is available
  const clients = await self.clients.matchAll();
  clients.forEach((client) => {
    client.postMessage({
      type: "SYNC_AVAILABLE",
      timestamp: Date.now(),
    });
  });
}

// Listen for messages from the app
self.addEventListener("message", (event) => {
  if (event.data.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
});
