# SOURCES

## SAP — Fuel and Procurement Data

**Real-world format researched:** SAP flat-file exports via transaction MB51 (material document list) and ME2N (purchase orders by vendor). These are the most common paths for sustainability teams to extract fuel and procurement data without SAP BW or custom ABAP reports.

**What we learned:**

- SAP exports use semicolon delimiters in German locale configurations
- Column headers are in German: `Buchungsdatum` (posting date), `Menge` (quantity), `Einheit` (unit), `Werk` (plant), `Lieferant` (vendor)
- Decimal separator is comma, not period: `500,5` means 500.5
- Exports include a metadata header block before the data rows
- Plant codes (`IN01`, `IN02`) are internal identifiers requiring a lookup table to resolve to human-readable names
- Units vary by material: `L` (litres), `M3` (cubic metres), `KG` (kilograms), `TO` (tonnes)

**Sample data rationale:** 13 rows covering diesel, natural gas, heavy fuel oil, LPG, and coal across two plants. Includes deliberately messy cases: decimal comma quantities, zero quantity row, missing quantity row, unknown plant code (IN03), and mixed units requiring conversion (TO → KG).

**What would break in real deployment:**

- Plant code lookup table must be maintained manually or sourced from SAP material master
- Multi-company-code exports produce duplicate column headers
- Some SAP configurations export dates as YYYYMMDD, not DD.MM.YYYY
- German vs English header variation depending on SAP language setting
- Files over ~10,000 rows would require chunked processing

---

## Utility Electricity Data

**Real-world format researched:** CSV portal exports from Indian state electricity boards — MSEDCL (Maharashtra), BESCOM (Karnataka), TSSPDCL (Telangana), TNEB (Tamil Nadu), BYPL (Delhi). Most large commercial consumers have online portal access with CSV download.

**What we learned:**

- Billing periods are defined by meter reading dates, not calendar months
- A bill from December 12 to January 15 is common — it crosses a month boundary
- Demand (`kVA`) and consumption (`kWh`) are both reported — only consumption is relevant for Scope 2
- Tariff codes identify the rate structure (HT industrial, LT commercial, etc.)
- Multiple meters per site are common for large facilities
- Some portals export consumption in units other than kWh (e.g. `kVAh`) requiring conversion

**Sample data rationale:** 10 rows across 7 meters and 5 sites. Includes cross-month billing periods, a duplicate meter+period combination, zero consumption, and a missing unit field. Sites span Mumbai, Pune, Hyderabad, Chennai, Delhi, and Bangalore — realistic for a multi-site Indian enterprise client.

**What would break in real deployment:**

- PDF bills (common for smaller sites) require OCR parsing — not handled
- kVAh to kWh conversion requires power factor data — not handled
- Automated portal scraping would require maintaining scraper per utility as portals change
- Demand charges are ignored — relevant for some carbon accounting methodologies

---

## Corporate Travel — Flights, Hotels, Ground Transport

**Real-world format researched:** Concur Travel & Expense Report API (SAP Concur) and Navan (formerly TripActions) API. Both expose trip and expense data as JSON. Concur's `/api/expense/expensereport/v2.0/reports` endpoint returns report-level data; individual trips come from `/api/travel/trip/v1.1/`.

**What we learned:**

- Travel platforms categorize expenses by type: air, hotel, car, rail, ground transport
- Flight records often include origin/destination airport codes but not distance
- Business vs economy class matters for emission factor selection
- Hotel stays are reported as nights, not distance
- Ground transport may have distance or only cost
- Employee IDs are present but names are often anonymized in exports
- Some platforms report CO2 estimates directly — these should be treated as indicative, not authoritative

**Sample data rationale:** 10 trips covering economy flights, one business class flight, hotel stays, and ground transport. Includes unknown airport codes (XYZ→ABC), missing employee ID, hotel with no destination, and ground transport with no distance. Airport pairs use IATA codes for realistic Indian routes (BOM, DEL, BLR, MAA, HYD, CCU).

**What would break in real deployment:**

- International flights need a much larger airport distance table or live API
- Concur OAuth token management requires periodic refresh
- Some clients use custom travel management companies with proprietary export formats
- Rail travel (common in India) is not handled — different emission factor category
- Ride-sharing platforms (Ola, Uber corporate) export in different formats than traditional ground transport
