import { useEffect, useState } from 'react'
import api from '../api'

export default function RecordDetail({ recordId }) {
  const [record, setRecord] = useState(null)
  const [loading, setLoading] = useState(true)
  const [flagReason, setFlagReason] = useState('')
  const [flagMsg, setFlagMsg] = useState(null)
  const [editNotes, setEditNotes] = useState('')
  const [editQty, setEditQty] = useState('')
  const [editMsg, setEditMsg] = useState(null)

  function load() {
    // Fetch the single record via the run records endpoint isn't ideal,
    // but we don't have a single-record endpoint — we'll add it minimally
    api.get(`/review/records/${recordId}/`)
      .then(res => {
        setRecord(res.data)
        setEditQty(res.data.normalized_quantity)
        setEditNotes(res.data.edit_notes)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }

  useEffect(() => { load() }, [recordId])

  function handleFlag(e) {
    e.preventDefault()
    if (!flagReason.trim()) return
    api.post(`/review/records/${recordId}/flag/`, { reason: flagReason })
      .then(() => {
        setFlagMsg('Flag added')
        setFlagReason('')
        load()
      })
  }

  function handleEdit(e) {
    e.preventDefault()
    api.patch(`/review/records/${recordId}/edit/`, {
      normalized_quantity: editQty,
      edit_notes: editNotes
    })
      .then(res => {
        setRecord(res.data)
        setEditMsg('Saved')
      })
  }

  if (loading || !record) return <p>Loading record...</p>

  const isApproved = record.approval_status === 'APPROVED'

  return (
    <div style={{ maxWidth: 700 }}>
      <h2>Record #{record.id}</h2>

      <section style={section}>
        <h3 style={sectionTitle}>Activity Data</h3>
        <Row label="Source" value={record.source_type} />
        <Row label="Scope" value={record.scope} />
        <Row label="Category" value={record.category} />
        <Row label="Date" value={record.activity_date} />
        <Row label="Quantity" value={`${parseFloat(record.normalized_quantity).toLocaleString()} ${record.normalized_unit}`} />
        <Row label="Original" value={`${parseFloat(record.quantity).toLocaleString()} ${record.original_unit}`} />
        <Row label="Location" value={record.location || '—'} />
        <Row label="Vendor" value={record.supplier_vendor || '—'} />
        <Row label="Description" value={record.description || '—'} />
        <Row label="Manually Edited" value={record.is_manually_edited ? 'Yes' : 'No'} />
        <Row label="Approval" value={record.approval_status} />
      </section>

      {record.flags && record.flags.length > 0 && (
        <section style={section}>
          <h3 style={sectionTitle}>Flags</h3>
          {record.flags.map(flag => (
            <div key={flag.id} style={{ padding: '8px', background: '#fef3c7', borderRadius: 4, marginBottom: 6, fontSize: 13 }}>
              <strong>{flag.flagged_by_username}</strong>: {flag.reason}
              {flag.resolved && <span style={{ color: '#16a34a', marginLeft: 8 }}>✓ Resolved</span>}
            </div>
          ))}
        </section>
      )}

      {!isApproved && (
        <>
          <section style={section}>
            <h3 style={sectionTitle}>Add Flag</h3>
            <form onSubmit={handleFlag} style={{ display: 'flex', gap: 8 }}>
              <input
                value={flagReason}
                onChange={e => setFlagReason(e.target.value)}
                placeholder="Describe the issue..."
                style={{ flex: 1, padding: '6px 10px', border: '1px solid #cbd5e1', borderRadius: 4 }}
              />
              <button type="submit" style={btnSecondary}>Add Flag</button>
            </form>
            {flagMsg && <p style={{ color: '#16a34a', fontSize: 13, marginTop: 6 }}>{flagMsg}</p>}
          </section>

          <section style={section}>
            <h3 style={sectionTitle}>Edit Record</h3>
            <form onSubmit={handleEdit}>
              <div style={{ marginBottom: 10 }}>
                <label style={label}>Normalized Quantity</label>
                <input
                  type="number"
                  value={editQty}
                  onChange={e => setEditQty(e.target.value)}
                  style={{ display: 'block', width: '100%', padding: '6px 10px', border: '1px solid #cbd5e1', borderRadius: 4 }}
                />
              </div>
              <div style={{ marginBottom: 10 }}>
                <label style={label}>Edit Notes</label>
                <textarea
                  value={editNotes}
                  onChange={e => setEditNotes(e.target.value)}
                  rows={3}
                  placeholder="Why was this edited?"
                  style={{ display: 'block', width: '100%', padding: '6px 10px', border: '1px solid #cbd5e1', borderRadius: 4 }}
                />
              </div>
              <button type="submit" style={btnPrimary}>Save Edit</button>
              {editMsg && <span style={{ marginLeft: 10, color: '#16a34a', fontSize: 13 }}>{editMsg}</span>}
            </form>
          </section>
        </>
      )}

      {isApproved && (
        <p style={{ color: '#16a34a', fontWeight: 600, marginTop: 16 }}>
          ✓ This record is approved and locked for audit.
        </p>
      )}
    </div>
  )
}

function Row({ label, value }) {
  return (
    <div style={{ display: 'flex', padding: '5px 0', borderBottom: '1px solid #f1f5f9', fontSize: 14 }}>
      <span style={{ width: 160, color: '#64748b', flexShrink: 0 }}>{label}</span>
      <span>{value}</span>
    </div>
  )
}

const section = { marginBottom: 24, padding: 16, border: '1px solid #e2e8f0', borderRadius: 6 }
const sectionTitle = { margin: '0 0 12px', fontSize: 15 }
const label = { display: 'block', marginBottom: 4, fontSize: 13, color: '#374151' }
const btnPrimary = { background: '#1e40af', color: 'white', border: 'none', padding: '6px 14px', borderRadius: 4, cursor: 'pointer' }
const btnSecondary = { background: '#f1f5f9', border: '1px solid #cbd5e1', padding: '6px 14px', borderRadius: 4, cursor: 'pointer' }