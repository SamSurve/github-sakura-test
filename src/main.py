import os
import sys
import argparse
from src.github_api import get_contribution_data
from src.png_renderer import render_png
from src.theme import CANVAS_WIDTH, CANVAS_HEIGHT

def run_test_data(username):
    print(f"Fetching contribution data for {username}...")
    try:
        data = get_contribution_data(username)
    except Exception as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)
        
    days = data.get("days", [])
    if not days:
        print("No contribution data found.")
        sys.exit(0)
        
    start_date = days[0]["date"]
    end_date = days[-1]["date"]
    total_contributions = data["total_contributions"]
    max_daily = max(d["count"] for d in days)
    
    print("\n--- CONTRIBUTION DATA REPORT ---")
    print(f"GitHub User: {username}")
    print(f"Date Range: {start_date} to {end_date}")
    print(f"Total Weeks: {len(data.get('weeks', []))}")
    print(f"Total Days: {len(days)}")
    print(f"Total Contributions: {total_contributions}")
    print(f"Max Daily Contributions: {max_daily}")
    print("--------------------------------\n")

def main():
    parser = argparse.ArgumentParser(description="Generate Sakura Contributions PNG")
    parser.add_argument("--test-data", action="store_true", help="Fetch and validate data without generating image")
    parser.add_argument("--output", default=os.path.join("assets", "sakura-contributions.png"), help="Output PNG path")
    args = parser.parse_args()

    username = os.environ.get("GITHUB_USERNAME", "SamSurve")
    
    if args.test_data:
        run_test_data(username)
        return

    print(f"Fetching contribution data for {username}...")
    try:
        calendar_data = get_contribution_data(username)
    except Exception as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)
        
    print(f"Generating Sakura Contribution PNG ({CANVAS_WIDTH}x{CANVAS_HEIGHT})...")
    output_path = render_png(calendar_data, args.output)
    
    file_size = os.path.getsize(output_path)
    print(f"Successfully generated {output_path}!")
    print(f"Resolution: {CANVAS_WIDTH} x {CANVAS_HEIGHT}")
    print(f"File size: {file_size:,} bytes")

if __name__ == "__main__":
    main()
