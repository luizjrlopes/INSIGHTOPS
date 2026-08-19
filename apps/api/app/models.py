from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

def now(): return datetime.now(timezone.utc)
def uid(prefix: str): return f"{prefix}-{uuid4().hex[:8].upper()}"

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    role: Mapped[str] = mapped_column(String(30), index=True)

class DataSource(Base):
    __tablename__ = "data_sources"
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    kind: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(30), default="Saudável")
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    invalid_count: Mapped[int] = mapped_column(Integer, default=0)
    last_loaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class DatasetLoad(Base):
    __tablename__ = "dataset_loads"
    id: Mapped[str] = mapped_column(String(50), primary_key=True, default=lambda: uid("LOAD"))
    source_id: Mapped[str] = mapped_column(ForeignKey("data_sources.id"), index=True)
    file_name: Mapped[str] = mapped_column(String(240))
    status: Mapped[str] = mapped_column(String(30), index=True)
    rows_read: Mapped[int] = mapped_column(Integer, default=0)
    rows_accepted: Mapped[int] = mapped_column(Integer, default=0)
    rows_rejected: Mapped[int] = mapped_column(Integer, default=0)
    actor_name: Mapped[str] = mapped_column(String(120))
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class RejectedRow(Base):
    __tablename__ = "rejected_rows"
    id: Mapped[str] = mapped_column(String(50), primary_key=True, default=lambda: uid("REJ"))
    load_id: Mapped[str] = mapped_column(ForeignKey("dataset_loads.id", ondelete="CASCADE"), index=True)
    row_number: Mapped[int] = mapped_column(Integer)
    field: Mapped[str] = mapped_column(String(80))
    value: Mapped[str] = mapped_column(Text, default="")
    rule: Mapped[str] = mapped_column(String(240))
    row_json: Mapped[dict] = mapped_column(JSON, default=dict)

class SalesRecord(Base):
    __tablename__ = "sales_records"
    id: Mapped[str] = mapped_column(String(50), primary_key=True, default=lambda: uid("SALE"))
    load_id: Mapped[str] = mapped_column(ForeignKey("dataset_loads.id", ondelete="CASCADE"), index=True)
    date: Mapped[str] = mapped_column(String(10), index=True)
    order_id: Mapped[str] = mapped_column(String(80), index=True)
    sku: Mapped[str] = mapped_column(String(80), index=True)
    region: Mapped[str] = mapped_column(String(80), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Float)
    returned: Mapped[bool] = mapped_column(Boolean, default=False)
    support_tickets: Mapped[int] = mapped_column(Integer, default=0)

class InventorySnapshot(Base):
    __tablename__ = "inventory_snapshots"
    id: Mapped[str] = mapped_column(String(50), primary_key=True, default=lambda: uid("INV"))
    sku: Mapped[str] = mapped_column(String(80), index=True)
    region: Mapped[str] = mapped_column(String(80), index=True)
    on_hand: Mapped[int] = mapped_column(Integer)
    daily_demand: Mapped[float] = mapped_column(Float)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class KpiSnapshot(Base):
    __tablename__ = "kpi_snapshots"
    id: Mapped[str] = mapped_column(String(50), primary_key=True, default=lambda: uid("KPI"))
    load_id: Mapped[str | None] = mapped_column(ForeignKey("dataset_loads.id"), nullable=True, index=True)
    metric: Mapped[str] = mapped_column(String(100), index=True)
    display_value: Mapped[str] = mapped_column(String(80))
    numeric_value: Mapped[float] = mapped_column(Float)
    change_label: Mapped[str] = mapped_column(String(80), default="")
    kind: Mapped[str] = mapped_column(String(20), default="good")
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Anomaly(Base):
    __tablename__ = "anomalies"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    metric: Mapped[str] = mapped_column(String(100))
    scope: Mapped[str] = mapped_column(String(180))
    severity: Mapped[str] = mapped_column(String(30), index=True)
    score: Mapped[float] = mapped_column(Float)
    delta: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(30), index=True)
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    evidence: Mapped[list[AnomalyEvidence]] = relationship(back_populates="anomaly", cascade="all, delete-orphan")

class AnomalyEvidence(Base):
    __tablename__ = "anomaly_evidence"
    id: Mapped[str] = mapped_column(String(50), primary_key=True, default=lambda: uid("EV"))
    anomaly_id: Mapped[str] = mapped_column(ForeignKey("anomalies.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(String(160))
    value: Mapped[str] = mapped_column(String(80))
    source: Mapped[str] = mapped_column(String(120))
    anomaly: Mapped[Anomaly] = relationship(back_populates="evidence")

class ExportRecord(Base):
    __tablename__ = "export_records"
    id: Mapped[str] = mapped_column(String(50), primary_key=True, default=lambda: uid("EXP"))
    format: Mapped[str] = mapped_column(String(20))
    file_name: Mapped[str] = mapped_column(String(200))
    actor_name: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[str] = mapped_column(String(50), primary_key=True, default=lambda: uid("AUD"))
    actor: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(30))
    action: Mapped[str] = mapped_column(String(100), index=True)
    entity_type: Mapped[str] = mapped_column(String(60))
    entity_id: Mapped[str] = mapped_column(String(120))
    details: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class SystemFlag(Base):
    __tablename__ = "system_flags"
    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
