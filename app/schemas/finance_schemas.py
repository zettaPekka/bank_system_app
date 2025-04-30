from pydantic import BaseModel, Field

class TopupSchema(BaseModel):
    amount: int = Field(gt=0)

class SendMoneySchema(BaseModel):
    receiver_login: str = Field(min_length=4, max_length=20)
    amount: int = Field(gt=0)

class DepositSchema(BaseModel):
    amount: int = Field(gt=0)
    period: int = Field(gt=0, le=36)