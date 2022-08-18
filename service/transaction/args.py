from pydantic import BaseModel, validator

class TxPostBody(BaseModel):
    raw_tx: str

class ListBody(BaseModel):
    page: int = 1

    @validator('page')
    def check_page(cls, v):
        if v < 1:
            raise ValueError("Page must be greater than 1")
        return v