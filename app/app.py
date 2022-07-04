from .models import SQLModel, engine
from .transaction import transaction
from fastapi import FastAPI

app = FastAPI()

app.include_router(transaction)

SQLModel.metadata.create_all(engine)
