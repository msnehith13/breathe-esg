# DATA MODEL

## Overview

The schema is organized around a clear separation of concerns:

- **What came in** (ingestion layer)
- **What it means** (emissions layer)
- **What happened to it** (review and audit layer)
- **Who owns it** (organization layer)

Every normalized record traces back to a raw record, which traces back to an ingestion run. Nothing is orphaned. Nothing is silently dropped.

---

## Organizations

### `Organization`

The tenant root. Every record in the system belongs to an org. Multi-tenancy is implemented as shared schema with org FK isolation — simpler than schema-per-tenant and sufficient for a prototype with a clear path to row-level security if needed.

Fields: `id`, `name`, `slug`, `created_at`

### `User` (extends Django AbstractUser)

Custom user model with an `org` FK. Extending AbstractUser rather than using a profile model avoids the join on every auth check and is Django's own recommendation when you know you'll need custom fields. Superusers may have `org=None` for platform-level administration.

**Why extend before first migration:** Django's auth system caches the user model. Swapping it after migrations exist requires a full reset. We set `AUTH_USER_MODEL` before running any migration.

---

## Ingestion Layer

### `IngestionRun`

One record per upload event. Tracks the source type, who uploaded, what file, and the outcome (row counts, status). This exists so that if something goes wrong, you know exactly which file caused it and when.

Status lifecycle: `PENDING → PROCESSING → COMPLETED | FAILED`

**Why track counts here:** Analysts need a summary before drilling into individual records. The dashboard shows run-level health at a glance.

### `RawRecord`

One record per row in the original file, stored as-is in a JSONField. Never modified after creation.

**This is the source-of-truth anchor.** If normalization has a bug, we can re-run the normalization logic against raw records without re-uploading the file. The original data is never lost.

`parse_errors` is a JSON array of error strings — multiple things can be wrong with one row simultaneously.

---

## Emissions Layer

### `NormalizedRecord`

The clean, unified output. One per successfully parsed raw row, linked back via OneToOne FK to its RawRecord.

**Why OneToOne and not FK:** Each raw record produces at most one normalized record. OneToOne enforces this at the database level and makes the reverse lookup unambiguous.

**Key design decisions:**

- `scope` uses GHG Protocol categories (Scope 1/2/3) as a controlled vocabulary
- `category` is free text — GHG Protocol sub-categories vary enough that an enum would be premature
- `original_unit` and `normalized_unit` are both stored — we never throw away what the source said
- `normalized_quantity` is the post-conversion value (e.g. SAP tonnes converted to KG)
- `is_manually_edited` is a boolean flag — if an analyst changed any field, this is true regardless of what changed
- `approval_status` drives the analyst workflow: `PENDING → APPROVED | REJECTED`
- Approved records are immutable — enforced at the service layer

**Scope assignment rationale:**

- SAP fuel/procurement → Scope 1 (direct combustion)
- Utility electricity → Scope 2 (purchased energy)
- Corporate travel → Scope 3 (value chain)

---

## Review Layer

### `AnalystFlag`

Analyst-raised flags on specific records. Separate model because a record can accumulate multiple flags across its lifecycle. Collapsing this into a single field on NormalizedRecord would lose history.

Flags can be resolved — `resolved`, `resolved_by`, `resolved_at` track the full lifecycle.

### `AuditLog`

Immutable log of every meaningful state change. Written at the service layer, never updated, never deleted. `before_state` and `after_state` are JSON snapshots.

**Why immutable:** Auditors require a tamper-evident trail. We enforce immutability by removing add/change permissions in Django admin and never calling `.save()` on existing log entries in the service layer.

Actions: `INGESTED`, `FLAGGED`, `EDITED`, `APPROVED`, `REJECTED`, `FLAG_RESOLVED`

---

## What This Schema Deliberately Does Not Include

- **Emission factors** — out of scope per assignment brief
- **Carbon calculations** — out of scope per assignment brief
- **Role-based permissions** — one analyst role is sufficient for prototype; RBAC would be the next addition
- **File storage** — files are not persisted to disk; raw data is stored in JSONField on RawRecord
