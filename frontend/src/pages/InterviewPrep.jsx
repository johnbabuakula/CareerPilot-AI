
import { useEffect, useState } from 'react'
import { apiFetch } from '../api'
import './InterviewPrep.css'

function InterviewPrep() {
  const [jobRole, setJobRole] = useState('')
  const [topic, setTopic] = useState('')
  const [totalQuestions, setTotalQuestions] = useState('')

  const [session, setSession] = useState(null)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [answer, setAnswer] = useState('')
  const [evaluation, setEvaluation] = useState(null)

  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  // FETCH INTERVIEW HISTORY
  async function fetchHistory() {
    try {
      const response = await apiFetch('/interviews/')

      if (!response.ok) {
        throw new Error('Could not load interview history.')
      }

      const data = await response.json()
      setHistory(data)

    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => {
    fetchHistory()
  }, [])

  // START A NEW INTERVIEW
  async function startInterview(event) {
    event.preventDefault()

    if (!jobRole || !topic || !totalQuestions) {
      setError('Please select all the options.')
      return
    }

    try {
      setLoading(true)
      setError('')
      setSession(null)
      setEvaluation(null)
      setAnswer('')
      setCurrentIndex(0)

      const response = await apiFetch('/interviews/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          job_role: jobRole,
          topic: topic,
          total_questions: Number(totalQuestions)
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Could not start interview.')
      }

      setSession(data)
      await fetchHistory()

    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // SUBMIT INTERVIEW ANSWER
  async function submitAnswer() {
    if (!answer.trim()) {
      setError('Please enter your answer.')
      return
    }

    const question = session.questions[currentIndex]

    try {
      setSubmitting(true)
      setError('')

      const response = await apiFetch(
        `/interviews/${session.id}/questions/${question.id}/answer`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ answer })
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Answer submission failed.')
      }

      setEvaluation(data)
      await fetchHistory()

    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  // MOVE TO NEXT QUESTION
  function nextQuestion() {
    setCurrentIndex((previous) => previous + 1)
    setAnswer('')
    setEvaluation(null)
    setError('')
  }

  // FINISH INTERVIEW
  function finishInterview() {
    setSession(null)
    setAnswer('')
    setEvaluation(null)
    setCurrentIndex(0)
    setError('')
    fetchHistory()
  }

  const currentQuestion = session?.questions[currentIndex]

  const isLastQuestion =
    session && currentIndex === session.questions.length - 1

  return (
    <div className="interview-page">

      <div className="interview-header">
        <h1>AI Interview Preparation</h1>
        <p>Practice interviews and improve your confidence.</p>
      </div>

      {error && (
        <div className="interview-error">
          {error}
        </div>
      )}

      {!session && (
        <div className="interview-card">

          <h2>Start a New Interview</h2>
          <p>Choose your role and topic to begin practicing.</p>

          <form onSubmit={startInterview}>

            <label>Job Role</label>

            <select
              value={jobRole}
              onChange={(e) => setJobRole(e.target.value)}
              required
            >
              <option value="">Select a Job Role</option>
              <option value="Python Developer">Python Developer</option>
              <option value="Java Developer">Java Developer</option>
              <option value="Software Developer">Software Developer</option>
              <option value="Data Analyst">Data Analyst</option>
              <option value="AI/ML Engineer">AI/ML Engineer</option>
            </select>

            <label>Interview Topic</label>

            <select
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              required
            >
              <option value="">Select an Interview Topic</option>
              <option value="Python">Python</option>
              <option value="SQL">SQL</option>
              <option value="DSA">DSA</option>
              <option value="HR">HR</option>
            </select>

            <label>Number of Questions</label>

            <select
              value={totalQuestions}
              onChange={(e) => setTotalQuestions(e.target.value)}
              required
            >
              <option value="">Select Number of Questions</option>
              <option value="3">3 Questions</option>
              <option value="5">5 Questions</option>
              <option value="10">10 Questions</option>
            </select>

            <button type="submit" disabled={loading}>
              {loading ? 'Starting...' : 'Start Interview'}
            </button>

          </form>
        </div>
      )}

      {session && currentQuestion && (
        <div className="interview-card question-card">

          <div className="question-progress">
            Question {currentIndex + 1} of {session.questions.length}
          </div>

          <h2>{currentQuestion.question}</h2>

          <label>Your Answer</label>

          <textarea
            rows="7"
            placeholder="Write your answer here..."
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            disabled={!!evaluation}
          />

          {!evaluation ? (

            <button onClick={submitAnswer} disabled={submitting}>
              {submitting ? 'Evaluating...' : 'Submit Answer'}
            </button>

          ) : (

            <div className="evaluation-result">

              <h3>Answer Evaluation</h3>

              <h2>Score: {evaluation.score}/10</h2>

              <p>{evaluation.feedback}</p>

              {isLastQuestion ? (
                <button onClick={finishInterview}>
                  Finish Interview
                </button>
              ) : (
                <button onClick={nextQuestion}>
                  Next Question
                </button>
              )}

            </div>
          )}

        </div>
      )}

      {!session && (
        <div className="interview-card history-card">

          <h2>Interview History</h2>

          {history.length === 0 ? (

            <p>No interview sessions yet.</p>

          ) : (

            history.map((item) => (
              <div className="history-item" key={item.id}>

                <div>
                  <h3>{item.job_role}</h3>
                  <p>{item.topic} Interview</p>
                  <small>{item.total_questions} Questions</small>
                </div>

                <strong>{item.score}/10</strong>

              </div>
            ))

          )}

        </div>
      )}

    </div>
  )
}

export default InterviewPrep
