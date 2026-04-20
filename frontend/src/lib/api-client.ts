/**
 * Axios API client — ImoOS
 * Pattern: in-memory access token + httpOnly refresh cookie
 * Skill: api-client-tenant-header
 */
import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// In-memory token store — cleared on page unload (XSS safe)
let _accessToken: string | null = null;
let _tenantSchema: string | null = null;

export function setAccessToken(token: string | null): void {
  _accessToken = token;
}

export function setTenantSchema(schema: string | null): void {
  _tenantSchema = schema;
}

export function getAccessToken(): string | null {
  return _accessToken;
}

export function getTenantSchema(): string | null {
  return _tenantSchema;
}

// ------------------------------------------------------------------

const apiClient = axios.create({
  baseURL: `${API_URL}/api/v1`,
  timeout: 10_000,
  headers: { "Content-Type": "application/json" },
});

// Request interceptor — inject JWT + tenant header + trailing slash
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken();
  const schema = getTenantSchema();

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  if (schema) {
    // Observability / logging; Django uses JWT claim for actual auth
    config.headers["X-Tenant-Schema"] = schema;
  }
  
  // Ensure trailing slash on backend requests to prevent Django 301 redirects destroying POST data
  if (config.url && !config.url.endsWith('/') && !config.url.includes('?')) {
    config.url += '/';
  } else if (config.url && config.url.includes('?') && !config.url.split('?')[0].endsWith('/')) {
    const parts = config.url.split('?');
    config.url = `${parts[0]}/?${parts[1]}`;
  }

  return config;
});

// Response interceptor — handle 401 with one refresh attempt
let _isRefreshing = false;
let _refreshQueue: Array<(token: string | null) => void> = [];

function processQueue(token: string | null): void {
  _refreshQueue.forEach((resolve) => resolve(token));
  _refreshQueue = [];
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (_isRefreshing) {
        return new Promise((resolve, reject) => {
          _refreshQueue.push((token) => {
            if (!token) return reject(error);
            originalRequest.headers.Authorization = `Bearer ${token}`;
            resolve(apiClient(originalRequest));
          });
        });
      }

      originalRequest._retry = true;
      _isRefreshing = true;

      try {
        // Call Next.js API route — reads httpOnly refresh cookie
        const resp = await fetch("/api/auth/refresh", { method: "POST" });
        if (!resp.ok) throw new Error("Refresh failed");
        const { access_token, tenant_schema } = await resp.json();

        setAccessToken(access_token);
        setTenantSchema(tenant_schema);
        processQueue(access_token);

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);
      } catch {
        processQueue(null);
        setAccessToken(null);
        setTenantSchema(null);
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
        return Promise.reject(error);
      } finally {
        _isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
