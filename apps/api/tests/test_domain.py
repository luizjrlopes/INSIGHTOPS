import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.domain import anomaly_severity, can, can_transition, parse_bool, validate_sales_row, z_score
from app.agent_policy import ALLOWED_TOOLS, LocalAgentProvider

class DomainTests(unittest.TestCase):
    def test_rbac(self):
        self.assertTrue(can("ANALISTA","data:import")); self.assertFalse(can("AUDITOR","data:import"))
    def test_anomaly_transition(self):
        self.assertTrue(can_transition("Aberta","Investigando")); self.assertFalse(can_transition("Aberta","Resolvida"))
    def test_bool_parser(self):
        self.assertIs(parse_bool("maybe"),None); self.assertTrue(parse_bool("yes")); self.assertFalse(parse_bool("0"))
    def test_valid_row(self):
        row={"date":"2026-08-01","order_id":"O1","sku":"A-1","region":"Sul","quantity":2,"unit_price":10,"returned":"false","support_tickets":0}
        self.assertEqual(validate_sales_row(row),[])
    def test_invalid_row(self):
        row={"date":"bad","order_id":"","sku":"","region":"","quantity":0,"unit_price":-1,"returned":"maybe","support_tickets":-1}
        self.assertGreaterEqual(len(validate_sales_row(row)),8)
    def test_z_score_and_severity(self):
        score=z_score(20,[9,10,10,11,10]); self.assertGreater(score,3); self.assertEqual(anomaly_severity(score),"Alta")
    def test_provider_uses_safe_tools(self):
        reqs=LocalAgentProvider().plan("Compare ruptura, velocidade de venda e chamados")
        self.assertTrue(reqs); self.assertTrue(all(r.name in ALLOWED_TOOLS for r in reqs))
    def test_unsafe_plan_requests_unregistered_tool(self):
        req=LocalAgentProvider().plan("x",unsafe=True)[0]
        self.assertEqual(req.name,"execute_sql"); self.assertNotIn(req.name,ALLOWED_TOOLS)

if __name__ == "__main__": unittest.main()
