from sqlmodel import Relationship
from typing import Optional, List
from .base import BaseTable

class Currency(BaseTable, table=True):
    name: Optional[str]
    indexes_in: List["Index"] = Relationship(back_populates="currency_in")
    indexes_out: List["Index"] = Relationship(back_populates="currency_out")
