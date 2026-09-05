# Developer Guide

This guide explains how to run, configure, maintain, and extend FitBlueprint.

## Local Setup

### 1. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it:

```bash
# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Then set your Groq API key:

```env
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

`GROQ_MODEL` is optional. If it is missing, the app uses the default model from `src/core/config.py`.

### 4. Run the App

```bash
streamlit run app.py
```

## Configuration

Configuration is centralized in `src/core/config.py`.

| Setting | Location | Purpose |
|---|---|---|
| `GROQ_API_KEY` | `.env` / environment | Required for API calls. |
| `GROQ_MODEL` | `.env` / environment | Optional model override. |
| `SUPPORTED_MODELS` | `src/core/config.py` | Approved model list. |
| `DEFAULT_MODEL` | `src/core/config.py` | Fallback model. |

## Adding a New View

To add a new navigation section:

1. Add the nav item in `app.py`.
2. Create a `render_new_view()` function in `src/ui/views.py`.
3. Add a route in the view router inside `app.py`.
4. Use existing presentation patterns from `presentation-style.md`.

Example route shape:

```python
elif _nav == "📈 Progress Tracker":
    render_progress_tracker_view()
```

## Adding a New Preset

Curated presets live in `src/ui/state.py` inside `PRESETS`.

Add a new dictionary entry:

```python
"🔥 4-Day Athletic Power": {
    "goal": "General fitness",
    "experience": "Intermediate",
    "days": 4,
    "equipment": "Full gym",
    "duration": 60,
    "limitations": "Prioritize explosive movement quality and full recovery",
},
```

Make sure the values match the available form options where applicable.

## Modifying Prompt Behavior

Prompts live in `src/core/prompts.py`.

Use `build_workout_prompt()` when changing full routine generation behavior. Use `build_swap_prompt()` when changing the exercise replacement behavior.

When editing prompts, preserve these rules:

- Return valid JSON only
- Respect exact training frequency
- Respect equipment access
- Respect injuries and limitations
- Include disclaimers when limitations exist
- Avoid medical diagnosis language

## Modifying API Behavior

Groq API calls live in `WorkoutGenerator._call_api()`.

Keep all API-related logic in `src/core/generator.py`, including:

- Client creation
- Model selection
- Token limits
- Temperature
- Error handling
- Response extraction

UI views should call public methods like `generate_plan()` and `replace_exercise()` instead of calling Groq directly.

## Testing Notes

The current test file references an older module path named `workout_generator`. The current codebase uses `src/core/generator.py` and exposes `WorkoutGenerator` through `src.core`.

Recommended fix:

- Update tests to import `WorkoutGenerator` from `src.core`
- Mock `src.core.generator.Groq`
- Test `WorkoutGenerator.validate_inputs()` directly
- Test `generate_plan()` with mocked API responses
- Test `replace_exercise()` with mocked API responses

Example import direction:

```python
from src.core import WorkoutGenerator
```

## Safe Change Checklist

Before shipping a code change:

- Run the app locally with `streamlit run app.py`
- Generate a plan for each equipment category
- Test a limitation such as `bad knees`
- Test one exercise swap
- Test Markdown download
- Test plain text download
- Confirm navigation still works
- Confirm no API key is committed
- Confirm the UI still matches the presentation style guide

## Common Troubleshooting

### `Groq API Key is missing`

Set `GROQ_API_KEY` in `.env` or your shell environment.

### `The groq Python package is not installed`

Run:

```bash
pip install groq
```

### Streamlit does not reflect style changes

Refresh the browser and rerun the Streamlit server. CSS is injected from `styles.css` at app startup.

### AI returns invalid JSON

The generator attempts to parse the response. If parsing fails, the raw text is preserved. Tighten the output instructions in `src/core/prompts.py` if invalid JSON becomes frequent.

## Contribution Standard

New code should keep the same separation of concerns:

- UI in `src/ui`
- LLM prompts in `src/core/prompts.py`
- API calls in `src/core/generator.py`
- Formatting helpers in `src/utils`
- Styling in `styles.css`
- Documentation in `docs/`
