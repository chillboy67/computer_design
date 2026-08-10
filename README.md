# Intelligent Health Management Design System
English | [中文](README.cn.md)

An intelligent health management application built on Python and PyQt5, integrating AI large language models to provide users with personalized health assessment and exercise prescription services.

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
- Secure registration/login
- Automatic credential saving
- User history management

### 🎨 Interface Features
- Modern UI design
- Smooth loading animations
- Responsive interaction experience

## Tech Stack

| Category | Technology |
|------|------|
| GUI Framework | PyQt5 |
| AI Integration | Tongyi Qianwen/Other LLM APIs |
| Database | SQLite |
| ORM | SQLAlchemy |

## Directory Structure

```
project/
├── main.py           # Program entry
├── main_window.py    # Main window
├── login03.py        # Login/Registration interface
├── health_page.py    # Health assessment page
├── sport_page.py     # Exercise prescription page
├── fresh.py          # Loading animation/Image processing
├── ai_for_halthy.py  # AI integration
├── llm_utils.py      # LLM utility class
├── user_service.py   # User service
├── models.py         # Data models
├── db_utils.py       # Database utilities
├── .env              # Environment configuration
└── users.db          # User database
```

## Quick Start

### Environment Requirements
- Python 3.8+
- PyQt5
- requests library

### Install Dependencies

```bash
pip install PyQt5 requests sqlalchemy
```

### Configuration Instructions

Configure AI services in the `.env` file:

```env
AI_API_KEY=your_api_key
AI_ENDPOINT=your_endpoint
```

### Run Application

```bash
python main.py
```

## User Guide

### Login/Register
1. Upon first launch, enter the login page
2. Click "Register" to create a new account
3. After logging in, choose to save credentials

### Health Assessment
1. Enter the main interface after logging in
2. Click "Health Assessment" to start evaluation
3. AI will generate a health report based on input

### Get Exercise Prescription
1. After completing health assessment
2. Click "Exercise Prescription" to get personalized advice
3. Can print or save the report

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

The project supports various AI service integration methods:

```python
from llm_utils import get_LLM_response

# Call AI to get health advice
response = get_LLM_response("Please analyze the user's cardiovascular health status...")
```

## Database Design

### Users Table
- `id`: Primary Key
- `username`: Username
- `email`: Email
- `password_hash`: Encrypted password
- `last_login`: Last login time

### Health Records Table
- `id`: Primary Key
- `user_id`: Foreign key linking to user
- `Assessment Data`: Stored in JSON format
- `Created Time`: Record timestamp

## Security Features

- 🔒 Passwords stored using hash encryption
- 🔑 Credentials saved locally encrypted
- ✅ Special verification for admin accounts

## Development Roadmap

- [ ] Add more health indicator assessments
- [ ] Support data export functionality
- [ ] Integrate wearable device data
- [ ] Add multi-language support

## License

This project is open source under the MIT License.

## Contributors

Welcome to submit Issues and Pull Requests to help improve the project!
