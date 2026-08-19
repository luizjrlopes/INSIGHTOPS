from sqlalchemy import delete
from sqlalchemy.orm import Session
from .models import Anomaly, AnomalyEvidence, AuditEvent, DataSource, DatasetLoad, ExportRecord, InventorySnapshot, KpiSnapshot, RejectedRow, SalesRecord, SystemFlag, User

def reset_demo(db: Session):
    for model in [AnomalyEvidence,RejectedRow,SalesRecord,KpiSnapshot,DatasetLoad,ExportRecord,AuditEvent,SystemFlag,Anomaly,InventorySnapshot,DataSource,User]:
        db.execute(delete(model))
    db.flush()
    seed(db, force=True)

def seed(db: Session, force: bool = False):
    if not force and db.get(User,"u1"):
        return
    db.add_all([User(id="u1",name="Marina Alves",role="ADMIN"),User(id="u2",name="Rafael Tanaka",role="ANALISTA"),User(id="u3",name="Beatriz Nogueira",role="GESTOR"),User(id="u4",name="Otávio Prado",role="AUDITOR")])
    db.add_all([
        DataSource(id="sales",name="sales_july.csv",kind="CSV",row_count=8420,invalid_count=7),
        DataSource(id="stock",name="Estoque Mock",kind="CONNECTOR",row_count=1260),
        DataSource(id="customers",name="Clientes Mock",kind="CONNECTOR",row_count=2334),
        DataSource(id="returns",name="Devoluções Mock",kind="CONNECTOR",row_count=318,invalid_count=2),
        DataSource(id="tickets",name="Chamados Mock",kind="CONNECTOR",row_count=640),
        DataSource(id="calendar",name="Calendário Mock",kind="CONNECTOR",row_count=365),
    ])
    load=DatasetLoad(id="LOAD-1000",source_id="sales",file_name="sales_july.csv",status="Concluída",rows_read=8420,rows_accepted=8413,rows_rejected=7,actor_name="Pipeline")
    db.add(load)
    metrics=[("Receita líquida","R$ 1,84 mi",1840000,"+8,4%","good"),("Pedidos","12.480",12480,"+5,1%","good"),("Ticket médio","R$ 147,44",147.44,"+3,2%","good"),("Ruptura de estoque","7,8%",7.8,"+2,1 pp","warn"),("Taxa de devolução","4,6%",4.6,"+0,8 pp","warn"),("Chamados / 1k pedidos","18,2",18.2,"-1,4","good")]
    db.add_all([KpiSnapshot(load_id=load.id,metric=m,display_value=d,numeric_value=n,change_label=c,kind=k,active=True) for m,d,n,c,k in metrics])
    db.add_all([InventorySnapshot(sku="A-184",region="Sul",on_hand=51,daily_demand=30),InventorySnapshot(sku="A-184",region="Sudeste",on_hand=240,daily_demand=28)])
    db.add_all([SalesRecord(load_id=load.id,date="2026-07-12",order_id=f"ORD-{i:03d}",sku="A-184",region="Sul",quantity=4 if i<24 else 3,unit_price=149.9,returned=False,support_tickets=1 if i<14 else 0) for i in range(30)])
    anomalies=[
        Anomaly(id="AN-104",metric="Ruptura de estoque",scope="Sul / SKU A-184",severity="Alta",score=3.4,delta="+18,2%",status="Aberta"),
        Anomaly(id="AN-103",metric="Devoluções",scope="Categoria Eletrônicos",severity="Média",score=2.6,delta="+7,9%",status="Investigando"),
        Anomaly(id="AN-101",metric="Receita líquida",scope="Canal Marketplace",severity="Baixa",score=2.1,delta="-5,4%",status="Resolvida",resolution_note="Sazonalidade de marketplace confirmada via evidências; sem ação corretiva necessária."),
    ]
    db.add_all(anomalies); db.flush()
    anomalies[0].evidence=[AnomalyEvidence(label="Ruptura SKU A-184",value="26,1%",source="inventory_risk_view"),AnomalyEvidence(label="Velocidade de venda",value="+31,4%",source="sales_velocity_view"),AnomalyEvidence(label="Cobertura estimada",value="1,7 dias",source="inventory_days_cover"),AnomalyEvidence(label="Chamados relacionados",value="14",source="support_ticket_rollup")]
    db.add_all([SystemFlag(key="pipeline_fail",enabled=False),SystemFlag(key="unsafe_agent",enabled=False)])
    db.add_all([
        AuditEvent(actor="Pipeline",role="SISTEMA",action="LOAD_COMPLETED",entity_type="SOURCE",entity_id="sales_july.csv",details="8.420 linhas lidas"),
        AuditEvent(actor="Validator",role="SISTEMA",action="ROWS_REJECTED",entity_type="SOURCE",entity_id="sales_july.csv",details="7 linhas isoladas"),
        AuditEvent(actor="Anomaly Engine",role="SISTEMA",action="ANOMALY_CREATED",entity_type="ANOMALY",entity_id="AN-104",details="z-score 3.4"),
        AuditEvent(actor="Agent Tool",role="SISTEMA",action="TOOL_CALLED",entity_type="AGENT",entity_id="get_inventory_risk",details="scope=Sul; sku=A-184"),
        AuditEvent(actor="Agent",role="SISTEMA",action="ANSWER_GENERATED",entity_type="AGENT",entity_id="chat-771",details="4 evidências citadas"),
    ])
    db.commit()
