"""
Structured data extraction from transcript and metadata.
"""
from ..api.models import Transcript, StructuredData, VisitorDetails, QuestionnaireCompletion


def extract_structured_data(transcript: Transcript) -> StructuredData:
    """
    Extract fields like visitor details and questionnaire completion status.
    """
    md = transcript.metadata
    visitor = VisitorDetails(
        ring_bearer=False, 
        gear_prepared=md.questionnaire.gear_discussed,
        hazard_knowledge="unknown",  # stub
        fitness_level="unknown",
        permit_status=md.mount_doom_permit_status
    )
    questionnaire = QuestionnaireCompletion(
        purpose_of_visit=md.questionnaire.purpose_of_visit_asked,
        experience_level=md.questionnaire.experience_assessed,
        risk_acknowledgment=md.questionnaire.risk_acknowledged,
        gear_assessment=md.questionnaire.gear_discussed,
        item_disposal_intent=md.questionnaire.any_items_to_dispose_of_asked,
    )
    return StructuredData(visitor_details=visitor, questionnaire_completion=questionnaire)
