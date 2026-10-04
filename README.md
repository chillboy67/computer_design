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

### 🔐 User System
- Registration/login with input validation
- "Remember me" via a random login token (no plain-text password is stored)
- Passwords hashed with bcrypt

### 🎨 Interface Features
- Material-style UI (qt-material)
- AI requests run in a background thread with a cancellable loading animation
- Reports rendered from Markdown, with section navigation, printing and PDF export

## Tech Stack

| Category | Technology |
|------|------|
| GUI Framework | PySide6 + qt-material |
| AI Integration | Zhipu AI GLM-4 (`zhipuai`) |
| Database | SQLite |
| ORM | SQLAlchemy 2.x |
| Password Hashing | bcrypt |
| Configuration | python-dotenv |

## Directory Structure

```
project/
├── main.py              # Program entry
├── config.py            # Configuration (paths, database, AI service), read from .env
├── login03.py           # Login/Registration interface
├── main_window.py       # Health data input window
├── report_page.py       # Shared report page (navigation, Markdown rendering, print/PDF)
├── health_page.py       # Health assessment report page
├── sport_page.py        # Exercise prescription report page
├── fresh.py             # Loading animation + background AI worker thread
├── llm_utils.py         # LLM client (Zhipu AI)
├── prompts.py           # Input fields, prompt building, response section parsing
├── user_service.py      # User service (registration, login, remember-me token)
├── models.py            # Data models
├── db_utils.py          # Database initialization
├── base.py              # SQLAlchemy declarative base
├── assets/              # Images
├── tests/               # Unit tests
├── requirements.txt     # Dependencies
└── .env.example         # Configuration template
```

## Quick Start

### Environment Requirements
- Python 3.9+

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configuration Instructions

Copy `.env.example` to `.env` and fill in your Zhipu AI API key ([open.bigmodel.cn](https://open.bigmodel.cn/)):

```env
ZHIPUAI_API_KEY=your_api_key
LLM_MODEL=glm-4-plus
# Optional: create a demo account on first launch
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=your_demo_password
```

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

```python
from llm_utils import get_health_assessment, get_sport_prescription
from prompts import build_health_prompt

data = {"gender": "男", "age": 30, "height": 175, "weight": 70}
report = get_health_assessment(build_health_prompt(data))  # Markdown text
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
- `sbp` / `dbp` / `glucose` / `triglycerides`: Key indicators
- `created_at`: Record timestamp

Missing columns are added automatically on startup, so databases created by older versions keep working.

## Security Features

- 🔒 Passwords hashed with bcrypt
- 🔑 "Remember me" stores a random token locally and only its hash in the database, never the password
- 🗝️ API keys and other secrets are read from `.env`, which is not committed

## Disclaimer

Reports are generated by AI for health management reference only and are not a substitute for diagnosis or treatment by a doctor.

## Development Roadmap

- [ ] Save assessment history and show indicator trends
- [ ] Add more health indicator assessments
- [ ] Integrate wearable device data
- [ ] Add multi-language support

## License

This project is open source under the MIT License.

## Contributors

Welcome to submit Issues and Pull Requests to help improve the project!

original project link https://gitee.com/haotian-tang/computer_design
