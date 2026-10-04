# Intelligent Health Management Design System
English | [中文](README.cn.md)

An intelligent health management application built on Python and PySide6 (Qt 6), integrating AI large language models to provide users with personalized health assessment and exercise prescription services.

## Features

### 🏥 Health Assessment
- Cardiovascular health assessment
- Metabolic health analysis
- Body composition analysis
- AI-driven health report generation

### 🏃 Exercise Prescription
- Personalized exercise recommendations
- Targeted training plans
- Scientific fitness guidance

### 📈 History & Trends
- Every report is saved together with the data it was based on
- View or delete past reports, and reload the last data into the form
- Trend charts for weight, BMI, blood pressure, heart rate, glucose and more, with reference lines

### 🔐 User System
- Registration/login with input validation
- "Remember me" via a random login token (no plain-text password is stored)
- Passwords hashed with bcrypt

### 🎨 Interface Features
- Material-style UI (qt-material)
- AI output is streamed: the report appears as it is generated and can be stopped at any time
- Reports rendered from Markdown, with section navigation, printing and PDF export

## Tech Stack

| Category | Technology |
|------|------|
| GUI Framework | PySide6 + qt-material + QtCharts |
| AI Integration | Zhipu AI GLM-4 (`zhipuai`), switchable to any OpenAI-compatible LLM |
| Database | SQLite |
| ORM | SQLAlchemy 2.x |
| Password Hashing | bcrypt |
| Configuration | python-dotenv |
| Packaging | PyInstaller |
| CI | GitHub Actions |

## Directory Structure

```
project/
├── main.py              # Program entry
├── config.py            # Configuration (paths, database, AI service), read from .env
├── login03.py           # Login/Registration interface
├── main_window.py       # Health data input window
├── report_page.py       # Shared report page (navigation, streaming, Markdown rendering, print/PDF)
├── health_page.py       # Health assessment report page
├── sport_page.py        # Exercise prescription report page
├── history_page.py      # History list and trend charts
├── fresh.py             # Loading animation + background streaming worker thread
├── llm_utils.py         # LLM client (Zhipu AI)
├── prompts.py           # Input fields, prompt building, response section parsing
├── user_service.py      # User service (registration, login, remember-me token)
├── record_service.py    # Health record service (save, list, delete, trends)
├── models.py            # Data models
├── db_utils.py          # Database initialization
├── base.py              # SQLAlchemy declarative base
├── assets/              # Images
├── tests/               # Unit and GUI tests
├── health_app.spec      # PyInstaller packaging config
├── .github/workflows/   # CI: tests, Windows build
├── requirements.txt     # Dependencies
└── .env.example         # Configuration template
```

## Download (Windows, no Python needed)

