# Phase 4 Report: GitHub Integration & Automation

## Workflow Architecture
The core automation relies on a GitHub Actions workflow located in `.github/workflows/generate-sakura.yml`. This workflow serves as a deterministic pipeline tying together the Phase 2 data engine and the Phase 3 visual renderer.
- **Trigger Events**: The workflow runs on a strict schedule using cron `0 0 * * *` (Midnight UTC daily) and supports manual triggering via `workflow_dispatch`.
- **Environment Context**: It utilizes an `ubuntu-latest` runner and leverages the `actions/setup-python@v5` action to provision a fresh Python 3.12 environment with pip caching.
- **Generation Pipeline**: Dependencies are installed from `requirements.txt`, and the engine is executed as a module (`python -m src.main`).

## Authentication & Token Strategy
The system absolutely refuses to hardcode credentials.
- **Secret Management**: The workflow securely passes the built-in GitHub Actions `GITHUB_TOKEN` to the `src.main` process via the `env:` block.
- **Zero Configuration**: Users do not have to create manual Personal Access Tokens (PATs) for the action to work, as the built-in token has sufficient read access to public user contribution data natively.

## Permissions
The workflow operates under the principle of least privilege:
- Only the `contents: write` permission is explicitly requested. This grants exactly the permissions needed to check out the repository, generate the asset, and commit/push the SVG back to the repo without bleeding excessive administrative rights to the runner.

## README Integration
The repository `README.md` was significantly updated.
- It clearly defines the project and visually displays the output image.
- A **SamSurve Profile Integration** section was added. This provides copy-paste ready HTML/Markdown utilizing the `<picture>` tag. It references the raw file cleanly: `https://raw.githubusercontent.com/SamSurve/contribution-universe/main/assets/sakura-contributions.svg`, guaranteeing flawless display directly on your personal GitHub profile README.

## Testing & Validation
- **Engine Failure Fallback**: The `src/main.py` entrypoint wraps the GitHub API fetch in a `try...except` block. If the API rate limits, times out, or fails authentication, the script calls `sys.exit(1)`. This forcefully stops the GitHub Actions step, meaning the workflow crashes *before* it attempts to write an empty SVG or commit an invalid file to the repository.
- **Idempotency and Diff Checking**: Unnecessary commits are prevented. The bash sequence `git commit -m "Auto-generate" || exit 0` catches the scenario where the generated SVG is binary-identical to the existing SVG. In this case, `git` exits with a non-zero code because there is nothing to commit, and the script exits safely without attempting to push a duplicate commit.

## Known Limitations
- The integration assumes the GitHub Actions bot will commit directly to the `main` branch. Branch protection rules (like requiring PR reviews) on the repository would block this automated push. If branch protection is enabled, a service account or specific PAT might be needed instead of the default `GITHUB_TOKEN`.
- The generation pipeline only visualizes the *public* contributions of the user tied to the `GITHUB_USERNAME` environment variable, which gracefully inherits from `${{ github.repository_owner }}`.
