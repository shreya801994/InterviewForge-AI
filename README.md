# InterviewForge AI

InterviewForge AI is an advanced, AI-powered interview preparation platform that generates adaptive technical interviews, evaluates answers, tracks performance, and creates personalized study roadmaps. It bridges the gap between resume claims and technical reality by automatically parsing resumes and tailoring interviews to the candidate's exact experience level.

---

## 🌟 Key Features

*   **Intelligent Resume Analysis:** Upload your PDF resume to instantly extract skills, evaluate projects, and receive an ATS (Applicant Tracking System) Readiness Score and formatting suggestions.
*   **Adaptive Technical Interviews:** Engage in simulated interview sessions powered by Gemini 2.5 Flash. The AI dynamically generates coding, system design, and behavioral questions tailored to your chosen role and difficulty.
*   **Comprehensive Reports:** After every session, receive a detailed evaluation including a 10-point scale score, strengths, weaknesses, and a consistency check against your resume claims.
*   **Performance Dashboard:** Track your progress over time with aggregated statistics, average scores across multiple sessions, and your historical interview timeline.
*   **Resilient AI Layer:** Built-in safeguards against API rate limits and quotas. Includes automatic retries, exponential backoff, and a graceful UI banner alerting users during Google AI Studio quota exhaustion.

---

## 🏗️ Architecture

```
Frontend (React + Vite + TailwindCSS)
      │
      ▼
FastAPI Backend (Python 3.10+)
      │
      ├─► Service Layer (AuthService, ResumeService, InterviewService, DashboardService)
      │
      ▼
AI Layer (Google GenAI SDK - gemini-2.5-flash)
      │
      ▼
Database (SQLAlchemy ORM + SQLite / PostgreSQL)
```

---

## 📁 Repository Structure

```
interview-forge-ai/
├── backend/
│   ├── app/
│   │   ├── ai/                # AI clients, prompt templates, structured parsing
│   │   ├── routers/           # FastAPI endpoints (Auth, Resume, Interview, Dashboard)
│   │   ├── services/          # Business logic and database orchestration
│   │   ├── middleware/        # Rate limiting and error handling
│   │   ├── models.py          # SQLAlchemy relational models
│   │   ├── schemas.py         # Pydantic validation schemas
│   │   └── main.py            # API Entrypoint
│   ├── tests/                 # Pytest automated test suite
│   ├── alembic/               # Database migrations
│   └── .env                   # Backend environment configuration
│
└── frontend/
    ├── src/
    │   ├── api/               # Axios client and API service wrappers
    │   ├── components/        # Reusable UI components (Navbar, Sidebar, Loaders)
    │   ├── context/           # React Context (AuthContext)
    │   ├── pages/             # Route views (Dashboard, Session, Resume, Login)
    │   └── App.jsx            # Routing and layout structure
    ├── index.html             # HTML entry point
    └── tailwind.config.js     # Tailwind design system tokens
```

---

## 🚀 Setup & Local Installation

### Prerequisites
*   **Node.js** (v18+)
*   **Python** (3.10+)
*   **Google Gemini API Key**

### 1. Clone the Repository
```bash
git clone https://github.com/shreya801994/InterviewForge-AI.git
cd InterviewForge-AI
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

**Environment Variables:**
Create a `.env` file in the `backend/` directory:
```env
ENV=development
JWT_SECRET_KEY=your_secure_random_string_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
GEMINI_API_KEY=your_google_gemini_api_key_here

# Set to true to bypass real API calls during UI testing
AI_MOCK_MODE=false
```
*Note: The app uses a local SQLite database (`interview_forge.db`) automatically if no `DATABASE_URL` is provided.*

**Start Backend Server:**
```bash
uvicorn app.main:app --reload
```
API runs at `http://127.0.0.1:8000`. Interactive docs are available at `http://127.0.0.1:8000/docs`.

### 3. Frontend Setup
Open a new terminal window:
```bash
cd frontend
npm install

# Start Frontend Dev Server
npm run dev
```
The React application will be available at `http://localhost:5173`.

---

## 🧪 Testing

### Backend Tests
The backend features a comprehensive `pytest` suite simulating end-to-end API flows, database persistence, and AI mocking.
```bash
cd backend
pytest
```

### Mock Mode
If you want to rapidly test frontend components without consuming your Gemini API quota, you can enable Mock Mode:
1. Set `AI_MOCK_MODE=true` in `backend/.env`.
2. Restart the backend server.
3. The AI layer will instantly return safe, structured mock data (e.g. 8.5/10 scores) instead of making live network requests.

---

## 🛡️ License & Contact
Created by Shreya Dubey. All rights reserved.
