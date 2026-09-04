"""Unit tests verifying input validation, prompt constraints, and Groq API error handling."""

import unittest
from unittest.mock import MagicMock, patch
from workout_generator import generate_workout_plan, swap_exercise


class TestWorkoutGenerator(unittest.TestCase):

    def test_missing_api_key(self):
        success, msg = generate_workout_plan("Build muscle", "Beginner", 3, "No equipment", api_key="")
        self.assertFalse(success)
        self.assertIn("API key is missing", msg)

    def test_invalid_days_zero(self):
        success, msg = generate_workout_plan("Build muscle", "Beginner", 0, "No equipment", api_key="dummy")
        self.assertFalse(success)
        self.assertIn("between 1 and 7", msg)

    def test_invalid_days_excessive(self):
        success, msg = generate_workout_plan("Build muscle", "Beginner", 8, "No equipment", api_key="dummy")
        self.assertFalse(success)
        self.assertIn("between 1 and 7", msg)

    def test_missing_required_fields(self):
        success, msg = generate_workout_plan("", "Beginner", 3, "No equipment", api_key="dummy")
        self.assertFalse(success)
        self.assertIn("required inputs", msg)

    def test_bad_api_key_authentication_error(self):
        success, msg = generate_workout_plan("Build muscle", "Beginner", 3, "No equipment", api_key="gsk_bad_key")
        self.assertFalse(success)
        self.assertIn("Authentication failed", msg)

    @patch("workout_generator.Groq")
    def test_empty_llm_response(self, mock_groq):
        mock_groq.return_value.chat.completions.create.return_value.choices = [MagicMock(message=MagicMock(content=""))]
        success, msg = generate_workout_plan("Build muscle", "Beginner", 3, "No equipment", api_key="dummy")
        self.assertFalse(success)
        self.assertIn("empty response", msg.lower())

    @patch("workout_generator.Groq")
    def test_successful_generation(self, mock_groq):
        mock_groq.return_value.chat.completions.create.return_value.choices = [
            MagicMock(message=MagicMock(content="### 3-Day Plan\nDay 1: Pushups"))
        ]
        success, result = generate_workout_plan("Build muscle", "Beginner", 3, "No equipment", api_key="dummy")
        self.assertTrue(success)
        self.assertIn("3-Day Plan", result)

    def test_swap_exercise_validation(self):
        success, msg = swap_exercise("", "Knee pain", "Dumbbells", api_key="dummy")
        self.assertFalse(success)
        self.assertIn("specify an exercise", msg)

    @patch("workout_generator.Groq")
    def test_swap_exercise_success(self, mock_groq):
        mock_groq.return_value.chat.completions.create.return_value.choices = [
            MagicMock(message=MagicMock(content="1. Goblet Squat\n2. Leg Press"))
        ]
        success, result = swap_exercise("Barbell Squat", "Knee pain", "Home dumbbells", api_key="dummy")
        self.assertTrue(success)
        self.assertIn("Goblet Squat", result)


if __name__ == "__main__":
    unittest.main()

