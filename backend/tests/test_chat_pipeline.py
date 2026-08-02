import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.models import User, Session
from app.database.session import get_db
from app.main import app
from app.router.router import IntentRouter, IntentType
from app.services.mock_services import MockQAService, MockEssayService, MockArtifactService

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
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
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_intent_router():
    router = IntentRouter()
    assert router.route("How to scale product?", []) == IntentType.QA
    assert router.route("/essay Write about PLG", []) == IntentType.ESSAY
    assert router.route("create artifact template", []) == IntentType.ARTIFACT


def test_mock_services():
    qa = MockQAService()
    essay = MockEssayService()
    artifact = MockArtifactService()

    assert "Answer to query" in qa.process("test query", [])["content"]
    assert "Outlined essay topic" in essay.process("test essay", [])["content"]
    assert "Created template artifact" in artifact.process("test artifact", [])["content"]


def test_chat_pipeline_flow(client, db_session):
    # Setup User & Session
    user = User(email="testchat@example.com")
    db_session.add(user)
    db_session.commit()

    session = Session(user_id=user.id, title="Chat Pipeline Test")
    db_session.add(session)
    db_session.commit()

    # 1. Send QA message
    payload = {
        "user_id": str(user.id),
        "session_id": str(session.id),
        "message": "What is retention rate?"
    }
    res = client.post("/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["session_id"] == str(session.id)
    assert data["intent"] == "qa"
    assert data["history_count"] == 1
    assert len(data["response_message"]["content"]) > 0

    # 2. Send Essay message to check history loading & routing
    payload_essay = {
        "user_id": str(user.id),
        "session_id": str(session.id),
        "message": "/essay Write about retention strategy"
    }
    res2 = client.post("/chat", json=payload_essay)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["intent"] == "essay"
    assert data2["history_count"] == 3  # (msg1 user, msg1 assistant, msg2 user)
    assert len(data2["response_message"]["content"]) > 0


def test_chat_pipeline_invalid_session(client, db_session):
    payload = {
        "user_id": str(uuid.uuid4()),
        "session_id": str(uuid.uuid4()),
        "message": "Hello"
    }
    res = client.post("/chat", json=payload)
    assert res.status_code == 404
