# intenthire - Approach Document

## Problem Statement

Recruiters handling volume hiring need faster ways to screen resumes, map candidate skills to job requirements, and prioritize the best-fit applicants without manual review bottlenecks.

## Solution Overview

`intenthire` provides an AI-assisted hiring workflow:

- Resume ingestion and parsing
- Structured candidate profile extraction
- Ranking/scoring candidates against job intent
- Dashboard and ranking views for recruiter decisions

The application is designed for end-to-end usability so evaluators can see core AI capability in action, not just isolated model outputs.

## Architecture and Tech Stack Choices

### Frontend

- **Next.js + React + TypeScript**
  - Chosen for fast UI development, routing, and strong type safety.
  - Supports modular components for dashboard, upload, and ranking flows.

### Backend and AI Layer

- **Python-based services**
  - Chosen for strong AI/ML ecosystem and easy integration with parsing/NLP pipelines.
  - Suitable for resume text processing and score generation.

### Why this stack

- Rapid development during a 2-week sprint
- Clear separation between UX and AI processing
- Easy to extend with more ranking logic and model improvements

## Key Design Decisions

- Built around recruiter workflows (dashboard first, then upload and ranking)
- Prioritized practical output: parsed data + ranking visibility
- Kept architecture modular to support future feature additions

## What Worked Well

- Fast iteration on user interface
- End-to-end pipeline demonstration with core AI functionality
- Clear flow from input (resumes) to actionable output (ranked candidates)

## Improvements with More Time

- Better explainability for candidate scores (feature-level breakdown)
- Advanced filtering and search for recruiters
- Stronger evaluation metrics and benchmark datasets
- Authentication/role-based access
- Deployment hardening, CI checks, and monitoring
- Automated tests across frontend and backend

## Conclusion

`intenthire` delivers a functional AI hiring assistant prototype that demonstrates meaningful recruiter value within sprint timelines, with a clear roadmap for production readiness.
