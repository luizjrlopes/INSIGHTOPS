from __future__ import annotations
from dataclasses import dataclass

ALLOWED_TOOLS={"get_inventory_risk","get_sales_velocity","get_support_signal","get_anomaly","compare_kpi"}

@dataclass
class ToolRequest:
    name: str
    arguments: dict

class UnsafeToolError(ValueError):
    pass

class LocalAgentProvider:
    def plan(self, question: str, *, unsafe: bool=False) -> list[ToolRequest]:
        if unsafe: return [ToolRequest("execute_sql",{"sql":"select * from sales_records"})]
        q=question.lower(); requests=[]
        if "ruptura" in q or "estoque" in q: requests.append(ToolRequest("get_inventory_risk",{"region":"Sul","sku":"A-184"}))
        if "velocidade" in q or "venda" in q: requests.append(ToolRequest("get_sales_velocity",{"region":"Sul","sku":"A-184","window_days":7}))
        if "chamado" in q or "suporte" in q: requests.append(ToolRequest("get_support_signal",{"region":"Sul","sku":"A-184"}))
        if not requests: requests.append(ToolRequest("get_anomaly",{"anomaly_id":"AN-104"}))
        return requests

    def answer(self, question: str, evidence: list[dict]) -> str:
        if not evidence: return "Não há evidência suficiente para responder com segurança."
        inv=next((x for x in evidence if "rupture_risk_pct" in x),None)
        vel=next((x for x in evidence if "change_pct" in x),None)
        sup=next((x for x in evidence if "support_tickets" in x),None)
        parts=[]
        if inv: parts.append(f"a ruptura estimada está em {inv['rupture_risk_pct']:.1f}% e a cobertura em {inv['days_cover']} dias")
        if vel: parts.append(f"a velocidade de venda está {vel['change_pct']:+.1f}% acima da referência")
        if sup: parts.append(f"há {sup['support_tickets']} chamados relacionados")
        return "Os dados disponíveis mostram que " + "; ".join(parts) + ". Isso demonstra correlação operacional, não uma causa confirmada."
