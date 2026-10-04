import os
import sys
import argparse
from src.github_api import get_contribution_data
from src.svg_builder import build_svg

def run_test_data(username):
    print(f"Fetching contribution data for {username}...")
    try:
        data = get_contribution_data(username)
    except Exception as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)
        
    days = data["days"]
    if not days:
        print("No contribution data found.")
        sys.exit(0)
        
    start_date = days[0]["date"]
    end_date = days[-1]["date"]
    total_contributions = data["total_contributions"]
    max_daily = max(d["count"] for d in days)
    
    print("\n--- TEST DATA REPORT ---")
    print(f"GitHub User: {username}")
    print(f"Date Range: {start_date} to {end_date}")
    print(f"Contribution Days: {len(days)}")
    print(f"Total Contributions: {total_contributions}")
    print(f"Maximum Daily Contributions: {max_daily}")
    print("------------------------\n")

def main():
    parser = argparse.ArgumentParser(description="Generate Sakura Contributions SVG")
    parser.add_argument("--test-data", action="store_true", help="Fetch and validate data without generating SVG")
    args = parser.parse_args()

    username = os.environ.get("GITHUB_USERNAME", "SamSurve")
    
    if args.test_data:
        run_test_data(username)
        return

    print(f"Fetching contribution data for {username}...")
    try:
        # Note: SVG builder is expecting the old raw data format from github_api.py.
        # But we were instructed: "Do NOT change the visual artwork yet. Do NOT redesign the SVG yet."
        # Wait, if we change get_contribution_data to return a normalized dict, 
        # svg_builder.py will break if we don't adjust it.
        # The prompt says: "Do NOT change the visual artwork yet. Do NOT redesign the SVG yet."
        # This means we should only modify what is necessary to pass Phase 2.
        # ... svg generation logic
        calendar_data = get_contribution_data(username)
    except Exception as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)
        
    print("Generating Sakura SVG...")
    svg_content = build_svg(calendar_data)
    
    os.makedirs("assets", exist_ok=True)
    output_path = os.path.join("assets", "sakura-contributions.svg")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
        
    print(f"Successfully generated {output_path}!")

if __name__ == "__main__":
    main()
