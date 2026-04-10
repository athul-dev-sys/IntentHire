import os
import re
from datetime import datetime
from typing import Iterable, List

from google import genai
from google.genai import types

from app.models.schema import CandidateProfile, Experience

try:
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key) if api_key else None
except Exception as exc:
    print(f"WARNING: Google GenAI client failed to initialize: {exc}")
    client = None


SKILL_PATTERNS = {
    "Python": [r"\bpython\b", r"\bpandas\b", r"\bnumpy\b"],
    "Java": [r"\bjava\b", r"\bjvm\b"],
    "Backend": [r"\bbackend\b", r"\bapi\b", r"\bmicroservice", r"\bfastapi\b", r"\bdjango\b", r"\bflask\b", r"\bspring\b"],
    "Frontend": [r"\bfrontend\b", r"\breact\b", r"\bnext\.?js\b", r"\bjavascript\b", r"\btypescript\b", r"\bhtml\b", r"\bcss\b", r"\bangular\b", r"\bvue\b"],
    "Machine Learning": [r"\bmachine learning\b", r"\bdeep learning\b", r"\bml\b", r"\bpytorch\b", r"\btensorflow\b", r"\bscikit\b", r"\bnlp\b", r"\bcomputer vision\b"],
    "Data Engineering": [r"\bdata pipeline", r"\betl\b", r"\bspark\b", r"\bairflow\b", r"\bwarehouse\b"],
    "Databases": [r"\bsql\b", r"\bpostgres", r"\bmysql\b", r"\bmongodb\b", r"\bredis\b"],
    "Cloud": [r"\baws\b", r"\bazure\b", r"\bgcp\b", r"\bcloud\b", r"\bterraform\b"],
    "DevOps": [r"\bdocker\b", r"\bkubernetes\b", r"\bcicd\b", r"\bci/cd\b", r"\bjenkins\b", r"\bgithub actions\b"],
    "Product Leadership": [r"\bteam lead\b", r"\bleadership\b", r"\bstakeholder\b", r"\broadmap\b", r"\bmentored\b"],
}

TOOL_PATTERNS = {
    "PyTorch": r"\bpytorch\b",
    "TensorFlow": r"\btensorflow\b",
    "React": r"\breact\b",
    "Next.js": r"\bnext\.?js\b",
    "TypeScript": r"\btypescript\b",
    "FastAPI": r"\bfastapi\b",
    "Django": r"\bdjango\b",
    "Spring Boot": r"\bspring boot\b",
    "Docker": r"\bdocker\b",
    "Kubernetes": r"\bkubernetes\b",
    "AWS": r"\baws\b",
    "SQL": r"\bsql\b",
}

SECTION_HEADINGS = {
    "professional_experience": ["experience", "work history", "employment", "professional background"],
    "academic_projects": ["projects", "academic", "education", "research"],
    "certifications": ["certifications", "certificates", "licenses"],
}


def extract_semantic_profile(raw_text: str) -> CandidateProfile:
    if client:
        try:
            return _extract_with_gemini(raw_text)
        except Exception as exc:
            print(f"WARNING: Gemini extraction failed, using local fallback: {exc}")

    return _extract_locally(raw_text)


def infer_skills(text: str) -> List[str]:
    lower_text = text.lower()
    skills: List[str] = []

    for skill, patterns in SKILL_PATTERNS.items():
        if any(re.search(pattern, lower_text) for pattern in patterns):
            skills.append(skill)

    for tool, pattern in TOOL_PATTERNS.items():
        if re.search(pattern, lower_text):
            skills.append(tool)

    return _ordered_unique(skills)


def estimate_years(text: str) -> float:
    explicit_years = []
    date_range_years = []
    current_year = datetime.utcnow().year

    explicit_matches = re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs)", text.lower())
    explicit_years.extend(float(value) for value in explicit_matches)

    for start, end in re.findall(r"\b(20\d{2}|19\d{2})\s*[-–—]\s*(present|current|20\d{2}|19\d{2})", text.lower()):
        start_year = int(start)
        end_year = current_year if end in {"present", "current"} else int(end)
        if end_year >= start_year:
            date_range_years.append(float(end_year - start_year))

    if date_range_years:
        return sum(date_range_years)
    return max(explicit_years) if explicit_years else 0.0


def profile_total_years(profile: CandidateProfile) -> float:
    total = sum(exp.years_of_experience for exp in profile.professional_experience)
    return round(total, 1) if total > 0 else round(estimate_years(profile.overall_summary), 1)


def top_profile_skills(profile: CandidateProfile, limit: int = 5) -> List[str]:
    return profile.global_skills[:limit]


