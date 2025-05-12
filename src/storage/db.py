import os
import asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, JSON, Text
from datetime import datetime

# Async SQLAlchemy setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/mordor")
engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)
Base = declarative_base()

class RawTranscript(Base):
    __tablename__ = "raw_transcripts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    transcript_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    session_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    data: Mapped[dict] = mapped_column(JSON)

class ProcessedResultModel(Base):
    __tablename__ = "processed_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    transcript_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    processed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    structured: Mapped[dict] = mapped_column(JSON, nullable=False)
    analysis: Mapped[dict] = mapped_column(JSON, nullable=False)

async def init_db() -> None:
    """
    Initialize database tables.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def save_raw_transcript(transcript_data: dict) -> None:
    """
    Persist raw transcript JSON into DB.
    """
    async with AsyncSessionLocal() as session:
        raw = RawTranscript(
            transcript_id=transcript_data.get("transcript_id"),
            session_id=transcript_data.get("session_id"),
            data=transcript_data,
        )
        session.add(raw)
        await session.commit()

async def save_processed_result(result_data: dict) -> None:
    """
    Persist processed result into DB.
    """
    async with AsyncSessionLocal() as session:
        proc = ProcessedResultModel(
            transcript_id=result_data.get("transcript_id"),
            processed_at=result_data.get("processing_timestamp"),
            summary=result_data.get("summary"),
            structured=result_data.get("structured_data"),
            analysis=result_data.get("analysis"),
        )
        session.add(proc)
        await session.commit()

if __name__ == "__main__":
    asyncio.run(init_db())
