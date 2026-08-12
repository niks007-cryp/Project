# VERCEL PREVIEW 404 — DIAGNOSTIC & REPAIR WALKTHROUGH

## 1. Original Error
- **Error**: `404: NOT_FOUND` (`Code: NOT_FOUND`, ID `bom1::j7ctl-1786514114840-6ef1e02eeabb`)
- **Symptom**: Accessing the root Vercel deployment URL resulted in a Vercel routing 404 page.

---

## 2. Deployment Architecture & Root Cause Analysis

### Architecture Identity
- **Framework**: Client-side Single Page Application (SPA) built with Vanilla HTML5/CSS/JavaScript served via Python HTTP API server in local mode (`src/clipper/web/static/index.html`).
- **Repository Structure**: Mono-repo structure under `https://github.com/niks007-cryp/Project.git` where `local-ai-clipper` lives in subfolder `/local-ai-clipper`.

### Root Cause
Vercel was attempting to build and serve files from the root of the repository without an explicit static output directory or route rewrites. Because `index.html` was located at `src/clipper/web/static/index.html` rather than the repository root `/`, Vercel looked for `/index.html` at the top level and returned `404: NOT_FOUND`.

---

## 3. Minimal Fix Applied

Created and committed `vercel.json` with explicit `outputDirectory` and SPA `rewrites`:

```json
{
  "version": 2,
  "outputDirectory": "src/clipper/web/static",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

- Created `N:\local-ai-clipper\vercel.json`
- Created `N:\_temp_project\vercel.json` (root level mapping: `local-ai-clipper/src/clipper/web/static`)
- Created `N:\_temp_project\local-ai-clipper\vercel.json`

---

## 4. Verification & Testing

- **Secret Audit**: `scan_secrets.py` executed on 212 files: 0 secrets detected.
- **Pytest Suite**: 97/97 tests passed cleanly (51.86s).
- **Git Push**: Commit `33f04b4` (`fix(vercel): add routing configuration vercel.json to resolve 404`) pushed to `https://github.com/niks007-cryp/Project.git` on `main`.

---

## 5. Deployment & Vercel Dashboard Settings

To ensure Vercel builds the SPA entry point correctly:
1. **Root Directory in Vercel Settings**: `local-ai-clipper`
2. **Framework Preset**: `Other` (Static)
3. **Build Command**: Leave blank (no build step needed for pure HTML/CSS/JS)
4. **Output Directory**: `src/clipper/web/static`

---

## 6. Files Created / Modified

- **Created**:
  - `N:\local-ai-clipper\vercel.json`
  - `N:\local-ai-clipper\VERCEL_404_DIAGNOSTIC_WALKTHROUGH.md`
- **Pushed to GitHub (`niks007-cryp/Project`)**: Commit `33f04b4`
