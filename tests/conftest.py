import pytest
import base64
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.config import settings

# Mock base64 image (1x1 transparent PNG)
MOCK_BASE64_IMAGE = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="


def mock_image(description="Test image"):
    """Helper function to create mock image data for tests"""
    return {
        "base64": MOCK_BASE64_IMAGE,
        "image_description": description
    }

# Create a test database URL (using same DB but will clear it)
TEST_DATABASE_URL = settings.database_url

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    # Drop all tables and recreate them
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with fresh database"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_seller(client):
    """Create a sample seller and return its data"""
    response = client.post(
        "/createSeller",
    )
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def sample_buyer(client):
    """Create a sample buyer and return its data"""
    response = client.post(
        "/createBuyer",
        json={"name": "Test Buyer"}
    )
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def sample_product(client, sample_seller):
    """Create a sample product and return its data"""
    product_data = {
        "name": "Test Product",
        "short_description": "A test product",
        "long_description": "This is a detailed description of the test product",
        "price": 1999,
        "image": {
            "base64": MOCK_BASE64_IMAGE,
            "image_description": "Test product image"
        }
    }
    
    response = client.post(
        "/product/test-product-1",
        json=product_data,
        headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
    )
    assert response.status_code == 200
    return {
        "id": "test-product-1",
        "seller": sample_seller,
        **product_data
    }
