from pydantic import BaseModel, Field


class Account(BaseModel):
    id: str
    name: str
    type: str
    balance: float
    currency: str = "CAD"


class PaymentRequest(BaseModel):
    from_account_id: str = Field(min_length=1)
    to_payee: str = Field(min_length=1)
    amount: float = Field(gt=0)
    currency: str = "CAD"


class PaymentResponse(BaseModel):
    payment_id: str
    status: str
    message: str

