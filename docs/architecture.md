# Architecture

InsightOps is intentionally a small data product rather than a generic data platform.

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
safe agent tools (read only)
```

## Boundaries

- **Pipeline** owns parsing, validation, transformation, load lineage and rejected rows.
- **Analytics** owns deterministic KPI formulas.
- **Anomaly engine** owns statistical rules and severity; the LLM/provider cannot create an anomaly by opinion.
- **Agent** receives only outputs from allowlisted, typed tools. It cannot execute SQL or mutate state.
- **Workflow/API** owns RBAC and anomaly state transitions.
- **Audit** records material user/system actions.

The local demo uses PostgreSQL directly as the analytics store because the portfolio dataset is intentionally small. A warehouse or streaming system would add complexity without improving the demonstrated product contract.
