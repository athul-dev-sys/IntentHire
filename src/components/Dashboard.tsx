"use client";

import React, { useEffect, useState } from "react";

import { apiUrl } from "./api";
import { DashboardData } from "./types";

type DashboardProps = {
  refreshKey: number;
};

const emptyDashboard: DashboardData = {
  active_roles: 0,
  total_resumes: 0,
  recent_uploads: 0,
  pending_reviews: 0,
  role_breakdown: [],
  batch_breakdown: [],
  top_talent: null,
};

export default function Dashboard({ refreshKey }: DashboardProps) {
  const [dashboard, setDashboard] = useState<DashboardData>(emptyDashboard);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const loadDashboard = async () => {
      setIsLoading(true);
      try {
        const response = await fetch(apiUrl("/api/dashboard"));
        const data = (await response.json()) as DashboardData;
        if (!cancelled) {
          setDashboard(data);
        }
      } catch (error) {
        console.error(error);
        if (!cancelled) {
          setDashboard(emptyDashboard);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    loadDashboard();
    return () => {
      cancelled = true;
    };
  }, [refreshKey]);

  return (
    <div className="animate-enter">
      <div className="flex-between section-heading">
        <div>
          <h2>Recruiter Dashboard</h2>
          <p>Track active hiring lanes, upload volume, and the strongest talent in the pool.</p>
        </div>
      </div>

      <div className="grid grid-cols-4" style={{ marginBottom: "2rem" }}>
        <MetricCard label="Active Job Roles" value={String(dashboard.active_roles)} accent="var(--accent-base)" />
        <MetricCard label="Resumes Uploaded" value={String(dashboard.total_resumes)} accent="var(--chart-success)" />
        <MetricCard label="Uploaded Today" value={String(dashboard.recent_uploads)} accent="var(--chart-warn)" />
        <MetricCard label="Needs Review" value={String(dashboard.pending_reviews)} accent="var(--chart-danger)" />
      </div>

      <div className="grid grid-cols-2">
        <div className="glass-panel">
          <h3 style={{ marginBottom: "1rem" }}>Job Role Coverage</h3>
          {dashboard.role_breakdown.length === 0 ? (
            <p>{isLoading ? "Loading dashboard..." : "No uploaded resumes yet."}</p>
          ) : (
            <div className="stack-list">
              {dashboard.role_breakdown.map((item) => (
                <div key={item.role} className="row-card">
                  <div>
                    <strong>{item.role}</strong>
                    <p style={{ margin: "0.25rem 0 0" }}>Candidate pool for this role</p>
                  </div>
                  <span className="badge">{item.count}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="glass-panel">
          <h3 style={{ marginBottom: "1rem" }}>Batch Organization</h3>
          {dashboard.batch_breakdown.length === 0 ? (
            <p>{isLoading ? "Loading dashboard..." : "Create a batch by uploading resumes."}</p>
          ) : (
            <div className="stack-list">
              {dashboard.batch_breakdown.map((item) => (
                <div key={item.label} className="row-card">
                  <div>
                    <strong>{item.label}</strong>
                    <p style={{ margin: "0.25rem 0 0" }}>Upload batch grouping</p>
                  </div>
                  <span className="badge">{item.count}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="glass-panel" style={{ marginTop: "2rem" }}>
        <h3 style={{ marginBottom: "1rem" }}>Top Talent Preview</h3>
        {dashboard.top_talent ? (
          <div>
            <div className="flex-between" style={{ gap: "1rem", marginBottom: "1rem" }}>
              <div>
                <p style={{ margin: 0, color: "var(--text-main)", fontSize: "1.2rem", fontWeight: 600 }}>
                  {dashboard.top_talent.name}
                </p>
                <p style={{ margin: "0.35rem 0 0" }}>
                  {dashboard.top_talent.job_role} • {dashboard.top_talent.years_of_experience.toFixed(1)} years
                </p>
              </div>
              <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", justifyContent: "flex-end" }}>
                {dashboard.top_talent.top_skills.map((skill) => (
                  <span key={skill} className="badge subtle">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
            <div className="insight-card">
              <em>{dashboard.top_talent.overall_summary}</em>
            </div>
          </div>
        ) : (
          <p>Upload a batch to generate the first talent preview.</p>
        )}
      </div>
    </div>
  );
}

function MetricCard({ label, value, accent }: { label: string; value: string; accent: string }) {
  return (
    <div className="glass-panel">
      <p>{label}</p>
      <h3 style={{ fontSize: "2rem", color: accent, marginTop: "0.5rem" }}>{value}</h3>
    </div>
  );
}
