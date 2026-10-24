from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from .core.orchestrator import broker
from .core.red_team import red_team
from .core.audit_ledger import ledger

app = FastAPI(
    title="SealedBid - Secure Adversarial AI Safety Testing API",
    description="Multi-tenant zero-trust infrastructure for adversarial AI evaluation",
    version="1.0.0"
)

# Enable CORS for frontend dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EvaluationRequest(BaseModel):
    attack_type: Optional[str] = None
    custom_prompt: Optional[str] = None

@app.get("/api/health")
def health_check():
    return {
        "status": "OPERATIONAL",
        "service": "SealedBid Secure Evaluation Mesh",
        "isolation_tier": "SANDBOX_SECCOMP_L3",
        "multi_tenant_boundaries": "ENFORCED"
    }

@app.get("/api/metrics")
def get_metrics():
    return broker.get_system_metrics()

@app.get("/api/benchmarks")
def get_benchmarks():
    return red_team.get_benchmarks()

@app.post("/api/evaluate")
def run_evaluation(payload: EvaluationRequest):
    try:
        result = broker.run_adversarial_test(
            attack_type=payload.attack_type,
            custom_prompt=payload.custom_prompt
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/audit/ledger")
def get_audit_ledger(limit: int = 50):
    return {
        "integrity": ledger.verify_integrity(),
        "entries": ledger.get_entries(limit=limit)
    }

@app.post("/api/audit/verify")
def verify_audit_ledger():
    return ledger.verify_integrity()
