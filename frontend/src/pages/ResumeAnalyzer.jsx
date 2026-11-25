
import { useState } from 'react'
import { apiFetch } from '../api'
import './ResumeAnalyzer.css'

function ResumeAnalyzer() {
  const [resume, setResume] = useState(null)
  const [jobDescription, setJobDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  // HANDLE RESUME FILE SELECTION
  function handleFileChange(event) {
    const selectedFile = event.target.files[0]

    if (selectedFile) {
      if (selectedFile.type !== 'application/pdf') {
        alert('Please upload a PDF file.')
        event.target.value = ''
        setResume(null)
        return
      }

      setResume(selectedFile)
      setResult(null)
      setError('')
    }
  }

  // ANALYZE RESUME
  async function handleSubmit(event) {
    event.preventDefault()

    if (!resume) {
      setError('Please upload your resume.')
      return
    }

    if (!jobDescription.trim()) {
      setError('Please enter a job description.')
      return
    }

    const formData = new FormData()
    formData.append('resume', resume)
    formData.append('job_description', jobDescription)

    try {
      setLoading(true)
      setError('')
      setResult(null)

      const response = await apiFetch('/resume/analyze', {
        method: 'POST',
        body: formData
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Resume analysis failed.')
      }

      setResult(data)

    } catch (err) {
      setError(err.message || 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="resume-page">

      <h1>AI Resume Analyzer</h1>

      <p className="resume-subtitle">
        Analyze your resume and discover how well it matches your target job.
      </p>

      <div className="resume-card">

        <form onSubmit={handleSubmit}>

          <label>Upload Your Resume (PDF)</label>

          <input
            type="file"
            accept="*/*"
            onChange={handleFileChange}
          />

          {resume && (
            <p className="selected-file">
              Selected file: {resume.name}
            </p>
          )}

          <label>Job Description</label>

          <textarea
            rows="8"
            placeholder="Paste the job description here..."
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
          />

          <button type="submit" disabled={loading}>
            {loading ? 'Analyzing...' : 'Analyze Resume'}
          </button>

        </form>
      </div>

      {/* ERROR MESSAGE */}
      {error && (
        <p className="error-message">{error}</p>
      )}

      {/* ANALYSIS RESULTS */}
      {result && (
        <div className="resume-result">

          <h2>Analysis Results</h2>

          <h3>
            Match Percentage: {result.analysis.match_percentage}%
          </h3>

          <p>
            Total Required Skills: {result.analysis.total_required_skills}
          </p>

          {/* MATCHED SKILLS */}
          <h3>Matched Skills</h3>

          {result.analysis.matched_skills.length > 0 ? (
            <ul>
              {result.analysis.matched_skills.map((skill) => (
                <li key={skill}>{skill}</li>
              ))}
            </ul>
          ) : (
            <p>No matching skills found.</p>
          )}

          {/* MISSING SKILLS */}
          <h3>Missing Skills</h3>

          {result.analysis.missing_skills.length > 0 ? (
            <ul>
              {result.analysis.missing_skills.map((skill) => (
                <li key={skill}>{skill}</li>
              ))}
            </ul>
          ) : (
            <p>No missing skills found.</p>
          )}

          {/* IMPROVEMENT SUGGESTIONS */}
          <h3>Improvement Suggestions</h3>

          {result.analysis.suggestions &&
          result.analysis.suggestions.length > 0 ? (
            <ul>
              {result.analysis.suggestions.map((suggestion, index) => (
                <li key={index}>{suggestion}</li>
              ))}
            </ul>
          ) : (
            <p>No suggestions available.</p>
          )}

        </div>
      )}

    </div>
  )
}

export default ResumeAnalyzer
