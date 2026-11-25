
# CareerPilot AI 🚀

### AI-Powered Job Search & Career Management Platform

CareerPilot AI is a full-stack web application designed to help job seekers organize their job search, analyze resumes against job descriptions, prepare for interviews, manage reminders, and track career progress through analytics.

The platform brings essential job-search activities together in one place with secure authentication and an interactive dashboard.

---

## ✨ Features

### 1. User Authentication
- User registration and login
- Secure password hashing
- JWT-based authentication
- HttpOnly cookie-based sessions
- CSRF protection
- Protected routes and user-specific data

### 2. Job Application Tracker
- Create, view, update, and delete job applications
- Track company names and job roles
- Manage application statuses:
  - Applied
  - Assessment
  - Interview
  - Selected
  - Rejected
- Search and filter applications
- Kanban-style status management

### 3. Resume Analyzer
- Upload PDF resumes
- Extract resume text
- Compare resume skills with job descriptions
- Calculate skill match percentage
- Identify missing skills
- Provide skill improvement suggestions

### 4. Interview Assistant
- Prepare for interviews based on job roles and topics
- Generate questions from predefined question banks
- Submit interview answers
- Receive basic answer feedback
- Save interview sessions

### 5. Career Analytics
- Track total job applications
- View application status breakdown
- Monitor application conversion statistics
- Analyze monthly application trends
- Review company-wise application activity

### 6. Smart Reminders
- Create interview and follow-up reminders
- Set deadlines
- Update and delete reminders
- Track completed and pending tasks
- Identify overdue reminders

---

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Frontend | React 19, JavaScript |
| Frontend Tooling | Vite 8 |
| Routing | React Router |
| Backend | Python, FastAPI |
| Database | MySQL |
| ORM | SQLAlchemy |
| Authentication | JWT, HttpOnly Cookies |
| Password Security | pwdlib, Argon2 |
| CSRF Protection | Signed CSRF Tokens |
| PDF Processing | pypdf |
| API Testing | FastAPI TestClient |
| Automated Testing | Pytest |
| Version Control | Git, GitHub |

---

## 🏗️ Project Architecture

```text
CareerPilot-AI/
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── csrf.py
│   │   │   ├── dependencies.py
│   │   │   └── jwt.py
│   │   │
│   │   ├── database/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── utils/
│   │   └── main.py
│   │
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── pages/
│   │   ├── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   └── package.json
│
├── .gitignore
└── README.md
```

---

## ⚙️ Installation and Setup

### Prerequisites

Install the following:

- Python
- Node.js and npm
- MySQL Server
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/johnbabuakula/CareerPilot-AI.git

cd CareerPilot-AI
```

### 2. Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Database Configuration

Start your MySQL server and create a database:

```sql
CREATE DATABASE careerpilot;
```

Create a `.env` file inside the `backend/` directory.

Add the following configuration:

```env
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=careerpilot

SECRET_KEY=your_secure_random_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

COOKIE_SECURE=false

FRONTEND_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Replace the placeholder values with your local configuration.

Generate a strong secret key and never commit your actual `.env` file.

Ensure database tables are initialized using the database initialization module provided in the project.

### 4. Start the Backend Server

From the `backend/` directory:

```bash
python -m uvicorn app.main:app --reload
```

Backend URL:

http://localhost:8000

Interactive API documentation:

http://localhost:8000/docs

### 5. Frontend Setup

Open another terminal and navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Frontend URL:

http://localhost:5173

The frontend uses `http://localhost:8000` as its default API URL.

Configure `VITE_API_URL` if you use a different backend address.

---

## 🧪 Testing

The backend includes automated tests for:

- Authentication
- Job applications
- Interview sessions
- Reminders
- Resume analysis
- PDF parsing

Run the complete test suite:

```bash
python -m pytest tests/ -v
```

### Test Results

**57 tests passed successfully.**

---

## 🔐 Security Features

- Secure password hashing
- JWT authentication
- HttpOnly authentication cookies
- CSRF token validation
- Origin and Referer validation
- Protected API endpoints
- Environment-based configuration
- User-specific data access

---

## 🎯 Project Objectives

- Simplify job application management.
- Help candidates identify missing skills.
- Improve interview preparation.
- Organize interviews and job-search deadlines.
- Provide insights into job-search progress.
- Demonstrate practical full-stack development skills.

---

## 🚀 Future Enhancements

- LLM-powered resume feedback
- AI-based interview evaluation
- Personalized learning recommendations
- Email notifications for reminders
- Advanced career analytics
- Cloud deployment

---

## 👨‍💻 Developer

**John Babu Akula**

B.Tech – Artificial Intelligence and Machine Learning  
SRKR Engineering College

GitHub: [johnbabuakula](https://github.com/johnbabuakula)

Project Repository:  
https://github.com/johnbabuakula/CareerPilot-AI

---

## 📄 License

This project is currently available as a portfolio project. A formal open-source license can be added separately.
