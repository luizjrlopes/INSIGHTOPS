from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import agent, anomalies, audit, auth, dashboard, data, demo, quality, reports, users
app=FastAPI(title="InsightOps API",version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_list,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
for router in [auth.router,dashboard.router,data.router,quality.router,anomalies.router,agent.router,reports.router,audit.router,users.router,demo.router]: app.include_router(router)
@app.get("/health")
def health(): return {"status":"ok"}
