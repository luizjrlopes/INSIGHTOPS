from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..agent import LocalAgentProvider, UnsafeToolError, dispatch, unsafe_enabled
from ..auth import require
from ..audit import record
from ..db import get_db
from ..models import User
router=APIRouter(prefix="/agent",tags=["agent"])
class QueryBody(BaseModel): question:str=Field(min_length=3,max_length=800)
@router.post("/query")
def query(body:QueryBody,user:User=Depends(require("agent:query")),db:Session=Depends(get_db)):
    provider=LocalAgentProvider(); requests=provider.plan(body.question,unsafe=unsafe_enabled(db)); evidence=[]; calls=[]
    for req in requests:
        try: result=dispatch(db,req)
        except UnsafeToolError as exc:
            record(db,user=user,action="TOOL_BLOCKED",entity_type="AGENT",entity_id=req.name,details=str(exc)); db.commit(); raise HTTPException(403,str(exc))
        calls.append({"tool":req.name,"arguments":req.arguments}); evidence.append(result)
        record(db,user=user,action="TOOL_CALLED",entity_type="AGENT",entity_id=req.name,details="Safe read tool executed",metadata=req.arguments)
    answer=provider.answer(body.question,evidence)
    record(db,user=user,action="ANSWER_GENERATED",entity_type="AGENT",entity_id="analysis",details=f"{len(evidence)} evidence items used"); db.commit()
    return {"answer":answer,"tool_calls":calls,"evidence":evidence,"safety":"read-only allowlist"}
