import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.config import settings
from app.models import Image
from app.services.phase_manager import Phase

# Use the same database as production (no clearing)
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
def battle_id():
    """Generate a unique battle_id for each test"""
    return str(uuid.uuid4())


@pytest.fixture(scope="function")
def db_session():
    """Create a database session for each test (no clearing)"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db_session, battle_id):
    """Create a test client with battle-specific configuration"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        admin_key = settings.admin_api_key
        if not admin_key:
            raise ValueError("Admin API key is not set")
        settings.admin_api_key = admin_key
        test_client.headers.update({"X-Admin-Key": admin_key})
        
        # Initialize battle-specific metadata
        response = test_client.post(
            "/admin/phase", json={"battle_id": battle_id, "phase": Phase.SELLER_MANAGEMENT.value}
        )
        assert response.status_code == 200, response.text
        response = test_client.post("/admin/day", json={"battle_id": battle_id, "day": 0})
        assert response.status_code == 200, response.text
        response = test_client.post("/admin/round", json={"battle_id": battle_id, "round": 1})
        assert response.status_code == 200, response.text
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_seller(client, battle_id):
    """Create a sample seller for this battle and return its data"""
    response = client.post(
        "/createSeller",
        json={"battle_id": battle_id}
    )
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def sample_buyer(client, battle_id):
    """Create a sample buyer for this battle and return its data"""
    response = client.post(
        "/createBuyer",
        json={"battle_id": battle_id}
    )
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def sample_images(db_session):
    """Fetch existing images from the database (loaded during migration)"""
    # Query images by product_number
    images_01 = db_session.query(Image).filter(Image.product_number == "01").limit(3).all()
    images_02 = db_session.query(Image).filter(Image.product_number == "02").limit(2).all()
    images_03 = db_session.query(Image).filter(Image.product_number == "03").limit(3).all()
    uncategorized = db_session.query(Image).filter(Image.product_number == None).first()

    # Ensure we have images loaded
    if not images_01 or not images_02 or not images_03:
        raise RuntimeError(
            "Images not found in database. Please run 'uv run images/create_image_descriptions.py' first."
        )

    all_images = images_01 + images_02 + images_03

    result = {
        "all": all_images,
        "01": images_01,
        "02": images_02,
        "03": images_03
    }

    # Add uncategorized if it exists (may be None if no uncategorized images in DB)
    if uncategorized:
        result["uncategorized"] = uncategorized

    return result


@pytest.fixture
def set_phase(client, battle_id):
    """Utility fixture to change marketplace phase during a test."""

    def _set(phase: Phase):
        response = client.post(
            "/admin/phase",
            json={"battle_id": battle_id, "phase": phase.value if isinstance(phase, Phase) else phase},
        )
        assert response.status_code == 200, response.text
        return response.json()

    return _set


@pytest.fixture
def set_day(client, battle_id):
    """Utility fixture to configure the simulated marketplace day during a test."""

    def _set(day: int):
        response = client.post(
            "/admin/day",
            json={"battle_id": battle_id, "day": day},
        )
        assert response.status_code == 200, response.text
        return response.json()

    return _set


@pytest.fixture
def set_round(client, battle_id):
    """Utility fixture to configure the simulation round during a test."""

    def _set(round_number: int):
        response = client.post(
            "/admin/round",
            json={"battle_id": battle_id, "round": round_number},
        )
        assert response.status_code == 200, response.text
        return response.json()

    return _set


@pytest.fixture
def sample_product(client, battle_id, sample_seller, sample_images):
    """Create a sample product and return its data"""
    # Use images from product_number 01
    image_ids = [img.id for img in sample_images["01"]]

    # Use battle_id to make product ID unique per battle
    product_id = f"test-product-{battle_id[:8]}"

    product_data = {
        "name": "Test Product",
        "short_description": "A test product",
        "long_description": "This is a detailed description of the test product",
        "price": 1999,
        "image_ids": image_ids,
        "towel_variant": "budget"  # Category 01 = budget
    }

    response = client.post(
        f"/product/{product_id}",
        json=product_data,
        headers={"Authorization": f"Bearer {sample_seller['auth_token']}"}
    )
    assert response.status_code == 200
    return {
        "id": product_id,
        "seller": sample_seller,
        "image_ids": image_ids,
        **product_data
    }
