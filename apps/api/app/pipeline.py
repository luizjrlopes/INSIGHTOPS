from __future__ import annotations
from io import BytesIO
import polars as pl
from sqlalchemy import update
from sqlalchemy.orm import Session
from .audit import record
from .domain import parse_bool, validate_sales_row
from .models import DataSource, DatasetLoad, KpiSnapshot, RejectedRow, SalesRecord, SystemFlag, User

REQUIRED_COLUMNS={"date","order_id","sku","region","quantity","unit_price","returned","support_tickets"}

def pipeline_failed(db: Session) -> bool:
    flag=db.get(SystemFlag,"pipeline_fail")
    return bool(flag and flag.enabled)

def import_sales_csv(db: Session, *, content: bytes, file_name: str, user: User) -> DatasetLoad:
    source=db.get(DataSource,"sales")
    load=DatasetLoad(source_id="sales",file_name=file_name,status="Validando",actor_name=user.name)
    db.add(load); db.flush()
    if pipeline_failed(db):
        load.status="Falhou"; load.error="Pipeline failure scenario enabled"
        record(db,user=user,action="LOAD_BLOCKED",entity_type="LOAD",entity_id=load.id,details="Falha simulada antes da ativação do snapshot")
        db.commit(); return load
    try:
        frame=pl.read_csv(BytesIO(content),infer_schema_length=1000)
    except Exception as exc:
        load.status="Falhou"; load.error=f"CSV parse error: {exc}"
        db.commit(); return load
    missing=REQUIRED_COLUMNS-set(frame.columns)
    if missing:
        load.status="Falhou"; load.error=f"Missing columns: {', '.join(sorted(missing))}"
        db.commit(); return load
    rows=frame.to_dicts(); accepted=[]; rejected=[]
    for index,row in enumerate(rows,start=2):
        errors=validate_sales_row(row)
        if errors:
            for field,value,rule in errors:
                rejected.append(RejectedRow(load_id=load.id,row_number=index,field=field,value=value,rule=rule,row_json=row))
        else:
            accepted.append(row)
    load.rows_read=len(rows); load.rows_accepted=len(accepted); load.rows_rejected=len({r.row_number for r in rejected})
    db.add_all(rejected)
    for row in accepted:
        db.add(SalesRecord(load_id=load.id,date=str(row["date"]),order_id=str(row["order_id"]),sku=str(row["sku"]),region=str(row["region"]),quantity=int(row["quantity"]),unit_price=float(row["unit_price"]),returned=bool(parse_bool(row["returned"])),support_tickets=int(row["support_tickets"])))
    load.status="Concluída"
    source.row_count=load.rows_read; source.invalid_count=load.rows_rejected; source.last_loaded_at=load.created_at
    activate_kpis(db,load.id,accepted)
    record(db,user=user,action="LOAD_COMPLETED",entity_type="LOAD",entity_id=load.id,details=f"{load.rows_read} linhas lidas; {load.rows_rejected} linhas rejeitadas")
    db.commit(); return load

def activate_kpis(db: Session, load_id: str, rows: list[dict]) -> None:
    db.execute(update(KpiSnapshot).where(KpiSnapshot.active.is_(True)).values(active=False))
    if not rows: return
    revenue=sum(int(r["quantity"])*float(r["unit_price"]) for r in rows if not bool(parse_bool(r["returned"])))
    orders=len({str(r["order_id"]) for r in rows})
    average=revenue/orders if orders else 0.0
    returns=sum(1 for r in rows if bool(parse_bool(r["returned"]))) / len(rows) * 100
    support=sum(int(r["support_tickets"]) for r in rows)
    support_rate=support/max(orders,1)*1000
    metrics=[
        ("Receita líquida",f"R$ {revenue:,.2f}",revenue,"","good"),
        ("Pedidos",f"{orders:,}",float(orders),"","good"),
        ("Ticket médio",f"R$ {average:,.2f}",average,"","good"),
        ("Taxa de devolução",f"{returns:.1f}%",returns,"","warn" if returns>5 else "good"),
        ("Chamados / 1k pedidos",f"{support_rate:.1f}",support_rate,"","good"),
    ]
    db.add_all([KpiSnapshot(load_id=load_id,metric=m,display_value=d,numeric_value=n,change_label=c,kind=k,active=True) for m,d,n,c,k in metrics])
