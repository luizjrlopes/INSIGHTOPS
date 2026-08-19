from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..auth import require
from ..db import get_db
from ..models import DataSource, DatasetLoad, User
from ..pipeline import import_sales_csv

router=APIRouter(prefix="/data",tags=["data"])
@router.get("/sources")
def sources(user:User=Depends(require("data:read")),db:Session=Depends(get_db)):
    return [{"id":s.id,"name":s.name,"kind":s.kind,"status":s.status,"rows":s.row_count,"invalid":s.invalid_count,"last_loaded_at":s.last_loaded_at} for s in db.scalars(select(DataSource).order_by(DataSource.id)).all()]
@router.get("/loads")
def loads(user:User=Depends(require("data:read")),db:Session=Depends(get_db)):
    xs=db.scalars(select(DatasetLoad).order_by(DatasetLoad.created_at.desc()).limit(20)).all()
    return [{"id":x.id,"file_name":x.file_name,"status":x.status,"rows_read":x.rows_read,"rows_accepted":x.rows_accepted,"rows_rejected":x.rows_rejected,"actor":x.actor_name,"error":x.error,"created_at":x.created_at} for x in xs]
@router.post("/import")
async def import_csv(file:UploadFile=File(...),user:User=Depends(require("data:import")),db:Session=Depends(get_db)):
    content=await file.read()
    x=import_sales_csv(db,content=content,file_name=file.filename or "upload.csv",user=user)
    return {"id":x.id,"status":x.status,"rows_read":x.rows_read,"rows_accepted":x.rows_accepted,"rows_rejected":x.rows_rejected,"error":x.error}
