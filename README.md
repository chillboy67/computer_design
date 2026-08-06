# YuanQi Compass — AI-Powered Personal Health Management System

> A full-stack desktop application that delivers personalized health assessments and exercise prescriptions through LLM integration, built for the National College Computer Design Competition.

---

## Core Features

- **Secure Authentication** — Password hashing with `bcrypt`; session-aware login/registration flow built on top of SQLAlchemy ORM
- **Health Data Dashboard** — Users log daily vitals (BMI, blood pressure, sleep, activity) with persistent SQLite storage and real-time visual feedback
- **AI Health Report Generation** — Structured prompts sent to ZhipuAI's GLM model produce individualized health assessments and actionable recommendations
- **Personalized Exercise Prescriptions** — The LLM reasons over user health profiles to generate sport-specific training plans tailored to fitness level and goals
- **Refresh & History View** — Dedicated buffer/refresh page (`fresh.py`) enables historical data review and report regeneration without re-entering data
- **Modular Desktop UI** — Multi-page PySide6 interface with clean page routing via `main_window.py`, separating concerns across login, health, and sport modules

---

## Tech Stack & Architecture

| Layer | Technology |
|---|---|
| UI Framework | PySide6 (Qt6 for Python) |
| AI / LLM | ZhipuAI Python SDK (GLM-4 series) |
| ORM & Database | SQLAlchemy + SQLite |
| Auth & Security | bcrypt password hashing |
| Config Management | python-dotenv (`.env` for API keys) |
| Language | Python 3.10+ |

**Architecture:** The app follows a layered pattern — `models.py` defines the data schema, `db_utils.py` handles all database operations, `user_service.py` encapsulates business logic for user management, `llm_utils.py` abstracts all LLM calls, and page modules (`health_page.py`, `sport_page.py`) own only UI rendering.

---

## AI Integration Highlights

`llm_utils.py` acts as the dedicated LLM service layer:

- **Context-Aware Prompting** — User health records are serialized and injected into system prompts, giving the model full context before generating any output
- **Structured Output Parsing** — LLM responses are parsed and rendered back into the UI as formatted health reports
- **Separation of Concerns** — All ZhipuAI API calls are centralized, making it trivial to swap models or providers without touching UI code
- **Async-Ready Design** — LLM calls are isolated from the UI thread to keep the interface responsive during inference

---

## Why This Project Demonstrates Engineering Depth

This is not a prototype — it is a **production-quality competition submission** with real users, real data persistence, and a real AI backend. It demonstrates:

- **Full-stack ownership**: from database schema design to LLM prompt engineering to pixel-level UI
- **AI product thinking**: integrating an LLM not as a gimmick but as a functional feature that processes domain-specific data
- **Engineering discipline**: environment-based config, modular file structure, ORM abstraction, and secure auth from day one

---

## Repository Structure

```
computer_design/
├── main.py              # App entry point
├── main_window.py       # Central page router and window manager
├── login03.py           # Login & registration UI
├── health_page.py       # Health data input and display
├── sport_page.py        # Exercise prescription page
├── fresh.py             # History / refresh buffer page
├── ai_for_halthy.py     # AI report trigger and rendering
├── llm_utils.py         # ZhipuAI API abstraction layer
├── user_service.py      # User business logic
├── db_utils.py          # Database CRUD operations
├── models.py            # SQLAlchemy ORM models
├── base.py              # Declarative base setup
├── .env                 # API keys (not committed)
├── pict/                # UI assets
└── pict 02/             # Login screen assets
```

---

## Getting Started

```bash
# 1. Clone the repository
git clone https://github.com/chillboy67/computer_design.git
cd computer_design

# 2. Install dependencies
pip install pyside6 sqlalchemy bcrypt zhipuai python-dotenv

# 3. Configure your ZhipuAI API key
echo "ZHIPUAI_API_KEY=your_key_here" > .env

# 4. Launch the application
python main.py
```

> Requires Python 3.10+. A valid ZhipuAI API key is needed for AI report generation.

---

## Screenshots

| Login | Health Dashboard | AI Report |
|---|---|---|
| *(coming soon)* | *(coming soon)* | *(coming soon)* |

---

*Built with Python, PySide6, and ZhipuAI. Competition entry — National College Computer Design Competition.*

Origin from https://gitee.com/haotian-tang/computer_design
