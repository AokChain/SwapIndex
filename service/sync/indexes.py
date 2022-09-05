from sqlmodel.ext.asyncio.session import AsyncSession
from ..models import Currency, Index, Transaction
from ..clients import Bitcoin
from sqlmodel import select
from .. import utils
from .. import db
import config

async def sync_indexes():
    utils.log_message("Syncing indexes")
    client = Bitcoin(config.endpoint, rid=config.rid)

    async with AsyncSession(db.async_engine) as session:
        statement = select(Transaction).where(Transaction.indexed != True)
        results = await session.exec(statement)

        for transaction in results:
            transaction_id = transaction.id
            data = await client.make_request("decoderawtransaction", [transaction.raw_tx])

            if data['error']:
                return

            data = data['result']

            if "token" in data["vout"][0]["scriptPubKey"].keys():
                currency_name = data["vout"][0]["scriptPubKey"]["token"]["name"]
                statement_currency = select(Currency).where(Currency.name == currency_name)
                results = await session.exec(statement_currency)

                if not (currency := results.one_or_none()):
                    currency = Currency(
                        reference=utils.get_uuid(),
                        name=currency_name
                    )

                    session.add(currency)
                    await session.commit()
                    await session.refresh(currency)

                statement_index = select(Index).where(Index.transaction_id == transaction_id)
                results = await session.exec(statement_index)

                if not (index := results.one_or_none()):
                    index = Index(
                        reference=utils.get_uuid(),
                        currency_out_id=currency.id,
                        currency_out=currency,
                        transaction_id=transaction_id,
                        transaction=transaction
                    )

                    session.add(index)
                    await session.commit()
                else:
                    index.currency_out_id = currency.id
                    index.currency_out = currency
            else:
                statement_currency = select(Currency).where(Currency.name == "AOK")
                results = await session.exec(statement_currency)

                if not (currency := results.one_or_none()):
                    currency = Currency(
                        reference=utils.get_uuid(),
                        name="AOK"
                    )
                    session.add(currency)
                    await session.commit()
                    await session.refresh(currency)

                statement_index = select(Index).where(Index.transaction_id == transaction_id)
                results = await session.exec(statement_index)

                if not (index := results.one_or_none()):
                    index = Index(
                        reference=utils.get_uuid(),
                        currency_out_id=currency.id,
                        currency_out=currency,
                        transaction_id=transaction_id,
                        transaction=transaction
                    )

                    session.add(index)
                    await session.commit()
                else:
                    index.currency_out_id = currency.id
                    index.currency_out = currency

            for vin in data["vin"]:
                input_txid = vin["txid"]
                input_vout = vin["vout"]

                data = await client.make_request("getrawtransaction", [input_txid, True])

                if data['error']:
                    return

                data = data["result"]

                vout = data["vout"][input_vout]

                if "token" in vout["scriptPubKey"].keys():
                    currency_name = vout["scriptPubKey"]["token"]["name"]
                    statement_currency = select(Currency).where(Currency.name == currency_name)
                    results = await session.exec(statement_currency)

                    if not (currency := results.one_or_none()):
                        currency = Currency(
                            reference=utils.get_uuid(),
                            name=currency_name
                        )

                        session.add(currency)
                        await session.commit()
                        await session.refresh(currency)

                    statement_index = select(Index).where(Index.transaction_id == transaction_id)
                    results = await session.exec(statement_index)

                    if not (index := results.one_or_none()):
                        index = Index(
                            reference=utils.get_uuid(),
                            currency_in_id=currency.id,
                            currency_in=currency,
                            transaction_id=transaction_id,
                            transaction=transaction
                        )

                        session.add(index)
                        await session.commit()
                    else:
                        index.currency_in_id = currency.id
                        index.currency_in = currency

                        session.add(index)
                        await session.commit()
                else:
                    statement_currency = select(Currency).where(Currency.name == "AOK")
                    results = await session.exec(statement_currency)

                    if not (currency := results.one_or_none()):
                        currency = Currency(
                            reference=utils.get_uuid(),
                            name="AOK"
                        )
                        session.add(currency)
                        await session.commit()
                        await session.refresh(currency)

                    statement_index = select(Index).where(Index.transaction_id == transaction_id)
                    results = await session.exec(statement_index)

                    if not (index := results.one_or_none()):
                        index = Index(
                            reference=utils.get_uuid(),
                            currency_in_id=currency.id,
                            currency_in=currency,
                            transaction_id=transaction_id,
                            transaction=transaction
                        )

                        session.add(index)
                        await session.commit()
                    else:
                        index.currency_in_id = currency.id
                        index.currency_in = currency

                        session.add(index)
                        await session.commit()

            transaction.indexed = True
            session.add(transaction)
            await session.commit()
