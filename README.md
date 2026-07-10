# InterviewForge AI - Full-Stack Platform

InterviewForge AI is an AI-powered interview preparation platform that generates adaptive technical interviews, evaluates answers, tracks performance, and creates personalized study roadmaps.

This repository covers **Phase 1: Authentication Module** setup and service-layer backend implementation.

---

## Architecture

```
Frontend (React)
      ↓
FastAPI Backend
      ↓
Service Layer  ← (AuthService, ResumeService, InterviewService, etc.)
      ↓
AI Layer       ← (app/ai package: AIClient, prompts, parser, retry)
      ↓
Database (PostgreSQL / SQLite fallback) + Google GenAI SDK
```

---

## Database Schema (SQLAlchemy)

The application defines the following tables:
1. **users**: Primary user identity, emails, and bcrypt-hashed credentials.
2. **resumes**: Extracted text and parsed fields (skills, projects, strengths, focus areas).
3. **interview_sessions**: Holds role, difficulty, and states (`CREATED`, `ACTIVE`, `EVALUATING`, `COMPLETED`).
4. **interview_messages**: Tracks specific chat history of questions, answers, and evaluations.
5. **reports**: Detailed recommendations, strengths, weaknesses, and roadmaps.
6. **skill_scores**: Dynamic skill tracker containing performance score trends per technical topic (e.g. Graphs: 72, DBMS: 67).

---

## Backend Directory Layout (Phase 1)

```
interview-forge-ai/
└── backend/
    ├── app/
    │   ├── main.py            # FastAPI configuration & CORS
    │   ├── config.py          # Settings & Database URL fallback resolver
    │   ├── database.py        # SQLAlchemy Engine & session provider
    │   ├── models.py          # Relational Database Models
    │   ├── schemas.py         # Input/Output Pydantic Validation Schemas
    │   ├── security.py        # Password hashing & JWT encoder/decoder
    │   ├── ai/                # Centralized AI Module (google-genai)
    │   │   ├── client.py      # Reusable AIClient for all AI API calls
    │   │   ├── prompts.py     # Prompt templates
    │   │   ├── parser.py      # JSON and Markdown parsing
    │   │   └── retry.py       # Exponential backoff
    │   ├── routers/
    │   │   └── auth.py        # Registration, login & profile endpoints
    │   └── services/
    │       ├── auth_service.py # User registration and login business logic
    │       └── ...            # Architecture-compliant stubs for other services
    ├── requirements.txt
    └── .env
```

---

## Setup & Local Installation

### Prerequisites
- Python 3.10+
- Virtual environment tool (`venv`)

### Installation Steps

1. **Clone or Navigate to Project Directory**:
   Set `interview-forge-ai` as your active workspace directory.

2. **Navigate to backend**:
   ```bash
   cd backend
   ```

3. **Create and Activate Virtual Environment**:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux**:
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Environment Variables**:
   Create a `.env` file from the template:
   ```bash
   cp .env.example .env
   ```
   *Note: If `DATABASE_URL` is omitted, the application automatically boots in SQLite fallback mode, creating a local database file `interview_forge.db` inside the backend folder on startup.*
   
   **Mock Mode:** Set `AI_MOCK_MODE=true` in your `.env` file to bypass live Gemini API calls and save quota during local development. This mode returns realistic canned responses for all AI interactions and is highly recommended for UI/UX testing.

6. **Run Backend Server**:
   ```bash
   uvicorn app.main:app --reload
   ```
   The backend API will run on `http://127.0.0.1:8000`.
   Interactive Swagger docs will be available at `http://127.0.0.1:8000/docs`.

---

## API Documentation (Authentication Module)

### 1. User Registration
- **Endpoint**: `POST /api/auth/register`
- **Request Body (JSON)**:
  ```json
  {
    "name": "Jane Doe",
    "email": "jane.doe@example.com",
    "password": "securepassword123"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "id": "e6a2b8e3-54cd-4b13-9828-ea3a7263b65e",
    "name": "Jane Doe",
    "email": "jane.doe@example.com",
    "created_at": "2026-06-18T07:15:00.123456Z"
  }
  ```

### 2. User Login
- **Endpoint**: `POST /api/auth/login`
- **Request Body (JSON)**:
  ```json
  {
    "email": "jane.doe@example.com",
    "password": "securepassword123"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```

### 3. Fetch Profile (Authenticated)
- **Endpoint**: `GET /api/auth/me`
- **Headers**:
  `Authorization: Bearer <your_access_token_here>`
- **Response (200 OK)**:
  ```json
  {
    "id": "e6a2b8e3-54cd-4b13-9828-ea3a7263b65e",
    "name": "Jane Doe",
    "email": "jane.doe@example.com",
    "created_at": "2026-06-18T07:15:00.123456Z"
  }
  ```

---

## Testing

To run the automated tests (tests setup details in `backend/tests`):
```bash
pytest
```
