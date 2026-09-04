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
The core engine (`workout_generator.py`) acts as a Certified Strength and Conditioning Specialist (CSCS):
- **100% Constraint Compliance**: Equipment choices are strictly enforced (e.g., no barbells or cable machines if the user selected "Home dumbbells").
- **Exact Frequency Match**: Generates a Day 1 through Day N plan matching the chosen days per week, with intelligent recovery distribution.
- **Injury Adaptation & Medical Disclaimer**: Actively omits contraindicated exercises and includes a medical disclaimer whenever injuries or physical limitations are specified.
- **Structured Markdown Tables**: Clear, clean day-by-day breakdowns with Exercise, Sets, Reps/Time, Rest, and Form Coaching Cues.

### 3. Comprehensive Error Handling
- **Invalid / Empty Inputs**: Validates user selections (e.g., 0 days selected, missing fields) and displays friendly Streamlit warning alerts without crashing.
- **API Failure Resilience**: Gracefully intercepts `AuthenticationError` (bad/expired key), `RateLimitError`, `APIConnectionError` (network failure), and `APIStatusError`.
- **Empty / Malformed Responses**: Validates LLM responses and provides friendly fallback notices.

### 4. 🚀 Stretch Goals Implemented
- **🔄 Regenerate Variation**: Generate a fresh, alternative workout split while preserving user constraints.
- **💾 Session State Persistence**: Generated workouts persist across widget interactions and reruns via `st.session_state`.
- **📥 One-Click Export**: Download the customized routine as `.md` (Markdown) or `.txt` (Plain Text).
- **🔀 Exercise Swap Assistant**: Select any individual exercise from the plan, state a reason/discomfort, and receive 2-3 CSCS-approved direct substitutes matching the equipment and injury constraints.

---

## 🏗️ Architecture & Project Structure

```
routine-builder/
├── app.py                      # Streamlit web UI and session management
├── workout_generator.py        # Typed core logic, prompt engineering & Groq API caller
├── requirements.txt            # Project dependencies
├── .env.example                # Example environment file
├── .gitignore                  # Git ignore rules
├── README.md                   # Project documentation
├── styles.css                  # Spotify-themed custom styling
└── tests/
    └── test_workout_generator.py # Automated test suite (validation, prompts, error handling)
```

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

You can install dependencies using either method:

**Option A: Using requirements.txt (Recommended for quick setup)**
```bash
pip install -r requirements.txt
```

**Option B: Using pyproject.toml (Modern Python packaging)**
```bash
pip install -e .
```

Both methods install the same dependencies. The `pyproject.toml` file provides modern Python project configuration, while `requirements.txt` offers compatibility with older tools and deployment platforms.

### 4. Configure Your Groq API Key
Get your free Groq API key at [console.groq.com/keys](https://console.groq.com/keys).

You have two options to provide the key:
- **Option A (Recommended)**: Copy `.env.example` to `.env` and set your key:
  ```env
  GROQ_API_KEY=gsk_your_actual_groq_api_key_here
  ```
- **Option B**: Enter your key directly in the app's sidebar when prompted.

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
- Dark background (#121212) for reduced eye strain
- Green accent color (#1DB954) for primary actions
- Clean, professional UI with rounded corners
- Responsive design for all screen sizes

---

## 🧪 Running Automated Tests

Run the unit test suite to verify validation, prompt generation, and error handling:
```bash
python -m unittest discover tests
```
Output:
```
.........
----------------------------------------------------------------------
Ran 9 tests in 1.07s

OK
```

---

## 💡 Prompt Engineering Approach

The prompt design uses a **Role + Context + Constraint + Schema** framework:

1. **Role Definition**: Assigns the model the role of an elite CSCS coach, setting high standards for exercise selection, rep ranges, and rest intervals.
2. **Strict Negative Constraints**: Explicitly warns the model against prescribing equipment outside what the user specified.
3. **Condition-Specific Routing**: If injuries or limitations are provided, the prompt instructs the model to omit contraindicated movements and attach safety coaching cues to the affected muscle groups.
4. **Structured Output Enforcement**: Instructs the model to generate day-by-day markdown tables (`| Exercise | Sets | Reps | Rest | Notes |`) rather than walls of text.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