def _extract_with_gemini(raw_text: str) -> CandidateProfile:
    prompt = f"""
    You are an Expert Technical Recruiter Engine.
    Analyze the following extracted text from a candidate's resume.

    CRITICAL INSTRUCTIONS:
    1. Distinguish between paid professional work (Professional Experience), university classwork (Academic Projects), and certifications.
    2. Extract the literal 'Intent' behind their roles, focusing on architectural decisions, scale, and exact tools used.
    3. Normalize the skills used. E.g. If they list 'PyTorch', ensure the global_skills array includes 'Machine Learning'.

    Resume Text:
    {raw_text}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            "You are a structured data extraction AI.",
            prompt,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CandidateProfile,
            temperature=0.0,
        ),
    )
    return response.parsed


def _extract_locally(raw_text: str) -> CandidateProfile:
    cleaned_text = raw_text.strip()
    sections = _split_sections(cleaned_text)
    global_skills = infer_skills(cleaned_text)
    name = _extract_name(cleaned_text)

    professional_chunks = _chunk_section(sections.get("professional_experience") or cleaned_text)
    project_chunks = _chunk_section(sections.get("academic_projects") or "")
    cert_chunks = _chunk_section(sections.get("certifications") or "")

    professional_experience = [
        _build_experience(chunk, "Professional Experience")
        for chunk in professional_chunks[:3]
    ] or [_build_experience(cleaned_text, "Professional Experience")]

    academic_projects = [
        _build_experience(chunk, "Academic Project")
        for chunk in project_chunks[:2]
    ]

    certifications = _extract_certifications(cert_chunks, cleaned_text)
    overall_summary = _build_overall_summary(name, global_skills, professional_experience, academic_projects, certifications)

    return CandidateProfile(
        name=name,
        professional_experience=professional_experience,
        academic_projects=academic_projects,
        certifications=certifications,
        global_skills=global_skills or ["General Engineering"],
        overall_summary=overall_summary,
    )


def _split_sections(text: str) -> dict[str, str]:
    lines = [line.strip() for line in text.splitlines()]
    sections = {key: [] for key in SECTION_HEADINGS}
    current_key = None

    for line in lines:
        if not line:
            if current_key and sections[current_key] and sections[current_key][-1] != "":
                sections[current_key].append("")
            continue

        matched_key = None
        lower_line = line.lower()
        for key, headings in SECTION_HEADINGS.items():
            if any(heading in lower_line for heading in headings) and len(lower_line.split()) <= 5:
                matched_key = key
                break

        if matched_key:
            current_key = matched_key
            continue

        if current_key:
            sections[current_key].append(line)

    return {
        key: "\n".join(value).strip()
        for key, value in sections.items()
        if any(part.strip() for part in value)
    }


def _chunk_section(text: str) -> List[str]:
    if not text.strip():
        return []

    return [text.strip()]


def _extract_name(text: str) -> str:
    for line in text.splitlines()[:8]:
        candidate = line.strip()
        if not candidate or any(token in candidate.lower() for token in ["resume", "@", "linkedin", "github", "phone", "summary"]):
            continue
        words = re.findall(r"[A-Za-z]+", candidate)
        if 2 <= len(words) <= 4 and candidate == candidate.title():
            return candidate

    return "Candidate Profile"


def _build_experience(chunk: str, default_title: str) -> Experience:
    lines = [line.strip(" -") for line in chunk.splitlines() if line.strip()]
    headline = lines[0] if lines else default_title
    title = headline[:60]
    company = "Various Organizations"

    if " at " in headline.lower():
        title_part, company_part = re.split(r"\s+at\s+", headline, maxsplit=1, flags=re.IGNORECASE)
        title = title_part.strip() or default_title
        company = company_part.strip() or company
    elif len(lines) > 1 and len(lines[1].split()) <= 6:
        company = lines[1]

    skills = infer_skills(chunk)
    years = estimate_years(chunk)
    summary = _summarize_chunk(chunk, skills)

    return Experience(
        title=title,
        company=company,
        years_of_experience=years,
        semantic_summary=summary,
        skills_used=skills[:6],
    )


def _extract_certifications(cert_chunks: List[str], text: str) -> List[str]:
    certifications = []

    for chunk in cert_chunks:
        first_line = chunk.splitlines()[0].strip(" -")
        if first_line:
            certifications.append(first_line[:80])

    inferred = re.findall(r"\b(?:aws certified|azure fundamentals|coursera|udemy|scrum master|pmp)\b[^\n,.]*", text, flags=re.IGNORECASE)
    certifications.extend(item.strip() for item in inferred)
    return _ordered_unique(certifications)[:5]


def _build_overall_summary(
    name: str,
    global_skills: List[str],
    professional_experience: List[Experience],
    academic_projects: List[Experience],
    certifications: List[str],
) -> str:
    profile = CandidateProfile(
        name=name,
        professional_experience=professional_experience,
        academic_projects=academic_projects,
        certifications=certifications,
        global_skills=global_skills or ["General Engineering"],
        overall_summary="",
    )
    years = profile_total_years(profile)
    skill_blurb = ", ".join((global_skills or ["General Engineering"])[:5])
    project_blurb = f" Includes {len(academic_projects)} academic or side-project highlight(s)." if academic_projects else ""
    cert_blurb = f" Certifications noted: {', '.join(certifications[:2])}." if certifications else ""
    return (
        f"{name} appears to bring roughly {years or 0:.1f} years of relevant experience with strength in {skill_blurb}. "
        f"The profile emphasizes practical delivery, technical intent, and transferable capability across the hiring funnel."
        f"{project_blurb}{cert_blurb}"
    ).strip()


def _summarize_chunk(chunk: str, skills: List[str]) -> str:
    cleaned = re.sub(r"\s+", " ", chunk).strip()
    if len(cleaned) > 220:
        cleaned = cleaned[:217].rstrip() + "..."
    if skills:
        return f"{cleaned} Key strengths include {', '.join(skills[:4])}."
    return cleaned


def _ordered_unique(items: Iterable[str]) -> List[str]:
    seen = set()
    ordered = []
    for item in items:
        normalized = item.strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            ordered.append(normalized)
    return ordered
