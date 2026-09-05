# Functionality Guide

This document explains what the application does from a user and system perspective.

## Navigation Areas

FitBlueprint has four main user-facing areas:

| Area | Purpose |
|---|---|
| Current Routine | Displays the active generated workout plan and supports swaps, saves, and downloads. |
| Generate Routine | Collects trainee inputs and creates a new AI-generated routine. |
| Curated | Provides pre-built blueprint templates that can be generated directly or customized first. |
| Saved Routines | Shows routines saved during the current session and lets users reload or export them. |

## 1. Current Routine

The **Current Routine** screen is the main output view. It displays the active workout plan from `st.session_state.workout_plan`.

### Responsibilities

- Render the current plan as readable workout cards
- Show warmups, exercises, cooldowns, progression, recovery, and disclaimers
- Offer a swap button for individual exercises
- Allow the routine to be saved into history
- Provide export buttons for Markdown and plain text

### Empty State

If no routine has been generated yet, the app shows a friendly empty state and guides the user to generate a plan first.

### Workout Display

The display logic parses the stored plan as JSON. When parsing succeeds, the UI renders structured cards. When parsing fails, the fallback behavior displays the raw plan text so the user does not lose generated content.

## 2. Generate Routine

The **Generate Routine** screen is the primary intake flow.

### Inputs

| Input | Type | Purpose |
|---|---|---|
| Fitness Goal | Selectbox | Controls overall training objective. |
| Experience Level | Selectbox | Adjusts exercise complexity and training volume. |
| Days Available per Week | Slider | Forces the generated plan to match exact weekly frequency. |
| Target Session Duration | Select slider | Keeps the routine realistic for the user's schedule. |
| Equipment Access | Selectbox | Prevents impossible or unavailable exercises. |
| Injuries / Physical Limitations | Text input | Allows safety modifications and contraindication avoidance. |

### Generation Behavior

When the user clicks **Generate Science-Backed Routine**:

1. The view calls `WorkoutGenerator.generate_plan()`.
2. Inputs are validated.
3. A strict CSCS-style prompt is built.
4. The Groq API is called.
5. The response is parsed as JSON when possible.
6. The active plan and metadata are stored in session state.
7. The app routes the user to **Current Routine**.

### Quick Add Limitations

Quick limitation tags help users add common constraints without typing full descriptions. Current tags include:

- Bad knees
- Lower back pain
- Shoulder impingement
- No jumping / wrist pain

These tags append to the limitations field and rerun the page.

## 3. Curated Blueprints

The **Curated** screen provides pre-configured training templates stored in `src/ui/state.py` as `PRESETS`.

### Current Presets

| Preset | Goal | Experience | Days | Equipment | Duration |
|---|---|---:|---:|---|---:|
| 5-Day Push/Pull/Legs | Build muscle | Intermediate | 5 | Full gym | 60 min |
| 4-Day Upper/Lower Strength Split | Build muscle | Intermediate | 4 | Full gym | 60 min |
| 3-Day Home Dumbbell Recomp | Build muscle | Beginner | 3 | Home dumbbells | 45 min |
| 3-Day Busy Executive | General fitness | Beginner | 3 | Home dumbbells | 30 min |
| 3-Day Desk Worker Posture & Core | General fitness | Beginner | 3 | No equipment | 30 min |

### Actions

Each curated blueprint supports two actions:

1. **Set as Current Routine**  
   Immediately sends the preset to the generator and loads the result into Current Routine.

2. **Customize in Generator**  
   Copies the preset values into the generation form so the user can adjust the plan before generating.

## 4. Saved Routines

The **Saved Routines** screen acts as an in-session routine history.

### Save Model

Saved routines are stored in `st.session_state.saved_routines`. Each entry contains:

- Unique timestamp-based ID
- Display timestamp
- Title
- Goal
- Days
- Equipment
- Duration
- Experience
- Limitations
- Full plan text

### Supported Actions

| Action | Result |
|---|---|
| Set Current | Makes a saved routine the active routine. |
| Modify | Loads a saved routine into Current Routine for swaps or regeneration-related work. |
| Download MD | Exports a saved routine as Markdown. |
| Clear All Saved Routines | Removes all saved routines from session state. |

## Exercise Swap Feature

The inline swap feature lets users replace one exercise without regenerating the full plan.

### User Flow

1. User opens Current Routine.
2. User clicks **Swap** on an exercise card.
3. A modal dialog opens.
4. User selects or enters a reason.
5. The app sends the current JSON plan plus the target exercise to the AI.
6. The AI returns the same full plan with only that exercise replaced.
7. The old plan is archived.
8. The updated plan becomes current.

### Swap Constraints

The swap prompt instructs the model to:

- Replace exactly one named exercise
- Preserve the plan structure
- Preserve days, sets, reps format, and surrounding content
- Respect equipment access
- Respect physical limitations
- Return only valid JSON

## Export Functionality

Exports are handled by `src/utils/formatting.py`.

### Markdown Export

`format_plan_as_markdown()` converts valid JSON into a clean `.md` training document with:

- Program title
- Split rationale
- Day sections
- Warm-up lists
- Exercise details
- Cool-down lists
- Progression guidelines
- Recovery tips
- Disclaimer

If the plan is not valid JSON, the function returns the raw plan text.

### Plain Text Export

`format_plan_as_text()` starts from the Markdown export and strips basic Markdown syntax. This is useful for copying into notes, emails, or simple documents.

## Error Handling

`WorkoutGenerator` handles several failure modes gracefully.

| Failure | User-Facing Behavior |
|---|---|
| Missing Groq package | Explains that `groq` must be installed. |
| Missing API key | Asks the user to set `GROQ_API_KEY`. |
| Invalid API key | Shows an authentication failure message. |
| Rate limit | Asks the user to wait before trying again. |
| API connection error | Indicates a network problem. |
| API status error | Shows the returned API status/message. |
| Empty response | Tells the user the model returned blank content. |
| Malformed JSON | Keeps the raw content instead of discarding it. |

## Safety Functionality

The app is designed to provide fitness guidance, not medical diagnosis. When injuries or limitations are entered, the prompt requires:

- Avoiding aggravating movements
- Selecting safer alternatives
- Adding a medical disclaimer
- Avoiding clinical claims

This does not replace professional medical advice, but it helps the generated plan avoid obvious unsafe recommendations.

## Functional Extension Ideas

Good next features that fit the current architecture:

- Persistent saved routines using a database or local file
- User accounts
- Routine calendar scheduling
- Progress tracking by exercise
- Regenerate a single day instead of the whole plan
- More equipment categories
- More limitation quick tags
- PDF export
- Unit tests updated for the current `src.core` structure
