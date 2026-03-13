import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, ImagePlus, Zap } from 'lucide-react'

interface DropZoneProps {
  onFileSelected: (file: File) => void
  disabled?: boolean
}

export default function DropZone({ onFileSelected, disabled }: DropZoneProps) {
  const [preview, setPreview] = useState<string | null>(null)
  const [dragActive, setDragActive] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return
    const url = URL.createObjectURL(file)
    setPreview(url)
    onFileSelected(file)
  }, [onFileSelected])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpeg', '.jpg', '.png', '.webp'] },
    maxFiles: 1,
    disabled,
    onDragEnter: () => setDragActive(true),
    onDragLeave: () => setDragActive(false),
  })

  const active = isDragActive || dragActive

  return (
    <motion.div
      {...getRootProps()}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className={`relative cursor-pointer corner-clip transition-all duration-300 ${
        disabled ? 'opacity-50 cursor-not-allowed' : ''
      }`}
      style={{
        background: active
          ? 'rgba(0,212,255,0.08)'
          : preview
          ? 'rgba(10,10,26,0.9)'
          : 'rgba(5,5,16,0.8)',
        border: `1px solid ${active ? 'rgba(0,212,255,0.8)' : 'rgba(0,212,255,0.2)'}`,
        boxShadow: active
          ? '0 0 40px rgba(0,212,255,0.3), inset 0 0 40px rgba(0,212,255,0.05)'
          : preview
          ? '0 0 20px rgba(191,0,255,0.2)'
          : 'none',
        minHeight: '320px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <input {...getInputProps()} />

      <AnimatePresence mode="wait">
        {preview ? (
          <motion.div
            key="preview"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="relative w-full h-full"
            style={{ minHeight: '320px' }}
          >
            <img
              src={preview}
              alt="Preview"
              className="w-full h-full object-contain rounded"
              style={{ maxHeight: '320px' }}
            />
            <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-0 hover:bg-opacity-60 transition-all duration-300 group">
              <div className="opacity-0 group-hover:opacity-100 transition-opacity text-center">
                <ImagePlus className="w-8 h-8 mx-auto mb-2" style={{ color: '#00d4ff' }} />
                <p className="font-mono text-sm" style={{ color: '#00d4ff' }}>Replace Image</p>
              </div>
            </div>
            <div className="absolute top-3 right-3 px-2 py-1 text-xs font-mono corner-clip-sm"
              style={{ background: 'rgba(191,0,255,0.3)', border: '1px solid rgba(191,0,255,0.5)', color: '#bf00ff' }}>
              READY
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="empty"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="text-center p-12 select-none"
          >
            <motion.div
              animate={active ? { scale: 1.2, rotate: 5 } : { scale: 1, rotate: 0 }}
              transition={{ type: 'spring', stiffness: 300 }}
              className="mb-6 inline-flex items-center justify-center w-20 h-20 rounded-full"
              style={{
                background: 'rgba(0,212,255,0.1)',
                border: '1px solid rgba(0,212,255,0.3)',
                boxShadow: active ? '0 0 30px rgba(0,212,255,0.5)' : '0 0 15px rgba(0,212,255,0.2)',
              }}
            >
              {active ? (
                <Zap className="w-9 h-9" style={{ color: '#00d4ff' }} />
              ) : (
                <Upload className="w-9 h-9" style={{ color: '#00d4ff' }} />
              )}
            </motion.div>

            <h3 className="font-display text-xl font-bold mb-2 tracking-wider"
              style={{ color: active ? '#00d4ff' : '#a0a0c0' }}>
              {active ? 'DROP TO FORGE' : 'MAGIC DROPZONE'}
            </h3>
            <p className="font-mono text-sm mb-4" style={{ color: '#606080' }}>
              {active
                ? 'Release to upload your image...'
                : 'Drag & drop your image here, or click to browse'}
            </p>
            <div className="flex items-center justify-center gap-2 flex-wrap">
              {['JPEG', 'PNG', 'WEBP'].map((fmt) => (
                <span key={fmt} className="px-2 py-1 text-xs font-mono corner-clip-sm"
                  style={{ background: 'rgba(0,212,255,0.08)', border: '1px solid rgba(0,212,255,0.2)', color: '#607090' }}>
                  {fmt}
                </span>
              ))}
              <span className="px-2 py-1 text-xs font-mono corner-clip-sm"
                style={{ background: 'rgba(191,0,255,0.08)', border: '1px solid rgba(191,0,255,0.2)', color: '#907090' }}>
                MAX 20MB
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {active && (
        <motion.div
          className="absolute inset-0 pointer-events-none"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          style={{
            background: 'radial-gradient(ellipse at center, rgba(0,212,255,0.08) 0%, transparent 70%)',
          }}
        />
      )}
    </motion.div>
  )
}
