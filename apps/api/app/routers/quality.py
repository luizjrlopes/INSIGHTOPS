from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..auth import require
from ..db import get_db
from ..models import RejectedRow, User
router=APIRouter(prefix="/quality",tags=["quality"])
@router.get("/rejections")
def rejections(user:User=Depends(require("quality:read")),db:Session=Depends(get_db)):
    xs=db.scalars(select(RejectedRow).order_by(RejectedRow.id.desc()).limit(100)).all()
    return [{"id":x.id,"load_id":x.load_id,"row":x.row_number,"field":x.field,"value":x.value,"rule":x.rule,"row_json":x.row_json} for x in xs]
