from fastapi import FastAPI
from .db import init_db

def create_app() -> FastAPI:

    app = FastAPI()

    from .transaction import transaction

    app.include_router(transaction)

    @app.on_event("startup")
    async def on_startup():
        await init_db()

    return app