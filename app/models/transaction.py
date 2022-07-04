from sqlmodel import SQLModel, Field
from pydantic import condecimal
from typing import Optional

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    raw_tx: str
    send_token: Optional[str] = Field(default=None)
    send_amount: Optional[condecimal(max_digits=8, decimal_places=7)] = Field(default=0)
    receive_token: Optional[str] = Field(default=None)
    receive_amount: Optional[condecimal(max_digits=8, decimal_places=7)] = Field(default=0)
