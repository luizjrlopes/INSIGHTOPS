from __future__ import annotations
from datetime import datetime
import math

ROLE_PERMISSIONS = {
    "ADMIN": {"dashboard:read","data:read","data:import","quality:read","anomalies:read","anomalies:investigate","anomalies:resolve","agent:read","agent:query","reports:read","reports:export","audit:read","users:read","demo:control"},
    "ANALISTA": {"dashboard:read","data:read","data:import","quality:read","anomalies:read","anomalies:investigate","agent:read","agent:query","reports:read"},
    "GESTOR": {"dashboard:read","data:read","quality:read","anomalies:read","anomalies:resolve","agent:read","agent:query","reports:read","reports:export","audit:read"},
    "AUDITOR": {"dashboard:read","data:read","quality:read","anomalies:read","agent:read","reports:read","audit:read"},
}
ANOMALY_TRANSITIONS = {"Aberta":{"Investigando"},"Investigando":{"Resolvida","Aberta"},"Resolvida":{"Investigando"}}

def can(role: str, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())

def can_transition(current: str, target: str) -> bool:
    return target in ANOMALY_TRANSITIONS.get(current, set())

def z_score(value: float, history: list[float]) -> float:
    if len(history) < 2: return 0.0
    mean=sum(history)/len(history)
    variance=sum((x-mean)**2 for x in history)/len(history)
    std=math.sqrt(variance)
    if std == 0: return 0.0
    return (value-mean)/std

def anomaly_severity(score: float) -> str:
    absolute=abs(score)
    if absolute >= 3.0: return "Alta"
    if absolute >= 2.5: return "Média"
    return "Baixa"

def parse_bool(value: object) -> bool | None:
    if isinstance(value,bool): return value
    text=str(value).strip().lower()
    if text in {"true","1","yes","sim"}: return True
    if text in {"false","0","no","nao","não"}: return False
    return None

def validate_sales_row(row: dict) -> list[tuple[str,str,str]]:
    errors=[]
    try: datetime.strptime(str(row.get("date","")), "%Y-%m-%d")
    except ValueError: errors.append(("date",str(row.get("date","")),"valid ISO date"))
    if not str(row.get("order_id","")).strip(): errors.append(("order_id","","order_id required"))
    if not str(row.get("sku","")).strip(): errors.append(("sku","","sku required"))
    if not str(row.get("region","")).strip(): errors.append(("region","","region required"))
    try:
        if int(row.get("quantity",0)) <= 0: raise ValueError
    except (ValueError,TypeError): errors.append(("quantity",str(row.get("quantity","")),"quantity > 0"))
    try:
        if float(row.get("unit_price",-1)) < 0: raise ValueError
    except (ValueError,TypeError): errors.append(("unit_price",str(row.get("unit_price","")),"unit_price >= 0"))
    if parse_bool(row.get("returned")) is None: errors.append(("returned",str(row.get("returned","")),"boolean-like value"))
    try:
        if int(row.get("support_tickets",-1)) < 0: raise ValueError
    except (ValueError,TypeError): errors.append(("support_tickets",str(row.get("support_tickets","")),"support_tickets >= 0"))
    return errors
