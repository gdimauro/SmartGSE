# Contributing to Bilancio ESG (SmartGSE)

Thanks for your interest in improving this sustainability & carbon reporting starter. Contributions via issues, pull requests, and discussion are welcome.

## Guiding Principles

- Clarity & auditability: changes should preserve traceability of data → calculation → disclosure.
- Minimal dependencies: keep tooling lean (.NET 8 SDK only unless justified).
- Deterministic generation: CDM outputs must be reproducible (no hidden time / locale variance besides the ISO timestamp already written).
- Secure by default: never commit secrets; prefer environment variables or `dotnet user-secrets` for local use.
- Copilot-assisted, reviewer-owned: AI can help draft; humans are accountable.

## Project Layout

```text
CDM/                    # Generated Common Data Model artifacts (model.json + CSV partitions)
src/
  CdmBootstrapper/      # Generates CDM schema & entity seed CSVs
  DataverseSchemaSeeder/# Seeds Dataverse entities & relationships
.github/workflows/      # CI build pipeline
```

## Prerequisites

- .NET 8 SDK (Preview allowed as per current project state)
- (Optional) Dataverse environment + Azure AD app (ClientId, ClientSecret, TenantId, Url)
- PowerShell 7+ (Windows, Linux, macOS supported)

## Local Setup

```bash
# Restore & build
dotnet build

# Generate CDM artifacts
dotnet run --project src/CdmBootstrapper

# Seed Dataverse (ensure appsettings.json or env vars configured)
dotnet run --project src/DataverseSchemaSeeder
```

## Branching Strategy

- `main`: always buildable. Generated `CDM/` outputs may be committed when schema intentionally changes.
- Feature branches: `feat/<short-kebab>` (e.g., `feat/add-emission-factor-attr`)
- Fix branches: `fix/<short-kebab>`
- Chore / docs: `chore/...`, `docs/...`

## Commit Message Style

Conventional-ish, short imperative first line (≤ 72 chars):

```text
feat(cdm): add intensity attribute to EmissionAggregate
fix(seeder): correct relationship name for initiatives
chore(ci): normalize build workflow yaml
```

Reference issues with `#<id>` when applicable.

## Code Style

- C#: lean, top-level or small classes; prefer records for pure data.
- Use explicit types when clarity > brevity; `var` acceptable for obvious RHS.
- Keep methods < ~60 LOC; extract helpers for readability.
- Nullability enabled → honor warnings.
- Avoid premature abstractions; duplicate once before refactor.

## Generated Artifacts Policy

- `CDM/` folder is source-of-truth artifact for downstream consumers (e.g., lake ingestion, Power BI). Commit regenerated files ONLY when schema or attribute ordering changes.
- Do not hand-edit `model.json`; make changes via `CdmBootstrapper` logic.

## Tests (Future Provision)

Currently no automated tests. If adding logic (e.g., validation, transformation rules):

1. Add a test project (`BilancioESG.Tests`)
2. Add minimal tests (happy path + edge) using xUnit or NUnit
3. Update CI to run `dotnet test`

## Using GitHub Copilot / AI Productively

Include AI responsibly:

- Use it for scaffolding, boilerplate, bulk tuple parameter edits, documentation blocks.
- Always review generated code for: licensing, security (secrets), data correctness.
- Document non-trivial AI assistance in PR description under "Copilot Assistance".
- When prompting Copilot for schema/entity changes: keep a canonical prompt snippet (see below) to ensure consistent style.

### Recommended Prompt Snippet (CDM Changes)

```text
Modify CdmBootstrapper entities list:
Goal: <what you need>
Add/Change entities or attributes ensuring tuple format: ("name","datatype",<true|false>)
Maintain alphabetical consistency where practical; keep required=true only when essential for relational integrity.
```

### Recommended Prompt Snippet (Dataverse Seeder)

```text
Update schema seeder:
Goal: <describe>
Add Ensure<Entity|String|Lookup|Dec|Int|Date> calls preserving naming prefix esg_.
Ensure relationships use consistent schema & collection naming (singular vs plural).
```

## Pull Requests

Checklist BEFORE requesting review:

- [ ] Build passes locally (`dotnet build`)
- [ ] CDM regenerated intentionally (if applicable) & diff reviewed
- [ ] No secrets / credentials added
- [ ] Added or updated docs for user-facing changes
- [ ] PR description includes context + rationale
- [ ] Added "Copilot Assistance" section if AI drafting used

### PR Description Template (copy into PR)

```text
## Summary
<what & why>

## Change Type
- [ ] Feature
- [ ] Fix
- [ ] Refactor
- [ ] Docs
- [ ] Chore

## Implementation Notes
<design decisions>

## Validation
Steps:
1. ...
2. ...

## Copilot Assistance
Prompts used / extent of AI editing.

## Risks & Mitigations
<list>
```

## Filing Issues

See `.github/ISSUE_TEMPLATE/*`. Provide reproduction, expected vs actual behavior, and environment.

## Security / Secrets

Do NOT commit secrets. Use environment variables or local `appsettings.Development.json` not tracked by git. Redact tenant or org specifics when sharing logs.

## License & CLA

Project is under the LICENSE in root. By contributing you agree your work is licensed under the same terms.

## Roadmap (Living)

- Add unit test project
- Introduce emission calculation validation layer
- Add optional source-generated JSON context to remove trimming warnings

## Questions?

Open a discussion or issue.
