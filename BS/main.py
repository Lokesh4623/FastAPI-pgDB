from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from models import User, BankAccount, Transaction
from schemas import UserCreate, UserLogin, AccountCreate, AccountOut, TransactionCreate, TransactionOut
from auth import create_access_token, verify_token
from passlib.context import CryptContext
from typing import List
import random

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bank Account API")

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------- AUTH --------------------
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_pw = pwd_context.hash(user.password)
    new_user = User(username=user.username, password=hashed_pw)
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

# -------------------- BANK ACCOUNT --------------------
@app.post("/accounts/", response_model=AccountOut)
def create_account(account: AccountCreate, db: Session = Depends(get_db), token: dict = Depends(verify_token)):
    username = token["sub"]
    user = db.query(User).filter(User.username == username).first()
    new_account = BankAccount(
        account_number=account.account_number,
        owner_id=user.id,
        balance=0.0
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account

@app.get("/accounts/", response_model=List[AccountOut])
def get_accounts(db: Session = Depends(get_db), token: dict = Depends(verify_token)):
    username = token["sub"]
    user = db.query(User).filter(User.username == username).first()
    return user.accounts

@app.get("/accounts/{account_id}", response_model=AccountOut)
def get_account(account_id: int, db: Session = Depends(get_db), token: dict = Depends(verify_token)):
    account = db.query(BankAccount).filter(BankAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

# -------------------- TRANSACTIONS --------------------
@app.post("/accounts/{account_id}/transaction", response_model=TransactionOut)
def make_transaction(account_id: int, transaction: TransactionCreate, db: Session = Depends(get_db), token: dict = Depends(verify_token)):
    account = db.query(BankAccount).filter(BankAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if transaction.type == "withdraw" and account.balance < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    if transaction.type == "deposit":
        account.balance += transaction.amount
    elif transaction.type == "withdraw":
        account.balance -= transaction.amount
    else:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    txn = Transaction(account_id=account.id, type=transaction.type, amount=transaction.amount)
    db.add(txn)
    db.commit()
    db.refresh(txn)
    db.refresh(account)
    return txn

@app.get("/accounts/{account_id}/transactions", response_model=List[TransactionOut])
def get_transactions(account_id: int, db: Session = Depends(get_db), token: dict = Depends(verify_token)):
    account = db.query(BankAccount).filter(BankAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account.transactions
