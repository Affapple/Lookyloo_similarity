import { useState, useCallback } from 'react'

export interface ImageMeta {
  uid: string
  blob: string
  width: number
  height: number
  format: string
  fileSize: string
  capturedAt: string
  source: string
}

export interface SearchResultDTO {
  id: string
  match_percentage: number
  uid: string | null
  sha256?: string | null
  original_filename?: string | null
  capture_date?: string | null
  meta: Record<string, unknown> | null
  image_url?: string | null
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export function useIntroPage() {
  const [preview, setPreview] = useState<string | null>(null)
  const [image, setImage] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<SearchResultDTO[] | null>(null)
  const [modalItem, setModalItem] = useState<SearchResultDTO | null>(null)

  const handleFile = useCallback((file: File) => {
    if (!file.type.startsWith('image/')) return
    setImage(file)
    setPreview(URL.createObjectURL(file))
    setResults(null)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }, [handleFile])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback(() => {
    setIsDragging(false)
  }, [])

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }, [handleFile])

  const handleSearch = useCallback(async () => {
    if (!image) return
    setIsLoading(true)
    setResults(null)

    try {
      const formData = new FormData()
      formData.append('image', image)

      const response = await fetch(`${API_BASE_URL}/search/by-image`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`Upload failed with status: ${response.status}`)
      }

      const data = await response.json()
      console.log('Upload success:', data)
      const normalizedResults: SearchResultDTO[] = (data.results ?? []).map((item: SearchResultDTO) => ({
        ...item,
        image_url: item.image_url
          ? (item.image_url.startsWith('http') ? item.image_url : `${API_BASE_URL}${item.image_url}`)
          : null,
      }))
      setResults(normalizedResults)
    } catch (error) {
      console.error('Error uploading image to /search/by-image:', error)
      alert('Error uploading image to backend')
    } finally {
      setIsLoading(false)
    }
  }, [image])

  const handleReset = useCallback(() => {
    setPreview(null)
    setImage(null)
    setResults(null)
  }, [])

  const openModal = useCallback((item: SearchResultDTO) => {
  setModalItem(item)
}, [])

  const closeModal = useCallback(() => {
    setModalItem(null)
  }, [])

  return {
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
  }
}