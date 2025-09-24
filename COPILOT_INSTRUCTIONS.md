Here’s a ready-to-drop **`README.md`** (English) you can place at the root of the repo or under `docs/` as Copilot guidance.

---

# Bilancio ESG — CDM & Dataverse Starter

> **TL;DR**
> This project provides a production-ready baseline for **Sustainability & Carbon reporting** aligned with **ESRS/CSRD**, **GHG Protocol**, and **IFRS S2**, built on **Microsoft Common Data Model (CDM)** and **Dataverse**. It includes a lake-friendly **CDM folder** (`model.json` + CSV partitions) and a .NET 8 **Dataverse schema seeder**. It is designed for repeatable **ETL ingestion**, auditable **calculation runs**, **disclosure mapping**, and analytics (Power BI / XBRL).

---

## Project Objectives

* **Unify ESG data** in a transparent, versioned model (CDM + Dataverse) suitable for ETL, data-entry, and analytics.
* **Compute emissions** (Scope 1/2/3) with factor versioning and GWP sets; support **location-** and **market-based** electricity.
* **Map disclosures** to ESRS/IFRS datapoints for report tables and XBRL/ESRS digital taxonomy exports.
* **Enable governance**: approvals, locks, lineage, evidence, data-quality rules.
* **Stay extensible** to **water, waste, biodiversity, workforce (S), governance (G)** and product footprints.

### Non-Goals (for now)

* Full XBRL rendering engine (only mapping hooks provided).
* Proprietary factor datasets (bring your own source: IEA/DEFRA/etc.).
* Opinionated UI apps (we seed entities; apps/forms are up to your environment).

---

## Deliverables

* **CDM Folder**: `CDM/BilancioESG/model.json` + `entities/*.csv` (headers only; ready for ingestion).
* **Dataverse Schema Seeder** (.NET 8): creates `esg_*` tables, columns, lookups.
* **ETL-friendly structure**: `DataSource/IngestionJob/Transformation/DataQualityRule/Evidence/Lock`.
* **Disclosure bridge**: `Disclosure` + `DisclosureRequirement` mapped to ESRS/IFRS datapoints.

---

## Architecture Overview

```
      ERP/IoT/Files/Surveys ──► Dataflows/ADF/Synapse ──► CDM entities (Activity, Factors, …)
                                      │
                                      ▼
                           Calculation Model/Run (CO2e, GWP, S1/2/3)
                                      │
                                      ├─► Emission / EmissionAggregate
                                      └─► Evidence / Approval / Lock
                                      │
                                      ▼
                    DisclosureRequirement → Report tables → Power BI / XBRL
```

**Core domains**

* **Master**: Organization, LegalEntity, Site, Asset, Meter, Supplier/Customer
* **Reference**: Unit, UnitConversion, Scope3Category, GwpFactor, EmissionFactor, FactorSet
* **Activity Data**: Activity + ActivityDetail\_Electricity, Transport/Procurement (extensible)
* **Results**: Emission, EmissionAggregate; EnergyCertificate/Contract
* **Governance**: Materiality (optional), Risk/Control (optional), Approval, Evidence, Lock
* **Disclosure**: Disclosure, DisclosureRequirement, ReportTable

---

## Setup & Quickstart

### Prerequisites

* **.NET 8 SDK**
* **Dataverse** environment + AAD Application User (Client Id/Secret)
* (Optional) **Power BI / Dataflows** for analytics
* (Optional) Data Lake for CDM folder

### Build & Generate

```bash
dotnet build
# Generate CDM: writes CDM/BilancioESG/model.json and entities/*.csv
dotnet run --project src/CdmBootstrapper

# Seed Dataverse (fill appsettings.json first)
dotnet run --project src/DataverseSchemaSeeder
```

### Repository Layout

```
.
├─ CDM/
│  └─ BilancioESG/
│     ├─ model.json
│     └─ entities/*.csv
├─ src/
│  ├─ CdmBootstrapper/           # generates CDM artifacts
│  └─ DataverseSchemaSeeder/     # creates esg_* entities & lookups
├─ .github/workflows/build.yml   # CI: restore + build .NET
├─ README.md
├─ .gitignore
└─ LICENSE
```

---

## Data & Calculations (Essentials)