1. Open [Build Windows App](https://github.com/chillboy67/computer_design/actions/workflows/build.yml), click the latest successful run (green ✓) and download `HealthApp-windows` under **Artifacts** at the bottom of the page (requires a GitHub login)
2. Unzip it, open the `HealthApp` folder and copy `.env.example` to `.env`
3. Open `.env` in Notepad and put your API key after `LLM_API_KEY=` (see [Configuration](#configuration-instructions))
4. Double-click `HealthApp.exe` and register an account on first use

Notes:
- The app is not code-signed, so Windows may show "Windows protected your PC" on first launch; click "More info → Run anyway"
- Accounts and history are stored in `health_db.sqlite` in the same folder; keep it and `.env` when upgrading
- Downloads are kept for 90 days; after that, click **Run workflow** on the page above to build again

## Run from Source

### Environment Requirements
- Python 3.10+

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configuration Instructions

Copy `.env.example` to `.env` and fill it in. Zhipu AI is used by default, so only the API key from [open.bigmodel.cn](https://open.bigmodel.cn/) is needed:

```env
LLM_API_KEY=your_api_key
```

Any other OpenAI-compatible LLM service works too, without code changes — just set the endpoint and model:

| Service | LLM_BASE_URL | LLM_MODEL |
|------|------|------|
| Zhipu AI (default) | leave empty | `glm-4-plus` |
| DeepSeek | `https://api.deepseek.com` | `deepseek-chat` |
| Qwen (Tongyi Qianwen) | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` |
| Kimi | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` |

```env
# Example: DeepSeek
LLM_API_KEY=your_deepseek_key
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

Check each provider's documentation for the current endpoint and model names. The old `ZHIPUAI_API_KEY` setting still works.

Optional: set `DEFAULT_ADMIN_USERNAME` and `DEFAULT_ADMIN_PASSWORD` to create a demo account on first launch.

`.env` is ignored by git, so your key will not be committed.

### Run Application

```bash
python main.py
```

### Run Tests

```bash
pip install -r requirements-dev.txt
pytest
```

GUI tests use Qt's offscreen mode, so no window will pop up.

### Package as an Executable

```bash
pip install pyinstaller
pyinstaller health_app.spec
```

The app is generated in `dist/HealthApp/` (run `HealthApp.exe` on Windows). Put your `.env` next to the executable; the database is created there as well.

GitHub Actions runs the tests on every push. To get a Windows build without a Windows machine, click **Run workflow** on the [Build Windows App](https://github.com/chillboy67/computer_design/actions/workflows/build.yml) page and download the `HealthApp-windows` artifact.

## User Guide

### Login/Register
1. Upon first launch, enter the login page
2. Click "Register" to create a new account
3. Check "Remember password" to log in without typing the password next time

### Health Assessment
1. Enter the main interface after logging in
2. Fill in age, height and weight (required) and any clinical data you have
3. Click "Health Assessment"; AI generates a report covering cardiovascular health, glucose & lipid metabolism and body composition

### Get Exercise Prescription
1. Fill in the same health data
2. Click "Exercise Prescription" to get exercise type, frequency, intensity and precautions
3. Print the report or save it as PDF

### History & Trends
1. Click "History & Trends" to see all past reports
2. Double-click a record to reopen its report, or select a metric to see how it changes over time
3. Click "Load last data" in the main window to fill the form with your previous data

## System Architecture

```
┌─────────────────┐     ┌──────────────────┐
│   MainWindow    │────▶│  HealthPage      │
│                 │     │  - Cardiovascular│
├─────────────────┤     │  - Metabolic     │
│  User Auth      │────▶│  - Body Comp     │
│  - Login        │     └──────────────────┘
│  - Register     │     
├─────────────────┤     ┌─────────────────┐
│  Service Layer  │────▶│  SportPage      │
│  - UserService  │     │  - Exercise Rx  │
│  - DbUtils      │     │  - Training Plan│
└─────────────────┘     └─────────────────┘

        AI Service
    ┌─────────────┐
    │  get_LLM_   │
    │  response() │
    └─────────────┘
```

## API Integration

The service used is decided by `LLM_API_KEY`, `LLM_BASE_URL` and `LLM_MODEL` in `.env`:

```python
from llm_utils import get_health_assessment, stream_health_assessment
from prompts import build_health_prompt

data = {"gender": "男", "age": 30, "height": 175, "weight": 70}
report = get_health_assessment(build_health_prompt(data))  # full Markdown text

for piece in stream_health_assessment(build_health_prompt(data)):  # streaming
    print(piece, end="")
```

The system prompts ask the model to answer in Markdown with fixed `##` headings, which `prompts.split_sections()` uses to split the report into sections.

## Database Design

### Users Table (`users`)
- `id`: Primary Key
- `username`: Username (unique)
- `email`: Email (optional)
- `password_hash`: bcrypt hash
- `remember_token_hash`: SHA-256 of the "remember me" token
- `created_at` / `last_login`: Timestamps

### Health Records Table (`health_records`)
- `id`: Primary Key
- `user_id`: Foreign key linking to user
- `record_type`: `health` (assessment) or `sport` (exercise prescription)
- `gender` / `age` / `height` / `weight` / `bmi` / `body_fat` / `muscle_mass` / `waist`
- `sbp` / `dbp` / `heart_rate` / `glucose` / `triglycerides`
- `report_text`: The generated report (Markdown)
- `created_at`: Record timestamp

Missing columns are added automatically on startup, so databases created by older versions keep working.

## Security Features

- 🔒 Passwords hashed with bcrypt
- 🔑 "Remember me" stores a random token locally and only its hash in the database, never the password
- 🗝️ API keys and other secrets are read from `.env`, which is not committed

## Disclaimer

Reports are generated by AI for health management reference only and are not a substitute for diagnosis or treatment by a doctor.

## Development Roadmap

- [x] Save assessment history and show indicator trends
- [x] Streaming output
- [x] Windows executable packaging
- [ ] Add more health indicator assessments
- [ ] Integrate wearable device data
- [ ] Add multi-language support

## License

This project is open source under the MIT License.

## Contributors

Welcome to submit Issues and Pull Requests to help improve the project!

original project link https://gitee.com/haotian-tang/computer_design
