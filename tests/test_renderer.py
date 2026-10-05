import os
import struct
import unittest
from src.png_renderer import render_png, PureCanvas
from src.theme import (
    CANVAS_WIDTH, CANVAS_HEIGHT, CONTRIBUTION_COLORS,
    GRID_START_X, GRID_START_Y, CELL_SIZE, CELL_GAP,
    DISPLAY_WEEKDAYS
)

class TestPngRenderer(unittest.TestCase):
    def setUp(self):
        self.fixture_data = {
            "username": "SamSurve",
            "total_contributions": 15,
            "weeks": [
                {
                    "contributionDays": [
                        {"date": "2024-01-01", "contributionCount": 0, "contributionLevel": "NONE", "weekday": 1},
                        {"date": "2024-01-02", "contributionCount": 1, "contributionLevel": "FIRST_QUARTILE", "weekday": 2},
                        {"date": "2024-01-03", "contributionCount": 4, "contributionLevel": "SECOND_QUARTILE", "weekday": 3},
                        {"date": "2024-01-04", "contributionCount": 7, "contributionLevel": "THIRD_QUARTILE", "weekday": 4},
                        {"date": "2024-01-05", "contributionCount": 12, "contributionLevel": "FOURTH_QUARTILE", "weekday": 5}
                    ]
                }
            ],
            "days": [
                {"date": "2024-01-01", "count": 0, "weekday": 1, "month": "Jan", "level": "NONE", "week_idx": 0},
                {"date": "2024-01-02", "count": 1, "weekday": 2, "month": "Jan", "level": "FIRST_QUARTILE", "week_idx": 0},
                {"date": "2024-01-03", "count": 4, "weekday": 3, "month": "Jan", "level": "SECOND_QUARTILE", "week_idx": 0},
                {"date": "2024-01-04", "count": 7, "weekday": 4, "month": "Jan", "level": "THIRD_QUARTILE", "week_idx": 0},
                {"date": "2024-01-05", "count": 12, "weekday": 5, "month": "Jan", "level": "FOURTH_QUARTILE", "week_idx": 0}
            ]
        }
        self.test_output = os.path.join("assets", "test-contributions.png")

    def tearDown(self):
        if os.path.exists(self.test_output):
            try:
                os.remove(self.test_output)
            except Exception:
                pass

    def test_dimensions_and_constants(self):
        self.assertEqual(CANVAS_WIDTH, 1200)
        self.assertEqual(CANVAS_HEIGHT, 350)
        self.assertEqual(len(CONTRIBUTION_COLORS), 5)
        self.assertEqual(CONTRIBUTION_COLORS[0].upper(), "#FDF6F8")
        self.assertEqual(CONTRIBUTION_COLORS[1].upper(), "#FBC4D6")
        self.assertEqual(CONTRIBUTION_COLORS[2].upper(), "#F58EB7")
        self.assertEqual(CONTRIBUTION_COLORS[3].upper(), "#E84C8F")
        self.assertEqual(CONTRIBUTION_COLORS[4].upper(), "#C11E66")

    def test_weekdays_mapped(self):
        self.assertIn(1, DISPLAY_WEEKDAYS)
        self.assertEqual(DISPLAY_WEEKDAYS[1], "Mon")
        self.assertIn(3, DISPLAY_WEEKDAYS)
        self.assertEqual(DISPLAY_WEEKDAYS[3], "Wed")
        self.assertIn(5, DISPLAY_WEEKDAYS)
        self.assertEqual(DISPLAY_WEEKDAYS[5], "Fri")

    def test_pure_canvas_png_encoding(self):
        canvas = PureCanvas(CANVAS_WIDTH, CANVAS_HEIGHT, "#FCF8FA")
        png_bytes = canvas.to_png_bytes()
        
        # Verify PNG Signature
        self.assertTrue(png_bytes.startswith(b"\x89PNG\r\n\x1a\n"))
        
        # Verify IHDR chunk
        ihdr_offset = 8
        ihdr_len = struct.unpack(">I", png_bytes[ihdr_offset:ihdr_offset+4])[0]
        self.assertEqual(ihdr_len, 13)
        self.assertEqual(png_bytes[ihdr_offset+4:ihdr_offset+8], b"IHDR")
        
        width, height = struct.unpack(">II", png_bytes[ihdr_offset+8:ihdr_offset+16])
        self.assertEqual(width, 1200)
        self.assertEqual(height, 350)
        
        # Verify IEND chunk at end
        self.assertTrue(png_bytes.endswith(b"IEND\xaeB`\x82"))

    def test_render_png_creates_valid_file(self):
        out_path = render_png(self.fixture_data, self.test_output)
        self.assertTrue(os.path.exists(out_path))
        self.assertGreater(os.path.getsize(out_path), 1000)
        
        with open(out_path, "rb") as f:
            header = f.read(16)
        self.assertTrue(header.startswith(b"\x89PNG\r\n\x1a\n"))

if __name__ == "__main__":
    unittest.main()
