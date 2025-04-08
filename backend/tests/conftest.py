import pytest
from fastapi.testclient import TestClient
from ..main import app
from ..core.config import settings
import mongomock
from faker import Faker

fake = Faker()

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def mock_mongodb():
    return mongomock.MongoClient()

@pytest.fixture
def fake_user_data():
    return {
        "email": fake.email(),
        "password": fake.password(),
        "full_name": fake.name(),
        "role": "candidate"
    }

@pytest.fixture
def fake_job_data():
    return {
        "title": fake.job(),
        "description": fake.text(),
        "requirements": [fake.word() for _ in range(3)],
        "salary_range": f"{fake.random_int(min=30000, max=100000)}-{fake.random_int(min=100000, max=200000)}",
        "location": fake.city()
    } 