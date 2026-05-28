import { useEffect, useState } from 'react'
import api from '../api'

const STATUS_COLORS = {
  COMPLETED: '#16a34a',
  FAILED: '#dc2626',
  PROCESSING: '#d97706',
  PENDING: '#6b7280',
}

const SOURCE_LABELS = {
  SAP: 'SAP Export',
  UTILITY: 'Utility Electricity',
  TRAVEL: 'Corporate Travel',
}

export default function RunList({ onSelectRun }) {
  const [runs, setRuns] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.get('/review/runs/')
      .then(res => { setRuns(res.data); setLoading(false) })
      .catch(() => { setError('Failed to load runs'); setLoading(false) })
  }, [])

  if (loading) return <p>Loading ingestion runs...</p>
  if (error) return <p style={{ color: 'red' }}>{error}</p>

  return (
    <div>
      <h2 style={{ marginBottom: 16 }}>Ingestion Runs</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
        <thead>
          <tr style={{ background: '#f1f5f9', textAlign: 'left' }}>
            <th style={th}>ID</th>
            <th style={th}>Source</th>
            <th style={th}>File</th>
            <th style={th}>Status</th>
            <th style={th}>Rows</th>
            <th style={th}>Failed</th>
            <th style={th}>Flagged</th>
            <th style={th}>Uploaded</th>
            <th style={th}></th>
          </tr>
        </thead>
        <tbody>
          {runs.map(run => (
            <tr key={run.id} style={{ borderBottom: '1px solid #e2e8f0' }}>
              <td style={td}>{run.id}</td>
              <td style={td}>{SOURCE_LABELS[run.source_type] || run.source_type}</td>
              <td style={td}>{run.file_name}</td>
              <td style={td}>
                <span style={{
                  color: STATUS_COLORS[run.status],
                  fontWeight: 600
                }}>
                  {run.status}
                </span>
              </td>
              <td style={td}>{run.row_count}</td>
              <td style={td}>
                <span style={{ color: run.failed_count > 0 ? '#dc2626' : 'inherit' }}>
                  {run.failed_count}
                </span>
              </td>
              <td style={td}>
                <span style={{ color: run.flagged_count > 0 ? '#d97706' : 'inherit' }}>
                  {run.flagged_count}
                </span>
              </td>
              <td style={td}>{new Date(run.created_at).toLocaleString()}</td>
              <td style={td}>
                <button onClick={() => onSelectRun(run.id)}>Review →</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

const th = { padding: '8px 12px', fontWeight: 600, fontSize: 13 }
const td = { padding: '8px 12px' }