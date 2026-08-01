import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.models import User, Session
from app.database.session import get_db
from app.main import app
from app.repositories.session_repository import SessionRepository
from app.services.session_service import SessionService

# Setup in-memory SQLite database for testing session management
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user(db_session):
    user = User(email="testuser@example.com", full_name="Test User")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_session_repository_crud(db_session, sample_user):
    repo = SessionRepository(db_session)

    # Create
    sess = repo.create(user_id=sample_user.id, title="Test Session")
    assert sess.id is not None
    assert sess.title == "Test Session"
    assert sess.user_id == sample_user.id

    # Get by ID
    fetched = repo.get_by_id(sess.id)
    assert fetched is not None
    assert fetched.id == sess.id

    # Get all
    all_sessions = repo.get_all(user_id=sample_user.id)
    assert len(all_sessions) == 1

    # Update
    updated = repo.update(sess.id, title="Updated Title")
    assert updated.title == "Updated Title"

    # Delete
    deleted = repo.delete(sess.id)
    assert deleted is True
    assert repo.get_by_id(sess.id) is None


def test_session_service(db_session, sample_user):
    repo = SessionRepository(db_session)
    service = SessionService(repo)

    created = service.create_session(user_id=sample_user.id, title="Service Session")
    assert created.title == "Service Session"

    fetched = service.get_session(created.id)
    assert fetched.id == created.id

    listed = service.list_sessions(user_id=sample_user.id)
    assert len(listed) == 1

    updated = service.update_session(created.id, title="New Service Title")
    assert updated.title == "New Service Title"

    deleted = service.delete_session(created.id)
    assert deleted is True


def test_api_session_endpoints(client, sample_user):
    # 1. POST /sessions
    res = client.post("/sessions", json={"user_id": str(sample_user.id), "title": "API Session"})
    assert res.status_code == 201
    data = res.json()
    session_id = data["id"]
    assert data["title"] == "API Session"
    assert data["user_id"] == str(sample_user.id)

    # 2. GET /sessions/{id}
    res = client.get(f"/sessions/{session_id}")
    assert res.status_code == 200
    assert res.json()["id"] == session_id

    # 3. GET /sessions
    res = client.get(f"/sessions?user_id={sample_user.id}")
    assert res.status_code == 200
    sessions_list = res.json()
    assert len(sessions_list) == 1
    assert sessions_list[0]["id"] == session_id

    # 4. PATCH /sessions/{id}
    res = client.patch(f"/sessions/{session_id}", json={"title": "Patched API Session"})
    assert res.status_code == 200
    assert res.json()["title"] == "Patched API Session"

    # 5. DELETE /sessions/{id}
    res = client.delete(f"/sessions/{session_id}")
    assert res.status_code == 204

    # Verify 404 after delete
    res = client.get(f"/sessions/{session_id}")
    assert res.status_code == 404
