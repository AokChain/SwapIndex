import math

from pydantic import BaseModel, validator
from ..models import engine, Transaction
from sqlmodel import Session, select
from fastapi import APIRouter
from ..clients import Bitcoin
import config

router = APIRouter(prefix="/transaction")

class TxPostBody(BaseModel):
    raw_tx: str

@router.post("/add")
async def add(txbody: TxPostBody):
    result = {"data": {}, "error": None}
    client = Bitcoin(config.endpoint, rid=config.rid)
    with Session(engine) as session:
        statement = select(Transaction).where(Transaction.raw_tx == txbody.raw_tx)
        results = session.exec(statement)

        if not results.first():

            transaction = Transaction(
                raw_tx=txbody.raw_tx
            )

            data = client.make_request("decoderawtransaction", [transaction.raw_tx])["result"]

            if "token" in data["vout"][0]["scriptPubKey"].keys():
                transaction.receive_token = data["vout"][0]["scriptPubKey"]["token"]["name"]
                transaction.receive_amount = data["vout"][0]["scriptPubKey"]["token"]["amount"]
            else:
                transaction.receive_token = "AOK"
                transaction.receive_amount = data["vout"][0]["value"]

            input_txid = data["vin"][0]["txid"]
            input_vout = data["vin"][0]["vout"]

            data = client.make_request("getrawtransaction", [input_txid, True])["result"]

            for vout in data["vout"]:
                if vout["n"] == input_vout:
                    if "token" in vout["scriptPubKey"].keys():
                        transaction.send_token = vout["scriptPubKey"]["token"]["name"]
                        transaction.send_amount = vout["scriptPubKey"]["token"]["amount"]
                        break
                    else:
                        transaction.send_token = "AOK"
                        transaction.send_amount = vout["value"]
                        break

            session.add(transaction)
            session.commit()

            result["data"] = {
                "raw_tx": transaction.raw_tx,
                "send_token": transaction.send_token,
                "send_amount": float(transaction.send_amount),
                "receive_token": transaction.receive_token,
                "receive_amount": float(transaction.receive_amount)
            }

            return result

        result["error"] = "Transaction already exists"

        return result

class ListBody(BaseModel):
    page: int = 1

    @validator('page')
    def check_page(cls, v):
        if v < 1:
            raise ValueError("Page must be greater than 1")
        return v

@router.post("/list")
async def list_txs(listbody: ListBody):
    result = {"data": {}, "error": None}
    result["data"]["list"] = []
    size = 20

    with Session(engine) as session:
        statement = select(Transaction).where(Transaction.closed != True)
        results = session.exec(statement)

        total = len(results.fetchall())
        pages = math.ceil(total / size)
        current = listbody.page

        result["data"]["pagination"] = {
            "current": current,
            "total": total,
            "pages": pages
        }

        offset = listbody.page if listbody.page > 1 else 0

        statement = select(Transaction).where(Transaction.closed != True).offset(offset).limit(size)
        results = session.exec(statement)

        for transaction in results:
            result["data"]["list"].append({
                "raw_tx": transaction.raw_tx,
                "send_token": transaction.send_token,
                "send_amount": transaction.send_amount,
                "receive_token": transaction.receive_token,
                "receive_amount": transaction.receive_amount,
                "closed": transaction.closed
            })

        return result






