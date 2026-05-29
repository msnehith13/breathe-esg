# DECISIONS

## SAP Ingestion Format

**Decision:** Flat-file CSV with semicolon delimiter and German locale conventions.

**Alternatives considered:** IDoc (XML-based SAP message format), OData service, BAPI.

**Why CSV:** IDoc requires SAP middleware to generate and is difficult to simulate credibly without a live SAP system. OData requires a running SAP gateway. Flat-file exports via MB51 (material movements) and ME2N (purchase orders) are the most common actual export path for sustainability teams — they ask the SAP administrator to run a transaction and export to CSV. This is realistic.

**What we handle:** Semicolon delimiter, decimal comma (`500,5`), DD.MM.YYYY dates, plant codes requiring lookup, mixed units (L, M3, KG, TO), empty rows, zero quantities, missing fields.

**What we ignore:** Multi-company-code exports, IDoc envelope parsing, currency fields, cost center hierarchies, material master lookups beyond our static table.

**What we'd ask the PM:** Which SAP modules are in scope — MM (materials), FI (financials), or both? Do plant codes come with a master data export or do we maintain the lookup table manually?

---

## Utility Ingestion Format

**Decision:** CSV portal export with billing period fields.

**Alternatives considered:** PDF bill parsing (pdfplumber/camelot), direct utility API.

**Why CSV:** Most Indian facilities teams download CSVs from MSEDCL, BESCOM, TSSPDCL portals. PDF parsing adds OCR complexity and failure modes that would consume disproportionate time. Direct APIs exist for very few Indian utilities.

**Key complication handled:** Billing periods that don't align to calendar months. We store both `period_start` and `period_end`, use `period_start` as `activity_date`, and flag cross-month periods for analyst review. Proration logic is documented as a known limitation.

**What we'd ask the PM:** Should cross-month bills be prorated automatically or always flagged for manual split? What's the expected meter count per client?

---

## Travel Ingestion Format

**Decision:** Simulated Concur-style JSON API response ingested as a file upload.

**Alternatives considered:** CSV export from Concur, live Concur API integration.

**Why JSON file:** Concur's Trip and Expense Report APIs return JSON. Simulating this as a file upload demonstrates API-shaped ingestion (vs. CSV) without requiring OAuth credentials. The parser handles the same shape a real API pull would produce.

**Key complication handled:** Flights without distance — we use a static airport pair lookup table for common Indian routes. Unknown airport codes are flagged. This is documented as a known limitation — in production, we'd call an aviation distance API (Aviation Edge, OAG).

**What we'd ask the PM:** Does the client use Concur, Navan, or something else? Do they have access to the API or only CSV exports? Are hotel nights the right activity unit or should we use spend?

---

## Multi-tenancy

**Decision:** Shared schema with `org` FK on every tenant-owned model.

**Why:** Schema-per-tenant adds operational complexity (migration management, connection routing) that isn't justified at prototype scale. Shared schema with FK isolation is industry standard for SaaS at this scale and has a clear path to row-level security (PostgreSQL RLS) if needed.

**Risk:** A missing `.filter(org=request.user.org)` leaks cross-tenant data. We enforce this consistently in all views. In production, a custom QuerySet manager on NormalizedRecord would enforce this automatically.

---

## Approval Workflow Granularity

**Decision:** Batch-level approval (approve all pending records in a run) with row-level override (flag or reject individual records).

**Why:** Analysts typically review a batch together, not row by row. Batch approval is the common case. Row-level flagging handles exceptions. This mirrors how real audit workflows operate.

---

## Synchronous Ingestion

**Decision:** Ingestion runs synchronously in the request/response cycle. No Celery, no background tasks.

**Why:** At prototype scale with files of ~100 rows, synchronous is fine. The tradeoff is that large files would timeout. This is documented in TRADEOFFS.md.

---

## Authentication

**Decision:** HTTP Basic Auth for the prototype. Credentials hardcoded in the React API client.

**Why:** Token-based auth (JWT or DRF TokenAuth) is the right production choice but adds setup overhead. Basic Auth over HTTPS is secure enough for a prototype demo. The frontend api.js makes the credentials explicit and easy to find.

**What we'd change for production:** DRF TokenAuth or JWT with refresh tokens, login form in React, credentials from environment variables.
