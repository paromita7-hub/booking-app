import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app as fastapi_app
import app.models  # ensure all models are imported and registered on Base.metadata
from app.models.property import Property

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine_test = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine_test)
    session = TestingSessionLocal()

    # Seed the 4 standard properties for test isolation
    props = [
        Property(id=1, name="Olympic Hotel Paddington", booking_url="https://booking.com/1", location="Paddington, Sydney"),
        Property(id=2, name="Potts Point", booking_url="https://booking.com/2", location="Potts Point, Sydney"),
        Property(id=3, name="Central Sydney", booking_url="https://booking.com/3", location="Surry Hills, Sydney"),
        Property(id=4, name="Darling Harbour", booking_url="https://booking.com/4", location="Darling Harbour, Sydney"),
    ]
    for p in props:
        session.add(p)
    session.commit()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    fastapi_app.dependency_overrides[get_db] = override_get_db
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()
