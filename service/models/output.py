from sqlmodel import Field, Relationship
from pydantic import condecimal
from typing import Optional
from .base import BaseTable

class Output(BaseTable, table=True):
    txid: str
    amount: Optional[condecimal(max_digits=20, decimal_places=8)] = Field(default=0)
    currency: str
    spent: Optional[bool] = Field(default=False)

    transaction_id: int = Field(default=None, foreign_key="transaction.id")
    transaction: Optional["Transaction"] = Relationship(back_populates="outputs")

