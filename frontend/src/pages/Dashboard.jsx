
import { useEffect, useState } from 'react'
import { apiFetch } from '../api'
import './Dashboard.css'

function Dashboard() {
  const [user, setUser] = useState(null)
  const [analytics, setAnalytics] = useState(null)
  const [reminders, setReminders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [reminderError, setReminderError] = useState('')

  useEffect(() => {
    async function fetchDashboard() {
      try {
        const userResponse = await apiFetch('/auth/me')

        if (!userResponse.ok) {
          window.location.href = '/login'
          return
        }

        const userData = await userResponse.json()
        setUser(userData)

        const analyticsResponse = await apiFetch(
          '/applications/analytics'
        )

        if (!analyticsResponse.ok) {
          throw new Error('Could not load career statistics.')
        }

        const analyticsData = await analyticsResponse.json()
        setAnalytics(analyticsData)

        // Fetch reminders separately so reminder errors
        // do not prevent the main dashboard from loading.
        try {
          const remindersResponse = await apiFetch('/reminders/')

          if (!remindersResponse.ok) {
            throw new Error('Could not load reminders.')
          }

          const remindersData = await remindersResponse.json()
          setReminders(Array.isArray(remindersData) ? remindersData : [])
        } catch (err) {
          setReminderError(err.message)
        }

      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchDashboard()
  }, [])

  async function handleLogout() {
    try {
      const response = await apiFetch('/auth/logout', {
        method: 'POST',
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Logout failed')
      }

    } catch (err) {
      console.error('Logout error:', err)
    }

    window.location.href = '/login'
  }

  if (loading) {
    return <div className="dashboard-loading">Loading dashboard...</div>
  }

  if (error) {
    return <div className="dashboard-error">{error}</div>
  }

  const stats = [
    {
      title: 'Total Applications',
      value: analytics?.total_applications ?? 0,
      icon: '📁'
    },
    {
      title: 'Interviews',
      value: analytics?.interviews ?? 0,
      icon: '🤝'
    },
    {
      title: 'Offers',
      value: analytics?.offers ?? 0,
      icon: '🏆'
    },
    {
      title: 'Rejections',
      value: analytics?.rejections ?? 0,
      icon: '❌'
    }
  ]

  const now = new Date()

  const pendingReminders = reminders.filter(
    reminder => !reminder.is_completed
  )

  const overdueReminders = pendingReminders.filter(
    reminder => new Date(reminder.reminder_date) < now
  )

  const upcomingReminders = pendingReminders
    .filter(reminder => new Date(reminder.reminder_date) >= now)
    .sort(
      (a, b) =>
        new Date(a.reminder_date) - new Date(b.reminder_date)
    )
    .slice(0, 5)

  const formatReminderDate = (date) => {
    return new Date(date).toLocaleString('en-IN', {
      dateStyle: 'medium',
      timeStyle: 'short'
    })
  }

  return (
    <div className="dashboard-layout">

      <aside className="dashboard-sidebar">
        <h2 className="dashboard-logo">
          CareerPilot<span> AI</span>
        </h2>

        <nav className="sidebar-nav">
          <a href="/dashboard" className="active">Dashboard</a>
          <a href="/applications">My Applications</a>
          <a href="/resume-analyzer">Resume Analyzer</a>
          <a href="/interviews">Interview Prep</a>
          <a href="/analytics">Analytics</a>
          <a href="/reminders">My Reminders</a>
        </nav>

        <button className="logout-button" onClick={handleLogout}>
          Logout
        </button>
      </aside>

      <main className="dashboard-main">

        <header className="dashboard-header">
          <div className="welcome-text">
            <h1>Welcome, {user?.full_name}!</h1>
            <p>Here's your career progress at a glance.</p>
          </div>

          <div className="user-info">
            <span className="user-avatar">
              {user?.full_name?.charAt(0).toUpperCase()}
            </span>
            <span>{user?.email}</span>
          </div>
        </header>

        <section className="dashboard-stats">
          {stats.map((stat) => (
            <div className="dashboard-stat-card" key={stat.title}>
              <span className="dashboard-stat-icon">{stat.icon}</span>
              <h2>{stat.value}</h2>
              <p>{stat.title}</p>
            </div>
          ))}
        </section>

        <section className="career-overview">
          <h2>Career Overview</h2>
          <p>
            Keep track of your job search activities and work towards
            your career goals.
          </p>

          <div className="overview-highlight">
            <div>
              <span>Interview Conversion Rate</span>
              <h2>{analytics?.interview_conversion_rate ?? 0}%</h2>
            </div>
            <a href="/analytics">View Detailed Analytics →</a>
          </div>
        </section>

        {/* REMINDERS OVERVIEW */}

        <section className="dashboard-reminders">
          <div className="dashboard-reminders-header">
            <div>
              <h2>Reminders Overview</h2>
              <p>Stay prepared for your upcoming career activities.</p>
            </div>

            <a href="/reminders" className="view-reminders-link">
              View All Reminders →
            </a>
          </div>

          <div className="dashboard-reminder-stats">
            <div className="dashboard-reminder-stat">
              <span>📌</span>
              <div>
                <h3>{pendingReminders.length}</h3>
                <p>Pending</p>
              </div>
            </div>

            <div className="dashboard-reminder-stat">
              <span>⏰</span>
              <div>
                <h3>{upcomingReminders.length}</h3>
                <p>Upcoming</p>
              </div>
            </div>

            <div className="dashboard-reminder-stat">
              <span>⚠️</span>
              <div>
                <h3>{overdueReminders.length}</h3>
                <p>Overdue</p>
              </div>
            </div>
          </div>

          <div className="dashboard-upcoming-card">
            <h3>Upcoming Reminders</h3>

            {reminderError ? (
              <p className="dashboard-reminder-empty">
                Unable to load reminders. Please visit My Reminders.
              </p>
            ) : upcomingReminders.length === 0 ? (
              <p className="dashboard-reminder-empty">
                No upcoming reminders. Add one to stay organized!
              </p>
            ) : (
              <div className="dashboard-upcoming-list">
                {upcomingReminders.map(reminder => (
                  <div
                    className="dashboard-upcoming-item"
                    key={reminder.id}
                  >
                    <div className="dashboard-upcoming-info">
                      <h4>{reminder.title}</h4>
                      <p>{reminder.description || 'No description provided.'}</p>
                      <span>{reminder.reminder_type}</span>
                    </div>

                    <div className="dashboard-upcoming-date">
                      <span>
                        {formatReminderDate(reminder.reminder_date)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {overdueReminders.length > 0 && (
              <div className="dashboard-overdue-notice">
                <strong>Attention:</strong> You have {overdueReminders.length}
                {' '}overdue reminder{overdueReminders.length > 1 ? 's' : ''}.
                <a href="/reminders"> Review now</a>
              </div>
            )}
          </div>
        </section>

        <section className="dashboard-quick-links">
          <h2>Quick Access</h2>

          <div className="quick-link-grid">
            <a href="/applications" className="quick-link-card">
              <span>📋</span>
              <h3>Manage Applications</h3>
              <p>Track your job applications.</p>
            </a>

            <a href="/resume-analyzer" className="quick-link-card">
              <span>📄</span>
              <h3>Analyze Resume</h3>
              <p>Check your resume against a job description.</p>
            </a>

            <a href="/interviews" className="quick-link-card">
              <span>🎯</span>
              <h3>Practice Interviews</h3>
              <p>Prepare for your upcoming interviews.</p>
            </a>

            <a href="/analytics" className="quick-link-card">
              <span>📊</span>
              <h3>Career Analytics</h3>
              <p>Review your job search performance.</p>
            </a>

            <a href="/reminders" className="quick-link-card">
              <span>🔔</span>
              <h3>My Reminders</h3>
              <p>Manage interviews, deadlines and follow-ups.</p>
            </a>
          </div>
        </section>

      </main>
    </div>
  )
}

export default Dashboard
