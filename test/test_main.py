from fastapi.testclient import TestClient
from main import app
from fastapi import status
from router.auth import get_current_user
from database import Sessionlocal
from models import Transaction,User


client = TestClient(app)

def override_get_current_user():
    return {
        'id': 1, 
        'username': 'testuser'
    }

def test_transaction():
    
    db = Sessionlocal()
    
    user = db.query(Transaction).filter(Transaction.owner_id == 1).first()
    if not user:
        try:
            db.add(User
            (
                id = 1,
                user_name="testuser",
                email="test@example.com",
                hashed_password="hashedpassword")
            )
            db.commit()
        except:
            db.add(User(id = 1))
            db.commit()
        

    db.query(Transaction).filter(Transaction.id == 99).delete()
    transaction = Transaction(
        id = 99,
        title ="Test Transaction", 
        amount =100.0, 
        type ="income", 
        category ="Test",
        date ="2023-01-01", 
        owner_id =1
    )
    db.add(transaction)
    db.commit()
    
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_transactions():
    response = client.get("/transactions")
    assert response.status_code == status.HTTP_200_OK
    
def test_specific_transaction():
    response = client.get("/transactions/99")
    assert response.status_code == status.HTTP_200_OK
    
def test_create_transaction():
    
    transaction_data = {
        "title": "New Transaction",
        "amount": 50.0,
        "type": "expense",
        "category": "Test Category",
        "date": "2023-01-02"
    }
    response = client.post("/transactions", json = transaction_data)
    assert response.status_code == status.HTTP_201_CREATED
    
def test_update_transaction():
    test_transaction()
    updated_data = {

        "title": "Updated Transaction",
        "amount": 60.0,
        "type": "income",
        "category": "Updated Category",
    }
    response = client.put("/transactions/99", json = updated_data)
    assert response.status_code == status.HTTP_200_OK

    
def test_delete_transaction():
    response = client.delete("/transactions/99")
    assert response.status_code == status.HTTP_200_OK