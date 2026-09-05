# 📐 FitBlueprint — Workout Plan Generator

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Powered by Groq](https://img.shields.io/badge/Powered%20by-Groq-orange.svg)](https://groq.com)

**FitBlueprint** is a production-grade workout plan generator that creates personalized, science-backed weekly training programs based on your fitness goals, experience level, equipment availability, and physical limitations.

Powered by advanced AI through the **Groq API**, FitBlueprint delivers CSCS (Certified Strength and Conditioning Specialist) quality workout plans with strict adherence to your constraints and safety requirements.

---

## 🌟 Key Features

### 1. Structured Inputs (No Lazy Free-Text)
Rather than relying on vague free-form text boxes, the app collects structured inputs designed like a professional personal trainer intake form:
- **Fitness Goal**: Dropdown (`Build muscle`, `Lose fat`, `General fitness`, `Improve endurance`)
- **Experience Level**: Dropdown (`Beginner`, `Intermediate`, `Advanced`)
- **Days Available Per Week**: Interactive slider (`1` to `7` days)
- **Equipment Access**: Dropdown (`No equipment (Bodyweight only)`, `Home dumbbells`, `Full gym`)
- **Injuries or Limitations**: Free-text field with safety routing (e.g., *"bad knees, avoid high-impact jumping"*, *"no overhead pressing"*)
- **Target Session Duration**: Slider (`20` to `90` minutes)

### 2. Personal Trainer-Grade Prompt Design
The core engine (`src/core/generator.py`) acts as a Certified Strength and Conditioning Specialist (CSCS):
- **100% Constraint Compliance**: Equipment choices are strictly enforced (e.g., no barbells or cable machines if the user selected "Home dumbbells").
- **Exact Frequency Match**: Generates a Day 1 through Day N plan matching the chosen days per week, with intelligent recovery distribution.
- **Injury Adaptation & Medical Disclaimer**: Actively omits contraindicated exercises and includes a medical disclaimer whenever injuries or physical limitations are specified.
- **JSON-Structured Output**: Plans are returned as validated JSON, rendered into rich styled exercise cards in the UI.

### 3. Inline Exercise Swap
- Each exercise card in the **Current Routine** view has a **🔄 Swap** button.
- Clicking it opens a true modal dialog where you select a reason (e.g. joint pain, equipment unavailable).
- The AI replaces **only that specific exercise** in the full plan, preserving all other days, sets, reps, and structure.

### 4. Routine History & Saved Routines
- Every generated or swapped plan is **automatically archived** into the Saved Routines tab before being overwritten.
- Saved routines can be **Set as Current**, **Loaded for Modification (Swap/Regenerate)**, or **Downloaded as Markdown**.

### 5. Comprehensive Error Handling
- **Invalid / Empty Inputs**: Validates user selections and displays friendly Streamlit warning alerts.
- **API Failure Resilience**: Gracefully intercepts `AuthenticationError`, `RateLimitError`, `APIConnectionError`, and `APIStatusError`.
- **Empty / Malformed Responses**: Validates LLM responses and provides friendly fallback notices.

### 6. Export
- **📥 Download Markdown (.md)**: A fully formatted, human-readable training document.
- **📄 Download Plain Text (.txt)**: Clean plain text version (all markdown syntax stripped).

---

## 🏗️ Architecture & Project Structure

The project uses a class-based, package-oriented `src/` layout to cleanly separate concerns:

```
routine-builder/
├── app.py                        # Minimal Streamlit entry point (~90 lines)
├── styles.css                    # Spotify-themed dark UI design system
├── requirements.txt              # Project dependencies
├── pyproject.toml                # Modern Python project configuration
├── .env.example                  # Example environment file
├── .gitignore                    # Git ignore rules
├── README.md                     # Project documentation
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── config.py             # Environment, constants, model registry
│   │   ├── prompts.py            # All LLM prompt-building logic
│   │   └── generator.py          # WorkoutGenerator class (Groq API wrapper)
│   ├── ui/
│   │   ├── state.py              # Session state init, PRESETS, archive helper
│   │   ├── components.py         # display_workout_plan(), swap_exercise_dialog()
│   │   └── views.py              # render_*_view() functions for each nav section
│   └── utils/
│       └── formatting.py         # format_plan_as_markdown(), format_plan_as_text()
└── tests/
    └── test_workout_generator.py  # Automated test suite
```

### Module Responsibilities

| Module | Responsibility |
|---|---|
| `app.py` | Page config, CSS, banner, nav sidebar, view router |
| `src/core/config.py` | Model registry, `get_api_key()`, `get_model_name()` |
| `src/core/prompts.py` | `build_workout_prompt()`, `build_swap_prompt()` |
| `src/core/generator.py` | `WorkoutGenerator` class — `generate_plan()`, `replace_exercise()` |
| `src/ui/state.py` | `init_session_state()`, `PRESETS`, `archive_current_routine()` |
| `src/ui/components.py` | Exercise card renderer, `@st.dialog` swap modal |
| `src/ui/views.py` | `render_current_routine_view()`, `render_generate_routine_view()`, etc. |
| `src/utils/formatting.py` | Pure Python JSON → Markdown / Plain Text converters |

---

## ⚡ Quickstart & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/communitywork/routine-builder.git
cd routine-builder
```

### 2. Create and Activate a Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

**Option A: Using requirements.txt (Recommended for quick setup)**
```bash
pip install -r requirements.txt
```

**Option B: Using pyproject.toml (Modern Python packaging)**
```bash
pip install -e .
```

### 4. Configure Your Groq API Key
Get your free Groq API key at [console.groq.com/keys](https://console.groq.com/keys).

Copy `.env.example` to `.env` and set your key:
```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile   # optional, defaults to this model
```

### 5. Run the Streamlit App
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## 💰 Pricing & Support

### Free Version
- Limited API calls per day
- Access to all core features
- Standard Groq models

### Premium Access
For unlimited access and priority support, contact us at **sales@fitblueprint.com**

---

## 🎨 Design & Theme

FitBlueprint features a modern Spotify-inspired dark theme with:
- Dark background (`#121212`) for reduced eye strain
- Green accent color (`#1DB954`) for primary actions and cards
- Animated exercise cards with hover-lift effects
- Glassmorphism stat boxes and badge pills
- Responsive two-column layout (navigation + content)

---

## 🧪 Running Automated Tests

```bash
python -m unittest discover tests
```

---

## 💡 Prompt Engineering Approach

The prompt design in `src/core/prompts.py` uses a **Role + Context + Constraint + Schema** framework:

1. **Role Definition**: Assigns the model the role of an elite CSCS coach.
2. **Strict Negative Constraints**: Explicitly warns the model against prescribing equipment outside what the user specified.
3. **Condition-Specific Routing**: If injuries or limitations are provided, the prompt instructs the model to omit contraindicated movements and attach safety cues.
4. **JSON Schema Enforcement**: Instructs the model to return a fully structured JSON object (not markdown tables), which is then parsed, validated, and rendered as rich UI cards.
5. **Variation Seeding**: The regenerate endpoint injects a `variation_seed_hint` that nudges the model to produce a meaningfully different split.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
