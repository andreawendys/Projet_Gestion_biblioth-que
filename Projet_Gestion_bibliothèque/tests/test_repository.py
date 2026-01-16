import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from config.database import CassandraConnection
from models.user import UserRepository
from uuid import UUID

@pytest.fixture(scope="module")
def session():
    db = CassandraConnection()
    sess = db.connect()
    yield sess
    db.close()

def test_user_creation_and_retrieval(session):
    repo = UserRepository(session)
    email = "test@example.com"
    
    # 1. Test création
    user_id = repo.create_user(email, "Test", "User")
    assert isinstance(user_id, UUID)
    
    # 2. Test récupération
    user = repo.get_user(user_id)
    assert user is not None
    assert user.email == email