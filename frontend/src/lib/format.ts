/**
 * Format utilities — ImoOS
 * CVE/EUR currency, dates (pt-PT locale, UTC-1 Cape Verde)
 * Skill: unit-pricing-currency (CVE_EUR_RATE = 110.265 fixed parity)
 */

export const CVE_EUR_RATE = 110.265;

/** Format CVE as "1.234.567 CVE" (pt-PT style) */
export function formatCve(value: number | string | null | undefined): string {
  if (value == null || value === "") return "—";
  const n = typeof value === "string" ? parseFloat(value) : value;
  if (isNaN(n)) return "—";
  return (
    new Intl.NumberFormat("pt-PT", {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(n) + " CVE"
  );
}

/** Format EUR as "€ 11.234,56" */
export function formatEur(value: number | string | null | undefined): string {
  if (value == null || value === "") return "—";
  const n = typeof value === "string" ? parseFloat(value) : value;
  if (isNaN(n)) return "—";
  return new Intl.NumberFormat("pt-PT", {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(n);
}

/** Convert CVE to EUR using fixed parity */
export function cveToEur(cve: number | string): number {
  const n = typeof cve === "string" ? parseFloat(cve) : cve;
  return Math.round(n / CVE_EUR_RATE);
}

/** Compact: "2,4M CVE" or "450K CVE" */
export function formatCveCompact(value: number | null | undefined): string {
  if (value == null) return "—";
  if (value >= 1_000_000)
    return `${(value / 1_000_000).toLocaleString("pt-PT", { maximumFractionDigits: 1 })}M CVE`;
  if (value >= 1_000)
    return `${(value / 1_000).toLocaleString("pt-PT", { maximumFractionDigits: 0 })}K CVE`;
  return formatCve(value);
}

/** Format m² area */
export function formatArea(value: number | string | null | undefined): string {
  if (value == null || value === "") return "—";
  const n = typeof value === "string" ? parseFloat(value) : value;
  if (isNaN(n)) return "—";
  return `${new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 1 }).format(n)} m²`;
}

/** Format date as "12 Mar 2026" */
export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  return new Intl.DateTimeFormat("pt-PT", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "Atlantic/Cape_Verde",
  }).format(new Date(iso));
}

/** Format datetime as "12 Mar 2026, 14:30" */
export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return "—";
  return new Intl.DateTimeFormat("pt-PT", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "Atlantic/Cape_Verde",
  }).format(new Date(iso));
}
