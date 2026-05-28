import { useEffect, useState } from 'react'
import api from '../api'

const PARSE_COLORS = { OK: '#16a34a', FLAGGED: '#d97706', FAILED: '#dc2626' }
const APPROVAL_COLORS = { PENDING: '#6b7280', APPROVED: '#16a34a', REJECTED: '#dc2626' }

export default function RunDetail({ runId, onSelectRecord }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('ALL')
  const [approving, setApproving] = useState(false)
  const [approveMsg, setApproveMsg] = useState(null)

  function load() {
    setLoading(true)
    api.get(`/review/runs/${runId}/records/`)
      .then(res => { setData(res.data); setLoading(false) })
      .catch(() => setLoading(false))
  }

  useEffect(() => { load() }, [runId])

  function handleApprove() {
    setApproving(true)
    api.post(`/review/runs/${runId}/approve/`)
      .then(res => {
        setApproveMsg(`✓ Approved ${res.data.approved_count} records`)
        load()
      })
      .finally(() => setApproving(false))
  }

  if (loading || !data) return <p>Loading records...</p>

  const { run, records } = data

  const filtered = filter === 'ALL'
    ? records
    : records.filter(r => r.raw_parse_status === filter)

  const hasPending = records.some(r => r.approval_status === 'PENDING')

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 16 }}>
        <div>
          <h2 style={{ margin: 0 }}>Run #{run.id} — {run.source_type}</h2>
          <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: 13 }}>
            {run.file_name} · {run.row_count} rows · {run.failed_count} failed · {run.flagged_count} flagged
          </p>
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 8, alignItems: 'center' }}>
          {approveMsg && <span style={{ color: '#16a34a', fontSize: 13 }}>{approveMsg}</span>}
          {hasPending && (
            <button
              onClick={handleApprove}
              disabled={approving}
              style={{ background: '#16a34a', color: 'white', border: 'none', padding: '6px 14px', borderRadius: 4, cursor: 'pointer' }}
            >
              {approving ? 'Approving...' : 'Approve All Pending'}
            </button>
          )}
        </div>
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        {['ALL', 'OK', 'FLAGGED', 'FAILED'].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={{
              padding: '4px 12px',
              borderRadius: 4,
              border: '1px solid #cbd5e1',
              background: filter === f ? '#1e40af' : 'white',
              color: filter === f ? 'white' : '#374151',
              cursor: 'pointer',
              fontSize: 13
            }}
          >
            {f}
          </button>
        ))}
      </div>

      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
        <thead>
          <tr style={{ background: '#f1f5f9', textAlign: 'left' }}>
            <th style={th}>ID</th>
            <th style={th}>Category</th>
            <th style={th}>Scope</th>
            <th style={th}>Date</th>
            <th style={th}>Quantity</th>
            <th style={th}>Unit</th>
            <th style={th}>Location</th>
            <th style={th}>Parse</th>
            <th style={th}>Approval</th>
            <th style={th}></th>
          </tr>
        </thead>
        <tbody>
          {filtered.map(record => (
            <tr key={record.id} style={{ borderBottom: '1px solid #e2e8f0' }}>
              <td style={td}>{record.id}</td>
              <td style={td}>{record.category}</td>
              <td style={td}>{record.scope}</td>
              <td style={td}>{record.activity_date}</td>
              <td style={td}>{parseFloat(record.normalized_quantity).toLocaleString()}</td>
              <td style={td}>{record.normalized_unit}</td>
              <td style={td}>{record.location || '—'}</td>
              <td style={td}>
                <span style={{ color: PARSE_COLORS[record.raw_parse_status], fontWeight: 600 }}>
                  {record.raw_parse_status}
                </span>
              </td>
              <td style={td}>
                <span style={{ color: APPROVAL_COLORS[record.approval_status] }}>
                  {record.approval_status}
                </span>
              </td>
              <td style={td}>
                <button onClick={() => onSelectRecord(record.id)}>View</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

const th = { padding: '8px 12px', fontWeight: 600 }
const td = { padding: '8px 12px' }