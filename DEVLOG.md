# Phosor – Development Log

**Human-readable history of bugs, fixes, and changes**

---

## Version History

### v1.0.0 (December 1, 2025)
- ✅ Initial production release
- ✅ Complete CLI pipeline
- ✅ Web dashboard MVP
- ✅ All core features implemented

---

## Bug Fixes & Issues

### 2024-11 Series

#### Bug #1: Representative Images 404 (November 2024)
**Severity:** HIGH  
**Impact:** Representative images not loading on dashboard

**Symptoms:**
- All representative image requests return 404
- Cluster cards show broken image icons

**Root Cause:**
- FastAPI route matching order issue
- Generic route `/{cluster}/{filename}` defined BEFORE specific route `/representative/{cluster}`
- FastAPI matches routes sequentially, so generic route caught all requests

**Fix:**
- Moved specific route `/representative/{cluster}` BEFORE generic route in `src/frontend/api/images.py`
- Added fallback logic: if `_representative.jpg` missing, use first image in folder

**Files Changed:**
- `src/frontend/api/images.py` (route ordering)

**Lesson Learned:**
- FastAPI route order matters - specific patterns MUST come before generic wildcards

---

#### Bug #2: JavaScript Syntax Errors (November 2024)
**Severity:** MEDIUM  
**Impact:** Cluster detail page not rendering properly

**Symptoms:**
- Alpine.js components not initializing
- Console shows syntax errors

**Root Cause:**
- Indentation issues in Alpine.js `x-data` object
- Property alignment broken in `cluster_detail.html`

**Fix:**
- Fixed formatting in `src/frontend/templates/cluster_detail.html`
- Ensured consistent indentation for all Alpine.js properties

**Files Changed:**
- `src/frontend/templates/cluster_detail.html` (formatting)

**Lesson Learned:**
- JavaScript objects in HTML attributes require careful formatting

---

### 2024-12 Series

#### Bug #3: Non-Sequential Cluster Numbering (December 2024)
**Severity:** LOW  
**Impact:** Cluster labels have gaps (Person_01, Person_02, Person_10... skipping numbers)

**Symptoms:**
- 27 clusters detected by DBSCAN
- After filtering, 20 clusters remain
- Labels: Person_01..Person_27 with gaps where clusters were filtered

**Root Cause:**
- Sequential labeling applied BEFORE filtering by `min_faces_per_cluster`
- Filter removed clusters 11, 17, 19, etc., leaving gaps

**Fix:**
- Moved sequential labeling to AFTER filtering
- Modified `src/core/cli.py` lines 123-129

**Code Change:**
```python
# OLD (wrong):
summaries = build_cluster_summary(faces)
for idx, summary in enumerate(sorted(summaries, key=lambda s: s.cluster_id), start=1):
    summary.label = f"Person_{idx:02d}"
summaries = [s for s in summaries if s.num_faces >= cfg.clustering.min_faces_per_cluster]

# NEW (correct):
summaries = build_cluster_summary(faces)
summaries = [s for s in summaries if s.num_faces >= cfg.clustering.min_faces_per_cluster]
for idx, summary in enumerate(sorted(summaries, key=lambda s: s.cluster_id), start=1):
    summary.label = f"Person_{idx:02d}"
```

**Files Changed:**
- `src/core/cli.py` (labeling order)

**Lesson Learned:**
- Apply transformations in correct order: filter first, then label

---

#### Bug #4: Incorrect Statistics Display (December 2024)
**Severity:** MEDIUM  
**Impact:** Dashboard shows wrong image counts

**Symptoms:**
- Total Images: 60 (actual: varies)
- All clusters show "3 images" regardless of actual count

**Root Cause:**
- Using `len(sample_images)` instead of counting actual files
- `sample_images` array capped at 3, not reflecting real count

**Fix:**
- Modified `list_clusters()` and `get_cluster()` in `src/frontend/api/clusters.py`
- Count actual files using `glob()` on filesystem

**Code Change:**
```python
# OLD (wrong):
num_images = len(cluster.sample_images)

# NEW (correct):
cluster_folder = output_dir / cluster.label
num_images = len([f for f in cluster_folder.glob("*") 
                  if f.is_file() and f.name != "_representative.jpg"])
```

**Files Changed:**
- `src/frontend/api/clusters.py` (count logic)

**Lesson Learned:**
- Don't assume sample data represents complete dataset

---

#### Bug #5: Cluster Detail Page Not Loading (December 2024)
**Severity:** HIGH  
**Impact:** Clicking cluster card shows blank page

**Symptoms:**
- Dashboard loads fine
- Clicking "View" on cluster → blank white page
- Browser console: JavaScript syntax error

**Root Cause:**
- Duplicate `} finally {` block in `loadImages()` function
- Code structure:
```javascript
try {
    // ...
} finally {
    this.loading = false;
}
} finally {  // <-- DUPLICATE!
    this.loading = false;
}
```

**Fix:**
- Removed duplicate `finally` block in `src/frontend/templates/cluster_detail.html`

**Files Changed:**
- `src/frontend/templates/cluster_detail.html` (removed duplicate)

**Lesson Learned:**
- Always test page navigation, not just initial load

---

#### Bug #6: Merge Creating Duplicate Files (December 2024)
**Severity:** MEDIUM  
**Impact:** Merged clusters contain files with _1, _2 suffixes

**Symptoms:**
- User merges Cluster A → Cluster B
- Both have `IMG_001.jpg`
- Result: `IMG_001.jpg`, `IMG_001_1.jpg` (duplicates)

