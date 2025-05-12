"""
Analysis services: sentiment scoring, interest level, preparedness.
"""
from ..api.models import Transcript, Analysis


def analyze_transcript(transcript: Transcript) -> Analysis:
    """
    Perform sentiment analysis and derive other metrics.
    """
    # TODO: hook up sentiment model or service
    sentiment_score = 0.5  # placeholder
    interest_level = transcript.metadata.visitor_interest_level
    preparedness_level = "medium"  # stub logic
    action_items = ["[LLM GENERATED ACTION ITEM]"]
    return Analysis(
        sentiment=sentiment_score,
        interest_level=interest_level,
        preparedness_level=preparedness_level,
        action_items=action_items
    )
