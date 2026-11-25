
import { useEffect, useState } from 'react'
import { apiFetch } from '../api'
import './Applications.css'

const STATUSES = [
  'Applied',
  'Assessment',
  'Interview',
  'Selected',
  'Rejected'
]

function Applications() {
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [editingId, setEditingId] = useState(null)

  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('All')
  const [viewMode, setViewMode] = useState('list')
  const [updatingId, setUpdatingId] = useState(null)

  const [company, setCompany] = useState('')
  const [role, setRole] = useState('')
  const [status, setStatus] = useState('Applied')
  const [date, setDate] = useState('')
  const [description, setDescription] = useState('')

  // FETCH APPLICATIONS
  async function fetchApplications() {
    try {
      const response = await apiFetch('/applications/')

      if (!response.ok) {
        throw new Error('Failed to load applications.')
      }

      const data = await response.json()
      setApplications(data)

    } catch (error) {
      alert(error.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchApplications()
  }, [])

  // SEARCH AND FILTER
  const filteredApplications = applications.filter((app) => {
    const matchesSearch = app.company_name
      .toLowerCase()
      .includes(searchTerm.toLowerCase())

    const matchesStatus =
      filterStatus === 'All' || app.status === filterStatus

    return matchesSearch && matchesStatus
  })

  // RESET FORM
  function resetForm() {
    setCompany('')
    setRole('')
    setStatus('Applied')
    setDate('')
    setDescription('')
    setEditingId(null)
  }

  // CREATE OR UPDATE APPLICATION
  async function handleSubmit(event) {
    event.preventDefault()
    setSaving(true)

    try {
      const url = editingId
        ? `/applications/${editingId}`
        : '/applications/'

      const response = await apiFetch(url, {
        method: editingId ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          company_name: company,
          job_role: role,
          status: status,
          application_date: date,
          job_description: description
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Operation failed.')
      }

      alert(
        editingId
          ? 'Application updated successfully!'
          : 'Application added successfully!'
      )

      resetForm()
      await fetchApplications()

    } catch (error) {
      alert(error.message)
    } finally {
      setSaving(false)
    }
  }

  // EDIT APPLICATION
  function handleEdit(app) {
    setEditingId(app.id)
    setCompany(app.company_name)
    setRole(app.job_role)
    setStatus(app.status)
    setDate(app.application_date)
    setDescription(app.job_description || '')

    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    })
  }

  // DELETE APPLICATION
  async function handleDelete(id) {
    const confirmDelete = window.confirm(
      'Are you sure you want to delete this application?'
    )

    if (!confirmDelete) return

    try {
      const response = await apiFetch(
        `/applications/${id}`,
        {
          method: 'DELETE'
        }
      )

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to delete application.')
      }

      alert('Application deleted successfully!')

      await fetchApplications()

      if (editingId === id) {
        resetForm()
      }

    } catch (error) {
      alert(error.message)
    }
  }

  // UPDATE STATUS FROM KANBAN BOARD
  async function handleStatusChange(app, newStatus) {
    if (app.status === newStatus) return

    setUpdatingId(app.id)

    try {
      const response = await apiFetch(
        `/applications/${app.id}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            company_name: app.company_name,
            job_role: app.job_role,
            status: newStatus,
            application_date: app.application_date,
            job_description: app.job_description || ''
          })
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to update application status.')
      }

      setApplications((previous) =>
        previous.map((item) =>
          item.id === app.id ? data : item
        )
      )

    } catch (error) {
      alert(error.message)
    } finally {
      setUpdatingId(null)
    }
  }

  const statusColors = {
    Applied: '#3b82f6',
    Assessment: '#8b5cf6',
    Interview: '#f59e0b',
    Selected: '#16a34a',
    Rejected: '#ef4444'
  }

  return (
    <div className="applications-page">

      <h1>My Applications</h1>

      <p className="page-subtitle">
        Track and manage your job applications.
      </p>

      {/* APPLICATION FORM */}
      <div className="application-form-card">

        <h2>
          {editingId ? 'Edit Application' : 'Add New Application'}
        </h2>

        <form onSubmit={handleSubmit}>

          <label>Company Name</label>
          <input
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            placeholder="Enter company name"
            required
          />

          <label>Job Role</label>
          <input
            value={role}
            onChange={(e) => setRole(e.target.value)}
            placeholder="Enter job role"
            required
          />

          <label>Application Status</label>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            {STATUSES.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>

          <label>Application Date</label>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
          />

          <label>Job Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Enter job description"
            rows="4"
          />

          <button type="submit" disabled={saving}>
            {saving
              ? 'Saving...'
              : editingId
                ? 'Update Application'
                : 'Add Application'}
          </button>

          {editingId && (
            <button
              type="button"
              className="cancel-button"
              onClick={resetForm}
            >
              Cancel Edit
            </button>
          )}

        </form>
      </div>

      {/* APPLICATIONS VIEW */}
      <div className="applications-list">

        <div className="applications-heading">
          <div>
            <h2>Your Applications</h2>
            <p>{filteredApplications.length} applications found</p>
          </div>

          <div className="view-toggle">
            <button
              className={viewMode === 'list' ? 'active-view' : ''}
              onClick={() => setViewMode('list')}
            >
              List View
            </button>

            <button
              className={viewMode === 'kanban' ? 'active-view' : ''}
              onClick={() => setViewMode('kanban')}
            >
              Kanban Board
            </button>
          </div>
        </div>

        {/* SEARCH AND FILTER */}
        <div className="application-filters">

          <input
            type="text"
            placeholder="Search by company name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />

          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="All">All Statuses</option>
            {STATUSES.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>

        </div>

        {loading ? (
          <p>Loading applications...</p>
        ) : filteredApplications.length === 0 ? (
          <p>No matching applications found.</p>
        ) : viewMode === 'list' ? (

          /* LIST VIEW */
          filteredApplications.map((app) => (
            <div className="application-card" key={app.id}>

              <h3>{app.company_name}</h3>
              <p>{app.job_role}</p>

              <span className="status-label">
                {app.status}
              </span>

              <p>Applied on: {app.application_date}</p>
              <p>{app.job_description}</p>

              <div className="application-actions">

                <button
                  className="edit-button"
                  onClick={() => handleEdit(app)}
                >
                  Edit
                </button>

                <button
                  className="delete-button"
                  onClick={() => handleDelete(app.id)}
                >
                  Delete
                </button>

              </div>

            </div>
          ))

        ) : (

          /* KANBAN BOARD */
          <div className="kanban-board">

            {STATUSES.map((boardStatus) => {
              const boardApplications = filteredApplications.filter(
                (app) => app.status === boardStatus
              )

              return (
                <div className="kanban-column" key={boardStatus}>

                  <div className="kanban-column-header">
                    <h3>
                      <span
                        className="kanban-status-dot"
                        style={{
                          backgroundColor: statusColors[boardStatus]
                        }}
                      />
                      {boardStatus}
                    </h3>

                    <span className="kanban-count">
                      {boardApplications.length}
                    </span>
                  </div>

                  <div className="kanban-cards">

                    {boardApplications.length === 0 ? (
                      <p className="kanban-empty">
                        No applications
                      </p>
                    ) : (
                      boardApplications.map((app) => (
                        <div className="kanban-card" key={app.id}>

                          <h4>{app.company_name}</h4>
                          <p>{app.job_role}</p>

                          <span className="kanban-date">
                            Applied: {app.application_date}
                          </span>

                          <label>Change Status</label>

                          <select
                            value={app.status}
                            disabled={updatingId === app.id}
                            onChange={(e) =>
                              handleStatusChange(app, e.target.value)
                            }
                          >
                            {STATUSES.map((item) => (
                              <option key={item}>{item}</option>
                            ))}
                          </select>

                          {updatingId === app.id && (
                            <small>Updating...</small>
                          )}

                          <div className="application-actions">

                            <button
                              className="edit-button"
                              onClick={() => handleEdit(app)}
                            >
                              Edit
                            </button>

                            <button
                              className="delete-button"
                              onClick={() => handleDelete(app.id)}
                            >
                              Delete
                            </button>

                          </div>

                        </div>
                      ))
                    )}

                  </div>
                </div>
              )
            })}

          </div>
        )}

      </div>

    </div>
  )
}

export default Applications
