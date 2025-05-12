import pytest
import asyncio
from storage.db import init_db, save_raw_transcript, save_processed_result, RawTranscript, ProcessedResultModel, engine
from sqlalchemy import select

@pytest.mark.asyncio
async def test_db_crud(tmp_path, monkeypatch):
    # Use in-memory SQLite for test
    test_url = "sqlite+aiosqlite:///:memory:"
    monkeypatch.setenv("DATABASE_URL", test_url)
    # re-import engine with test URL
    from importlib import reload
    import storage.db as dbmod
    reload(dbmod)
    await dbmod.init_db()
    # Test saving raw
    sample = {"transcript_id":"t1","session_id":"s1","data":{}}
    await dbmod.save_raw_transcript(sample)
    async with dbmod.AsyncSessionLocal() as session:
        res = await session.execute(select(RawTranscript).where(RawTranscript.transcript_id=="t1"))
        row = res.scalar_one_or_none()
        assert row is not None
    # Test saving processed
    proc = {"transcript_id":"t1","processing_timestamp":"2025-05-01T00:00:00Z","summary":"sum","structured_data":{},"analysis":{}}
    await dbmod.save_processed_result(proc)
    async with dbmod.AsyncSessionLocal() as session:
        res2 = await session.execute(select(ProcessedResultModel).where(ProcessedResultModel.transcript_id=="t1"))
        row2 = res2.scalar_one_or_none()
        assert row2.summary == "sum"
