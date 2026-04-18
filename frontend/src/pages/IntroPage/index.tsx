import { useRef } from 'react'
import { useIntroPage } from './IntroPage'
import type { SearchResultDTO } from './IntroPage'
import './index.css'

type ResultMeta = {
  image_path?: string
}

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

const BACKEND_URL = 'http://localhost:8000'

function getImageUrl(item: SearchResultDTO) {
  const meta = item.meta as ResultMeta | null
  const imagePath = meta?.image_path

  if (!imagePath) {
    return null
  }

  return new URL(imagePath, `${BACKEND_URL}/`).toString()
}

function MetaModal({ item, onClose }: { item: SearchResultDTO; onClose: () => void }) {
  const imageUrl = getImageUrl(item)

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3 className="modal-title">Image Details : {item.id}</h3>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          {imageUrl && (
            <div className="modal-image-preview">
              <img
                src={imageUrl}
                alt={`Preview ${item.id}`}
                className="modal-preview-img"
                onError={(e) => { (e.target as HTMLImageElement).parentElement!.style.display = 'none' }}
              />
            </div>
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
            {item.meta && Object.entries(item.meta).map(([key, value]) => (
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

// ResultRow — add thumbnail as first cell
function ResultRow({ item, onShowDetails }: { item: SearchResultDTO; onShowDetails: (item: SearchResultDTO) => void }) {
  const color =
    item.match_percentage > 98 ? 'high' :
    item.match_percentage >= 95 ? 'mid' :
    item.match_percentage >= 90 ? 'low' : ''

  const imageUrl = getImageUrl(item)

  return (
    <tr className="result-row">
      <td className="thumb-cell">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={`Match ${item.id}`}
            className="result-thumb"
            onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
          />
        ) : (
          <div className="thumb-placeholder">?</div>
        )}
      </td>
      <td className="hash-cell">
        <code className="hash">{item.id}</code>
      </td>
      <td className="hash-cell">
        <code className="hash">{item.uid ?? '—'}</code>
      </td>
      <td className="score-cell">
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
                    <th>ID</th>
                    <th>UID</th>
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