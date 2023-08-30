from pydantic import BaseModel, validator
from typing import Any, Dict, List, Optional

from presidio_analyzer import PatternRecognizer

def create_recognizers(raw: str) -> List[PatternRecognizer]:
    return [ PatternRecognizer.from_dict(rec) for rec in raw ]

class AnalyzerRequest(BaseModel):
    """
    Analyzer request data.

    :param req_data: A request dictionary with the following fields:
        text: the text to analyze
        language: the language of the text
        entities: List of PII entities that should be looked for in the text.
        If entities=None then all entities are looked for.
        correlation_id: cross call ID for this request
        score_threshold: A minimum value for which to return an identified entity
        log_decision_process: Should the decision points within the analysis
        be logged
        return_decision_process: Should the decision points within the analysis
        returned as part of the response
    """

    text: str
    language: str
    entities: Optional[List[str]] = None
    correlation_id: Optional[str] = None
    score_threshold: Optional[float] = None
    return_decision_process: Optional[bool] = None
    ad_hoc_recognizers: Optional[List[Any]] = None
    _transform_recognizers = validator('ad_hoc_recognizers', pre=True, allow_reuse=True)(create_recognizers)
    context: Optional[List[str]] = None