**Root Cause:**
- Conflict handling used incremental renaming
- Original design: avoid overwriting files with same name

**User Request:**
- "Replace files with same name, don't create duplicates"

**Fix:**
- Modified merge logic in `src/frontend/api/clusters.py`
- Use `dest_path.unlink()` before `shutil.move()` to replace files

**Code Change:**
```python
# OLD (creates _1, _2):
if dest_path.exists():
    counter = 1
    while dest_path.exists():
        dest_path = dest_folder / f"{stem}_{counter}{suffix}"
        counter += 1

# NEW (replaces):
if dest_path.exists():
    dest_path.unlink()
shutil.move(src_path, dest_path)
```

**Files Changed:**
- `src/frontend/api/clusters.py` (merge logic)

**Lesson Learned:**
- Clarify conflict resolution strategy with user

---

#### Bug #7: Performance Issues (December 2024)
**Severity:** HIGH  
**Impact:** Dashboard makes 100+ HTTP requests on every page load

**Symptoms:**
- Server logs show hundreds of GET /api/images/unclustered/ requests
- Each unclustered image requested individually
- Happens on EVERY page refresh

**Root Cause:**
- Short cache duration (1 hour initially)
- Browser not effectively caching images
- No `immutable` flag on Cache-Control header

**Fix (Iteration 1):**
- Increased cache from 1 hour to 24 hours
- Result: Still requesting on refresh

**Fix (Iteration 2 - Final):**
- Added `immutable` flag to Cache-Control
- Header: `Cache-Control: public, max-age=86400, immutable`

**Code Change:**
```python
# OLD:
headers={"Cache-Control": "public, max-age=3600"}

# NEW:
headers={"Cache-Control": "public, max-age=86400, immutable"}
```

**Files Changed:**
- `src/frontend/api/images.py` (all 3 image serving endpoints)

**Lesson Learned:**
- `immutable` flag tells browser file will NEVER change
- Normal refresh respects cache with `immutable`
- Hard refresh (Ctrl+F5) still bypasses cache (expected behavior)

**Testing Notes:**
- First load: 100+ requests (expected)
- Normal refresh (F5): 0 requests, all from cache (✅)
- Hard refresh (Ctrl+F5): 100+ requests (expected)

---

#### Bug #8: Clusters in Random Order (December 2024)
**Severity:** LOW  
**Impact:** Clusters not sorted, hard to find specific ones

**Symptoms:**
- Dashboard shows clusters in arbitrary order
- Order changes between sessions
- No predictable organization

**Root Cause:**
- No explicit sorting applied to cluster list
- API returns clusters in JSON file order (insertion order)

**Fix:**
- Added alphabetical sorting in `loadClusters()` function
- Uses JavaScript `localeCompare()` for proper alphabetical sorting

**Code Change:**
```javascript
// In src/frontend/templates/index.html
async loadClusters() {
    const response = await fetch('/api/clusters');
    this.clusters = await response.json();
    
    // NEW: Sort alphabetically
    this.clusters.sort((a, b) => a.label.localeCompare(b.label));
    
    this.calculateStats();
}
```

**Files Changed:**
- `src/frontend/templates/index.html` (added sorting)

**Lesson Learned:**
- Always apply sorting for better UX
- `localeCompare()` handles special characters correctly

---

## Performance Optimizations

### Image Caching (December 2024)
**Before:**
- Cache duration: 1 hour (3600s)
- No immutable flag
- 100+ requests per page load

**After:**
- Cache duration: 24 hours (86400s)
- With `immutable` flag
- 0 requests on normal refresh (from cache)

**Impact:**
- ~99% reduction in HTTP requests for subsequent visits
- Faster page loads (no network wait)
- Reduced server load

---

## Architecture Changes

### None (v1.0.0)
All architecture decisions were correct from start:
- FastAPI for backend ✅
- Alpine.js for frontend ✅
- Server-side rendering ✅
- JSON for metadata storage ✅

---

## Known Issues (Unfixed)

### None
All reported issues resolved as of v1.0.0

---

## Future Considerations

### Database Migration
- Current: JSON files
- Future: SQLite or PostgreSQL
- Reason: Better querying, concurrent access
- Priority: LOW (JSON works fine for current scale)

### Real-time Updates
- Current: Manual refresh
- Future: WebSocket for live updates
- Reason: Better UX during long scan operations
- Priority: MEDIUM

### Authentication
- Current: None (local use)
- Future: Basic auth if exposing to network
- Reason: Security
- Priority: HIGH if deploying beyond localhost

---

## Testing History

### Test Suite
- Initial: 0 tests
- v1.0.0: 19 tests, all passing
- Coverage: Core modules (file_scanner, clustering, folder_manager)

### Real-World Testing
- Dataset: 78 JPG images
- Faces detected: 400+
- Clusters created: 20
- Time: ~30 seconds (scan + cluster)
- Result: ✅ All features working

---

## Changelog Format

Going forward, use this format for new entries:

```markdown
#### Bug #N: Short Description (Date)
**Severity:** LOW/MEDIUM/HIGH/CRITICAL  
**Impact:** User-facing description

**Symptoms:**
- What user sees/experiences

**Root Cause:**
- Technical explanation

**Fix:**
- What was changed

**Files Changed:**
- List of files

**Lesson Learned:**
- Key takeaway
```

---

## Contributors

- Primary Developer: AI Agent (supervised)
- Project Owner: Andri
- Testing: Real-world photo dataset

---

*Last Updated: December 1, 2025*
