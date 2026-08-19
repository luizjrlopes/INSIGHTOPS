from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from ..auth import current_user
from ..audit import record
from ..db import get_db
from ..domain import can, can_transition
from ..models import Anomaly, User
router=APIRouter(prefix="/anomalies",tags=["anomalies"])
class TransitionBody(BaseModel): status:str; note:str|None=None

def serialize(a): return {"id":a.id,"metric":a.metric,"scope":a.scope,"severity":a.severity,"score":a.score,"delta":a.delta,"status":a.status,"resolution_note":a.resolution_note,"evidence":[{"label":e.label,"value":e.value,"source":e.source} for e in a.evidence]}
@router.get("")
def list_all(user:User=Depends(current_user),db:Session=Depends(get_db)):
    if not can(user.role,"anomalies:read"): raise HTTPException(403)
    return [serialize(a) for a in db.scalars(select(Anomaly).options(selectinload(Anomaly.evidence)).order_by(Anomaly.score.desc())).all()]
@router.get("/{anomaly_id}")
def get_one(anomaly_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
    if not can(user.role,"anomalies:read"): raise HTTPException(403)
    a=db.scalar(select(Anomaly).options(selectinload(Anomaly.evidence)).where(Anomaly.id==anomaly_id))
    if not a: raise HTTPException(404)
    return serialize(a)
@router.post("/{anomaly_id}/transition")
def transition(anomaly_id:str,body:TransitionBody,user:User=Depends(current_user),db:Session=Depends(get_db)):
    a=db.get(Anomaly,anomaly_id)
    if not a: raise HTTPException(404)
    permission="anomalies:resolve" if body.status=="Resolvida" else "anomalies:investigate"
    if not can(user.role,permission): raise HTTPException(403,f"Missing permission: {permission}")
    if not can_transition(a.status,body.status): raise HTTPException(409,f"Invalid transition {a.status} -> {body.status}")
    old=a.status; a.status=body.status
    if body.status=="Resolvida":
        if not body.note or not body.note.strip(): raise HTTPException(422,"Resolution note required")
        a.resolution_note=body.note.strip()
    record(db,user=user,action="ANOMALY_TRANSITION",entity_type="ANOMALY",entity_id=a.id,details=f"{old} -> {body.status}",metadata={"note":body.note}); db.commit()
    return {"ok":True,"status":a.status}
