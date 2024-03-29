from sqlmodel import Field, Relationship
from pydantic import condecimal
from typing import Optional
from .base import BaseTable

class Output(BaseTable, table=True):
    amount: Optional[condecimal(max_digits=20, decimal_places=8)] = Field(default=0)
    spent: Optional[bool] = Field(default=False)
    currency: str
    txid: str

    transaction_id: Optional[int] = Field(default=None, foreign_key="transaction.id")
    transaction: Optional["Transaction"] = Relationship(back_populates="outputs")

