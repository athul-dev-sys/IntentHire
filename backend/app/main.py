from collections import Counter
from datetime import datetime
import json
from typing import List, Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.db.session import Base, engine, get_db
from app.models.orm import Candidate
from app.models.schema import CandidateProfile
from app.services.extractor import extract_semantic_profile, profile_total_years, top_profile_skills
from app.services.parser import extract_text_from_file
from app.services.ranker import calculate_compatibility


class RankRequest(BaseModel):
    jd_text: str
    top_k: int = 20


Base.metadata.create_all(bind=engine)
_ensure_candidate_columns = {
    "source_filename": "TEXT",
    "job_role": "TEXT",
    "batch_label": "TEXT",
    "created_at": "TEXT",
}
inspector = inspect(engine)
if "candidates" in inspector.get_table_names():
    existing_columns = {column["name"] for column in inspector.get_columns("candidates")}
    with engine.begin() as connection:
        for column_name, column_type in _ensure_candidate_columns.items():
            if column_name not in existing_columns:
                connection.execute(text(f"ALTER TABLE candidates ADD COLUMN {column_name} {column_type}"))


app = FastAPI(title="intenthire API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to intenthire API"}


@app.get("/api/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    candidates = db.query(Candidate).order_by(Candidate.created_at.desc()).all()
    summaries = [_candidate_to_summary(candidate) for candidate in candidates]

    role_counts = Counter(item["job_role"] or "Unassigned" for item in summaries)
    batch_counts = Counter(item["batch_label"] or "Unlabeled Batch" for item in summaries)
    today = datetime.utcnow().date().isoformat()
    top_talent = max(
        summaries,
        key=lambda item: (item["years_of_experience"], len(item["top_skills"])),
        default=None,
    )

    return {
        "active_roles": len(role_counts),
        "total_resumes": len(summaries),
        "recent_uploads": sum(1 for item in summaries if item["created_at"].startswith(today)),
        "pending_reviews": len([item for item in summaries if item["years_of_experience"] < 2]),
        "role_breakdown": [{"role": role, "count": count} for role, count in role_counts.most_common(6)],
        "batch_breakdown": [{"label": label, "count": count} for label, count in batch_counts.most_common(6)],
        "top_talent": top_talent,
    }


@app.get("/api/candidates")
def list_candidates(db: Session = Depends(get_db)):
    candidates = db.query(Candidate).order_by(Candidate.created_at.desc()).all()
    return {"candidates": [_candidate_to_summary(candidate) for candidate in candidates]}


@app.post("/api/upload")
async def upload_resumes(
    files: List[UploadFile] = File(...),
    job_role: str = Form("General Hiring"),
    batch_label: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    results = []
    batch_value = batch_label or datetime.utcnow().date().isoformat()

    for file in files:
        content = await file.read()
        raw_text = extract_text_from_file(content, file.content_type or "")

        if not raw_text:
            results.append({"filename": file.filename, "status": "failed", "message": "Unsupported or unreadable layout."})
            continue

        try:
            profile = extract_semantic_profile(raw_text)
            new_candidate = Candidate(
                name=profile.name,
                overall_summary=profile.overall_summary,
                raw_profile_json=profile.model_dump_json(),
                source_filename=file.filename,
                job_role=job_role,
                batch_label=batch_value,
                created_at=datetime.utcnow().isoformat(),
            )
            db.add(new_candidate)
            db.commit()
            db.refresh(new_candidate)

            results.append({
                "filename": file.filename,
                "status": "success",
                "db_id": new_candidate.id,
                "name": profile.name,
                "job_role": job_role,
                "batch_label": batch_value,
                "top_skills": profile.global_skills[:5],
            })
        except Exception as exc:
            db.rollback()
            results.append({"filename": file.filename, "status": "failed", "message": str(exc)})

    return {"data": results}


@app.post("/api/rank")
async def rank_candidates(req: RankRequest, db: Session = Depends(get_db)):
    if not req.jd_text.strip():
        raise HTTPException(status_code=400, detail="Job Description text required.")

    candidates = db.query(Candidate).all()
    ranked = calculate_compatibility(req.jd_text, candidates=candidates, top_k=req.top_k)
    return {"candidates": ranked}


def _candidate_to_summary(candidate: Candidate):
    profile = CandidateProfile.model_validate(json.loads(candidate.raw_profile_json))
    return {
        "id": candidate.id,
        "name": candidate.name,
        "overall_summary": candidate.overall_summary,
        "years_of_experience": profile_total_years(profile),
        "top_skills": top_profile_skills(profile, 5),
        "job_role": candidate.job_role or "Unassigned",
        "batch_label": candidate.batch_label or "Unlabeled Batch",
        "source_filename": candidate.source_filename,
        "created_at": candidate.created_at or "",
    }


if __name__ == "__main__":
    import dotenv
    import uvicorn

    dotenv.load_dotenv()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
