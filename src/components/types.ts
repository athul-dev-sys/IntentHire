export type UploadResult = {
  filename: string;
  status: string;
  message?: string;
  db_id?: string;
  name?: string;
  job_role?: string;
  batch_label?: string;
  top_skills?: string[];
};

export type CandidateSummary = {
  id: string;
  name: string;
  overall_summary: string;
  years_of_experience: number;
  top_skills: string[];
  job_role: string;
  batch_label: string;
  source_filename?: string;
  created_at: string;
};

export type RankedCandidate = CandidateSummary & {
  score: number;
  justification: string;
};

export type DashboardData = {
  active_roles: number;
  total_resumes: number;
  recent_uploads: number;
  pending_reviews: number;
  role_breakdown: Array<{ role: string; count: number }>;
  batch_breakdown: Array<{ label: string; count: number }>;
  top_talent: CandidateSummary | null;
};
