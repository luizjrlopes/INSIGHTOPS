# InsightOps AI

InsightOps AI is a locally runnable operational-intelligence product for simulated sales, inventory, returns and support data. It turns CSV and mock connectors into validated datasets, deterministic KPIs, explainable anomaly signals and evidence-backed natural-language analysis through a strictly allowlisted tool layer.

The repository is the final implementation derived from the validated prototype. It preserves the product boundary: **data engineering and anomaly detection are deterministic; the agent can only read through typed tools and cannot execute arbitrary SQL, mutate data, forecast financial results or make investment recommendations.**

## Final stack

- **Web:** Next.js 16.2.11, React 19.2, TypeScript, App Router
- **API:** Python 3.13, FastAPI 0.141.1, SQLAlchemy 2.0.51
- **Data processing:** Polars 1.43.1
- **Database:** PostgreSQL 18.4
- **Auth:** signed JWT demo sessions with server-side RBAC
- **Agent:** provider boundary + deterministic local provider + typed, allowlisted read tools
- **Local runtime:** Docker Compose

No paid service is required for the demo path.

## Product capabilities

- demo login for Administrator, Data Analyst, Operations Manager and Compliance Auditor;
- CSV ingestion plus simulated operational connectors;
- schema and business-rule validation before loading;
- explicit rejected-row quarantine with reasons and source lineage;
- deterministic transformations and KPI snapshots;
- dashboards and filters over the latest valid snapshot;
- statistical anomaly detection separated from agent interpretation;
- anomaly investigation and resolution workflow;
- evidence-backed agent answers using safe read-only tools;
- explicit blocking of arbitrary SQL / unsafe tools;
- report generation and CSV/JSON export history;
- audit trail for loads, anomalies, agent tools, exports and administrative actions;
- pipeline-failure simulation preserving the last valid snapshot;
- repeatable demo reset.

## Run locally

```bash
cp .env.example .env
docker compose up --build
```

Then open:

- Web: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`

The API creates the local schema and seeds the demo dataset automatically.

## Main demo flow

1. Login as **Rafael Tanaka / Analista de Dados**.
2. Open **Dados** and import `examples/sales_august.csv`.
3. Open **Qualidade** and inspect rejected rows and rules.
4. Open **Anomalias** and investigate `AN-104`.
5. Open **Agente** and ask why inventory risk increased.
6. Inspect every tool call and evidence item attached to the answer.
7. Login as **Beatriz Nogueira / Gestora de Operações** and resolve an anomaly with a note.
8. Export the operational report.
9. Login as **Otávio Prado / Auditor de Conformidade** and inspect the audit trail.

## Safety demo

As **Marina Alves / Administrador de Plataforma**, enable the unsafe-agent scenario. The agent attempts to request `execute_sql`; the allowlist blocks the call before any database execution and records the event.

Enable the pipeline-failure scenario and try importing a CSV. The new load is rejected while the last valid KPI snapshot remains active.

## Repository layout

```text
apps/
  api/       FastAPI API, data pipeline, analytics, anomaly engine and safe agent
  web/       Next.js application
examples/    demo CSV data
scripts/     deterministic repository validation
docs/        architecture, data contracts, agent safety and demo guide
```

## Validation

Dependency-light checks:

```bash
python scripts/validate_repo.py
python -m unittest discover apps/api/tests -v
```

Full runtime validation after dependencies are installed:

```bash
docker compose up --build
```

See `docs/architecture.md`, `docs/data-pipeline.md`, `docs/agent-safety.md`, and `docs/demo.md`.
