from fastapi import FastAPI,Depends,status, HTTPException
from database import Sessionlocal, engine
from pydantic import BaseModel,Field
from datetime import date
from sqlalchemy.orm import Session
from models import User
from models import Base,Transaction
from router.auth import router, db_dependency, get_current_user
from typing import Annotated,Literal, Optional
from mangum import Mangum

app = FastAPI()

app.include_router(router)

handler = Mangum(app)

# Base.metadata.create_all(bind = engine)




class TransactionBase(BaseModel):
    title : str 
    amount : float = Field(..., gt=0, description="Amount must be a positive number")
    type : Literal['income','expense']
    category : str
    date : date
    
class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    title : Optional[str] = None
    amount : Optional[float] = Field(default=None, gt = 0)
    type : Optional[Literal['income','expense']] = None
    category : Optional[str] = None
    date : Optional[date] = None


class TransactionSchema(TransactionBase):
    id : int
    owner_id : int
    
    class Config:
        from_attributes = True
    
    

@app.get("/transactions")
def get_transaction(db : db_dependency, current_user : dict = Depends(get_current_user)):
    transaction = db.query(Transaction).filter(Transaction.owner_id == current_user['id']).all()
    return transaction

@app.get("/transactions/filter")
def filter_transactions(db : db_dependency, current_user : dict = Depends(get_current_user), type : Optional[Literal['income','expense']] = None, category : Optional[str] = None, minimum_amount : Optional[float] = None, maximum_amount : Optional[float] = None):
    query = db.query(Transaction).filter(Transaction.owner_id == current_user['id'])
    
    if type:
        query = query.filter(Transaction.type == type)
    if category:
        query = query.filter(Transaction.category == category)
    if minimum_amount is not None:
        query = query.filter(Transaction.amount >= minimum_amount)
    if maximum_amount is not None:
        query = query.filter(Transaction.amount <= maximum_amount)
    
    transactions = query.all()
    return {"status": "success", "count": len(transactions), "data": transactions}

@app.post("/transactions",status_code=status.HTTP_201_CREATED)
def create_transaction(transaction : TransactionCreate,db : db_dependency,current_user : dict = Depends(get_current_user)):
    transaction_data = transaction.model_dump()
    transaction_data["owner_id"] = current_user['id']
    db_transaction = Transaction(**transaction_data)
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@app.get("/transactions/{transaction_id}")
def get_transaction_byId(db : db_dependency, transaction_id : int ,current_user : dict = Depends(get_current_user)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail= "Transaction not found")
    if transaction.owner_id != current_user['id']:
        raise HTTPException(status_code=403 , detail= "Not Authorized to perform this action")
    return transaction


@app.put("/transactions/{transaction_id}")
def update_transactions(db : db_dependency, transaction_id : int , update_data : TransactionUpdate, current_user : dict = Depends(get_current_user)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.owner_id == current_user['id']).first()
    if not transaction:
        raise HTTPException(status_code=404, detail=" Transaction not found")
    if transaction.owner_id != current_user['id']:
        raise HTTPException(status_code=403, detail= "Not Authorized to perform this action")
    

    update_transaction = update_data.model_dump(exclude_unset= True)
    
    for key, value in update_transaction.items():
        setattr(transaction,key, value)
    db.commit()
    db.refresh(transaction)
    return transaction

@app.delete("/transactions/{transaction_id}")
def delete_transaction(db : db_dependency, transaction_id : int , current_user : dict = Depends(get_current_user)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.owner_id == current_user['id']).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if transaction.owner_id != current_user['id']:
        raise HTTPException(status_code=403, detail= "Not Authorized to perform this action")
    
    db.delete(transaction)
    db.commit()
    return {"message": "Transaction deleted successfully"}


        