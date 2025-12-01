# Phosor – AI Agent Work Instructions

**IMPORTANT:** This file is for AI agents working on NEW features only.  
All sections below are **COMPLETED** ✅. Do not repeat them.

---

## 0. Global Rules for AI Agent

1. **Language & Stack**
   - Python 3.10+
   - Use existing dependencies (see `pyproject.toml`)

2. **Code Quality**
   - Use type hints
   - Small, single-responsibility functions
   - Minimal but clear docstrings

3. **Commit Style**
   - Logical commits: `feat: add X`, `fix: resolve Y`, `refactor: improve Z`

4. **Do Not Over-Engineer**
   - MVP first, advanced features later
   - Focus on working features over perfect architecture

5. **File Scope Restrictions**
   - **FROZEN:** Do NOT modify `src/core/*` unless explicitly instructed
   - **FROZEN:** Do NOT modify API endpoints in `src/frontend/api/*` unless explicitly instructed
   - **ALLOWED:** Templates in `src/frontend/templates/*` for UI improvements
   - **ALLOWED:** New features in separate modules

---

## 1-10. Core CLI Pipeline ✅ COMPLETED

All core features implemented:
- ✅ Project bootstrap
- ✅ Configuration handling
- ✅ File scanning
- ✅ Face detection (UniFace)
- ✅ Embedding generation
- ✅ DBSCAN clustering
- ✅ Output folder creation
- ✅ Representative images
- ✅ CLI commands (scan, summary, serve)
- ✅ Test suite (19/19 passing)

**Status:** Production-ready. Do not modify without explicit instruction.

---

## 11. Web Dashboard ✅ COMPLETED

All MVP features implemented:
- ✅ FastAPI backend setup
- ✅ 13 API endpoints (clusters + images + unclustered)
- ✅ Dashboard UI (Alpine.js + Tailwind CSS)
- ✅ Cluster detail page with lightbox
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ Merge clusters
- ✅ Move/copy unclustered images
- ✅ Search functionality
- ✅ Performance optimization (24h cache)
- ✅ Alphabetical sorting

**Status:** Production-ready. Do not modify without explicit instruction.

---

## 12. Future Work (NOT STARTED)

The following features are **NOT IMPLEMENTED** and are available for new work:

### 12.1 Incremental Updates
- **Goal:** Reuse embeddings for unchanged images
- **Approach:** Store image hashes, compare with previous scan
- **Files to create:** `src/core/incremental.py`
- **DO NOT modify:** Existing `src/core/*` files

### 12.2 Database Integration
- **Goal:** Replace JSON with SQLite for better querying
- **Approach:** 
  - Create `src/core/database.py`
  - Migrate data models to SQLAlchemy
  - Keep JSON export for backwards compatibility
- **DO NOT modify:** Existing API endpoints until migration complete

### 12.3 WebSocket Real-time Updates
- **Goal:** Show scan progress live in dashboard
- **Approach:**
  - Add `websockets` dependency
  - Create `/ws/scan-progress` endpoint
  - Add progress subscriber in `src/core/cli.py`
- **Files to create:** `src/frontend/api/websocket.py`

### 12.4 Face Search
- **Goal:** Upload photo, find all matching faces
- **Approach:**
  - Add `/api/search` endpoint
  - Use existing embeddings for comparison
  - Cosine similarity threshold
- **Files to create:** `src/frontend/api/search.py`

### 12.5 Cluster Quality Metrics
- **Goal:** Show confidence score per cluster
- **Approach:**
  - Calculate intra-cluster embedding distance
  - Add `quality_score` field to ClusterSummary
  - Display in UI with color coding
- **Files to modify:** `src/core/clustering.py` (add score calculation)

### 12.6 Export Functions
- **Goal:** Download cluster as ZIP, export to CSV
- **Approach:**
  - Add `/api/clusters/{id}/export` endpoint
  - Use `zipfile` module for ZIP creation
  - CSV with pandas for metadata
- **Files to create:** `src/frontend/api/export.py`

---

## Session Scope Guidelines

### If working on UI improvements:
**ALLOWED:**
- `src/frontend/templates/*.html`
- `src/frontend/static/*` (if adding CSS/JS)

**FORBIDDEN:**
- `src/frontend/api/*.py` (API changes require explicit approval)
- `src/core/*.py` (core logic frozen)

### If working on new features (12.1-12.6):
**ALLOWED:**
- Create new files in appropriate directories
- Add new API endpoints (with approval)
- Add new CLI commands (with approval)

**FORBIDDEN:**
- Modifying existing endpoints without explicit instruction
- Changing core clustering logic
- Breaking backwards compatibility

### If working on bug fixes:
**ALLOWED:**
- Minimal changes to fix specific bug
- Add tests for regression

**REQUIRED:**
- Document bug in `DEVLOG.md` before fixing
- Get confirmation of root cause before implementing fix

---

## How to Use This File

1. **Agent starts session:** Read this file first
2. **Check scope:** Identify which section (12.1-12.6) you're working on
3. **Follow restrictions:** Respect ALLOWED/FORBIDDEN file lists
4. **Update progress:** Mark tasks as complete with ✅
5. **Document bugs:** Any issues go to `DEVLOG.md`, not here

---

## Current Status Summary

**Phase 1-11:** ✅ COMPLETED (CLI + Web Dashboard MVP)  
**Phase 12+:** 📋 NOT STARTED (Future enhancements)

**Active Development:** None (all MVP features complete)  
**Next Recommended Task:** Section 12.1 (Incremental Updates) or 12.4 (Face Search)

---

## Version Control

- Current version: 1.0.0
- Last major update: December 1, 2025
- Next version target: 1.1.0 (when any Phase 12 feature completes)
