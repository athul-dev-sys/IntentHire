import React, { useEffect, useState } from "react";

import { apiUrl } from "./api";
import { CandidateSummary, RankedCandidate } from "./types";

type RankingViewProps = {
  refreshKey: number;
};

type DisplayCandidate = CandidateSummary & {
  score?: number;
  justification?: string;
};

export default function RankingView({ refreshKey }: RankingViewProps) {
  const [jdText, setJdText] = useState("");
  const [minYears, setMinYears] = useState("");
  const [skillFilter, setSkillFilter] = useState("");
  const [isRanking, setIsRanking] = useState(false);
  const [candidates, setCandidates] = useState<CandidateSummary[]>([]);
  const [rankedCandidates, setRankedCandidates] = useState<RankedCandidate[]>([]);

  useEffect(() => {
    let cancelled = false;

    const loadCandidates = async () => {
      try {
        const response = await fetch(apiUrl("/api/candidates"));
        const data = (await response.json()) as { candidates: CandidateSummary[] };
        if (!cancelled) {
          setCandidates(data.candidates || []);
          setRankedCandidates([]);
        }
      } catch (error) {
        console.error(error);
        if (!cancelled) {
          setCandidates([]);
        }
      }
    };

    loadCandidates();
    return () => {
      cancelled = true;
    };
  }, [refreshKey]);

  const handleRank = async () => {
    if (!jdText.trim()) return;
    setIsRanking(true);

    try {
      const response = await fetch(apiUrl("/api/rank"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jd_text: jdText, top_k: 20 }),
      });
      const data = (await response.json()) as { candidates?: RankedCandidate[] };
      setRankedCandidates(data.candidates || []);
    } catch (error) {
      console.error(error);
    } finally {
      setIsRanking(false);
    }
  };

  const sourceRows: DisplayCandidate[] = rankedCandidates.length > 0 ? rankedCandidates : candidates;
  const filteredRows = sourceRows.filter((candidate) => {
    const meetsYears = !minYears || candidate.years_of_experience >= Number(minYears);
    const matchesSkill = !skillFilter || candidate.top_skills.some((skill) => skill.toLowerCase().includes(skillFilter.toLowerCase()));
    return meetsYears && matchesSkill;
  });

  return (
    <div className="animate-enter">
      <div className="flex-between section-heading">
        <div>
          <h2>JD-to-Candidate Ranking Dashboard</h2>
          <p>Rank the uploaded pool and filter by years of experience or specific skill focus.</p>
        </div>
      </div>

      <div className="glass-panel" style={{ marginBottom: "2rem" }}>
        <textarea
          placeholder="Paste the job description here..."
          value={jdText}
          onChange={(e) => setJdText(e.target.value)}
          className="textarea-input"
        />
        <div className="grid grid-cols-3" style={{ marginTop: "1rem" }}>
          <label className="field-shell">
            <span className="field-label">Minimum Years</span>
            <input value={minYears} onChange={(e) => setMinYears(e.target.value)} className="text-input" placeholder="e.g. 3" />
          </label>
          <label className="field-shell">
            <span className="field-label">Top Skill Filter</span>
            <input value={skillFilter} onChange={(e) => setSkillFilter(e.target.value)} className="text-input" placeholder="React, Python, AWS..." />
          </label>
          <div style={{ display: "flex", alignItems: "flex-end" }}>
            <button className="btn-primary" onClick={handleRank} disabled={!jdText.trim() || isRanking}>
              {isRanking ? "Ranking..." : "Run Semantic Match"}
            </button>
          </div>
        </div>
      </div>

      <div className="glass-panel">
        <div className="flex-between" style={{ marginBottom: "1rem" }}>
          <h3>Candidate Table</h3>
          <p style={{ margin: 0 }}>{filteredRows.length} visible candidate(s)</p>
        </div>

        {filteredRows.length === 0 ? (
          <p>No candidates match the current filters yet.</p>
        ) : (
          <div className="table-shell">
            <table className="ranking-table">
              <thead>
                <tr>
                  <th>Candidate</th>
                  <th>Role / Batch</th>
                  <th>Years</th>
                  <th>Top Skills</th>
                  <th>Score</th>
                  <th>AI Justification</th>
                </tr>
              </thead>
              <tbody>
                {filteredRows.map((candidate) => (
                  <tr key={candidate.id}>
                    <td>
                      <strong>{candidate.name}</strong>
                      <p style={{ margin: "0.35rem 0 0" }}>{candidate.source_filename || "Uploaded resume"}</p>
                    </td>
                    <td>
                      <strong>{candidate.job_role}</strong>
                      <p style={{ margin: "0.35rem 0 0" }}>{candidate.batch_label}</p>
                    </td>
                    <td>{candidate.years_of_experience.toFixed(1)}</td>
                    <td>
                      <div style={{ display: "flex", gap: "0.35rem", flexWrap: "wrap" }}>
                        {candidate.top_skills.map((skill) => (
                          <span key={`${candidate.id}-${skill}`} className="badge subtle">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td>
                      {typeof candidate.score === "number" ? (
                        <span className={`badge ${candidate.score >= 75 ? "success" : candidate.score >= 50 ? "warn" : "danger"}`}>
                          {candidate.score}%
                        </span>
                      ) : (
                        <span className="badge subtle">Not ranked</span>
                      )}
                    </td>
                    <td>
                      <p style={{ margin: 0 }}>
                        {candidate.justification || candidate.overall_summary}
                      </p>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
