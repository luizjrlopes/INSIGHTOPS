# Data pipeline

## Canonical sales CSV

Required columns:

- `date` — ISO date
- `order_id` — non-empty identifier
- `sku` — non-empty identifier
- `region` — operational region
- `quantity` — integer greater than zero
- `unit_price` — number greater than or equal to zero
- `returned` — boolean-like value (`true/false/1/0/yes/no`)
- `support_tickets` — integer greater than or equal to zero

Rows violating a rule are quarantined in `rejected_rows`. They are never silently repaired.

A successful load creates a new immutable-ish `DatasetLoad` record and replaces the active KPI snapshot only after validation/transformation completes. If the pipeline-failure flag is enabled, the new load fails before snapshot activation, preserving the previous valid dashboard.
