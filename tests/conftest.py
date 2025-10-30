import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.config import settings
from app.models import Image
from app.services.phase_manager import Phase

# Mock base64 image (1x1 transparent PNG)
MOCK_BASE64_IMAGE = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

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
        admin_key = settings.admin_api_key
        if not admin_key:
            raise ValueError("Admin API key is not set")
        settings.admin_api_key = admin_key
        test_client.headers.update({"X-Admin-Key": admin_key})
        response = test_client.post(
            "/admin/phase", json={"phase": Phase.SELLER_MANAGEMENT.value}
        )
        assert response.status_code == 200, response.text
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
    )
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def sample_images(db_session):
    """Create sample images in the database with different product_numbers"""
    images = []
    
    # Product number 01 - 3 images
    for i in range(3):
        img = Image(
            base64=MOCK_BASE64_IMAGE,
            image_description=f"Product 01 - View {i+1}",
            product_number="01"
        )
        db_session.add(img)
        images.append(img)
    
    # Product number 02 - 2 images
    for i in range(2):
        img = Image(
            base64=MOCK_BASE64_IMAGE,
            image_description=f"Product 02 - View {i+1}",
            product_number="02"
        )
        db_session.add(img)
        images.append(img)
    
    # Product number 03 - 4 images
    for i in range(4):
        img = Image(
            base64=MOCK_BASE64_IMAGE,
            image_description=f"Product 03 - View {i+1}",
            product_number="03"
        )
        db_session.add(img)
        images.append(img)
    
    # Uncategorized image (no product_number)
    img = Image(
        base64=MOCK_BASE64_IMAGE,
        image_description="Uncategorized image",
        product_number=None
    )
    db_session.add(img)
    images.append(img)
    
    db_session.commit()
    
    # Refresh all images to get their IDs
    for img in images:
        db_session.refresh(img)
    
    return {
        "all": images,
        "01": images[0:3],
        "02": images[3:5],
        "03": images[5:9],
        "uncategorized": images[9]
    }


@pytest.fixture
def set_phase(client):
    """Utility fixture to change marketplace phase during a test."""

    def _set(phase: Phase):
        response = client.post(
            "/admin/phase",
            json={"phase": phase.value if isinstance(phase, Phase) else phase},
        )
        assert response.status_code == 200, response.text
        return response.json()

    return _set


@pytest.fixture
def sample_product(client, sample_seller, sample_images):
    """Create a sample product and return its data"""
    # Use images from product_number 01
    image_ids = [img.id for img in sample_images["01"]]
    
    product_data = {
        "name": "Test Product",
        "short_description": "A test product",
        "long_description": "This is a detailed description of the test product",
        "price": 1999,
        "image_ids": image_ids
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
        "image_ids": image_ids,
        **product_data
    }
