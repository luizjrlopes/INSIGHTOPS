# Agent safety

The analytical agent does not receive a database connection or free-form SQL tool.

Allowed tools:

- `get_inventory_risk(region, sku)`
- `get_sales_velocity(region, sku, window_days)`
- `get_support_signal(region, sku)`
- `get_anomaly(anomaly_id)`
- `compare_kpi(metric)`

Each tool validates arguments and returns a structured evidence object. The answer generator can summarize only those results.

`execute_sql`, filesystem writes, external HTTP calls and mutation tools are not registered. The unsafe demo flag deliberately asks the local provider for `execute_sql`; the dispatcher blocks it before execution and writes an audit event.
