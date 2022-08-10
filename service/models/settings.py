from sqlmodel import Field, SQLModel
from typing import Union

class Settings(SQLModel, table=True):
    id: Union[int, None] = Field(default=None, primary_key=True)
    latest_block_height: int = Field(default=0)
    latest_block_hash: str = Field(default="")
