from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..analytics import active_kpis
from ..auth import require
from ..db import get_db
from ..models import Anomaly, DatasetLoad, SystemFlag, User

router=APIRouter(prefix="/dashboard",tags=["dashboard"])
@router.get("")
def dashboard(user:User=Depends(require("dashboard:read")),db:Session=Depends(get_db)):
    kpis=[{"metric":k.metric,"display_value":k.display_value,"numeric_value":k.numeric_value,"change":k.change_label,"kind":k.kind} for k in active_kpis(db)]
    anomalies=db.scalars(select(Anomaly).where(Anomaly.status!="Resolvida").order_by(Anomaly.score.desc())).all()
    last=db.scalar(select(DatasetLoad).order_by(DatasetLoad.created_at.desc()))
    flag=db.get(SystemFlag,"pipeline_fail")
    return {"kpis":kpis,"anomalies":[{"id":a.id,"metric":a.metric,"scope":a.scope,"severity":a.severity,"score":a.score,"delta":a.delta,"status":a.status} for a in anomalies],"pipeline_failed":bool(flag and flag.enabled),"last_load":serialize_load(last) if last else None}

def serialize_load(x): return {"id":x.id,"file_name":x.file_name,"status":x.status,"rows_read":x.rows_read,"rows_rejected":x.rows_rejected,"created_at":x.created_at}
