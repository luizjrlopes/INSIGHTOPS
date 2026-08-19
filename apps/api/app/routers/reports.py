from csv import writer
from io import StringIO
import json
from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..analytics import active_kpis
from ..auth import current_user
from ..audit import record
from ..db import get_db
from ..domain import can
from ..models import Anomaly, ExportRecord, User
router=APIRouter(prefix="/reports",tags=["reports"])
@router.get("/summary")
def summary(user:User=Depends(current_user),db:Session=Depends(get_db)):
    if not can(user.role,"reports:read"): return Response(status_code=403)
    return {"kpis":[{"metric":k.metric,"value":k.display_value,"change":k.change_label} for k in active_kpis(db)],"anomalies":[{"id":a.id,"metric":a.metric,"status":a.status,"severity":a.severity} for a in db.scalars(select(Anomaly).order_by(Anomaly.id)).all()]}
@router.post("/export/{format}")
def export(format:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
    if not can(user.role,"reports:export"): return Response(status_code=403)
    if format not in {"csv","json"}: return Response(status_code=404)
    rows=[{"metric":k.metric,"value":k.display_value,"change":k.change_label} for k in active_kpis(db)]
    name=f"insightops_operational_summary.{format}"
    db.add(ExportRecord(format=format.upper(),file_name=name,actor_name=user.name)); record(db,user=user,action="REPORT_EXPORTED",entity_type="REPORT",entity_id=name,details=f"{format.upper()} export generated"); db.commit()
    if format=="json": return Response(json.dumps(rows,ensure_ascii=False,indent=2),media_type="application/json",headers={"Content-Disposition":f'attachment; filename="{name}"'})
    out=StringIO(); cw=writer(out); cw.writerow(["metric","value","change"]); [cw.writerow([r["metric"],r["value"],r["change"]]) for r in rows]
    return Response(out.getvalue(),media_type="text/csv",headers={"Content-Disposition":f'attachment; filename="{name}"'})
