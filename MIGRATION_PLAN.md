# Migration Plan: SamSurve/contribution-universe

## Overview
The goal is to seamlessly transition the existing `SamSurve/contribution-universe` repository from a Vercel-backed Node.js project into the new, robust Python + GitHub Actions automated generator completed in Phases 1–5, while preserving essential legacy assets.

## Comparison Analysis
- **Current Repo (`SamSurve/contribution-universe`)**: Uses a Node.js backend (`package.json`, `test.js`), relies on Vercel Serverless functions (`api/`, `vercel.json`), and outputs a `universe.svg` at the root.
- **New Repo (`E:\github-sakura-contributions`)**: Uses a standalone Python engine (`src/`, `requirements.txt`, `tests/`), relies securely on GitHub Actions (`.github/workflows/generate-sakura.yml`), and outputs to `assets/sakura-contributions.svg`.
- **Verdict**: The new 5-phase Python implementation is significantly more robust, natively automated (doesn't require a 3rd party Vercel hook), and strictly tested. We will pivot the repo to the Python architecture.

## Strategy

### 1. Files to Keep
- `universe.svg`: Must be preserved at the repository root. This guarantees backward compatibility so that any external GitHub READMEs currently linking to `https://raw.../universe.svg` do not unexpectedly break during the migration.
- `.github/`: The existing directory will be kept, but updated with the new workflow.

### 2. Files to Replace
- `README.md`: The existing README is very brief. We will replace it with the comprehensive `README.md` generated during Phase 4, but we will selectively **merge** the original repository title ("Contribution Universe") and introductory sentence to respect the repository's identity.

### 3. Files to Remove
Since the new architecture operates entirely via GitHub Actions and Python, the legacy Node/Vercel stack is obsolete and introduces unnecessary technical debt/security overhead. We will safely delete:
- `api/` (Vercel serverless endpoints)
- `vercel.json` (Vercel deployment config)
- `package.json` (Node.js dependencies)
- `test.js` (Legacy Node.js tests)
- `src/` (Any legacy Javascript source code inside will be overwritten by the new Python `src/`)

### 4. Files to Add (from the new Python project)
- `src/` (Python engine: `artwork.py`, `github_api.py`, `main.py`, `svg_builder.py`, `theme.py`)
- `tests/` (`test_parser.py`, `test_renderer.py`)
- `.github/workflows/generate-sakura.yml`
- `requirements.txt`
- `assets/sakura-contributions.svg`
- `PHASE_X_REPORT.md` (Archival reports from the 5-phase build)

## Final Expected Repository Structure
```text
SamSurve/contribution-universe
├── .github/
│   └── workflows/
│       └── generate-sakura.yml     (New automated GitHub Action)
├── assets/
│   └── sakura-contributions.svg    (New, beautiful output target)
├── src/
│   ├── __init__.py
│   ├── artwork.py
│   ├── github_api.py
│   ├── main.py
│   ├── svg_builder.py
│   └── theme.py
├── tests/
│   ├── test_parser.py
│   └── test_renderer.py
├── PHASE_2_REPORT.md               (Historical context)
├── PHASE_3_REPORT.md
├── PHASE_4_REPORT.md
├── PHASE_5_REPORT.md
├── README.md                       (Merged documentation)
├── requirements.txt                (Python dependencies)
└── universe.svg                    (Legacy asset kept for backward-compatibility)
```
