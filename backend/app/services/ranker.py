import json
import os
import re
from typing import Any, Dict, List

from google import genai
from pinecone import Pinecone

from app.models.schema import CandidateProfile
from app.services.extractor import estimate_years, infer_skills, profile_total_years, top_profile_skills

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) if os.getenv("GEMINI_API_KEY") else None
pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY")) if os.getenv("PINECONE_API_KEY") else None

INDEX_NAME = "intenthire-candidates"


def embed_text(text: str) -> List[float]:
    if not gemini_client:
        raise RuntimeError("Google GenAI client not configured for embeddings.")

    response = gemini_client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )
    return response.embeddings[0].values


def calculate_compatibility(jd_text: str, candidates: List[Any], top_k: int = 10) -> List[Dict[str, Any]]:
    jd_skills = infer_skills(jd_text)
    required_years = estimate_years(jd_text)
    jd_tokens = _meaningful_tokens(jd_text)
    ranked_candidates: List[Dict[str, Any]] = []

    for candidate in candidates:
        profile = CandidateProfile.model_validate(json.loads(candidate.raw_profile_json))
        candidate_skills = profile.global_skills
        matched_skills = [skill for skill in jd_skills if skill in candidate_skills]
        years = profile_total_years(profile)

        overlap_score = len(matched_skills) / max(1, len(jd_skills)) if jd_skills else min(len(candidate_skills), 4) / 4
        years_score = min(years / required_years, 1.0) if required_years else min(years / 5, 1.0)
        summary_text = " ".join([
            candidate.name or "",
            candidate.overall_summary or "",
            " ".join(candidate_skills),
            candidate.job_role or "",
        ])
        token_hits = len(jd_tokens & _meaningful_tokens(summary_text))
        token_score = token_hits / max(1, min(len(jd_tokens), 12)) if jd_tokens else 0

        score_percentage = int(round((overlap_score * 0.6 + years_score * 0.25 + token_score * 0.15) * 100))
        top_skills = matched_skills[:4] or top_profile_skills(profile, 4)

        ranked_candidates.append({
            "id": candidate.id,
            "name": candidate.name,
            "score": max(0, min(score_percentage, 100)),
            "justification": _build_justification(candidate.name, matched_skills, years, required_years, candidate_skills),
            "top_skills": top_skills,
            "years_of_experience": years,
            "job_role": candidate.job_role,
            "batch_label": candidate.batch_label,
            "overall_summary": candidate.overall_summary,
            "source_filename": candidate.source_filename,
        })

    ranked_candidates.sort(key=lambda item: (-item["score"], -item["years_of_experience"], item["name"] or ""))
    return ranked_candidates[:top_k]


def _meaningful_tokens(text: str) -> set[str]:
    stop_words = {
        "the", "and", "for", "with", "from", "this", "that", "have", "has",
        "into", "your", "their", "role", "team", "years", "year", "experience",
    }
    return {
        token for token in re.findall(r"[a-zA-Z]{3,}", text.lower())
        if token not in stop_words
    }


def _build_justification(
    name: str,
    matched_skills: List[str],
    years: float,
    required_years: float,
    candidate_skills: List[str],
) -> str:
    if matched_skills:
        first_sentence = f"{name} aligns with the JD through direct strength in {', '.join(matched_skills[:3])}."
    else:
        first_sentence = f"{name} shows adjacent capability through {', '.join(candidate_skills[:3])}."

    if required_years:
        second_sentence = f"The profile indicates about {years:.1f} years of relevant depth against a target of {required_years:.1f} years."
    else:
        second_sentence = f"The resume shows about {years:.1f} years of relevant experience with transferable technical depth."

    return f"{first_sentence} {second_sentence}"
