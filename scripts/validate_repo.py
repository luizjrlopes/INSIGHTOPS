from pathlib import Path
import json, tomllib
root=Path(__file__).resolve().parents[1]
required=["README.md","docker-compose.yml",".env.example","apps/api/pyproject.toml","apps/api/app/main.py","apps/api/app/pipeline.py","apps/api/app/agent.py","apps/api/app/agent_policy.py","apps/api/app/domain.py","apps/web/package.json","apps/web/app/page.tsx","examples/sales_august.csv","docs/architecture.md","docs/agent-safety.md"]
missing=[p for p in required if not (root/p).exists()]
if missing: raise SystemExit("missing: "+", ".join(missing))
json.loads((root/"apps/web/package.json").read_text())
with (root/"apps/api/pyproject.toml").open("rb") as f: tomllib.load(f)
text="\n".join((root/p).read_text(errors="ignore") for p in required)
for token in ["Polars","execute_sql","AN-104","pipeline_fail","unsafe_agent","data:import","anomalies:resolve","reports:export"]:
    if token not in text: raise SystemExit("coverage token missing: "+token)
print("REPO_VALIDATION: PASS")
