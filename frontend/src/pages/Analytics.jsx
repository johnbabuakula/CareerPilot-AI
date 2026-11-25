
import { useEffect, useState } from 'react'
import { apiFetch } from '../api'
import './Analytics.css'

function Analytics() {
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function fetchAnalytics() {
      try {
        const response = await apiFetch('/applications/analytics')

        const data = await response.json()

        if (!response.ok) {
          throw new Error(data.detail || 'Could not load analytics.')
        }

        setAnalytics(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchAnalytics()
  }, [])

  if (loading) {
    return <div className="analytics-page">Loading analytics...</div>
  }

  if (error) {
    return <div className="analytics-page analytics-error">{error}</div>
  }

  if (!analytics) {
    return <div className="analytics-page">No analytics available.</div>
  }

  const stats = [
    {
      title: 'Total Applications',
      value: analytics.total_applications,
      icon: '📁'
    },
    {
      title: 'Assessments',
      value: analytics.assessments,
      icon: '📝'
    },
    {
      title: 'Interviews',
      value: analytics.interviews,
      icon: '🤝'
    },
    {
      title: 'Offers',
      value: analytics.offers,
      icon: '🏆'
    },
    {
      title: 'Rejections',
      value: analytics.rejections,
      icon: '❌'
    }
  ]

  const performanceStats = [
    {
      title: 'Interview Conversion',
      value: analytics.interview_conversion_rate,
      description: 'Applications reaching interview stage'
    },
    {
      title: 'Offer Conversion',
      value: analytics.offer_conversion_rate,
      description: 'Applications resulting in offers'
    },
    {
      title: 'Progression Rate',
      value: analytics.progression_rate,
      description: 'Applications moving beyond Applied'
    }
  ]

  const statusColors = {
    Applied: '#3b82f6',
    Assessment: '#8b5cf6',
    Interview: '#f59e0b',
    Selected: '#16a34a',
    Rejected: '#ef4444'
  }

  const monthlyMaximum = Math.max(
    1,
    ...analytics.monthly_trend.map(item => item.applications)
  )

  return (
    <div className="analytics-page">

      <div className="analytics-header">
        <h1>Career Analytics</h1>
        <p>Track your job search progress and performance.</p>
      </div>

      {/* APPLICATION STATISTICS */}
      <div className="analytics-stats">
        {stats.map((stat) => (
          <div className="analytics-stat-card" key={stat.title}>
            <span className="analytics-icon">{stat.icon}</span>
            <h2>{stat.value ?? 0}</h2>
            <p>{stat.title}</p>
          </div>
        ))}
      </div>

      {/* CONVERSION AND PROGRESSION */}
      <div className="performance-grid">
        {performanceStats.map((item) => (
          <div className="performance-card" key={item.title}>
            <h3>{item.title}</h3>
            <div className="performance-value">
              {item.value ?? 0}%
            </div>
            <p>{item.description}</p>
          </div>
        ))}
      </div>

      {/* APPLICATION STATUS */}
      <div className="analytics-section">
        <h2>Application Status Breakdown</h2>

        {Object.entries(analytics.status_breakdown).map(([status, count]) => {
          const percentage = analytics.total_applications > 0
            ? (count / analytics.total_applications) * 100
            : 0

          return (
            <div className="status-row" key={status}>
              <div className="status-label">
                <span>{status}</span>
                <strong>{count}</strong>
              </div>

              <div className="status-track">
                <div
                  className="status-fill"
                  style={{
                    width: `${percentage}%`,
                    backgroundColor: statusColors[status] || '#64748b'
                  }}
                />
              </div>
            </div>
          )
        })}
      </div>

      {/* MONTHLY APPLICATION TRENDS */}
      <div className="analytics-section">
        <h2>Monthly Application Trends</h2>

        {analytics.monthly_trend.length === 0 ? (
          <p>
            No application trends available yet. Add job applications
            to see your progress.
          </p>
        ) : (
          <div className="monthly-trend">
            {analytics.monthly_trend.map((item) => (
              <div className="monthly-item" key={item.month}>
                <div className="monthly-bar-container">
                  <div
                    className="monthly-bar"
                    style={{
                      height: `${Math.max(
                        (item.applications / monthlyMaximum) * 150,
                        8
                      )}px`
                    }}
                  />
                </div>

                <strong>{item.applications}</strong>
                <span>{item.month}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* COMPANY-WISE PERFORMANCE */}
      <div className="analytics-section">
        <h2>Company-wise Performance</h2>

        {!analytics.company_breakdown ||
        analytics.company_breakdown.length === 0 ? (
          <p>
            No company data available yet. Add job applications
            to see company-wise performance.
          </p>
        ) : (
          <div className="company-table-wrapper">
            <table className="company-table">
              <thead>
                <tr>
                  <th>Company</th>
                  <th>Applications</th>
                  <th>Interviews</th>
                  <th>Offers</th>
                  <th>Rejections</th>
                </tr>
              </thead>

              <tbody>
                {analytics.company_breakdown.map((company) => (
                  <tr key={company.company}>
                    <td>{company.company}</td>
                    <td>{company.applications}</td>
                    <td>{company.interviews}</td>
                    <td>{company.offers}</td>
                    <td>{company.rejections}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  )
}

export default Analytics
