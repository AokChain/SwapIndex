from sqlmodel import Field, Relationship
from typing import Optional, List
from pydantic import condecimal
from .base import BaseTable

class Transaction(BaseTable, table=True):
    receive_amount: Optional[
        condecimal(max_digits=20, decimal_places=8)
    ] = Field(default=0)

    send_amount: Optional[
        condecimal(max_digits=20, decimal_places=8)
    ] = Field(default=0)

    outputs: List["Output"] = Relationship(back_populates="transaction")
    receive_token: Optional[str] = Field(default=None)
    send_token: Optional[str] = Field(default=None)
    txid: Optional[str] = Field(default=None)
    closed: bool = Field(default=True)
    raw_tx: str
