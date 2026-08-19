from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..auth import current_user, issue_token
from ..audit import record
from ..db import get_db
from ..models import User

router=APIRouter(prefix="/auth",tags=["auth"])
class LoginBody(BaseModel): user_id: str

@router.get("/users")
def users(db:Session=Depends(get_db)):
    return [{"id":u.id,"name":u.name,"role":u.role} for u in db.scalars(select(User).order_by(User.id)).all()]

@router.post("/login")
def login(body:LoginBody,db:Session=Depends(get_db)):
    user=db.get(User,body.user_id)
    if not user: raise HTTPException(404,"Unknown demo user")
    record(db,user=user,action="LOGIN",entity_type="SESSION",entity_id=user.id,details=f"{user.name} authenticated as {user.role}"); db.commit()
    return {"token":issue_token(user),"user":{"id":user.id,"name":user.name,"role":user.role}}

@router.get("/me")
def me(user:User=Depends(current_user)):
    return {"id":user.id,"name":user.name,"role":user.role}
