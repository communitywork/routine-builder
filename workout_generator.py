"""
workout_generator.py
--------------------
Core business logic for the Workout Plan Generator application.
Handles prompt construction, input validation, and Groq API communication
with strict error handling and type annotations.
"""

from __future__ import annotations

import json
import os
import sys
import locale

# Set UTF-8 encoding for Windows compatibility
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass
from typing import Any, List, Optional, Tuple, Union

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

# Supported Groq Models
SUPPORTED_MODELS: List[str] = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
]

DEFAULT_MODEL = SUPPORTED_MODELS[0]


def validate_inputs(
    fitness_goal: str,
    experience_level: str,
    days_per_week: int,
    equipment_access: Union[str, List[str]],
    session_duration_mins: int = 45,
) -> Tuple[bool, Optional[str]]:
    """
    Validates structured user inputs before sending to the LLM.

    Parameters:
        fitness_goal (str): Target fitness objective (e.g. Build muscle).
        experience_level (str): User experience (Beginner, Intermediate, Advanced).
        days_per_week (int): Training days per week (must be 1-7).
        equipment_access (Union[str, List[str]]): Available gear or facility.
        session_duration_mins (int): Target session duration in minutes.

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message_if_invalid)
    """
    if not fitness_goal or not fitness_goal.strip():
        return False, "Please select a fitness goal."

    if not experience_level or not experience_level.strip():
        return False, "Please select an experience level."

    if not isinstance(days_per_week, int) or days_per_week < 1 or days_per_week > 7:
        return False, f"Days available per week must be between 1 and 7 (received: {days_per_week})."

    if not isinstance(session_duration_mins, int) or session_duration_mins < 1:
        return False, "It doesn't make sense to have 0 target session minutes. Please select a duration greater than 0."

    if isinstance(equipment_access, list):
        if len(equipment_access) == 0:
            return False, "Please select at least one equipment access option."
    elif not equipment_access or not equipment_access.strip():
        return False, "Please select your equipment access."

    return True, None


def build_workout_prompt(
    fitness_goal: str,
    experience_level: str,
    days_per_week: int,
    equipment_access: Union[str, List[str]],
    injuries_or_limitations: Optional[str] = None,
    session_duration_mins: int = 45,
    variation_seed_hint: Optional[str] = None,
) -> str:
    """
    Builds a rigorous, structured prompt directing the LLM to create an actionable,
    custom workout plan strictly respecting all constraints.

    Parameters:
        fitness_goal (str): Target fitness goal.
        experience_level (str): Experience level.
        days_per_week (int): Workout days per week (1-7).
        equipment_access (Union[str, List[str]]): Available equipment.
        injuries_or_limitations (Optional[str]): Free-text injuries or physical limitations.
        session_duration_mins (int): Approximate minutes per session.
        variation_seed_hint (Optional[str]): Optional modifier to generate a distinct variation.

    Returns:
        str: Formatted prompt for the LLM.
    """
    # Normalize equipment string
    if isinstance(equipment_access, list):
        equipment_str = ", ".join(equipment_access)
    else:
        equipment_str = str(equipment_access).strip()

    limitations_str = (
        injuries_or_limitations.strip()
        if injuries_or_limitations and injuries_or_limitations.strip()
        else "None reported"
    )

    has_injuries = limitations_str != "None reported"

    variation_instruction = ""
    if variation_seed_hint:
        variation_instruction = f"\n- VARIATION NOTE: Provide a fresh variation/alternative split structure ({variation_seed_hint}).\n"

    prompt = f"""You are an elite Certified Strength and Conditioning Specialist (CSCS) and physical trainer.
Create a personalized, practical, and highly structured weekly workout plan based on the client profile below.

### CLIENT PROFILE:
- Primary Fitness Goal: {fitness_goal}
- Experience Level: {experience_level}
- Training Frequency: Exactly {days_per_week} days per week
- Session Duration: ~{session_duration_mins} minutes per workout
- Equipment Access: {equipment_str}
- Physical Limitations / Injuries: {limitations_str}
{variation_instruction}

### CRITICAL CONSTRAINTS (MUST STRICTLY FOLLOW):
1. **EQUIPMENT COMPLIANCE**: Prescribe ONLY exercises that can be performed with '{equipment_str}'.
   - If 'No equipment (Bodyweight only)', DO NOT prescribe barbell, dumbbell, or cable exercises.
   - If 'Home dumbbells', DO NOT include barbells, leg press, lat pulldown machines, or cable towers.
   - Respect this rule 100% without exception.

2. **FREQUENCY ACCURACY**: Generate a plan for EXACTLY {days_per_week} training day(s). Clearly designate:
   - Day 1 through Day {days_per_week}.
   - If days < 7, indicate how rest or active recovery days should be distributed across the week.

3. **INJURY & LIMITATION ADAPTATION**:
   {f"- The client has noted: '{limitations_str}'. You MUST actively exclude any movements that aggravate this condition and prescribe safe, pain-free alternatives. Highlight safety modifications with a note next to the exercise." if has_injuries else "- The client has no reported injuries. Ensure standard safe biomechanics and warm-ups."}

4. **APPROPRIATELY SCOPE & DISCLAIMER**:
   - Provide fitness and training advice only; make NO medical claims or clinical diagnoses.
   {f"- MANDATORY: Because the user has reported limitations/injuries ('{limitations_str}'), you MUST include a clear medical disclaimer advising consultation with a physician or physical therapist." if has_injuries else "- Include a brief general safety disclaimer."}

### DESIRED OUTPUT FORMAT:
Return your response as a valid JSON object with the following structure:

```json
{{
  "program_name": "Program Name (e.g., Full Body, Upper/Lower, Push/Pull/Legs)",
  "split_rationale": "Brief explanation of why this split fits the {days_per_week}-day schedule and {fitness_goal} goal",
  "days": [
    {{
      "day_number": 1,
      "title": "Day Title & Target Muscle Groups (e.g., Upper Body Strength & Posture)",
      "warmup": ["2-3 targeted mobility drills"],
      "exercises": [
        {{
          "number": 1,
          "name": "Exercise Name",
          "sets": "Sets (e.g., 3)",
          "reps": "Reps/Time (e.g., 8-12)",
          "rest": "Rest period (e.g., 60-90s)",
          "form_cue": "Form cue / coaching note"
        }}
      ],
      "cooldown": ["1-2 minutes stretch"]
    }}
  ],
  "progression_guidelines": "Concrete instructions on how to progress (progressive overload, adding reps or weight)",
  "recovery_tips": "Recovery tips (hydration, sleep, nutrition recommendations)",
  "disclaimer": "Clear safety and medical disclaimer"
}}
```

Ensure the JSON is valid and can be parsed. Do not include any text outside the JSON object.
"""
    return prompt.strip()


