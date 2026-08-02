import time
import uuid
import json
from typing import Any, Dict, List, Optional, AsyncGenerator
from uuid import UUID

from app.core.config import settings
from app.database.models import Message, Session
from app.providers.factory import ProviderFactory
from app.repositories.message_repository import MessageRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.artifact_repository import ArtifactRepository
from app.router.router import IntentRouter, IntentType
from app.services.llm_service import LLMService
from app.services.qa_service import QAService
from app.services.essay_service import EssayService
from app.services.artifact_service import ArtifactService
from app.retrieval.hybrid_retriever import HybridRetriever
from app.prompts.qa_prompt import build_qa_prompt
from app.prompts.essay_prompt import build_essay_prompt
from app.prompts.artifact_prompt import build_artifact_prompt
from app.utils.logger import log_request_metrics
from app.api.routes.settings import runtime_settings


class ChatService:
    """
    Service layer orchestrating the full Chat pipeline:
    1. Receive user message & load/verify session
    2. Load conversation history
    3. Call IntentRouter (QA, ESSAY, ARTIFACT)
    4. Execute Hybrid Retrieval (Dense ChromaDB + Sparse BM25 via RRF) if QA
    5. Construct prompt via Prompt Builder
    6. Call LLM Provider via LLMService (Anthropic or Ollama)
    7. Persist user & assistant messages and any generated artifacts to DB
    8. Return structured response & log observability metrics
    """

    def __init__(
        self,
        session_repo: SessionRepository,
        message_repo: MessageRepository,
        artifact_repo: Optional[ArtifactRepository] = None,
        router: Optional[IntentRouter] = None,
        retriever: Optional[HybridRetriever] = None,
        qa_service: Optional[QAService] = None,
        essay_service: Optional[EssayService] = None,
        artifact_service: Optional[ArtifactService] = None,
    ):
        self.session_repo = session_repo
        self.message_repo = message_repo
        self.artifact_repo = artifact_repo or ArtifactRepository(session_repo.db)
        self.router = router or IntentRouter()
        self.retriever = retriever or HybridRetriever()
        self.qa_service = qa_service
        self.essay_service = essay_service
        self.artifact_service = artifact_service

    def _get_llm_service(self) -> LLMService:
        provider = ProviderFactory.create_provider(settings)
        return LLMService(provider=provider)

    async def process_chat(
        self,
        user_id: UUID,
        session_id: UUID,
        message_text: str,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Asynchronous processing of chat request pipeline.
        """
        start_time = time.time()
        req_id = request_id or str(uuid.uuid4())

        # Verify session exists
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Load history prior to current message
        history = self.message_repo.get_session_history(session_id)
        prior_history_count = len(history)

        # 1. Receive & save user message
        self.message_repo.create_message(
            session_id=session_id,
            role="user",
            content=message_text,
        )

        # 2. Call IntentRouter
        intent = self.router.classify_intent(message_text, history)

        retrieval_latency = 0.0
        llm_latency = 0.0
        citations = []
        artifact_data = None
        current_model = runtime_settings.get("model") or (
            settings.OLLAMA_MODEL
            if (settings.MODEL_PROVIDER or "").lower() == "ollama"
            else settings.ANTHROPIC_MODEL
        )

        llm_service = self._get_llm_service()

        if intent == IntentType.ESSAY:
            srv = self.essay_service or EssayService(llm_service=llm_service)
            t_llm_start = time.time()
            if hasattr(srv, "generate_essay"):
                res = await srv.generate_essay(message_text, history)
            else:
                res = srv.process(message_text, history)
            llm_latency = (time.time() - t_llm_start) * 1000
            content = res.get("content", "")
            message_metadata = res.get("metadata", {})

        elif intent == IntentType.ARTIFACT:
            art_type = "html" if "html" in message_text.lower() else "css" if "css" in message_text.lower() else "markdown"
            srv = self.artifact_service or ArtifactService(llm_service=llm_service)
            t_llm_start = time.time()
            if hasattr(srv, "generate_artifact"):
                res = await srv.generate_artifact(message_text, artifact_type=art_type, history=history)
            else:
                res = srv.process(message_text, history)
            llm_latency = (time.time() - t_llm_start) * 1000
            content = res.get("content", "")
            message_metadata = res.get("metadata", {})

            # Create artifact in DB
            title = res.get("title") or f"Generated {art_type.upper()} Artifact"
            db_artifact = self.artifact_repo.create_artifact(
                session_id=session_id,
                title=title,
                artifact_type=art_type,
                content=content,
            )
            artifact_data = {
                "id": str(db_artifact.id),
                "title": db_artifact.title,
                "artifact_type": db_artifact.artifact_type,
                "content": db_artifact.content,
                "version": db_artifact.version,
            }
            message_metadata["artifact_id"] = artifact_data["id"]
            message_metadata["artifact"] = artifact_data

        else: # QA
            srv = self.qa_service or QAService(retriever=self.retriever, llm_service=llm_service)
            t_llm_start = time.time()
            if hasattr(srv, "answer_question"):
                res = await srv.answer_question(message_text, history)
            else:
                res = srv.process(message_text, history)
            llm_latency = (time.time() - t_llm_start) * 1000
            content = res.get("content", "")
            citations = res.get("citations", [])
            message_metadata = res.get("metadata", {})
            message_metadata["sources"] = citations
            message_metadata["citations"] = citations
            message_metadata["model"] = current_model
            message_metadata["provider"] = settings.MODEL_PROVIDER

        total_response_time = (time.time() - start_time) * 1000

        # 4. Persist assistant response message
        assistant_msg = self.message_repo.create_message(
            session_id=session_id,
            role="assistant",
            content=content,
            metadata_json=message_metadata,
        )

        # Log metrics
        log_request_metrics(
            request_id=req_id,
            session_id=str(session_id),
            model=current_model,
            retrieval_latency_ms=retrieval_latency,
            llm_latency_ms=llm_latency,
            total_response_time_ms=total_response_time,
            retrieved_doc_count=len(citations),
        )

        return {
            "session_id": str(session_id),
            "intent": intent.value,
            "response_message": {
                "id": str(assistant_msg.id),
                "session_id": str(assistant_msg.session_id),
                "role": assistant_msg.role,
                "content": assistant_msg.content,
                "created_at": assistant_msg.created_at.isoformat() if assistant_msg.created_at else "",
                "metadata": message_metadata,
                "citations": citations,
            },
            "history_count": prior_history_count + 1,
            "metadata": message_metadata,
            "artifact": artifact_data,
        }

    async def process_chat_stream(
        self,
        user_id: UUID,
        session_id: UUID,
        message_text: str,
        request_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        SSE Generator for streaming tokens token-by-token.
        """
        start_time = time.time()
        req_id = request_id or str(uuid.uuid4())

        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        history = self.message_repo.get_session_history(session_id)
        prior_history_count = len(history)

        self.message_repo.create_message(session_id=session_id, role="user", content=message_text)
        intent = self.router.classify_intent(message_text, history)
        retrieved_chunks = []
        citations = []
        retrieval_latency = 0.0
        current_model = runtime_settings.get("model") or (
            settings.OLLAMA_MODEL
            if (settings.MODEL_PROVIDER or "").lower() == "ollama"
            else settings.ANTHROPIC_MODEL
        )

        if intent == IntentType.QA:
            t_ret_start = time.time()
            try:
                retrieved_chunks = await self.retriever.retrieve(query=message_text, top_k=5)
            except Exception:
                retrieved_chunks = []
            retrieval_latency = (time.time() - t_ret_start) * 1000

            for chunk in retrieved_chunks:
                meta = chunk.metadata or {}
                citations.append({
                    "id": chunk.chunk_id,
                    "title": meta.get("title") or f"Episode with {meta.get('guest', 'Guest')}",
                    "source": meta.get("youtube_url") or meta.get("guest") or "Lenny's Podcast",
                    "snippet": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                    "relevance_score": round(float(chunk.score), 3) if chunk.score is not None else 0.85,
                    "chunk_id": chunk.chunk_id,
                    "guest": meta.get("guest") or "Unknown Guest",
                    "episode_title": meta.get("title") or "Lenny's Podcast Episode",
                    "youtube_url": meta.get("youtube_url") or "",
                })
            prompt = build_qa_prompt(query=message_text, context_chunks=retrieved_chunks)
        elif intent == IntentType.ESSAY:
            prompt = build_essay_prompt(topic=message_text, history=history)
        else: # ARTIFACT
            art_type = "html" if "html" in message_text.lower() else "css" if "css" in message_text.lower() else "markdown"
            prompt = build_artifact_prompt(prompt=message_text, artifact_type=art_type, history=history)

        # Emit initial metadata event
        meta_event = {
            "type": "metadata",
            "intent": intent.value,
            "sources": citations,
            "citations": citations,
            "retrieval_time_ms": round(retrieval_latency, 2),
            "confidence_score": 0.88 if citations else 0.0,
            "model": current_model,
        }
        yield f"data: {json.dumps(meta_event)}\n\n"

        llm_service = self._get_llm_service()
        full_content = ""
        t_llm_start = time.time()

        try:
            async for chunk in llm_service.stream(prompt):
                full_content += chunk
                token_event = {"type": "token", "content": chunk}
                yield f"data: {json.dumps(token_event)}\n\n"
        except Exception as err:
            err_msg = f"\n\n[Generation Error: {str(err)}]"
            full_content += err_msg
            yield f"data: {json.dumps({'type': 'token', 'content': err_msg})}\n\n"

        llm_latency = (time.time() - t_llm_start) * 1000
        total_time = (time.time() - start_time) * 1000

        artifact_data = None
        if intent == IntentType.ARTIFACT:
            art_type = "html" if "html" in message_text.lower() else "css" if "css" in message_text.lower() else "markdown"
            db_artifact = self.artifact_repo.create_artifact(
                session_id=session_id,
                title=f"Generated {art_type.upper()} Artifact",
                artifact_type=art_type,
                content=full_content,
            )
            artifact_data = {
                "id": str(db_artifact.id),
                "title": db_artifact.title,
                "artifact_type": db_artifact.artifact_type,
                "content": db_artifact.content,
                "version": db_artifact.version,
            }

        final_metadata = {
            "service": f"{intent.value.capitalize()}Service",
            "intent": intent.value,
            "retrieval_performed": intent == IntentType.QA,
            "has_artifacts": artifact_data is not None,
            "is_essay": intent == IntentType.ESSAY,
            "retrieval_time_ms": round(retrieval_latency, 2),
            "confidence_score": 0.88 if citations else 0.0,
            "model": current_model,
            "provider": settings.MODEL_PROVIDER,
            "sources": citations,
            "citations": citations,
            "artifact_id": artifact_data["id"] if artifact_data else None,
            "artifact": artifact_data,
        }

        # Persist final assistant message
        assistant_msg = self.message_repo.create_message(
            session_id=session_id,
            role="assistant",
            content=full_content,
            metadata_json=final_metadata,
        )

        log_request_metrics(
            request_id=req_id,
            session_id=str(session_id),
            model=current_model,
            retrieval_latency_ms=retrieval_latency,
            llm_latency_ms=llm_latency,
            total_response_time_ms=total_time,
            retrieved_doc_count=len(retrieved_chunks),
        )

        done_event = {
            "type": "done",
            "response_message": {
                "id": str(assistant_msg.id),
                "session_id": str(assistant_msg.session_id),
                "role": assistant_msg.role,
                "content": assistant_msg.content,
                "metadata": final_metadata,
                "citations": citations,
            },
            "history_count": prior_history_count + 1,
            "metadata": final_metadata,
            "artifact": artifact_data,
        }
        yield f"data: {json.dumps(done_event)}\n\n"
