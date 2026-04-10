from datetime import datetime
from sqlalchemy import Column, String, Text
from app.db.session import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())


def utc_now_iso():
    return datetime.utcnow().isoformat()

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    name = Column(String, index=True)
    overall_summary = Column(Text)
    source_filename = Column(String, nullable=True)
    job_role = Column(String, nullable=True, index=True)
    batch_label = Column(String, nullable=True, index=True)
    created_at = Column(String, default=utc_now_iso, index=True)

    # Store complete JSON directly in relational DB for display purposes, 
    # relying on Pinecone vectors for actual semantic search
    raw_profile_json = Column(Text) 
