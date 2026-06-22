from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class TransactionType(str, Enum):
    credit = "credit"
    debit = "debit"


class TransactionCreate(BaseModel):
    amount: float = Field(..., description="Transaction amount, must be > 0")
    type: TransactionType
    description: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("amount must be greater than 0")
        return v


class Transaction(TransactionCreate):
    id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Balance(BaseModel):
    balance: float
    transaction_count: int
