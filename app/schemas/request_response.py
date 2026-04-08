from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class FraudRequest(BaseModel):
    amount: float
    age: int
    hour: int
    category: str
    device_fingerprint: str
    location: str
    description: str

class FraudResponse(BaseModel):
    user_id: int
    risk_score: float
    probability: float
    #transaction: dict
    #behavior: dict
    #image: dict
    is_fraud: bool
    status: str