* **Emission = Activity.quantity × EmissionFactor.value**; **CO₂e = Σ(gas × GWP100)**.
* **Electricity**: compute **location-based** (grid average) and **market-based** (contracts/GO/REC, residual mix).
* **Scope 3**: categories 1-15 supported by structure; start with Cat. 1 (Purchased goods), 3/4 (Up/Downstream transport), 6 (Business travel), 9 (Downstream transport).
* **Versioning**: FactorSet + GWP set are time-bound (`validFrom/validTo`); **Lock** prevents retroactive changes post-approval.
* **Lineage/Audit**: IngestionJob → Transformation → CalculationRun → Emission/Aggregate with Evidence & Approval.

---

## Data Governance & Security

* **Roles**: Data Engineer (ETL), ESG Analyst (validation/calculation), Approver, Auditor.
* **Controls**: DataQualityRule checks (completeness, units, time logic); Evidence with SHA-256; Approval & Lock per period.
* **Privacy**: store sensitive HR/social data as aggregates unless otherwise required.

---

## Conventions

* **Entity prefix** (Dataverse): `esg_…`
* **IDs**: `id` (GUID), lookups use `{entityName}id` in Dataverse.
* **Units**: SI where possible; conversions defined in reference tables.
* **Scopes**: `1`, `2-location`, `2-market`, `3.<catCode>` (e.g., `3.1`, `3.6`).
* **Naming**: PascalCase for CDM entity names, snake or lower for CSV headers only if mandated by downstream tools.

---

## How to Work with GitHub Copilot (Guidance)

> Add this section to orient Copilot/AI tools when assisting contributors.

### Copilot Goals

* Generate **C#** for Dataverse entity/attribute creation aligned with the `esg_*` schema.
* Generate **ETL mappings** (Power Query M hints or C# mapping stubs) into `Activity`, `EmissionFactor`, etc.
* Propose **DAX measures** (e.g., Scope1/2/3 totals, intensity metrics).
* Draft **Gherkin** acceptance tests for ingestion, calculation, approval/lock flows.

### Prompts You Can Paste in Copilot Chat

* *“Create a C# method that inserts Activity rows with validation for unit and scope, using esg\_* entity names.”\*
* *“Generate DAX for Scope 2 market vs location and a delta measure with conditional formatting.”*
* *“Write Power Query M to normalize electricity bills into Activity + ActivityDetail\_Electricity.”*
* *“Propose Gherkin scenarios to validate period Lock prevents Activity edits.”*

### Style & Review Rules for Copilot Output

* Prefer **.NET 8**; avoid adding external packages unless required.
* Do **not change** existing column names without an ADR.
* Use **Conventional Commits**: `feat:`, `fix:`, `docs:`, `chore:`…
* Always include **unit/integ tests** for calculations and a **README update** when schema changes.

---

## Roadmap (MVP → Next)

**MVP**

* Core CDM + Seeder (done).
* Scope 1 & 2 (location/market) ingestion + calc.
* Scope 3 priority categories (1,3,4,6,9) ingest + basic calc.
* Disclosure mapping for ESRS E1 + governance hooks (Approval/Lock/Evidence).

**Next**

* Water/Waste/Biodiversity tables and dashboards.
* Product Footprint (PCF) and item linkage.
* Power BI template with measures & visuals.
* XBRL export helpers (sample mappings, not a full engine).

---

## Glossary (Quick)

* **ESRS/CSRD**: EU sustainability reporting standards/regulation.
* **GHG Protocol**: Standard for accounting Scope 1/2/3 emissions.
* **IFRS S2**: Climate-related disclosure requirements.
* **CDM**: Common Data Model (schema + partitions for analytics).
* **Dataverse**: Microsoft data platform for structured apps.
* **GO/REC**: Guarantees of Origin / Renewable Energy Certificates.

---

## License

MIT — see `LICENSE`.

---

## Maintainers

* Data & Model: Sustainability/Finance team
* Platform: Data Engineering
* Contact: `your-team@company.tld`

---

**Copy this file as `README.md` (or `docs/COPILOT_README.md`) in your repo.** If you want, I can also add a short **CONTRIBUTING.md** and **ISSUE/PR templates** tuned for Copilot-assisted workflows.
