# NAV Ingestion Strategy

## Objective
Ensure reliable, accurate, and auditable ingestion of mutual fund and benchmark NAV data.

---

## Data Sources
- Primary: AMFI / MFAPI
- Secondary (fallback): Paid data providers

---

## Ingestion Modes
1. Daily batch ingestion
2. Historical backfill
3. Manual re-fetch (admin only)

---

## Handling Edge Cases
- Market holidays: skip or carry-forward
- Missing NAVs: retry & flag
- Scheme mergers: mapping table maintained

---

## Design Rules
- Append-only storage
- No overwrites
- Source tagging per NAV