from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..auth import current_user
from ..audit import record
from ..db import get_db
from ..domain import can
from ..models import SystemFlag, User
from ..seed import reset_demo
router=APIRouter(prefix="/demo",tags=["demo"])
class FlagBody(BaseModel): enabled:bool
@router.put("/flags/{key}")
def flag(key:str,body:FlagBody,user:User=Depends(current_user),db:Session=Depends(get_db)):
    if not can(user.role,"demo:control"): raise HTTPException(403)
    if key not in {"pipeline_fail","unsafe_agent"}: raise HTTPException(404)
    item=db.get(SystemFlag,key); item.enabled=body.enabled
    record(db,user=user,action="DEMO_FLAG_CHANGED",entity_type="FLAG",entity_id=key,details=f"enabled={body.enabled}"); db.commit(); return {"key":key,"enabled":item.enabled}
@router.post("/reset")
def reset(user:User=Depends(current_user),db:Session=Depends(get_db)):
    if not can(user.role,"demo:control"): raise HTTPException(403)
    reset_demo(db); return {"ok":True}
