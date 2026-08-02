import pytest
from app.router.router import IntentRouter, IntentType


class DummyQAService:
    name = "QAService"


class DummyEssayService:
    name = "EssayService"


class DummyArtifactService:
    name = "ArtifactService"


@pytest.fixture
def router():
    return IntentRouter(
        qa_service=DummyQAService(),
        essay_service=DummyEssayService(),
        artifact_service=DummyArtifactService(),
    )


def test_classify_intent_qa(router):
    assert router.classify_intent("How to optimize growth metrics?") == IntentType.QA
    assert router.classify_intent("What is conversion rate?") == IntentType.QA


def test_classify_intent_essay(router):
    assert router.classify_intent("/essay Write about growth strategies") == IntentType.ESSAY
    assert router.classify_intent("Please write an essay on user retention") == IntentType.ESSAY
    assert router.classify_intent("Can you draft essay for product launch?") == IntentType.ESSAY
    assert router.classify_intent("Write a ship30 essay about product-led growth") == IntentType.ESSAY


def test_classify_intent_artifact(router):
    assert router.classify_intent("/artifact Create PRD template") == IntentType.ARTIFACT
    assert router.classify_intent("Please generate artifact for onboarding") == IntentType.ARTIFACT
    assert router.classify_intent("create artifact layout") == IntentType.ARTIFACT
    assert router.classify_intent("build artifact standard") == IntentType.ARTIFACT
    assert router.classify_intent("Create an artifact based on the chat we had") == IntentType.ARTIFACT
    assert router.classify_intent("Make an artifact summarizing key points") == IntentType.ARTIFACT


def test_get_service_returns_appropriate_service(router):
    qa_srv = router.get_service("What is churn?")
    assert isinstance(qa_srv, DummyQAService)
    assert qa_srv.name == "QAService"

    essay_srv = router.get_service("/essay Write about acquisition channels")
    assert isinstance(essay_srv, DummyEssayService)
    assert essay_srv.name == "EssayService"

    artifact_srv = router.get_service("generate artifact template")
    assert isinstance(artifact_srv, DummyArtifactService)
    assert artifact_srv.name == "ArtifactService"


def test_deterministic_routing_no_llm(router):
    # Ensure classification is purely deterministic based on rules
    for _ in range(5):
        assert router.classify_intent("Write an essay on viral loops") == IntentType.ESSAY
        assert router.get_service("/artifact metrics dashboard").name == "ArtifactService"
        assert router.get_service("Explain NPS score").name == "QAService"
