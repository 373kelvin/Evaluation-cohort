"""Domain models for the fintech platform demo."""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class KycStatus(str, Enum):
    pending = "pending"
    verified = "verified"
    rejected = "rejected"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class User(BaseModel):
    id: int
    email: EmailStr
    kyc_status: KycStatus = KycStatus.pending
    created_at: datetime


class Account(BaseModel):
    id: int
    user_id: int
    currency: str = "INR"
    balance: float = 0.0


class TransactionType(str, Enum):
    credit = "credit"
    debit = "debit"
    transfer = "transfer"


class TransactionCreate(BaseModel):
    account_id: int
    amount: float = Field(gt=0)
    txn_type: TransactionType
    merchant_ref: Optional[str] = None


class FraudAlert(BaseModel):
    id: int
    transaction_id: int
    risk_score: int = Field(ge=0, le=100)
    reasons: list[str] = []
