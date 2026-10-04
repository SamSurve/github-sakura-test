from .theme import *
from .artwork import generate_sakura_tree

def get_color_for_level(count, level):
    if count == 0:
        return CONTRIBUTION_COLORS[0]
    
    # Map GraphQL contribution levels to our theme
    # NONE, FIRST_QUARTILE, SECOND_QUARTILE, THIRD_QUARTILE, FOURTH_QUARTILE
    if level == "FIRST_QUARTILE":
        return CONTRIBUTION_COLORS[1]
    elif level == "SECOND_QUARTILE":
        return CONTRIBUTION_COLORS[2]
    elif level == "THIRD_QUARTILE":
        return CONTRIBUTION_COLORS[3]
    elif level == "FOURTH_QUARTILE":
        return CONTRIBUTION_COLORS[4]
    
    # Fallback to count-based mapping if level is unexpected or "NONE" with count > 0
    if count <= 2: return CONTRIBUTION_COLORS[1]
    elif count <= 5: return CONTRIBUTION_COLORS[2]
    elif count <= 10: return CONTRIBUTION_COLORS[3]
    else: return CONTRIBUTION_COLORS[4]

def build_svg(calendar_data):
    svg_elements = []
    
    svg_elements.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" role="img" aria-labelledby="svg-title svg-desc">')
    svg_elements.append(f'<title id="svg-title">Sakura GitHub Contributions</title>')
    
    total = calendar_data.get("total_contributions", 0)
    username = calendar_data.get("username", "User")
    svg_elements.append(f'<desc id="svg-desc">{username} made {total} contributions in the last year.</desc>')
    
    # Background and Border
    svg_elements.append(f'<rect x="1" y="1" width="{SVG_WIDTH-2}" height="{SVG_HEIGHT-2}" fill="{BG_COLOR}" rx="15" stroke="{BORDER_COLOR}" stroke-width="2"/>')
    
    # Artwork (Sky, Mountains, Pagoda, Tree, Petals)
    svg_elements.append(generate_sakura_tree())
    
    # Title
    svg_elements.append(f'<text x="{GRID_START_X}" y="{GRID_START_Y - 35}" font-family="sans-serif" font-size="22" font-weight="bold" fill="{TEXT_COLOR}">{total} Contributions in the last year</text>')
    
    # Weekdays Labels
    weekdays = ["Mon", "Wed", "Fri"]
    for i, w in enumerate([1, 3, 5]):
        y = GRID_START_Y + (w * (CELL_SIZE + CELL_GAP)) + CELL_SIZE - 2
        svg_elements.append(f'<text x="{GRID_START_X - 30}" y="{y}" font-family="sans-serif" font-size="10" fill="{TEXT_MUTED}">{weekdays[i]}</text>')

    # Grid & Months
    days = calendar_data.get("days", [])
    if days:
        max_week = max(d["week_idx"] for d in days)
    else:
        max_week = 0

    months_added = []
    last_month_week = -10
    
    for day in days:
        week_idx = day["week_idx"]
        weekday = day["weekday"] # 0=Sun, 1=Mon, ..., 6=Sat
        count = day["count"]
        level = day["level"]
        month_name = day["month"]
        date_str = day["date"]
        
        x = GRID_START_X + (week_idx * (CELL_SIZE + CELL_GAP))
        y = GRID_START_Y + (weekday * (CELL_SIZE + CELL_GAP))
        
        # Month labels
        if month_name not in months_added and (week_idx - last_month_week > 3) and (max_week - week_idx > 2):
            # Only add month if it's sufficiently spaced from the last one and not too close to the edge
            svg_elements.append(f'<text x="{x}" y="{GRID_START_Y - 10}" font-family="sans-serif" font-size="10" fill="{TEXT_MUTED}">{month_name}</text>')
            months_added.append(month_name)
            last_month_week = week_idx
            
        color = get_color_for_level(count, level)
        
        # Contribution cell
        svg_elements.append(f'<rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" fill="{color}" rx="{CELL_RADIUS}">')
        svg_elements.append(f'  <title>{date_str} — {count} contributions</title>')
        svg_elements.append(f'</rect>')

    # Legend
    legend_start_x = SVG_WIDTH - 200
    legend_start_y = GRID_START_Y + (7 * (CELL_SIZE + CELL_GAP)) + 15
    svg_elements.append(f'<text x="{legend_start_x - 35}" y="{legend_start_y + 9}" font-family="sans-serif" font-size="10" fill="{TEXT_MUTED}">Less</text>')
    
    for i, color in enumerate(CONTRIBUTION_COLORS):
        lx = legend_start_x + (i * (CELL_SIZE + CELL_GAP))
        svg_elements.append(f'<rect x="{lx}" y="{legend_start_y}" width="{CELL_SIZE}" height="{CELL_SIZE}" fill="{color}" rx="{CELL_RADIUS}"/>')
        
    svg_elements.append(f'<text x="{legend_start_x + (5 * (CELL_SIZE + CELL_GAP)) + 5}" y="{legend_start_y + 9}" font-family="sans-serif" font-size="10" fill="{TEXT_MUTED}">More</text>')

    svg_elements.append('</svg>')
    
    return "\n".join(svg_elements)
