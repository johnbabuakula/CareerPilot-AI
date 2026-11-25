
import { BrowserRouter, Routes, Route } from 'react-router-dom'

import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Applications from './pages/Applications'
import ResumeAnalyzer from './pages/ResumeAnalyzer'
import InterviewPrep from './pages/InterviewPrep'
import Analytics from './pages/Analytics'
import Reminders from './pages/Reminders'

import './App.css'

function Home() {
  return (
    <div className="app">
      <nav className="navbar">
        <h2>CareerPilot<span> AI</span></h2>

        <div className="nav-links">
          <a href="#features">Features</a>
          <a href="#about">About</a>
          <a href="/login" className="login-btn">Login</a>
          <a href="/register" className="signup-btn">Get Started</a>
        </div>
      </nav>

      <main className="hero">
        <div className="hero-content">
          <p className="tagline">YOUR AI-POWERED CAREER COMPANION</p>

          <h1>
            Take Control of Your
            <span> Career Journey.</span>
          </h1>

          <p className="description">
            Track job applications, analyze your resume, and prepare
            for interviews with AI-powered assistance — all in one place.
          </p>

          <div className="hero-buttons">
            <a href="/register" className="primary-btn">Get Started Free →</a>
            <a href="#features" className="secondary-btn">Explore Features</a>
          </div>

          <p className="note">Your journey to your dream job starts here.</p>
        </div>

        <div className="hero-card">
          <div className="card-header">
            <h3>Career Dashboard</h3>
            <span>● Live Overview</span>
          </div>

          <div className="stats">
            <div className="stat-box">
              <h2>12</h2>
              <p>Applications</p>
            </div>
            <div className="stat-box">
              <h2>04</h2>
              <p>Interviews</p>
            </div>
            <div className="stat-box">
              <h2>85%</h2>
              <p>Resume Score</p>
            </div>
          </div>

          <div className="activity">
            <h3>Recent Activity</h3>
            <p>✓ Resume analysis completed</p>
            <p>✓ Interview preparation started</p>
            <p>✓ New application added</p>
          </div>
        </div>
      </main>

      <section className="features" id="features">
        <h2>Everything You Need to Move Forward</h2>
        <p>Smart tools to support every step of your career journey.</p>

        <div className="feature-grid">
          <div className="feature-box">
            <h3>📄 AI Resume Analyzer</h3>
            <p>Analyze your resume and discover missing skills.</p>
          </div>

          <div className="feature-box">
            <h3>🎯 Job Tracker</h3>
            <p>Manage and track your job applications easily.</p>
          </div>

          <div className="feature-box">
            <h3>🤖 AI Interview Assistant</h3>
            <p>Practice interview questions and improve your answers.</p>
          </div>
        </div>
      </section>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/applications" element={<Applications />} />
        <Route path="/resume-analyzer" element={<ResumeAnalyzer />} />
        <Route path="/interviews" element={<InterviewPrep />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/reminders" element={<Reminders />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