def generate_workout_plan(
    fitness_goal: str,
    experience_level: str,
    days_per_week: int,
    equipment_access: Union[str, List[str]],
    injuries_or_limitations: Optional[str] = None,
    api_key: Optional[str] = None,
    model: str = "llama-3.3-70b-versatile",
    session_duration_mins: int = 45,
    variation_seed_hint: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Main function to validate inputs, build prompt, call the Groq API,
    and return the generated workout plan with complete error handling.

    Parameters:
        fitness_goal (str): User's fitness objective.
        experience_level (str): Beginner, Intermediate, or Advanced.
        days_per_week (int): Training days per week (1-7).
        equipment_access (Union[str, List[str]]): Equipment available.
        injuries_or_limitations (Optional[str]): Optional injury or limitation notes.
        api_key (Optional[str]): Groq API key. If None, reads from GROQ_API_KEY env var.
        model (str): Groq model identifier to query.
        session_duration_mins (int): Desired session duration in minutes.
        variation_seed_hint (Optional[str]): Variation hint for regeneration.

    Returns:
        Tuple[bool, str]: (Success flag, Result text or Friendly Error Message)
    """
    # 1. Validate Structured Inputs
    is_valid, validation_err = validate_inputs(
        fitness_goal=fitness_goal,
        experience_level=experience_level,
        days_per_week=days_per_week,
        equipment_access=equipment_access,
        session_duration_mins=session_duration_mins,
    )
    if not is_valid:
        return False, validation_err or "Invalid input parameters."

    # 2. Check Groq library installation
    if Groq is None:
        return (
            False,
            "The `groq` Python package is not installed. Please run `pip install groq` in your environment.",
        )

    # 3. Resolve API Key
    effective_api_key = (api_key or os.getenv("GROQ_API_KEY", "")).strip()
    if not effective_api_key:
        return (
            False,
            "Groq API Key is missing. Please enter your Groq API Key in the sidebar or set the `GROQ_API_KEY` environment variable in a `.env` file.",
        )

    # 4. Build Prompt
    prompt = build_workout_prompt(
        fitness_goal=fitness_goal,
        experience_level=experience_level,
        days_per_week=days_per_week,
        equipment_access=equipment_access,
        injuries_or_limitations=injuries_or_limitations,
        session_duration_mins=session_duration_mins,
        variation_seed_hint=variation_seed_hint,
    )

    # 5. Call Groq API with robust try/except
    try:
        client = Groq(api_key=effective_api_key)

        # Ensure all strings are ASCII-safe for Windows compatibility
        system_content = (
            "You are an expert Certified Strength and Conditioning Specialist (CSCS). "
            "You design realistic, scientifically sound, structured training programs. "
            "You strictly obey all user constraints regarding equipment, schedule, and injuries."
        )
        
        # Encode to bytes with utf-8, then decode with ascii ignoring errors
        system_content_safe = system_content.encode('utf-8', errors='ignore').decode('ascii', errors='ignore')
        prompt_safe = prompt.encode('utf-8', errors='ignore').decode('ascii', errors='ignore')

        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_content_safe,
                },
                {"role": "user", "content": prompt_safe},
            ],
            temperature=0.7 if not variation_seed_hint else 0.85,
            max_tokens=2500,
        )

        # 6. Validate LLM Response
        if not completion or not completion.choices:
            return (
                False,
                "Received an empty response from the Groq API. Please try again.",
            )

        content = completion.choices[0].message.content
        if not content or not content.strip():
            return (
                False,
                "The AI model generated a blank response. Please try clicking 'Regenerate' to try again.",
            )

        # Try to parse JSON response
        try:
            # Extract JSON from response (in case there's markdown code blocks)
            json_str = content.strip()
            if json_str.startswith('```json'):
                json_str = json_str[7:]
            if json_str.startswith('```'):
                json_str = json_str[3:]
            if json_str.endswith('```'):
                json_str = json_str[:-3]
            json_str = json_str.strip()

            parsed_data = json.loads(json_str)
            return True, json.dumps(parsed_data, indent=2)
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw content
            return True, content.strip()

    except AuthenticationError:
        return (
            False,
            "Authentication failed: The provided Groq API key is invalid or expired. "
            "Please check your API key in the sidebar. You can generate a free key at https://console.groq.com/keys.",
        )
    except RateLimitError:
        return (
            False,
            "You are using the free version of this application. "
            "Please contact siteadmin at sales@fitblueprint.com for upgraded access.",
        )
    except APIConnectionError:
        return (
            False,
            "Network connection error: Unable to reach Groq API servers. "
            "Please check your internet connection or proxy settings.",
        )
    except APIStatusError as err:
        return (
            False,
            f"Groq API error (Status code {err.status_code}): {err.message if hasattr(err, 'message') else str(err)}",
        )
    except Exception as err:
        return (
            False,
            f"An unexpected error occurred while communicating with the Groq API: {str(err)}",
        )


def swap_exercise(
    current_exercise: str,
    reason_or_preference: str,
    equipment_access: Union[str, List[str]],
    injuries_or_limitations: Optional[str] = None,
    api_key: Optional[str] = None,
    model: str = "llama-3.3-70b-versatile",
) -> Tuple[bool, str]:
    """
    Stretch Goal Feature:
    Swaps out a specific exercise from the workout plan with an appropriate alternative
    that strictly satisfies equipment and physical limitation constraints.

    Parameters:
        current_exercise (str): Name of the exercise the user wants to replace.
        reason_or_preference (str): Why they want to swap it (e.g., knee pain, don't like it).
        equipment_access (Union[str, List[str]]): Available equipment.
        injuries_or_limitations (Optional[str]): Physical limitations.
        api_key (Optional[str]): Groq API key.
        model (str): Groq model identifier.

    Returns:
        Tuple[bool, str]: (Success flag, Proposed replacement details or error message)
    """
    if not current_exercise or not current_exercise.strip():
        return False, "Please specify the name of the exercise you want to swap."

    if Groq is None:
        return False, "The `groq` Python package is not installed."

    effective_api_key = (api_key or os.getenv("GROQ_API_KEY", "")).strip()
    if not effective_api_key:
        return False, "Groq API Key is missing. Please provide it in the sidebar."

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

    swap_prompt = f"""You are an expert strength coach. A client wants to replace an exercise in their routine.

- Exercise to Replace: {current_exercise.strip()}
- Reason / User Feedback: {reason_or_preference.strip() if reason_or_preference else "User wants an alternative"}
- Equipment Available: {equipment_str}
- Physical Limitations: {limitations_str}

Please recommend 2-3 excellent direct substitute exercises that:
1. Target the exact same or complementary movement pattern / muscle groups.
2. Strictly use the available equipment ('{equipment_str}').
3. Are safe given their limitation ('{limitations_str}').

For each alternative, provide:
- **Exercise Name**
- **Recommended Sets & Reps**
- **Why it is a good swap**
- **Key Form Cue**
Keep your response concise and formatted in Markdown.
"""

    try:
        client = Groq(api_key=effective_api_key)
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a CSCS certified strength coach providing safe, accurate exercise alternatives.",
                },
                {"role": "user", "content": swap_prompt},
            ],
            temperature=0.6,
            max_tokens=800,
        )

        if not completion or not completion.choices:
            return False, "Received an empty response from the API."

        content = completion.choices[0].message.content
        if not content or not content.strip():
            return False, "Generated empty alternative response."

        return True, content.strip()

    except Exception as err:
        return False, f"Failed to find exercise replacement: {str(err)}"
