"""Business services."""
from app.models import TransactionCreate, UserCreate
from app.repositories import AccountRepository, FraudRepository, TransactionRepository, UserRepository


class AuthService:
    def __init__(self):
        self.users = UserRepository()

    def register(self, payload: UserCreate) -> dict:
        return {"id": self.users.insert(payload.email, "hashed")}


class PaymentService:
    def __init__(self):
        self.accounts = AccountRepository()
        self.transactions = TransactionRepository()
        self.fraud = FraudRepository()

    def process(self, payload: TransactionCreate) -> dict:
        bal = self.accounts.get_balance(payload.account_id)
        if payload.txn_type == "debit" and bal < payload.amount:
            return {"status": "failed", "reason": "insufficient funds"}
        txn_id = self.transactions.insert(payload.account_id, payload.amount, payload.txn_type)
        score = 90 if payload.amount > 10000 else 10
        if score > 70:
            self.fraud.insert_alert(txn_id, score, ["large amount"])
        return {"status": "completed", "transaction_id": txn_id, "risk_score": score}


class ReportingService:
    def daily_summary(self) -> dict:
        return {"credits": 0, "debits": 0, "alerts": 0}
