from sqlmodel import Field, Relationship
from typing import Optional
from .base import BaseTable

class Index(BaseTable, table=True):
    currency_in_id: Optional[int] = Field(default=None, foreign_key="currency.id")
    currency_in: Optional["Currency"] = Relationship(back_populates="indexes_in")

    currency_out_id: Optional[int] = Field(default=None, foreign_key="currency.id")
    currency_out: Optional["Currency"] = Relationship(back_populates="indexes_out")

    transaction_id: Optional[int] = Field(default=None, foreign_key="transaction.id")
    transaction: Optional["Transaction"] = Relationship(back_populates="indexes")

