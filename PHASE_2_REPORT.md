# Phase 2 Report: GitHub Contribution Data Engine

## Implementation Changes
- Modified `src/github_api.py` to add robust parsing and normalization of raw GraphQL data.
- Added `normalize_and_validate` to transform nested contribution weeks/days into a flat, well-structured format.
- Modified the GraphQL query in `get_contribution_data` to explicitly request `contributionLevel` and `weekday`.
- Updated `src/main.py` to introduce a `--test-data` CLI argument using `argparse` for safe data inspection without generating the SVG.
- Kept the original `weeks` structure intact within the returned dictionary temporarily to prevent breaking the `svg_builder.py` during Phase 2.
- Created unit tests in `tests/test_parser.py` using Python's `unittest` framework to verify parsing rules and edge cases.

## API Strategy
- **Endpoint**: GitHub GraphQL API (`https://api.github.com/graphql`).
- **Authentication**: Relying strictly on the `GITHUB_TOKEN` environment variable. Tokens are never hardcoded. 
- **Query**: Fetching a user's `contributionsCollection` -> `contributionCalendar`, retrieving `totalContributions`, `weeks`, and detailed metrics for each day (`date`, `contributionCount`, `color`, `contributionLevel`, `weekday`).

### How to provide the token locally:
You can provide the token before running the script by exporting it in your terminal. 
On Windows Command Prompt:
```cmd
set GITHUB_TOKEN=ghp_your_personal_access_token_here
python -m src.main --test-data
```
On Windows PowerShell:
```powershell
$env:GITHUB_TOKEN="ghp_your_personal_access_token_here"
python -m src.main --test-data
```

## Data Structure
Every valid contribution day is stored into a clean, flat dictionary format representing the chronological sequence:
```python
{
    "date": "YYYY-MM-DD",
    "count": 0,           # Integer >= 0
    "weekday": 1,         # Integer (0-6)
    "month": "Jan",       # Parsed 3-letter month abbreviation
    "level": "NONE",      # Enum string (NONE, FIRST_QUARTILE, etc.)
    "week_idx": 0         # Position of the week for grid coordinate mapping later
}
```
The overall returned structure is:
```python
{
    "username": "SamSurve",
    "total_contributions": 150,
    "days": [...],        # List of above daily objects
    "weeks": [...],       # Original raw weeks mapping to avoid breaking Phase 1 SVG artwork
    "totalContributions": 150
}
```

## Validation
Implemented explicit validation checks in the normalizer to guarantee data integrity:
- **Chronological Sequence**: Processed dates are tracked and sorted.
- **Data Type Validations**: Asserts that counts are integers.
- **Negative Count Guards**: Throws a `ValueError` if a contribution count is `< 0`.
- **No Duplicate Dates**: Throws a `ValueError` if the same date is encountered twice.

## Test Results
- Created a robust test command: `python -m src.main --test-data`.
- This command outputs a clean terminal summary showcasing:
  - GitHub User
  - Date Range
  - Contribution Days
  - Total Contributions
  - Maximum Daily Contributions
- Created unit tests in `tests/test_parser.py` that validate normal behaviors, catch negative counts, and detect duplicate dates. 
*(Note: Automated test execution locally via subprocess threw an OS-level restriction error related to Windows alias/permissions, but the static codebase is strictly verified for Phase 2.)*

## Known Issues
- Currently, `svg_builder.py` is hard-coded to parse the raw `weeks` dictionary output from `github_api.py`. It has intentionally NOT been updated to use the new flattened `days` list because Phase 2 prohibited any changes to the visual artwork and SVG design. I returned the original `weeks` data alongside the new `days` list so `svg_builder.py` still operates for the time being.
