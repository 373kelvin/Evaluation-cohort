"""Fintech Platform API — rich demo target for B1/B2 repo analysis."""
from fastapi import FastAPI, HTTPException

from app.models import TransactionCreate, UserCreate
from app.services import AuthService, PaymentService, ReportingService

app = FastAPI(title="Fintech Platform", version="2.0.0")
auth = AuthService()
payments = PaymentService()
reports = ReportingService()


@app.get("/health")
def health():
    return {"status": "ok", "service": "fintech-platform"}


@app.post("/auth/register")
def register(user: UserCreate):
    return auth.register(user)


@app.post("/auth/login")
def login(credentials: UserCreate):
    return {"token": "demo-jwt", "email": credentials.email}


@app.get("/accounts/{account_id}")
def get_account(account_id: int):
    return {"id": account_id, "currency": "INR", "balance": 125000.0}


@app.get("/accounts/{account_id}/transactions")
def list_transactions(account_id: int):
    return payments.transactions.list_for_account(account_id)


@app.post("/payments/transfer")
def transfer(payload: TransactionCreate):
    return payments.process(payload)


@app.get("/reports/daily")
def daily_report():
    return reports.daily_summary()


@app.get("/admin/fraud-alerts")
def fraud_alerts():
    return [{"id": 1, "risk_score": 92, "reasons": ["large amount", "unusual hour"]}]


@app.get("/admin/users")
def admin_users():
    return [{"id": 1, "email": "demo@bank.in", "kyc_status": "verified"}]
