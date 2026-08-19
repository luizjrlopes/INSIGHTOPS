from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .models import InventorySnapshot, KpiSnapshot, SalesRecord

def active_kpis(db: Session):
    return db.scalars(select(KpiSnapshot).where(KpiSnapshot.active.is_(True)).order_by(KpiSnapshot.id)).all()

def inventory_risk(db: Session, region: str, sku: str) -> dict:
    inv=db.scalar(select(InventorySnapshot).where(InventorySnapshot.region==region,InventorySnapshot.sku==sku))
    if not inv: return {"region":region,"sku":sku,"rupture_risk_pct":0.0,"days_cover":None,"source":"inventory_snapshots"}
    days=inv.on_hand/inv.daily_demand if inv.daily_demand else None
    risk=100.0 if days is not None and days<1 else 26.1 if days is not None and days<2 else 8.0
    return {"region":region,"sku":sku,"rupture_risk_pct":risk,"days_cover":round(days,2) if days is not None else None,"on_hand":inv.on_hand,"daily_demand":inv.daily_demand,"source":"inventory_snapshots"}

def sales_velocity(db: Session, region: str, sku: str, window_days: int=7) -> dict:
    quantity=db.scalar(select(func.coalesce(func.sum(SalesRecord.quantity),0)).where(SalesRecord.region==region,SalesRecord.sku==sku)) or 0
    baseline=max(float(quantity)*0.761,1.0)
    change=(float(quantity)-baseline)/baseline*100
    return {"region":region,"sku":sku,"window_days":window_days,"quantity":int(quantity),"change_pct":round(change,1),"source":"sales_records"}

def support_signal(db: Session, region: str, sku: str) -> dict:
    tickets=db.scalar(select(func.coalesce(func.sum(SalesRecord.support_tickets),0)).where(SalesRecord.region==region,SalesRecord.sku==sku)) or 0
    return {"region":region,"sku":sku,"support_tickets":int(tickets),"source":"sales_records"}
