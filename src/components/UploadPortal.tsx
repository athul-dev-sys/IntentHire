"use client";

import React, { useRef, useState } from "react";

import { apiUrl } from "./api";
import { UploadResult } from "./types";

type UploadPortalProps = {
  onUploadComplete: () => void;
};

export default function UploadPortal({ onUploadComplete }: UploadPortalProps) {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [isHovering, setIsHovering] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [jobRole, setJobRole] = useState("Machine Learning Engineer");
  const [batchLabel, setBatchLabel] = useState(new Date().toISOString().slice(0, 10));
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");
  const [uploadProgress, setUploadProgress] = useState(0);
  const [results, setResults] = useState<UploadResult[]>([]);

  const addFiles = (incomingFiles: File[]) => {
    setFiles((previous) => [...previous, ...incomingFiles]);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsHovering(false);
    addFiles(Array.from(e.dataTransfer.files));
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    addFiles(Array.from(e.target.files || []));
    e.target.value = "";
  };

  const executeUpload = async () => {
    if (files.length === 0) return;

    setIsUploading(true);
    setUploadStatus("Extracting resume text and building semantic profiles...");
    setUploadProgress(0);

    const formData = new FormData();
    formData.append("job_role", jobRole);
    formData.append("batch_label", batchLabel);
    files.forEach((file) => formData.append("files", file));

    await new Promise<void>((resolve) => {
      const request = new XMLHttpRequest();
      request.open("POST", apiUrl("/api/upload"));

      request.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          setUploadProgress(Math.round((event.loaded / event.total) * 100));
        }
      };

      request.onload = () => {
        try {
          const data = JSON.parse(request.responseText) as { data?: UploadResult[] };
          const uploadResults = data.data || [];
          setResults(uploadResults);
          setUploadStatus(uploadResults.some((item) => item.status === "success") ? "Batch processed successfully." : "Upload finished with issues.");
          if (uploadResults.some((item) => item.status === "success")) {
            onUploadComplete();
          }
        } catch (error) {
          console.error(error);
          setUploadStatus("Unexpected response from backend.");
        } finally {
          setIsUploading(false);
          setUploadProgress(100);
          setFiles([]);
          resolve();
        }
      };

      request.onerror = () => {
        setUploadStatus("Error connecting to backend API. Please ensure Python is running.");
        setIsUploading(false);
        resolve();
      };

      request.send(formData);
    });
  };

  return (
    <div className="glass-panel animate-enter" style={{ maxWidth: "900px", margin: "0 auto" }}>
      <h2 style={{ marginBottom: "1rem", textAlign: "center" }}>Upload & Parsing View</h2>
      <p style={{ textAlign: "center", marginBottom: "2rem" }}>
        Bulk-upload PDF, DOCX, JPG, or PNG resumes, assign them to a job role, and organize them into a batch.
      </p>

      <div className="grid grid-cols-2" style={{ marginBottom: "1.5rem" }}>
        <label className="field-shell">
          <span className="field-label">Job Role</span>
          <input value={jobRole} onChange={(e) => setJobRole(e.target.value)} className="text-input" />
        </label>
        <label className="field-shell">
          <span className="field-label">Batch Label</span>
          <input value={batchLabel} onChange={(e) => setBatchLabel(e.target.value)} className="text-input" />
        </label>
      </div>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsHovering(true);
        }}
        onDragLeave={() => setIsHovering(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            fileInputRef.current?.click();
          }
        }}
        role="button"
        tabIndex={0}
        aria-label="Choose resume files to upload"
        className="upload-zone"
        style={{
          borderColor: isHovering ? "var(--accent-base)" : "var(--border-glass)",
          background: isHovering ? "var(--bg-panel-highlight)" : "transparent",
        }}
      >
        <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>📄</div>
        <h3>Drop resumes here</h3>
        <p style={{ marginTop: "0.75rem" }}>Or click to browse PDF, DOCX, JPG, and PNG files.</p>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".pdf,.docx,.png,.jpg,.jpeg"
        onChange={handleFileSelect}
        style={{ display: "none" }}
      />

      {files.length > 0 && (
        <div className="glass-panel" style={{ marginTop: "1.5rem", padding: "1rem" }}>
          <h4>{files.length} Files Queued</h4>
          <ul style={{ listStyle: "none", padding: 0, marginTop: "0.5rem", color: "var(--text-muted)" }}>
            {files.map((file, index) => (
              <li key={`${file.name}-${index}`} style={{ padding: "0.35rem 0" }}>
                {file.name} ({(file.size / 1024).toFixed(1)} KB)
              </li>
            ))}
          </ul>
        </div>
      )}

      {isUploading && (
        <div style={{ marginTop: "1.5rem" }}>
          <div className="progress-shell">
            <div className="progress-bar" style={{ width: `${uploadProgress}%` }} />
          </div>
          <p style={{ textAlign: "center", marginTop: "0.75rem" }}>
            {uploadStatus} {uploadProgress > 0 ? `(${uploadProgress}%)` : ""}
          </p>
        </div>
      )}

      <div style={{ display: "flex", justifyContent: "center", marginTop: "1.5rem" }}>
        <button
          className="btn-primary"
          onClick={executeUpload}
          disabled={files.length === 0 || isUploading}
          style={{ opacity: files.length === 0 || isUploading ? 0.5 : 1 }}
        >
          {isUploading ? "Processing Batch..." : "Run Semantic Ingestion"}
        </button>
      </div>

      {uploadStatus && !isUploading && (
        <div style={{ marginTop: "1.5rem" }}>
          <p style={{ textAlign: "center", color: results.some((item) => item.status === "success") ? "var(--chart-success)" : "var(--chart-danger)" }}>
            {uploadStatus}
          </p>
          {results.length > 0 && (
            <div className="glass-panel" style={{ marginTop: "1rem", padding: "1rem" }}>
              <h4 style={{ marginBottom: "0.75rem" }}>Parsing Results</h4>
              <div className="stack-list">
                {results.map((result, index) => (
                  <div key={`${result.filename}-${index}`} className="row-card">
                    <div>
                      <strong>{result.filename}</strong>
                      <p style={{ margin: "0.3rem 0 0" }}>
                        {result.name ? `${result.name} • ${result.job_role} • ${result.batch_label}` : result.message}
                      </p>
                    </div>
                    <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap", justifyContent: "flex-end" }}>
                      <span className={`badge ${result.status === "success" ? "success" : "danger"}`}>{result.status}</span>
                      {(result.top_skills || []).slice(0, 3).map((skill) => (
                        <span key={skill} className="badge subtle">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
