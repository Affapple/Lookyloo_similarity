import { useRef } from 'react'
import { useIntroPage } from './IntroPage'
import type { SearchResultDTO } from './IntroPage'
import './index.css'

function UploadZone({
  preview,
  isDragging,
  onDrop,
  onDragOver,
  onDragLeave,
  onInputChange,
  onReset,
}: {
  preview: string | null
  isDragging: boolean
  onDrop: (e: React.DragEvent) => void
  onDragOver: (e: React.DragEvent) => void
  onDragLeave: () => void
  onInputChange: (e: React.ChangeEvent<HTMLInputElement>) => void
  onReset: () => void
}) {
  const inputRef = useRef<HTMLInputElement>(null)

  return (
    <div
      className={`upload-zone ${isDragging ? 'dragging' : ''} ${preview ? 'has-preview' : ''}`}
      onDrop={onDrop}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onClick={() => !preview && inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        style={{ display: 'none' }}
        onChange={onInputChange}
      />

      {preview ? (
        <div className="preview-wrapper">
          <img src={preview} alt="Uploaded preview" className="preview-img" />
          <button className="reset-btn" onClick={(e) => { e.stopPropagation(); onReset() }}>
            ✕ Remove
          </button>
        </div>
      ) : (
        <div className="upload-placeholder">
          <div className="upload-icon">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
          </div>
          <p className="upload-title">Drag & drop your image here</p>
          <p className="upload-sub">or click to browse</p>
          <p className="upload-formats">JPG · PNG · WEBP · GIF</p>
        </div>
      )}
    </div>
  )
}

function MetaModal({ item, onClose }: { item: SearchResultDTO; onClose: () => void }) {
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3 className="modal-title">Image Details : {item.id}</h3>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          {item.image_url && (
            <img src={item.image_url} alt={`Matched ${item.id}`} className="modal-img" />
          )}
          <div className="meta-grid">
            <div className="meta-row">
              <span className="meta-label">ID</span>
              <code className="meta-value mono">{item.id}</code>
            </div>
            <div className="meta-row">
              <span className="meta-label">UID</span>
              <code className="meta-value mono">{item.uid ?? '—'}</code>
            </div>
            <div className="meta-row">
              <span className="meta-label">Match</span>
              <span className="meta-value">{item.match_percentage.toFixed(1)}%</span>
            </div>
            <div className="meta-row">
              <span className="meta-label">Filename</span>
              <span className="meta-value">{item.original_filename ?? '—'}</span>
            </div>
            <div className="meta-row">
              <span className="meta-label">Capture Date</span>
              <span className="meta-value">{item.capture_date ?? '—'}</span>
            </div>
            <div className="meta-row">
              <span className="meta-label">SHA-256</span>
              <code className="meta-value mono small">{item.sha256 ?? '—'}</code>
            </div>
            {item.meta && Object.entries(item.meta)
              .filter(([key]) => !['sha256', 'original_filename', 'capture_date'].includes(key))
              .map(([key, value]) => (
              <div className="meta-row" key={key}>
                <span className="meta-label">{key}</span>
                <span className="meta-value">{String(value)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function ResultRow({ item, onShowDetails }: { item: SearchResultDTO; onShowDetails: (item: SearchResultDTO) => void }) {
  const color =
    item.match_percentage > 98 ? 'high' :
    item.match_percentage >= 95 ? 'mid' :
    item.match_percentage >= 90 ? 'low' : ''

  return (
    <tr className="result-row">
      <td className="thumb-cell">
        {item.image_url ? (
          <img src={item.image_url} alt={`Matched ${item.id}`} className="thumb" />
        ) : (
          '—'
        )}
      </td>
      <td className="url-cell">
        <span title={item.original_filename ?? ''}>
          {item.original_filename ?? '—'}
        </span>
      </td>
      <td>
        {item.capture_date ?? '—'}
      </td>
      <td className="hash-cell">
        <span className={`badge ${color}`}>{item.match_percentage.toFixed(1)}%</span>
      </td>
      <td className="actions-cell">
        <button className="details-btn" onClick={() => onShowDetails(item)}>
          Show Details
        </button>
      </td>
    </tr>
  )
}

export function IntroPage() {
  const {
    preview,
    image,
    isDragging,
    isLoading,
    results,
    modalItem,
    handleDrop,
    handleDragOver,
    handleDragLeave,
    handleInputChange,
    handleSearch,
    handleReset,
    openModal,
    closeModal,
  } = useIntroPage()

  return (
    <div className="page">
      <header className="header">
        <div className="header-logos">
          <img
            src="universite-du-luxembourg-logo.svg"
            alt="University of Luxembourg"
            className="header-logo uni-logo"
          />
          {/*
          <img
            src="crest-ucd.png"
            alt="UCD Crest"
            className="header-logo ucd-logo"
          />
          */}
          <img
            src="https://lookyloo.circl.lu/static/lookyloo.png"
            alt="Lookyloo"
            className="header-logo lookyloo-logo"
          />
        </div>
      </header>

      <main className="main">
        <div className="hero-text">
          <h1>Find similar images</h1>
          <p>Upload an image and find visually similar matches with similarity score.</p>
        </div>

        <UploadZone
          preview={preview}
          isDragging={isDragging}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onInputChange={handleInputChange}
          onReset={handleReset}
        />

        <button
          className="search-btn"
          onClick={handleSearch}
          disabled={!image || isLoading}
        >
          {isLoading ? (
            <span className="loading-text">
              <span className="spinner" />
              Searching...
            </span>
          ) : (
            'Find Similar Images'
          )}
        </button>

        {results && (
          <div className="results-section">
            <h2 className="results-title">Top {results.length} similar images</h2>
            <div className="table-wrapper">
              <table className="results-table">
                <thead>
                  <tr>
                    <th>Image</th>
                    <th>Filename</th>
                    <th>Capture Date</th>
                    <th>Similarity</th>
                    <th>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map(item => (
                    <ResultRow key={item.id} item={item} onShowDetails={openModal} />
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>

      {modalItem && <MetaModal item={modalItem} onClose={closeModal} />}
    </div>
  )
}

export default IntroPage