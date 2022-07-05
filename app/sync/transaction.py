from ..models import engine, Transaction
from sqlmodel import Session, select
from ..clients import Bitcoin
from . import utils
import config

def sync_transactions():
    utils.log_message("Syncing transactions")
    client = Bitcoin(config.endpoint, rid=config.rid)

    with Session(engine) as session:
        statement = select(Transaction).where(Transaction.closed)
        results = session.exec(statement)

        for transaction in results:
            data = client.make_request("decoderawtransaction", [transaction.raw_tx])['result']

            input_txid = data["vin"][0]["txid"]
            input_vout = data["vin"][0]["vout"]

            data = client.make_request("gettxout", [input_txid, input_vout])

            if data["result"]:
                transaction.closed = False
                session.add(transaction)
                session.commit()

