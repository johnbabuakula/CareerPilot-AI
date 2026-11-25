
import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { apiFetch } from '../api'
import './Auth.css'

function Register() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')

  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [loading, setLoading] = useState(false)

  const navigate = useNavigate()

  // PASSWORD STRENGTH CHECK
  const passwordChecks = [
    password.length >= 8,
    password.length >= 12,
    /[A-Z]/.test(password),
    /[a-z]/.test(password),
    /[0-9]/.test(password),
    /[^A-Za-z0-9]/.test(password),
  ]

  const strengthScore = passwordChecks.filter(Boolean).length

  let strength = ''
  let strengthColor = '#94a3b8'

  if (password) {
    if (strengthScore <= 2) {
      strength = 'Weak'
      strengthColor = '#ef4444'
    } else if (strengthScore <= 4) {
      strength = 'Medium'
      strengthColor = '#f59e0b'
    } else {
      strength = 'Strong'
      strengthColor = '#16a34a'
    }
  }

  // PASSWORD EYE ICON
  function PasswordToggle({ visible, onToggle }) {
    return (
      <button
        type="button"
        onClick={onToggle}
        aria-label={visible ? 'Hide password' : 'Show password'}
        title={visible ? 'Hide password' : 'Show password'}
        style={{
          position: 'absolute',
          right: '18px',
          top: '35%',
          transform: 'translateY(-50%)',
          background: 'transparent',
          border: 'none',
          padding: '5px',
          cursor: 'pointer',
          color: '#64748b',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {visible ? (
          <svg width="21" height="21" viewBox="0 0 24 24"
            fill="none" stroke="currentColor" strokeWidth="2"
            strokeLinecap="round" strokeLinejoin="round">
            <path d="M3 3l18 18" />
            <path d="M10.6 10.6a2 2 0 002.8 2.8" />
            <path d="M9.9 5.2A10.8 10.8 0 0112 5c5 0 8.5 4.5 9.5 7-.4 1.1-1.2 2.2-2.2 3.2" />
            <path d="M6.2 6.2C3.9 7.6 2.5 9.8 2 12c1 2.5 4.5 7 10 7 1.1 0 2.1-.2 3-.5" />
          </svg>
        ) : (
          <svg width="21" height="21" viewBox="0 0 24 24"
            fill="none" stroke="currentColor" strokeWidth="2"
            strokeLinecap="round" strokeLinejoin="round">
            <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z" />
            <circle cx="12" cy="12" r="3" />
          </svg>
        )}
      </button>
    )
  }

  async function handleRegister(event) {
    event.preventDefault()

    if (!name.trim() || !email || !password || !confirmPassword) {
      alert('Please fill in all fields.')
      return
    }

    if (password !== confirmPassword) {
      alert('Passwords do not match.')
      return
    }

    if (password.length < 8 || password.length > 128) {
      alert('Password must contain between 8 and 128 characters.')
      return
    }

    setLoading(true)

    try {
      const response = await apiFetch('/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          full_name: name.trim(),
          email,
          password,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Registration failed')
      }

      alert('Registration successful! Please log in.')

      setName('')
      setEmail('')
      setPassword('')
      setConfirmPassword('')
      setShowPassword(false)
      setShowConfirmPassword(false)

      navigate('/login')

    } catch (error) {
      alert(error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>CareerPilot <span>AI</span></h2>

        <h1>Create Account</h1>

        <p>Start managing your career journey today.</p>

        <form onSubmit={handleRegister}>
          <label>Full Name</label>

          <input
            type="text"
            placeholder="Enter your full name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            required
          />

          <label>Email Address</label>

          <input
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />

          <label>Password</label>

          <div style={{ position: 'relative', width: '100%' }}>
            <input
              type={showPassword ? 'text' : 'password'}
              placeholder="Create a password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              minLength={8}
              maxLength={128}
              required
              style={{
                paddingRight: '52px',
                width: '100%',
              }}
            />

            <PasswordToggle
              visible={showPassword}
              onToggle={() => setShowPassword(!showPassword)}
            />
          </div>

          {password && (
            <div style={{ marginTop: '-12px', marginBottom: '20px' }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginBottom: '7px',
                fontSize: '13px',
                fontWeight: '600',
              }}>
                <span>Password Strength</span>

                <span style={{ color: strengthColor }}>
                  {strength}
                </span>
              </div>

              <div style={{
                height: '6px',
                background: '#e2e8f0',
                borderRadius: '10px',
                overflow: 'hidden',
              }}>
                <div style={{
                  height: '100%',
                  width: `${(strengthScore / 6) * 100}%`,
                  background: strengthColor,
                  borderRadius: '10px',
                  transition: 'all 0.2s ease',
                }} />
              </div>

              <div style={{
                fontSize: '12px',
                color: '#64748b',
                marginTop: '9px',
                lineHeight: '1.8',
              }}>
                <div style={{ color: password.length >= 8 ? '#16a34a' : '#64748b' }}>
                  {password.length >= 8 ? '✓' : '○'} At least 8 characters
                </div>

                <div style={{ color: /[A-Z]/.test(password) ? '#16a34a' : '#64748b' }}>
                  {/[A-Z]/.test(password) ? '✓' : '○'} One uppercase letter
                </div>

                <div style={{ color: /[a-z]/.test(password) ? '#16a34a' : '#64748b' }}>
                  {/[a-z]/.test(password) ? '✓' : '○'} One lowercase letter
                </div>

                <div style={{ color: /[0-9]/.test(password) ? '#16a34a' : '#64748b' }}>
                  {/[0-9]/.test(password) ? '✓' : '○'} One number
                </div>

                <div style={{ color: /[^A-Za-z0-9]/.test(password) ? '#16a34a' : '#64748b' }}>
                  {/[^A-Za-z0-9]/.test(password) ? '✓' : '○'} One special character
                </div>
              </div>
            </div>
          )}

          <label>Confirm Password</label>

          <div style={{ position: 'relative', width: '100%' }}>
            <input
              type={showConfirmPassword ? 'text' : 'password'}
              placeholder="Re-enter your password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              minLength={8}
              maxLength={128}
              required
              style={{
                paddingRight: '52px',
                width: '100%',
              }}
            />

            <PasswordToggle
              visible={showConfirmPassword}
              onToggle={() => setShowConfirmPassword(!showConfirmPassword)}
            />
          </div>

          {confirmPassword && (
            <p style={{
              fontSize: '12px',
              color: password === confirmPassword ? '#16a34a' : '#ef4444',
              marginTop: '-12px',
              marginBottom: '18px',
              textAlign: 'left',
            }}>
              {password === confirmPassword
                ? '✓ Passwords match'
                : '✗ Passwords do not match'}
            </p>
          )}

          <button type="submit" disabled={loading}>
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  )
}

export default Register
