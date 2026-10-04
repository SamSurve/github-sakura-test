import os
import requests
from datetime import datetime

def get_contribution_data(username):
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set. Please set it to run locally.")

    query = """
    query($username: String!) {
      user(login: $username) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
                color
                contributionLevel
                weekday
              }
            }
          }
        }
      }
    }
    """
    
    variables = {"username": username}
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://api.github.com/graphql",
        headers=headers,
        json={"query": query, "variables": variables}
    )

    if response.status_code != 200:
        raise Exception(f"Query failed with code {response.status_code}: {response.text}")

    data = response.json()
    if "errors" in data:
        raise Exception(f"GraphQL errors: {data['errors']}")

    calendar = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return normalize_and_validate(calendar, username)

def normalize_and_validate(calendar, username):
    total_contributions = calendar.get("totalContributions", 0)
    weeks = calendar.get("weeks", [])
    
    normalized_days = []
    seen_dates = set()
    
    for week_idx, week in enumerate(weeks):
        for day in week.get("contributionDays", []):
            date_str = day.get("date")
            count = day.get("contributionCount", 0)
            level = day.get("contributionLevel", "NONE")
            weekday = day.get("weekday", 0)
            
            # Validation: date must be chronological (by checking no duplicates and sort later)
            if date_str in seen_dates:
                raise ValueError(f"Duplicate date found: {date_str}")
            seen_dates.add(date_str)
            
            # Validation: counts are integers and >= 0
            if not isinstance(count, int) or count < 0:
                raise ValueError(f"Invalid contribution count for {date_str}: {count}")
            
            # Parse month
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            month = dt.strftime("%b") # e.g., "Jan"
            
            normalized_days.append({
                "date": date_str,
                "count": count,
                "weekday": weekday,
                "month": month,
                "level": level,
                "week_idx": week_idx
            })
            
    # Sort just in case to ensure chronological
    normalized_days.sort(key=lambda x: x["date"])
    
    return {
        "username": username,
        "total_contributions": total_contributions,
        "days": normalized_days,
        "weeks": weeks, # preserve for svg_builder so it doesn't break
        "totalContributions": total_contributions
    }
