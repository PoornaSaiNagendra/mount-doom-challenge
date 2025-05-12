import pytest
from datetime import datetime
from api.models import Transcript, TranscriptTurn, Metadata, MetadataQuestionnaire
from processing.summarizer import summarize_transcript
from processing.extractor import extract_structured_data
from processing.analyzer import analyze_transcript

@pytest.fixture
def sample_transcript():
    turns = [TranscriptTurn(speaker="agent", text="Hello", timestamp=datetime.utcnow())]
    md_q = MetadataQuestionnaire(True, True, True, True, True)
    md = Metadata(questionnaire=md_q, visitor_interest_level="high", potential_issue="naive", mount_doom_permit_status="pending", language="en")
    return Transcript(transcript_id="t1", session_id="s1", timestamp=datetime.utcnow(), agent_type="cs", duration_seconds=5, participants={"agent":"A","customer":"C"}, transcript_text=turns, metadata=md)

@pytest.mark.asyncio
async def test_summarizer_stub(sample_transcript):
    summary = await summarize_transcript(sample_transcript)
    assert isinstance(summary, str)
    assert summary

def test_extractor(sample_transcript):
    structured = extract_structured_data(sample_transcript)
    assert structured.visitor_details.permit_status == "pending"

@pytest.mark.asyncio
async def test_analyzer_stub(sample_transcript):
    analysis = await analyze_transcript(sample_transcript)
    assert 0.0 <= analysis.sentiment <= 1.0
    assert isinstance(analysis.action_items, list)

