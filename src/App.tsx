import { useState, useCallback } from 'react'
import { Cpu, AlertCircle, CheckCircle2, Timer } from 'lucide-react'
import DropZone from './components/DropZone'
import LoadingState from './components/LoadingState'
import ModelViewer from './components/ModelViewer'

export default function App() {
  const [appState, setAppState] = useState('idle')
  const [modelUrl, setModelUrl] = useState(null)
  const [errorMsg, setErrorMsg] = useState('')

  const handleFileSelected = useCallback(async (file: File) => {
    setAppState('processing')
    setErrorMsg('')

    try {
      const formData = new FormData()
      formData.append('image', file)

      // ÖNEMLİ: Backend 3001'de çalıştığı için buraya direkt tam adres yazıyoruz
      const res = await fetch('http://localhost:3001/api/forge', { 
        method: 'POST', 
        body: formData 
      })

      // Eğer cevap JSON değilse (HTML ise) burada yakalıyoruz
      const contentType = res.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        throw new Error("Sunucu JSON yerine hata sayfası döndürdü. Backend'in (node server/index.js) açık olduğundan emin ol kanka!");
      }

      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Yükleme başarısız')

      setModelUrl(data.modelUrl)
      setAppState('done')
    } catch (err: any) {
      setAppState('error')
      setErrorMsg(err.message)
    }
  }, [])

  return (
    <div className="min-h-screen relative" style={{ background: '#020208', color: '#fff', padding: '20px' }}>
      <nav className="flex justify-between items-center mb-10 pb-4" style={{ borderBottom: '1px solid #1a1a2e' }}>
        <div className="flex items-center gap-2">
          <Cpu className="text-blue-400" />
          <span className="font-bold tracking-widest text-blue-400">ATLAS AI v2.1</span>
        </div>
        <div className="text-xs text-green-500 animate-pulse">● SYSTEM ONLINE (Port: 5174)</div>
      </nav>

      <main className="max-w-4xl mx-auto text-center">
        <h1 className="text-6xl font-black mb-6" style={{ letterSpacing: '-2px' }}>
          <span style={{ color: '#00d4ff' }}>IMAGE</span> TO <span style={{ color: '#bf00ff' }}>3D</span>
        </h1>

        <div className="p-8 rounded-xl" style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(0,212,255,0.2)' }}>
          {appState === 'idle' && <DropZone onFileSelected={handleFileSelected} disabled={false} />}
          {appState === 'processing' && <LoadingState progress={50} status="AI motoru modeli işliyor..." />}
          {appState === 'done' && (
            <div>
              <ModelViewer modelUrl={modelUrl} onDownload={() => {}} isDownloading={false} />
              <button onClick={() => setAppState('idle')} className="mt-4 text-blue-400 underline">Yeni Model</button>
            </div>
          )}
          {appState === 'error' && (
            <div className="py-10">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <p className="text-red-400 font-bold">HATA ALINDI</p>
              <p className="text-xs opacity-60 mt-2">{errorMsg}</p>
              <button onClick={() => setAppState('idle')} className="mt-6 px-6 py-2 bg-blue-600 rounded">Tekrar Dene</button>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}