from __future__ import annotations
from sqlalchemy.orm import Session
from .analytics import inventory_risk, sales_velocity, support_signal
from .models import Anomaly, SystemFlag
from .agent_policy import ALLOWED_TOOLS, LocalAgentProvider, ToolRequest, UnsafeToolError

def dispatch(db: Session, request: ToolRequest) -> dict:
    if request.name not in ALLOWED_TOOLS: raise UnsafeToolError(f"Tool not allowed: {request.name}")
    a=request.arguments
    if request.name=="get_inventory_risk": return inventory_risk(db,str(a["region"]),str(a["sku"]))
    if request.name=="get_sales_velocity": return sales_velocity(db,str(a["region"]),str(a["sku"]),int(a.get("window_days",7)))
    if request.name=="get_support_signal": return support_signal(db,str(a["region"]),str(a["sku"]))
    if request.name=="get_anomaly":
        anomaly=db.get(Anomaly,str(a["anomaly_id"]))
        return {"id":anomaly.id,"metric":anomaly.metric,"scope":anomaly.scope,"score":anomaly.score,"delta":anomaly.delta,"status":anomaly.status,"source":"anomalies"} if anomaly else {"id":a["anomaly_id"],"missing":True,"source":"anomalies"}
    return {"metric":str(a.get("metric","unknown")),"message":"Metric comparison available through dashboard snapshots","source":"kpi_snapshots"}

def unsafe_enabled(db: Session) -> bool:
    flag=db.get(SystemFlag,"unsafe_agent")
    return bool(flag and flag.enabled)
