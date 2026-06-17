import uuid
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import func
from app.db.base import Base, TimestampMixin


class Call(Base, TimestampMixin):
    __tablename__ = "calls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=True)
    stream_sid = Column(String(255), nullable=True)
    status = Column(String(50), default="completed")  # completed, failed
    duration_seconds = Column(Integer, nullable=True)
    transcript = Column(Text, nullable=True)  # full JSON of conversation
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)

    agent = relationship("Agent", backref="calls")