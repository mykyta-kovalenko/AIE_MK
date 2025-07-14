from typing import TypedDict, Optional

class RealityCheckState(TypedDict):
    """State that gets passed between agent nodes."""
    topic: str
    reddit_results: Optional[str]
    web_results: Optional[str]
    academic_results: Optional[str]
    final_analysis: Optional[str]
    current_step: str 