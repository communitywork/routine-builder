"""
src/core/prompts.py
-------------------
All LLM prompt-building logic, isolated from business logic and UI concerns.
"""
from __future__ import annotations

from typing import List, Optional, Union


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
    Build a rigorous, structured prompt directing the LLM to create an actionable,
    custom workout plan strictly respecting all constraints.
    """
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
        variation_instruction = (
            f"\n- VARIATION NOTE: Provide a fresh variation/alternative split structure "
            f"({variation_seed_hint}).\n"
        )

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


def build_swap_prompt(
    current_plan_json: str,
    exercise_to_replace: str,
    reason_or_preference: str,
    equipment_str: str,
    limitations_str: str,
) -> str:
    """
    Build the prompt to replace a single exercise within an existing JSON plan.
    """
    return f"""You are an expert Certified Strength and Conditioning Specialist (CSCS).
I have a JSON workout plan, and I need you to swap out EXACTLY ONE specific exercise.

- **Exercise to Replace**: {exercise_to_replace.strip()}
- **Reason for Swap**: {reason_or_preference.strip() if reason_or_preference else "User wants an alternative"}
- **Equipment Available**: {equipment_str}
- **Physical Limitations**: {limitations_str}

### INSTRUCTIONS:
1. Find every occurrence of "{exercise_to_replace.strip()}" in the provided JSON plan.
2. Replace it with a biomechanically sound alternative that targets the same muscle groups.
3. Ensure the alternative uses ONLY the available equipment ('{equipment_str}') and respects limitations ('{limitations_str}').
4. Do NOT change anything else in the plan (keep the same days, sets, reps format, etc.).
5. Return the ENTIRE updated JSON object in the exact same schema.

### CURRENT PLAN:
{current_plan_json}

### OUTPUT FORMAT:
Output ONLY valid JSON. Do not include any explanation or markdown formatting outside the JSON object.
"""
