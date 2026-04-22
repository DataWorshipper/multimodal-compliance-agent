from typing import List, Optional, Any
from pydantic import BaseModel, Field
import operator
from typing_extensions import Annotated

class ComplianceIssue(BaseModel):
    category: str = Field(description="The type of violation (e.g., 'Sponsorship Disclosure', 'Health Claim', 'Financial Advice').")
    severity: str = Field(description="The severity level ('Critical', 'Warning', 'Minor').")
    description: str = Field(description="Detailed explanation of the violation and which specific rule it broke.")
    timestamp: Optional[str] = Field(None, description="Approximate timestamp or context cue where it occurred.")

class AgentState(BaseModel):
    video_url: str
    transcript: Optional[str] = None
    ocr_text: Optional[str] = None
    compliance_rules: Optional[str] = None
    needs_web_search: Optional[str] = None
    web_search_results: Optional[str] = None
    compliance_issues: Annotated[List[ComplianceIssue], operator.add] = Field(default_factory=list)
    final_status: Optional[str] = Field(None, description="'PASS' or 'FAIL'")
    final_report: Optional[str] = None