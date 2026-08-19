from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..auth import require
from ..db import get_db
from ..models import User
router=APIRouter(prefix="/users",tags=["users"])
@router.get("")
def users(user:User=Depends(require("users:read")),db:Session=Depends(get_db)):
    return [{"id":x.id,"name":x.name,"role":x.role} for x in db.scalars(select(User).order_by(User.id)).all()]
