# InsightOps AI

[English](README.md) | [Português](README.pt-BR.md)

InsightOps AI is an operational-intelligence platform for transforming sales, inventory, returns and support data into validated datasets, deterministic KPIs, explainable anomaly signals and evidence-backed analysis.

The system is designed around a strict separation of responsibilities: data engineering, KPI calculation and anomaly detection remain deterministic, while the AI layer can only inspect approved information through typed, read-only tools. The agent cannot execute arbitrary SQL, mutate operational data, generate financial forecasts or issue investment recommendations.

## What InsightOps solves

Operational teams often receive data from disconnected sources and need to answer three questions quickly:

1. **Can this data be trusted?**
2. **What changed or looks abnormal?**
3. **What evidence supports the explanation?**

InsightOps addresses that flow end to end by ingesting operational data, validating and quarantining invalid rows, producing reproducible analytics, detecting anomalies through statistical rules and exposing the resulting evidence through dashboards and a constrained AI assistant.

## Core capabilities

- CSV ingestion and simulated operational connectors;
- schema and business-rule validation before data is accepted;
- rejected-row quarantine with explicit reasons and source lineage;
- deterministic transformations with Polars;
- KPI snapshots over the latest valid dataset;
- operational dashboards and filtering;
- statistical anomaly detection separated from AI interpretation;
- anomaly investigation and resolution workflow;
- evidence-backed natural-language analysis through safe tools;
- explicit blocking of arbitrary SQL and non-allowlisted tool calls;
- report generation with CSV/JSON export history;
- audit trail for data loads, anomalies, tool calls, exports and administrative actions;
- failure isolation that preserves the last valid analytical snapshot;
- repeatable local reset for controlled evaluation.

## Architecture

```text
CSV / simulated connectors
        ↓
validation + quarantine
        ↓
Polars transformations
        ↓
PostgreSQL operational analytics store
        ↓
KPI snapshots + anomaly engine
        ↓
FastAPI
        ↓
Next.js UI
        ↓
typed read-only agent tools
```

### Responsibility boundaries

- **Pipeline:** parsing, validation, transformation, load lineage and rejected rows.
- **Analytics:** deterministic KPI formulas and snapshots.
- **Anomaly engine:** statistical detection rules, severity and anomaly lifecycle inputs.
- **API/workflow layer:** RBAC, state transitions and operational actions.
- **Agent layer:** read-only access through explicitly allowlisted typed tools.
- **Audit:** traceability for material user and system actions.

## Technology stack

| Layer | Technology |
|---|---|
| Web | Next.js 16, React 19, TypeScript, App Router |
| API | Python 3.13, FastAPI, SQLAlchemy |
| Data processing | Polars |
| Database | PostgreSQL |
| Authentication | Signed JWT sessions with server-side RBAC |
| AI boundary | Provider abstraction + deterministic local provider + typed tools |
| Local runtime | Docker Compose |

The local environment does not require a paid external service.

## Agent safety model

The AI component is intentionally constrained. It receives operational context only through typed tools whose inputs and outputs are controlled by the application.

This means the agent cannot:

- execute arbitrary SQL;
- write directly to the database;
- mutate anomaly or workflow state;
- bypass RBAC;
- invent new operational metrics outside the deterministic analytics layer;
- perform financial forecasting or investment recommendations.

Unsafe tool requests are rejected before database execution and can be recorded in the audit trail.

## Data-quality model

Incoming records are validated before they become part of the active analytical snapshot. Invalid records are quarantined with their rejection reason and source lineage instead of being silently discarded.

A failed load does not replace the latest valid snapshot. This keeps dashboards and analytical queries on a known-good dataset even when a new import fails validation.

## Local execution

```bash
cp .env.example .env
docker compose up --build
```

Services:

- Web application: `http://localhost:3000`
- API and OpenAPI documentation: `http://localhost:8000/docs`

The API initializes the local schema and seeded dataset automatically.

## Example evaluation flow

A complete local evaluation can cover the main product boundaries:

1. import `examples/sales_august.csv`;
2. inspect validation results and quarantined rows;
3. review KPI changes and anomaly `AN-104`;
4. investigate the anomaly through the evidence-backed agent;
5. inspect the exact tool calls and evidence used by the answer;
6. resolve an anomaly through the authorized workflow;
7. generate an operational export;
8. inspect the resulting audit trail;
9. enable the unsafe-agent scenario and verify that `execute_sql` is blocked;
10. simulate a pipeline failure and confirm that the last valid snapshot remains active.

## Repository structure

```text
apps/
  api/       FastAPI API, pipeline, analytics, anomaly engine and safe agent
  web/       Next.js application
examples/    sample operational datasets
docs/        architecture, data pipeline and agent-safety documentation
scripts/     deterministic repository validation
```

## Validation

Repository and backend validation:

```bash
python scripts/validate_repo.py
python -m unittest discover apps/api/tests -v
```

Frontend validation:

```bash
cd apps/web
npm ci
npm run typecheck
npm run build
```

For the complete local environment:

```bash
docker compose up --build
```

## Documentation

Additional technical details are available in:

- `docs/architecture.md`
- `docs/data-pipeline.md`
- `docs/agent-safety.md`
- `docs/demo.md`
