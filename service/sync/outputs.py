from sqlmodel.ext.asyncio.session import AsyncSession
from ..models import Output, Settings
from ..clients import Bitcoin
from sqlmodel import select
from .. import utils
from .. import db
import config

async def sync_outputs():
    utils.log_message("Syncing outputs")
    client = Bitcoin(config.endpoint, rid=config.rid)

    async with AsyncSession(db.async_engine) as session:
        statement_settings = select(Settings)
        results = await session.exec(statement_settings)

        if not (settings := results.one_or_none()):
            return

        current_height = await client.make_request("getblockcount")

        if current_height["error"]:
            return

        current_height = current_height["result"]

        for height in range(settings.latest_block_height + 1, current_height + 1):
            data = await client.make_request("getblockhash", [height])

            if data["error"]:
                return

            block_hash = data["result"]
            data = await client.make_request("getblock", [block_hash])

            if data["error"]:
                return

            for tx in data["tx"]:
                tx_data = await client.make_request("getrawtransaction", [tx, True])

                if tx_data["error"]:
                    return

                for vin in tx_data["vin"]:
                    if "coinbase" in vin:
                        continue

                    statement_output = select(Output).where(Output.txid == vin["txid"])
                    results_output = await session.exec(statement_output)

                    if (output := results_output.first()):
                        output.spent = True
                        session.add(output)

                for vout in tx_data["vout"]:
                    if vout["scriptPubKey"]["type"] in ["nonstandard", "nulldata"]:
                        continue

                    statement_output = select(Output).where(Output.txid == vout["txid"])
                    results_output = await session.exec(statement_output)

                    if (output := results_output.first()):
                        output.spent = True
                        session.add(output)

        block_hash = await client.make_request("getblockhash", [current_height])

        if not block_hash["error"]:
            block_hash = block_hash["result"]

        settings.latest_block_height = current_height
        settings.latest_block_hash = block_hash

        session.add(settings)
        await session.commit()
