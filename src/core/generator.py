"""
src/core/generator.py
---------------------
WorkoutGenerator: class-based wrapper around the Groq API.
Encapsulates authentication, model selection, and all LLM call logic.
"""
from __future__ import annotations

import json
import os
from typing import List, Optional, Tuple, Union

from .config import DEFAULT_MODEL
from .prompts import build_swap_prompt, build_workout_prompt

try:
    from groq import (
        APIConnectionError,
        APIStatusError,
        AuthenticationError,
        Groq,
        RateLimitError,
    )
except ImportError:
    Groq = None  # type: ignore
    APIConnectionError = Exception  # type: ignore
    APIStatusError = Exception  # type: ignore
    AuthenticationError = Exception  # type: ignore
    RateLimitError = Exception  # type: ignore


class WorkoutGenerator:
    """
    High-level interface for all LLM-based workout generation and exercise swapping.

    Attributes:
        api_key (str): Groq API key.
        model (str): Groq model identifier to use for completions.
    """

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL) -> None:
        self.api_key = api_key.strip()
        self.model = model.strip()

    # ── Validation ─────────────────────────────────────────────────────────────
    @staticmethod
    def validate_inputs(
        fitness_goal: str,
        experience_level: str,
        days_per_week: int,
        equipment_access: Union[str, List[str]],
        session_duration_mins: int = 45,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate structured user inputs before sending to the LLM.

        Returns:
            (is_valid, error_message_or_None)
        """
        if not fitness_goal or not fitness_goal.strip():
            return False, "Please select a fitness goal."
        if not experience_level or not experience_level.strip():
            return False, "Please select an experience level."
        if not isinstance(days_per_week, int) or not (1 <= days_per_week <= 7):
            return False, f"Days per week must be 1-7 (got {days_per_week})."
        if not isinstance(session_duration_mins, int) or session_duration_mins < 1:
            return False, "Session duration must be greater than 0 minutes."
        if isinstance(equipment_access, list):
            if not equipment_access:
                return False, "Please select at least one equipment option."
        elif not equipment_access or not equipment_access.strip():
            return False, "Please select your equipment access."
        return True, None

    # ── Helpers ────────────────────────────────────────────────────────────────
    def _check_ready(self) -> Optional[Tuple[bool, str]]:
        """Return an error tuple if Groq is unavailable or no key is configured."""
        if Groq is None:
            return (
                False,
                "The `groq` Python package is not installed. Run `pip install groq`.",
            )
        if not self.api_key:
            return (
                False,
                "Groq API Key is missing. Set GROQ_API_KEY in your .env file.",
            )
        return None

    @staticmethod
    def _extract_json(content: str) -> str:
        """Strip markdown code fences and return the raw JSON string."""
        s = content.strip()
        for prefix in ("```json", "```"):
            if s.startswith(prefix):
                s = s[len(prefix):]
        if s.endswith("```"):
            s = s[:-3]
        return s.strip()

    def _call_api(
        self,
        system_msg: str,
        user_msg: str,
        temperature: float = 0.7,
        max_tokens: int = 2500,
    ) -> Tuple[bool, str]:
        """
        Make a chat completion call to the Groq API.

        Returns:
            (success, content_or_error)
        """
        guard = self._check_ready()
        if guard:
            return guard

        # Sanitise strings to ASCII for Windows compatibility
        sys_safe = system_msg.encode("utf-8", errors="ignore").decode("ascii", errors="ignore")
        usr_safe = user_msg.encode("utf-8", errors="ignore").decode("ascii", errors="ignore")

        try:
            client = Groq(api_key=self.api_key)
            completion = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": sys_safe},
                    {"role": "user", "content": usr_safe},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            if not completion or not completion.choices:
                return False, "Received an empty response from the Groq API. Please try again."
            content = completion.choices[0].message.content
            if not content or not content.strip():
                return False, "The AI model generated a blank response. Please try again."
            return True, content

        except AuthenticationError:
            return (
                False,
                "Authentication failed: The provided Groq API key is invalid or expired. "
                "Generate a free key at https://console.groq.com/keys.",
            )
        except RateLimitError:
            return (
                False,
                "Rate limit reached. Please wait a moment before trying again.",
            )
        except APIConnectionError:
            return (
                False,
                "Network error: Unable to reach Groq API servers. "
                "Please check your internet connection.",
            )
        except APIStatusError as err:
            return (
                False,
                f"Groq API error (status {err.status_code}): "
                f"{err.message if hasattr(err, 'message') else str(err)}",
            )
        except Exception as err:
            return False, f"Unexpected error: {err}"

    # ── Public API ─────────────────────────────────────────────────────────────
    def generate_plan(
        self,
        fitness_goal: str,
        experience_level: str,
        days_per_week: int,
        equipment_access: Union[str, List[str]],
        injuries_or_limitations: Optional[str] = None,
        session_duration_mins: int = 45,
        variation_seed_hint: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        Validate inputs, build prompt, call the Groq API, and return the workout plan JSON.

        Returns:
            (success, json_string_or_error_message)
        """
        is_valid, err = self.validate_inputs(
            fitness_goal, experience_level, days_per_week, equipment_access, session_duration_mins
        )
        if not is_valid:
            return False, err or "Invalid input parameters."

        prompt = build_workout_prompt(
            fitness_goal=fitness_goal,
            experience_level=experience_level,
            days_per_week=days_per_week,
            equipment_access=equipment_access,
            injuries_or_limitations=injuries_or_limitations,
            session_duration_mins=session_duration_mins,
            variation_seed_hint=variation_seed_hint,
        )

        system_msg = (
            "You are an expert Certified Strength and Conditioning Specialist (CSCS). "
            "You design realistic, scientifically sound, structured training programs. "
            "You strictly obey all user constraints regarding equipment, schedule, and injuries."
        )
        temperature = 0.85 if variation_seed_hint else 0.7
        success, content = self._call_api(system_msg, prompt, temperature=temperature, max_tokens=2500)
        if not success:
            return False, content

        try:
            parsed = json.loads(self._extract_json(content))
            return True, json.dumps(parsed, indent=2)
        except json.JSONDecodeError:
            return True, content.strip()

    def replace_exercise(
        self,
        current_plan_json: str,
        exercise_to_replace: str,
        reason_or_preference: str,
        equipment_access: Union[str, List[str]],
        injuries_or_limitations: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        Replace a single exercise in an existing JSON plan with a suitable alternative.

        Returns:
            (success, updated_json_string_or_error_message)
        """
        if not exercise_to_replace or not exercise_to_replace.strip():
            return False, "Please specify the name of the exercise you want to swap."

        equipment_str = (
            ", ".join(equipment_access)
            if isinstance(equipment_access, list)
            else str(equipment_access).strip()
        )
        limitations_str = (
            injuries_or_limitations.strip()
            if injuries_or_limitations and injuries_or_limitations.strip()
            else "None"
        )

        prompt = build_swap_prompt(
            current_plan_json=current_plan_json,
            exercise_to_replace=exercise_to_replace,
            reason_or_preference=reason_or_preference,
            equipment_str=equipment_str,
            limitations_str=limitations_str,
        )
        system_msg = "You are a CSCS certified strength coach who outputs only raw, valid JSON."

        success, content = self._call_api(system_msg, prompt, temperature=0.4, max_tokens=3000)
        if not success:
            return False, content

        try:
            parsed = json.loads(self._extract_json(content))
            return True, json.dumps(parsed, indent=2)
        except json.JSONDecodeError:
            return False, "Failed to parse the updated plan as valid JSON. Please try again."
