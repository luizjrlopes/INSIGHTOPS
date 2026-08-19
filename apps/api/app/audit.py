from sqlalchemy.orm import Session
from .models import AuditEvent, User

def record(db: Session, *, user: User | None, actor: str | None=None, role: str | None=None, action: str, entity_type: str, entity_id: str, details: str, metadata: dict | None=None):
    db.add(AuditEvent(actor=actor or (user.name if user else "Sistema"),role=role or (user.role if user else "SISTEMA"),action=action,entity_type=entity_type,entity_id=entity_id,details=details,metadata_json=metadata or {}))
