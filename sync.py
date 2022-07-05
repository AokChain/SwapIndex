from apscheduler.schedulers.blocking import BlockingScheduler
from app.sync import sync_transactions

if __name__ == "__main__":
    scheduler = BlockingScheduler()

    scheduler.add_job(sync_transactions, "interval", seconds=10)

    scheduler.start()
