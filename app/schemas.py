from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    login: str = Field(min_length=4, max_length=20)
    password: str = Field(min_length=8, max_length=20)

class TopupSchema(BaseModel):
    amount: int = Field(gt=0)