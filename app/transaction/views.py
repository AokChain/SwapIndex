from ..models import engine, Transaction
from sqlmodel import Session, select
from pydantic import BaseModel
from fastapi import APIRouter
from typing import Optional

router = APIRouter(prefix="/transaction")

class TxPostBody(BaseModel):
    raw_tx: str

@router.post("/add")
async def add(txbody: TxPostBody):
    result = {"data": {}, "error": None}
    with Session(engine) as session:
        statement = select(Transaction).where(Transaction.raw_tx == txbody.raw_tx)
        results = session.exec(statement)

        if not results.first():
            new_transaction = Transaction(
                raw_tx=txbody.raw_tx
            )

            session.add(new_transaction)
            session.commit()

            result["data"] = {
                "raw_tx": txbody.raw_tx
            }

            return result

        result["error"] = "Transaction already exists"

        return result

