"use client";

import { useState } from "react";

import Dashboard from "../components/Dashboard";
import RankingView from "../components/RankingView";
import UploadPortal from "../components/UploadPortal";

type TabState = "dashboard" | "upload" | "ranking";

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabState>("dashboard");
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <div>
      <nav className="tabs">
        <button
          className={`tab ${activeTab === "dashboard" ? "active" : ""}`}
          onClick={() => setActiveTab("dashboard")}
        >
          Recruiter Dashboard
        </button>
        <button
          className={`tab ${activeTab === "upload" ? "active" : ""}`}
          onClick={() => setActiveTab("upload")}
        >
          Upload & Parsing
        </button>
        <button
          className={`tab ${activeTab === "ranking" ? "active" : ""}`}
          onClick={() => setActiveTab("ranking")}
        >
          Ranking View
        </button>
      </nav>

      <section>
        {activeTab === "dashboard" && <Dashboard refreshKey={refreshKey} />}
        {activeTab === "upload" && (
          <UploadPortal
            onUploadComplete={() => {
              setRefreshKey((current) => current + 1);
              setActiveTab("dashboard");
            }}
          />
        )}
        {activeTab === "ranking" && <RankingView refreshKey={refreshKey} />}
      </section>
    </div>
  );
}
