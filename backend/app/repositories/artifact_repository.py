from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.database.models import Artifact


class ArtifactRepository:
    """
    Repository layer for Artifact operations using SQLAlchemy 2.0.
    """

    def __init__(self, db: DbSession):
        self.db = db

    def get_by_session(self, session_id: UUID) -> List[Artifact]:
        stmt = (
            select(Artifact)
            .where(Artifact.session_id == session_id)
            .order_by(Artifact.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, artifact_id: UUID) -> Optional[Artifact]:
        stmt = select(Artifact).where(Artifact.id == artifact_id)
        return self.db.scalars(stmt).first()

    def create_artifact(
        self,
        session_id: UUID,
        title: str,
        artifact_type: str,
        content: str,
        version: int = 1,
    ) -> Artifact:
        artifact = Artifact(
            session_id=session_id,
            title=title,
            artifact_type=artifact_type,
            content=content,
            version=version,
        )
        self.db.add(artifact)
        self.db.commit()
        self.db.refresh(artifact)
        return artifact
