from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..auth import require
from ..db import get_db
from ..models import AuditEvent, User
router=APIRouter(prefix="/audit",tags=["audit"])
@router.get("")
def events(user:User=Depends(require("audit:read")),db:Session=Depends(get_db)):
    xs=db.scalars(select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(200)).all()
    return [{"id":x.id,"at":x.created_at,"actor":x.actor,"role":x.role,"action":x.action,"entity_type":x.entity_type,"entity_id":x.entity_id,"details":x.details,"metadata":x.metadata_json} for x in xs]
