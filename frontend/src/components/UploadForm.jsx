import { useState } from 'react'
import api from '../api'

const SOURCE_OPTIONS = [
  { value: 'sap', label: 'SAP Export', accept: '.csv', endpoint: '/ingest/sap/' },
  { value: 'utility', label: 'Utility Electricity', accept: '.csv', endpoint: '/ingest/utility/' },
  { value: 'travel', label: 'Corporate Travel', accept: '.json', endpoint: '/ingest/travel/' },
]

export default function UploadForm({ onUploadComplete }) {
  const [sourceType, setSourceType] = useState('sap')
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const selected = SOURCE_OPTIONS.find(s => s.value === sourceType)

  function handleFileChange(e) {
    setFile(e.target.files[0])
    setResult(null)
    setError(null)
  }

  function handleSubmit(e) {
    e.preventDefault()
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    setUploading(true)
    setError(null)
    setResult(null)

    api.post(selected.endpoint, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
      .then(res => {
        setResult(res.data)
        setFile(null)
        // Reset file input
        document.getElementById('file-input').value = ''
        onUploadComplete()
      })
      .catch(err => {
        setError(err.response?.data?.error || 'Upload failed')
      })
      .finally(() => setUploading(false))
  }

  return (
    <div style={{
      border: '1px solid #e2e8f0',
      borderRadius: 8,
      padding: 20,
      marginBottom: 28,
      background: '#f8fafc'
    }}>
      <h3 style={{ margin: '0 0 14px', fontSize: 15 }}>Upload New Data</h3>
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: 12, alignItems: 'flex-end', flexWrap: 'wrap' }}>

        <div>
          <label style={labelStyle}>Source Type</label>
          <select
            value={sourceType}
            onChange={e => { setSourceType(e.target.value); setFile(null) }}
            style={inputStyle}
          >
            {SOURCE_OPTIONS.map(o => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label style={labelStyle}>File ({selected.accept})</label>
          <input
            id="file-input"
            type="file"
            accept={selected.accept}
            onChange={handleFileChange}
            style={inputStyle}
          />
        </div>

        <button
          type="submit"
          disabled={!file || uploading}
          style={{
            background: (!file || uploading) ? '#94a3b8' : '#1e40af',
            color: 'white',
            border: 'none',
            padding: '7px 18px',
            borderRadius: 4,
            cursor: (!file || uploading) ? 'default' : 'pointer',
            fontSize: 14,
            height: 34,
          }}
        >
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
      </form>

      {result && (
        <div style={{ marginTop: 12, padding: '10px 14px', background: '#dcfce7', borderRadius: 4, fontSize: 13 }}>
          ✓ Ingestion complete — Run #{result.ingestion_run_id} |
          {' '}{result.row_count} rows |
          {' '}<span style={{ color: '#dc2626' }}>{result.failed_count} failed</span> |
          {' '}<span style={{ color: '#d97706' }}>{result.flagged_count} flagged</span>
        </div>
      )}

      {error && (
        <div style={{ marginTop: 12, padding: '10px 14px', background: '#fee2e2', borderRadius: 4, fontSize: 13, color: '#dc2626' }}>
          ✗ {error}
        </div>
      )}
    </div>
  )
}

const labelStyle = { display: 'block', fontSize: 12, color: '#64748b', marginBottom: 4 }
const inputStyle = { padding: '6px 10px', border: '1px solid #cbd5e1', borderRadius: 4, fontSize: 13 }