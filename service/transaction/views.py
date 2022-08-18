from sqlmodel.ext.asyncio.session import AsyncSession
from ..models import Transaction, Output
from fastapi import APIRouter, Depends
from .args import TxPostBody, ListBody
from ..clients import Bitcoin
from sqlmodel import select
from .. import utils
from .. import db
import config
import math

router = APIRouter(prefix="/transaction")

@router.post("/add")
async def add(txbody: TxPostBody, session: AsyncSession = Depends(db.get_async_session)):
    result = {"data": {}, "error": None}
    client = Bitcoin(config.endpoint, rid=config.rid)

    statement = select(Transaction).where(Transaction.raw_tx == txbody.raw_tx)
    results = await session.exec(statement)

    if results.first():
        result["error"] = "Transaction already exists"
        return result

    transaction = Transaction(
        reference=utils.get_uuid(),
        raw_tx=txbody.raw_tx,
    )

    data = await client.make_request("decoderawtransaction", [transaction.raw_tx])

    if data["error"]:
        result["error"] = "Error with node. Try again later"
        return result

    data = data["result"]

    transaction.txid = data["txid"]

    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)

    if "token" in data["vout"][0]["scriptPubKey"].keys():
        transaction.receive_token = data["vout"][0]["scriptPubKey"]["token"]["name"]
        transaction.receive_amount = data["vout"][0]["scriptPubKey"]["token"]["amount"]
    else:
        transaction.receive_token = "AOK"
        transaction.receive_amount = data["vout"][0]["value"]

    for vin in data["vin"]:
        input_txid = vin["txid"]
        input_vout = vin["vout"]

        data = await client.make_request("getrawtransaction", [input_txid, True])

        if data["error"]:
            result["error"] = "Error with node. Try again later"
            return result

        data = data["result"]
        vout = data["vout"][input_vout]

        if "token" in vout["scriptPubKey"].keys():
            transaction.send_token = vout["scriptPubKey"]["token"]["name"]
            transaction.send_amount = vout["scriptPubKey"]["token"]["amount"]

            output = Output(
                reference=utils.get_uuid(),
                txid=input_txid,
                amount=vout["scriptPubKey"]["token"]["amount"],
                currency=vout["scriptPubKey"]["token"]["name"],
                transaction_id=transaction.id,
                transaction=transaction
            )

            session.add(output)
            break
        else:
            transaction.send_token = "AOK"
            transaction.send_amount = vout["value"]

            output = Output(
                reference=utils.get_uuid(),
                txid=input_txid,
                amount=vout["value"],
                currency="AOK",
                transaction_id=transaction.id,
                transaction=transaction
            )

            session.add(output)
            break

    result["data"] = {
        "raw_tx": transaction.raw_tx,
        "send_token": transaction.send_token,
        "send_amount": float(transaction.send_amount),
        "receive_token": transaction.receive_token,
        "receive_amount": float(transaction.receive_amount)
    }

    session.add(transaction)
    await session.commit()

    return result

@router.post("/list")
async def list_txs(listbody: ListBody, session: AsyncSession = Depends(db.get_async_session)):
    result = {"data": {}, "error": None}
    result["data"]["list"] = []
    size = 20

    statement = select(Transaction).where(Transaction.closed != True)
    results = await session.exec(statement)

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
    results = await session.exec(statement)

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






