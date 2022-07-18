from sqlmodel import Field, Relationship
from typing import Optional, List
from pydantic import condecimal
from .base import BaseTable

class Transaction(BaseTable, table=True):
    raw_tx: str
    send_token: Optional[str] = Field(default=None)
    send_amount: Optional[condecimal(max_digits=20, decimal_places=8)] = Field(default=0)
    receive_token: Optional[str] = Field(default=None)
    receive_amount: Optional[condecimal(max_digits=20, decimal_places=8)] = Field(default=0)
    closed: bool = Field(default=True)
    outputs: List["Output"] = Relationship(back_populates="transaction")
