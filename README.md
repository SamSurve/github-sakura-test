# GitHub Sakura Contributions 🌸

A live, custom GitHub contribution visualization with a Japanese Sakura / digital garden aesthetic.
This project fetches real contribution data directly from the GitHub GraphQL API, normalizes the chronological history, and renders it into a stunning, self-contained PNG image.

## Preview

<img
  src="https://raw.githubusercontent.com/SamSurve/github-sakura-test/main/assets/sakura-contributions.png"
  width="100%"
  alt="SamSurve Sakura GitHub Contribution Graph"
/>

## Features
- **Sakura Aesthetic**: A clean, premium off-white canvas featuring native artwork of Sakura branches, a coastal pagoda, Mount Fuji silhouettes, calm water reflections, and falling petals.
- **Dynamic Heatmap Hero**: Accurately fetches real GitHub contributions and maps them across all 52/53 weeks to a beautiful 5-tier pink color scale.
- **5 Pink Contribution Levels**:
  - `Level 0`: `#FDF6F8` (Zero contributions / pure pale Sakura snow)
  - `Level 1`: `#FBC4D6` (Light petal)
  - `Level 2`: `#F58EB7` (Vibrant cherry blossom)
  - `Level 3`: `#E84C8F` (Strong Sakura pink)
  - `Level 4`: `#C11E66` (Crimson Sakura dusk)
- **Dynamic Calendar Labels**: Month positions (Jan–Dec) calculated dynamically from actual contribution dates, along with Mon/Wed/Fri weekday labels and Less–More legend.
- **Zero Heavy Dependencies**: Ultra-fast portable rendering engine compatible with both pure Python and Pillow.

## How It Works
1. **GitHub GraphQL API**: Fetches real contribution counts, levels, dates, and week mappings for `SamSurve`.
2. **Data Normalization**: Validates chronological integrity and maps counts into standard intensity levels.
3. **PNG Visual Renderer**: High-performance raster engine generates the 1200 x 350 PNG asset.
4. **GitHub Actions Automation**: A scheduled workflow `.github/workflows/generate-sakura.yml` triggers daily at midnight UTC (`0 0 * * *`), updates the contribution graph, and pushes changes back to `assets/sakura-contributions.png`.

## Integration into `SamSurve` Profile README

To display this banner on your main GitHub profile (`SamSurve/SamSurve`):

```md
<div align="center">
  <img
    src="https://raw.githubusercontent.com/SamSurve/github-sakura-test/main/assets/sakura-contributions.png"
    width="100%"
    alt="SamSurve Sakura GitHub Contribution Graph"
  />
</div>
```

## Local Development & Testing
1. Ensure Python 3.12+ is installed.
2. Install dependencies: `pip install -r requirements.txt`
3. Optional: Export your GitHub token to test authenticated GraphQL:
   - Linux/macOS: `export GITHUB_TOKEN="your-token-here"`
   - Windows PowerShell: `$env:GITHUB_TOKEN="your-token-here"`
4. Run the data validation test: `python -m src.main --test-data`
5. Generate the PNG: `python -m src.main`
6. Run unit test suite: `python -m unittest discover tests`
