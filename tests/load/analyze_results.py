"""
analyze_results.py — Analisa CSVs de resultados do Locust
==========================================================

Uso:
    python tests/load/analyze_results.py tests/load/results/load_test_20260318_1200

O Locust gera dois ficheiros CSV:
    <prefix>_stats.csv      — estatísticas por endpoint
    <prefix>_stats_history.csv — evolução ao longo do tempo (não usado aqui)

Thresholds (go-live):
    p95  < 500ms  em todos os endpoints
    p95  < 800ms  em /inventory/units/ (query mais pesada)
    erro < 1%     global
    rps  > 50     req/s global
"""
import csv
import sys
from pathlib import Path

# ── Thresholds ──────────────────────────────────────────────────────────────
GLOBAL_P95_MS    = 500
INVENTORY_P95_MS = 800
MAX_FAILURE_RATE = 0.01   # 1%
MIN_RPS          = 50.0

# Endpoint com threshold relaxado
RELAXED_ENDPOINTS = {"/inventory/units/"}


def parse_stats_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def check(rows: list[dict]) -> bool:
    """Returns True if all thresholds pass."""
    passed = True

    # Find the aggregated row
    totals = [r for r in rows if r.get("Name") in ("Aggregated", "Total")]
    endpoints = [r for r in rows if r.get("Name") not in ("Aggregated", "Total", "")]

    print("\n" + "=" * 70)
    print(f"{'Endpoint':<42} {'p95(ms)':>8} {'Err%':>6} {'RPS':>7}  {'Status'}")
    print("-" * 70)

    for row in endpoints:
        name      = row.get("Name", "?")
        p95       = float(row.get("95%", 0) or 0)
        failures  = int(row.get("Failure Count", 0) or 0)
        requests  = int(row.get("Request Count", 0) or 1)
        rps       = float(row.get("Requests/s", 0) or 0)
        err_rate  = failures / max(requests, 1)

        threshold = INVENTORY_P95_MS if any(ep in name for ep in RELAXED_ENDPOINTS) else GLOBAL_P95_MS
        ok = p95 <= threshold and err_rate <= MAX_FAILURE_RATE
        status = "✅" if ok else "❌"
        if not ok:
            passed = False

        print(f"  {name:<40} {p95:>8.0f} {err_rate:>5.1%} {rps:>7.1f}  {status}")

    print("-" * 70)

    # Global summary from aggregated row
    if totals:
        agg = totals[-1]
        total_req  = int(agg.get("Request Count", 0) or 0)
        total_fail = int(agg.get("Failure Count", 0) or 0)
        global_p95 = float(agg.get("95%", 0) or 0)
        global_rps = float(agg.get("Requests/s", 0) or 0)
        global_err = total_fail / max(total_req, 1)

        print(f"\n  {'GLOBAL (Aggregated)':<40} {global_p95:>8.0f} {global_err:>5.1%} {global_rps:>7.1f}")
        print("=" * 70)

        if global_err > MAX_FAILURE_RATE:
            print(f"\n❌ Failure rate {global_err:.1%} > {MAX_FAILURE_RATE:.0%}")
            passed = False
        if global_rps < MIN_RPS:
            print(f"\n❌ Throughput {global_rps:.1f} req/s < {MIN_RPS} req/s")
            passed = False

    return passed


def main():
    if len(sys.argv) < 2:
        print("Uso: python analyze_results.py <prefix>")
        print("  ex: python analyze_results.py tests/load/results/load_test_20260318_1200")
        sys.exit(1)

    prefix = sys.argv[1].replace("_stats.csv", "").replace("_stats_history.csv", "")
    stats_path = Path(f"{prefix}_stats.csv")

    if not stats_path.exists():
        print(f"Ficheiro não encontrado: {stats_path}")
        sys.exit(1)

    print(f"\nAnalisando: {stats_path}")
    rows = parse_stats_csv(stats_path)
    passed = check(rows)

    if passed:
        print("\n✅ Todos os thresholds cumpridos — sistema pronto para go-live.\n")
        sys.exit(0)
    else:
        print("\n❌ Um ou mais thresholds falharam — optimizar antes do go-live.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
