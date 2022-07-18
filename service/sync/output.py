from sqlmodel.ext.asyncio.session import AsyncSession
from ..models import Output, Transaction
from ..clients import Bitcoin
from sqlmodel import select
from .. import utils as uuid
from . import utils as log
from .. import db
import config

async def sync_outputs():
    log.log_message("Syncing outputs")
    client = Bitcoin(config.endpoint, rid=config.rid)

    async with AsyncSession(db.async_engine) as session:
        statement = select(Transaction).where(Transaction.closed)
        results = await session.exec(statement)

        for transaction in results:

            data = await client.make_request("decoderawtransaction", [transaction.raw_tx])
            data = data["result"]

            statement = select(Output).where(Output.txid == data["txid"])
            results = await session.exec(statement)

            if not results.first():
                if "token" in data["vout"][0]["scriptPubKey"].keys():
                    output = Output(
                        reference=uuid.get_uuid(),
                        txid=data["txid"],
                        amount=data["vout"][0]["scriptPubKey"]["token"]["amount"],
                        currency=data["vout"][0]["scriptPubKey"]["token"]["name"],
                        transaction_id=transaction.id,
                        transaction=transaction
                    )

                    output_vout = data["vout"][0]["n"]

                    data = await client.make_request("gettxout", [data["txid"], output_vout])

                    if not data["result"]:
                        output.spent = False

                    session.add(output)
                    await session.commit()
                else:
                    output = Output(
                        reference=uuid.get_uuid(),
                        txid=data["txid"],
                        amount=data["vout"][0]["value"],
                        currency="AOK",
                        transaction_id=transaction.id,
                        transaction=transaction
                    )

                    output_vout = data["vout"][0]["n"]

                    data = await client.make_request("gettxout", [data["txid"], output_vout])

                    if not data["result"]:
                        output.spent = False

                    session.add(output)
                    await session.commit()
