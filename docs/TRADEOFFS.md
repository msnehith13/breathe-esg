# TRADEOFFS

## 1. No Background Task Queue

**What we didn't build:** Celery + Redis for async ingestion processing.

**Why not:** At prototype scale (files of 10-100 rows), synchronous ingestion completes in milliseconds. Adding Celery would require a Redis instance, worker processes, task state management, and retry logic — significant operational complexity for no observable benefit at this scale.

**What breaks in production:** Files with thousands of rows would cause HTTP request timeouts. The right fix is to return a job ID immediately, process async, and poll for status. The `IngestionRun` model is already designed for this — `status` and `completed_at` fields map directly to a task state model.

---

## 2. No Proration of Cross-Month Billing Periods

**What we didn't build:** Automatic proration of utility bills that span month boundaries.

**Why not:** Proration requires a business rule decision (calendar days? working days? consumption curve assumption?) that belongs to the PM, not the engineer. Building it without that input would be guessing. We flag cross-month bills for analyst review instead.

**What breaks in production:** Monthly carbon reports will show billing period consumption attributed to the wrong month. The analyst must manually split the bill or the PM must define the proration rule.

---

## 3. No Static Airport Distance API Integration

**What we didn't build:** A live aviation distance API call (Aviation Edge, OAG, or similar) for flight distance calculation.

**Why not:** These APIs require paid credentials and add a network dependency to the ingestion pipeline. We use a static lookup table for common Indian airport pairs and flag unknown pairs. This is sufficient to demonstrate the architecture.

**What breaks in production:** Any airport pair not in our static table produces a zero-distance record flagged for review. A client with international travel or non-metro domestic routes would generate large numbers of flagged records requiring manual resolution.

---

## 4. No Emission Factor Management

**What we didn't build:** Emission factor tables, carbon calculation, tCO2e output.

**Why not:** The assignment explicitly states the emphasis is on ingestion architecture, not carbon calculation accuracy. Building emission factors would require sourcing defensible values (IPCC, GHG Protocol, MoEFCC for India), versioning them, and attributing them to each record — a significant domain problem in its own right.

**What this means:** The system produces activity data (kWh consumed, km traveled, litres of diesel) ready for emission factor application. The NormalizedRecord schema supports adding `emission_factor`, `emission_factor_source`, and `tco2e` fields without structural changes.
