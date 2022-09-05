from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

def init_scheduler():
    scheduler = AsyncIOScheduler()

    from service.sync import sync_transactions
    from service.sync import sync_outputs
    from service.sync import sync_indexes

    # scheduler.add_job(sync_transactions, 'interval', minutes=5)
    # scheduler.add_job(sync_outputs, 'interval', minutes=5)
    scheduler.add_job(sync_indexes, 'interval', seconds=10)
    scheduler.start()

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    init_scheduler()