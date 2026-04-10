from pydantic import BaseModel, Field
from typing import List, Optional

class Experience(BaseModel):
    title: str = Field(..., description="The official job title")
    company: str = Field(..., description="The name of the company or academic institution")
    years_of_experience: float = Field(..., description="Calculated years of experience. E.g., 2.5 for two and a half years")
    semantic_summary: str = Field(..., description="A 1-2 sentence summary of the core responsibilities, impact, and intent behind the role")
    skills_used: List[str] = Field(default_factory=list, description="List of technical and soft skills utilized in this specific role")

class CandidateProfile(BaseModel):
    name: str = Field(..., description="Full name of the candidate")
    professional_experience: List[Experience] = Field(..., description="Paid, full-time or part-time professional roles")
    academic_projects: List[Experience] = Field(..., description="University capstones, research projects, or significant coursework")
    certifications: List[str] = Field(default_factory=list, description="Online courses, bootcamps, and professional certifications")
    global_skills: List[str] = Field(..., description="A fully deduplicated and normalized list of all skills across all experiences")
    overall_summary: str = Field(..., description="A dense 3-sentence summary of the candidate's entire profile for quick recruiter review")
