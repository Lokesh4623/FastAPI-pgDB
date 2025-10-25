from pydantic import BaseModel
from typing import List
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class AccountCreate(BaseModel):
    account_number: str

class AccountOut(BaseModel):
    id: int
    account_number: str
    balance: float

    class Config:
        orm_mode = True

class TransactionCreate(BaseModel):
    type: str  # deposit / withdraw
    amount: float

class TransactionOut(BaseModel):
    id: int
    type: str
    amount: float
    timestamp: datetime

    class Config:
        orm_mode = True
