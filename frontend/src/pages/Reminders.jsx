
import { useEffect, useState } from 'react'
import { apiFetch } from '../api'
import './Reminders.css'

function Reminders() {
  const [reminders, setReminders] = useState([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [updatingId, setUpdatingId] = useState(null)
  const [deletingId, setDeletingId] = useState(null)
  const [error, setError] = useState('')
  const [filter, setFilter] = useState('All')
  const [editingId, setEditingId] = useState(null)

  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [reminderType, setReminderType] = useState('Interview')
  const [reminderDate, setReminderDate] = useState('')

  useEffect(() => {
    fetchReminders()
  }, [])

  const fetchReminders = async () => {
    try {
      setLoading(true)
      setError('')

      const response = await apiFetch('/reminders/')

      if (!response.ok) {
        throw new Error(
          response.status === 401
            ? 'Please log in again to view your reminders.'
            : 'Unable to load reminders.'
        )
      }

      const data = await response.json()
      setReminders(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(err.message || 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setTitle('')
    setDescription('')
    setReminderType('Interview')
    setReminderDate('')
    setEditingId(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!title.trim() || !reminderDate) {
      setError('Please enter a title and reminder date.')
      return
    }

    try {
      setSaving(true)
      setError('')

      const path = editingId
        ? `/reminders/${editingId}`
        : '/reminders/'

      const method = editingId ? 'PUT' : 'POST'

      const payload = {
        title: title.trim(),
        description: description.trim() || null,
        reminder_type: reminderType,
        // Keep the selected local date and time without converting to UTC.
        reminder_date: `${reminderDate}:00`
      }

      const response = await apiFetch(path, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        let message = 'Unable to save reminder.'

        try {
          const data = await response.json()
          message = data.detail || message
        } catch {
          // Keep the default error message if the response is not JSON.
        }

        throw new Error(
          typeof message === 'string'
            ? message
            : 'Please check the reminder details.'
        )
      }

      resetForm()
      await fetchReminders()
    } catch (err) {
      setError(err.message || 'Unable to save reminder.')
    } finally {
      setSaving(false)
    }
  }

  const handleEdit = (reminder) => {
    setEditingId(reminder.id)
    setTitle(reminder.title)
    setDescription(reminder.description || '')
    setReminderType(reminder.reminder_type)

    // Backend datetime is treated as the selected local wall-clock time.
    setReminderDate(String(reminder.reminder_date).slice(0, 16))

    setError('')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleComplete = async (reminder) => {
    try {
      setUpdatingId(reminder.id)
      setError('')

      const response = await apiFetch(
        `/reminders/${reminder.id}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            is_completed: !reminder.is_completed
          })
        }
      )

      if (!response.ok) {
        throw new Error('Unable to update reminder status.')
      }

      await fetchReminders()
    } catch (err) {
      setError(err.message)
    } finally {
      setUpdatingId(null)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this reminder?')) {
      return
    }

    try {
      setDeletingId(id)
      setError('')

      const response = await apiFetch(`/reminders/${id}`, {
        method: 'DELETE'
      })

      if (!response.ok) {
        throw new Error('Unable to delete reminder.')
      }

      await fetchReminders()

      if (editingId === id) {
        resetForm()
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setDeletingId(null)
    }
  }

  const isOverdue = (reminder) => {
    return (
      !reminder.is_completed &&
      new Date(reminder.reminder_date).getTime() < Date.now()
    )
  }

  const sortedReminders = [...reminders].sort(
    (a, b) =>
      new Date(a.reminder_date).getTime() -
      new Date(b.reminder_date).getTime()
  )

  const filteredReminders = sortedReminders.filter((reminder) => {
    if (filter === 'Pending') return !reminder.is_completed
    if (filter === 'Completed') return reminder.is_completed
    if (filter === 'Overdue') return isOverdue(reminder)

    if (['Interview', 'Deadline', 'Follow-up'].includes(filter)) {
      return reminder.reminder_type === filter
    }

    return true
  })

  const pendingCount = reminders.filter(
    reminder => !reminder.is_completed
  ).length

  const completedCount = reminders.filter(
    reminder => reminder.is_completed
  ).length

  const overdueCount = reminders.filter(isOverdue).length

  const formatDate = (date) => {
    return new Date(date).toLocaleString('en-IN', {
      dateStyle: 'medium',
      timeStyle: 'short'
    })
  }

  return (
    <div className="reminders-page">
      <div className="reminders-header">
        <div>
          <h1>My Reminders</h1>
          <p>Keep track of interviews, deadlines and follow-ups.</p>
        </div>
      </div>

      <div className="reminder-stats">
        <div className="reminder-stat-card">
          <span>Total Reminders</span>
          <h2>{reminders.length}</h2>
        </div>

        <div className="reminder-stat-card">
          <span>Pending</span>
          <h2>{pendingCount}</h2>
        </div>

        <div className="reminder-stat-card">
          <span>Completed</span>
          <h2>{completedCount}</h2>
        </div>

        <div className="reminder-stat-card">
          <span>Overdue</span>
          <h2>{overdueCount}</h2>
        </div>
      </div>

      <div className="reminder-form-card">
        <h2>{editingId ? 'Edit Reminder' : 'Add New Reminder'}</h2>

        <form onSubmit={handleSubmit}>
          <div className="reminder-form-grid">
            <div className="reminder-field">
              <label>Reminder Title</label>
              <input
                type="text"
                value={title}
                onChange={e => setTitle(e.target.value)}
                placeholder="e.g. Python Developer Interview"
                maxLength={150}
                required
              />
            </div>

            <div className="reminder-field">
              <label>Reminder Type</label>
              <select
                value={reminderType}
                onChange={e => setReminderType(e.target.value)}
              >
                <option value="Interview">Interview</option>
                <option value="Deadline">Deadline</option>
                <option value="Follow-up">Follow-up</option>
              </select>
            </div>

            <div className="reminder-field">
              <label>Date and Time</label>
              <input
                type="datetime-local"
                value={reminderDate}
                onChange={e => setReminderDate(e.target.value)}
                required
              />
            </div>

            <div className="reminder-field">
              <label>Description</label>
              <input
                type="text"
                value={description}
                onChange={e => setDescription(e.target.value)}
                placeholder="Additional details"
              />
            </div>
          </div>

          <div className="reminder-form-actions">
            <button type="submit" disabled={saving}>
              {saving
                ? 'Saving...'
                : editingId
                  ? 'Update Reminder'
                  : 'Add Reminder'}
            </button>

            {editingId && (
              <button
                type="button"
                className="cancel-reminder-btn"
                onClick={resetForm}
              >
                Cancel
              </button>
            )}
          </div>
        </form>
      </div>

      {error && (
        <div className="reminder-error">
          {error}
        </div>
      )}

      <div className="reminders-list-card">
        <div className="reminders-list-header">
          <h2>Your Reminders</h2>

          <select
            value={filter}
            onChange={e => setFilter(e.target.value)}
          >
            <option value="All">All Reminders</option>
            <option value="Pending">Pending</option>
            <option value="Completed">Completed</option>
            <option value="Overdue">Overdue</option>
            <option value="Interview">Interviews</option>
            <option value="Deadline">Deadlines</option>
            <option value="Follow-up">Follow-ups</option>
          </select>
        </div>

        {loading ? (
          <p className="reminder-message">Loading reminders...</p>
        ) : filteredReminders.length === 0 ? (
          <p className="reminder-message">
            {reminders.length === 0
              ? 'No reminders yet. Add your first reminder above!'
              : 'No reminders match this filter.'}
          </p>
        ) : (
          <div className="reminder-items">
            {filteredReminders.map(reminder => (
              <div className="reminder-item" key={reminder.id}>
                <div className="reminder-item-main">
                  <div className="reminder-item-title">
                    <h3 className={reminder.is_completed ? 'completed-title' : ''}>
                      {reminder.title}
                    </h3>

                    <span
                      className={`reminder-status ${
                        reminder.is_completed
                          ? 'completed'
                          : isOverdue(reminder)
                            ? 'overdue'
                            : 'pending'
                      }`}
                    >
                      {reminder.is_completed
                        ? 'Completed'
                        : isOverdue(reminder)
                          ? 'Overdue'
                          : 'Pending'}
                    </span>
                  </div>

                  <p>
                    {reminder.description || 'No description provided.'}
                  </p>

                  <div className="reminder-meta">
                    <span>{reminder.reminder_type}</span>
                    <span>{formatDate(reminder.reminder_date)}</span>
                  </div>
                </div>

                <div className="reminder-actions">
                  <button
                    type="button"
                    className="complete-btn"
                    onClick={() => handleComplete(reminder)}
                    disabled={updatingId === reminder.id}
                  >
                    {updatingId === reminder.id
                      ? 'Updating...'
                      : reminder.is_completed
                        ? 'Mark Pending'
                        : 'Complete'}
                  </button>

                  <button
                    type="button"
                    className="edit-reminder-btn"
                    onClick={() => handleEdit(reminder)}
                  >
                    Edit
                  </button>

                  <button
                    type="button"
                    className="delete-reminder-btn"
                    onClick={() => handleDelete(reminder.id)}
                    disabled={deletingId === reminder.id}
                  >
                    {deletingId === reminder.id ? 'Deleting...' : 'Delete'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Reminders
