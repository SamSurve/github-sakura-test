import unittest
from src.github_api import normalize_and_validate

class TestParser(unittest.TestCase):
    def test_normalize_valid_data(self):
        # Mock raw calendar data from GitHub GraphQL
        raw_calendar = {
            "totalContributions": 42,
            "weeks": [
                {
                    "contributionDays": [
                        {
                            "contributionCount": 0,
                            "date": "2024-01-01",
                            "contributionLevel": "NONE",
                            "weekday": 1
                        },
                        {
                            "contributionCount": 5,
                            "date": "2024-01-02",
                            "contributionLevel": "FIRST_QUARTILE",
                            "weekday": 2
                        }
                    ]
                }
            ]
        }
        
        result = normalize_and_validate(raw_calendar, "TestUser")
        
        self.assertEqual(result["username"], "TestUser")
        self.assertEqual(result["total_contributions"], 42)
        
        days = result["days"]
        self.assertEqual(len(days), 2)
        
        self.assertEqual(days[0]["date"], "2024-01-01")
        self.assertEqual(days[0]["count"], 0)
        self.assertEqual(days[0]["level"], "NONE")
        self.assertEqual(days[0]["weekday"], 1)
        self.assertEqual(days[0]["month"], "Jan")
        self.assertEqual(days[0]["week_idx"], 0)
        
        self.assertEqual(days[1]["date"], "2024-01-02")
        self.assertEqual(days[1]["count"], 5)
        self.assertEqual(days[1]["level"], "FIRST_QUARTILE")
        self.assertEqual(days[1]["weekday"], 2)
        self.assertEqual(days[1]["month"], "Jan")
        self.assertEqual(days[1]["week_idx"], 0)

    def test_normalize_invalid_duplicate_dates(self):
        raw_calendar = {
            "totalContributions": 5,
            "weeks": [
                {
                    "contributionDays": [
                        {
                            "contributionCount": 0,
                            "date": "2024-01-01"
                        },
                        {
                            "contributionCount": 5,
                            "date": "2024-01-01"
                        }
                    ]
                }
            ]
        }
        with self.assertRaises(ValueError) as context:
            normalize_and_validate(raw_calendar, "TestUser")
        
        self.assertTrue("Duplicate date found" in str(context.exception))

    def test_normalize_invalid_negative_count(self):
        raw_calendar = {
            "totalContributions": 5,
            "weeks": [
                {
                    "contributionDays": [
                        {
                            "contributionCount": -1,
                            "date": "2024-01-01"
                        }
                    ]
                }
            ]
        }
        with self.assertRaises(ValueError) as context:
            normalize_and_validate(raw_calendar, "TestUser")
        
        self.assertTrue("Invalid contribution count" in str(context.exception))

if __name__ == "__main__":
    unittest.main()
