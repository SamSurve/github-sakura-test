import os
import json
import re
from datetime import datetime

try:
    import requests
except ImportError:
    requests = None

import urllib.request
import urllib.error

def fetch_graphql(username, token):
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
    payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Sakura-Contributions"
    }

    if requests:
        response = requests.post(
            "https://api.github.com/graphql",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"query": query, "variables": variables},
            timeout=30
        )
        if response.status_code != 200:
            raise Exception(f"GraphQL query failed with code {response.status_code}: {response.text}")
        data = response.json()
    else:
        req = urllib.request.Request("https://api.github.com/graphql", data=payload, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

    if "errors" in data:
        raise Exception(f"GraphQL errors: {data['errors']}")

    user_data = data.get("data", {}).get("user")
    if not user_data:
        raise Exception(f"User '{username}' not found on GitHub.")

    return user_data["contributionsCollection"]["contributionCalendar"]

def fetch_public_contributions(username):
    """
    Fallback fetcher for environments without GITHUB_TOKEN (e.g., local preview).
    Fetches real contribution calendar directly from the public GitHub profile.
    """
    url = f"https://github.com/users/{username}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8")

    # Extract total contributions
    m_total = re.search(r'([0-9,]+)\s+contributions\s+in\s+the\s+last\s+year', html)
    total_contributions = int(m_total.group(1).replace(",", "")) if m_total else 0

    # Parse all tooltips/days
    # Pattern matches table cells with date, level, and count
    day_matches = re.findall(
        r'<td[^>]*data-date="([0-9]{4}-[0-9]{2}-[0-9]{2})"[^>]*data-level="([0-4])"[^>]*id="(contribution-day-component-[0-9]+-[0-9]+)"',
        html
    )
    
    # Also extract counts from tooltips
    count_map = {}
    for date, count_str in re.findall(r'(\d+)\s+contributions?\s+on\s+([A-Za-z]+ \d+, \d{4})', html):
        try:
            dt = datetime.strptime(count_str, "%B %d, %Y")
            ds = dt.strftime("%Y-%m-%d")
            count_map[ds] = int(count_str)
        except Exception:
            pass

    level_names = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]

    # Reconstruct weeks
    days_by_date = {}
    for match in re.finditer(r'data-date="([0-9]{4}-[0-9]{2}-[0-9]{2})"[^>]*data-level="([0-4])"', html):
        d_str = match.group(1)
        lvl_num = int(match.group(2))
        dt = datetime.strptime(d_str, "%Y-%m-%d")
        # Python weekday: Monday is 0, Sunday is 6. GitHub calendar starts on Sunday (0)
        gh_weekday = (dt.weekday() + 1) % 7
        
        # Look for count in tooltips or near text
        c = count_map.get(d_str, lvl_num if lvl_num > 0 else 0)
        days_by_date[d_str] = {
            "date": d_str,
            "contributionCount": c,
            "contributionLevel": level_names[lvl_num],
            "weekday": gh_weekday
        }

    # Group into weeks chronologically
    sorted_days = sorted(days_by_date.values(), key=lambda x: x["date"])
    weeks = []
    current_week = []
    
    for day in sorted_days:
        if day["weekday"] == 0 and current_week:
            weeks.append({"contributionDays": current_week})
            current_week = []
        current_week.append(day)
    if current_week:
        weeks.append({"contributionDays": current_week})

    return {
        "totalContributions": total_contributions,
        "weeks": weeks
    }

def get_contribution_data(username="SamSurve"):
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        calendar = fetch_graphql(username, token)
    else:
        # Fallback to public real contributions when token is not available
        try:
            calendar = fetch_public_contributions(username)
        except Exception as e:
            raise ValueError(f"GITHUB_TOKEN not set and public fetch failed: {e}")

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
        "weeks": weeks,
        "totalContributions": total_contributions
    }
