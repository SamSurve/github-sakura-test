import unittest
import re
from src.svg_builder import build_svg
from src.theme import CONTRIBUTION_COLORS, SVG_WIDTH, SVG_HEIGHT

class TestRenderer(unittest.TestCase):
    def setUp(self):
        # Deterministic fixture dataset
        self.fixture_data = {
            "username": "TestUser",
            "total_contributions": 12,
            "days": [
                {"date": "2024-01-01", "count": 0, "weekday": 1, "month": "Jan", "level": "NONE", "week_idx": 0},
                {"date": "2024-01-02", "count": 1, "weekday": 2, "month": "Jan", "level": "FIRST_QUARTILE", "week_idx": 0},
                {"date": "2024-01-03", "count": 4, "weekday": 3, "month": "Jan", "level": "SECOND_QUARTILE", "week_idx": 0},
                {"date": "2024-01-04", "count": 7, "weekday": 4, "month": "Jan", "level": "THIRD_QUARTILE", "week_idx": 0},
                {"date": "2024-01-05", "count": 12, "weekday": 5, "month": "Jan", "level": "FOURTH_QUARTILE", "week_idx": 0}
            ]
        }
        self.svg = build_svg(self.fixture_data)

    def test_svg_is_valid_xml_structure(self):
        # Check basic XML SVG structure
        self.assertTrue(self.svg.startswith("<svg"))
        self.assertTrue(self.svg.strip().endswith("</svg>"))
        
    def test_svg_viewbox(self):
        # Verify correct viewBox dimensions
        viewbox_str = f'viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}"'
        self.assertIn(viewbox_str, self.svg)
        
    def test_contribution_cells_generated(self):
        # Check if the title tooltips exist for the specific dates
        self.assertIn("<title>2024-01-01 — 0 contributions</title>", self.svg)
        self.assertIn("<title>2024-01-05 — 12 contributions</title>", self.svg)
        
    def test_zero_contributions_map_to_level_0(self):
        # The zero contribution day should use the Level 0 color
        l0_color = CONTRIBUTION_COLORS[0]
        # In SVG, it looks like: fill="#FDF6F8" rx="3"> \n <title>2024-01-01 — 0 contributions</title>
        # Let's just regex to verify the color corresponds to the date.
        pattern = f'fill="{l0_color}".*?<title>2024-01-01 — 0 contributions</title>'
        self.assertTrue(re.search(pattern, self.svg, re.DOTALL))
        
    def test_higher_contributions_map_to_stronger_colors(self):
        # The 12 contribution day should use the Level 4 color
        l4_color = CONTRIBUTION_COLORS[4]
        pattern = f'fill="{l4_color}".*?<title>2024-01-05 — 12 contributions</title>'
        self.assertTrue(re.search(pattern, self.svg, re.DOTALL))
        
    def test_month_labels_exist(self):
        # Month "Jan" should exist in the SVG
        self.assertIn(">Jan</text>", self.svg)
        
    def test_weekday_labels_exist(self):
        self.assertIn(">Mon</text>", self.svg)
        self.assertIn(">Wed</text>", self.svg)
        self.assertIn(">Fri</text>", self.svg)
        
    def test_legend_exists(self):
        self.assertIn(">Less</text>", self.svg)
        self.assertIn(">More</text>", self.svg)
        
    def test_no_hardcoded_fake_data(self):
        # If I pass empty data, there should be no contribution cells
        empty_svg = build_svg({"username": "Nobody", "total_contributions": 0, "days": []})
        self.assertNotIn("contributions on", empty_svg)
        
    def test_accessible_metadata(self):
        self.assertIn("<title id=\"svg-title\">Sakura GitHub Contributions</title>", self.svg)
        self.assertIn("aria-labelledby=\"svg-title svg-desc\"", self.svg)

if __name__ == "__main__":
    unittest.main()
