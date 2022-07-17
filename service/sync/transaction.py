from sqlmodel.ext.asyncio.session import AsyncSession
from ..models import Transaction
from ..clients import Bitcoin
from sqlmodel import select
from . import utils
from .. import db
import config

async def sync_transactions():
    utils.log_message("Syncing transactions")
    client = Bitcoin(config.endpoint, rid=config.rid)

    async with AsyncSession(db.async_engine) as session:
        statement = select(Transaction).where(Transaction.closed)
        results = await session.exec(statement)

        for transaction in results:
            data = client.make_request("sendrawtransaction", [transaction.raw_tx])

            if data["result"]:
                continue

            data = client.make_request("decoderawtransaction", [transaction.raw_tx])['result']

            input_txid = data["vin"][0]["txid"]
            input_vout = data["vin"][0]["vout"]

            data = client.make_request("gettxout", [input_txid, input_vout])

            if data["result"]:
                transaction.closed = False
                session.add(transaction)
                await session.commit()

