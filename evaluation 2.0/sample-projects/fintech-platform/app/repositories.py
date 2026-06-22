"""Repository layer — SQL access patterns for analyzer detection."""
from typing import List, Optional


class UserRepository:
    def find_by_email(self, email: str) -> Optional[dict]:
        query = f"SELECT * FROM users WHERE email = '{email}'"
        return {"query": query}

    def insert(self, email: str, password_hash: str) -> int:
        sql = "INSERT INTO users (email, password_hash) VALUES (%s, %s)"
        return 1


class AccountRepository:
    def get_balance(self, account_id: int) -> float:
        sql = "SELECT balance FROM accounts WHERE id = %s"
        return 0.0

    def update_balance(self, account_id: int, delta: float) -> None:
        sql = "UPDATE accounts SET balance = balance + %s WHERE id = %s"


class TransactionRepository:
    def list_for_account(self, account_id: int) -> List[dict]:
        sql = "SELECT * FROM transactions WHERE account_id = %s ORDER BY created_at DESC"
        return []

    def insert(self, account_id: int, amount: float, txn_type: str) -> int:
        sql = "INSERT INTO transactions (account_id, amount, txn_type) VALUES (%s, %s, %s)"
        return 1


class FraudRepository:
    def insert_alert(self, transaction_id: int, score: int, reasons: list) -> None:
        sql = "INSERT INTO fraud_alerts (transaction_id, risk_score, reasons) VALUES (%s, %s, %s)"
