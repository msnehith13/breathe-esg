import { useState } from 'react'
import RunList from './components/RunList'
import RunDetail from './components/RunDetail'
import RecordDetail from './components/RecordDetail'
import UploadForm from './components/UploadForm'
import './App.css'

export default function App() {
  const [view, setView] = useState('runs')
  const [selectedRunId, setSelectedRunId] = useState(null)
  const [selectedRecordId, setSelectedRecordId] = useState(null)
  const [refreshKey, setRefreshKey] = useState(0)

  function openRun(runId) {
    setSelectedRunId(runId)
    setView('run_detail')
  }

  function openRecord(recordId) {
    setSelectedRecordId(recordId)
    setView('record_detail')
  }

  function goBack() {
    if (view === 'record_detail') setView('run_detail')
    else setView('runs')
  }

  function handleUploadComplete() {
    setRefreshKey(k => k + 1)
  }

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', padding: '24px', fontFamily: 'sans-serif' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 24 }}>
        <h1 style={{ margin: 0, fontSize: 22 }}>Breathe ESG — Analyst Dashboard</h1>
        {view !== 'runs' && (
          <button onClick={goBack} style={{ marginLeft: 'auto' }}>← Back</button>
        )}
      </div>

      {view === 'runs' && (
        <>
          <UploadForm onUploadComplete={handleUploadComplete} />
          <RunList key={refreshKey} onSelectRun={openRun} />
        </>
      )}
      {view === 'run_detail' && (
        <RunDetail runId={selectedRunId} onSelectRecord={openRecord} />
      )}
      {view === 'record_detail' && (
        <RecordDetail recordId={selectedRecordId} />
      )}
    </div>
  )
}