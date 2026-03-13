import { Suspense, useRef, useEffect, useState } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Environment, useGLTF, PresentationControls, ContactShadows, Html } from '@react-three/drei'
import { motion } from 'framer-motion'
import { RotateCcw, ZoomIn, ZoomOut, Download, Printer } from 'lucide-react'
import * as THREE from 'three'

function Model({ url }: { url: string }) {
  const { scene } = useGLTF(url)
  const groupRef = useRef<THREE.Group>(null)

  useEffect(() => {
    if (!scene) return
    scene.traverse((child) => {
      if ((child as THREE.Mesh).isMesh) {
        const mesh = child as THREE.Mesh
        mesh.castShadow = true
        mesh.receiveShadow = true
      }
    })
    const box = new THREE.Box3().setFromObject(scene)
    const center = box.getCenter(new THREE.Vector3())
    const size = box.getSize(new THREE.Vector3())
    const maxDim = Math.max(size.x, size.y, size.z)
    scene.position.sub(center)
    if (maxDim > 0) {
      const scale = 2 / maxDim
      scene.scale.setScalar(scale)
    }
  }, [scene])

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = state.clock.getElapsedTime() * 0.15
    }
  })

  return (
    <group ref={groupRef}>
      <primitive object={scene} />
    </group>
  )
}

function CyberGrid() {
  return (
    <gridHelper
      args={[20, 40, '#00d4ff', '#1a1a3a']}
      position={[0, -1.5, 0]}
    />
  )
}

function SceneSetup() {
  const { gl } = useThree()
  useEffect(() => {
    gl.shadowMap.enabled = true
    gl.shadowMap.type = THREE.PCFSoftShadowMap
  }, [gl])
  return null
}

interface ModelViewerProps {
  modelUrl: string
  onDownload: () => void
  onDownloadOptimized: () => void
  isDownloading: boolean
}

export default function ModelViewer({ modelUrl, onDownload, onDownloadOptimized, isDownloading }: ModelViewerProps) {
  const [zoom, setZoom] = useState(5)
  const controlsRef = useRef<any>(null)

  const handleReset = () => {
    if (controlsRef.current) {
      controlsRef.current.reset()
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6 }}
      className="flex flex-col gap-4"
    >
      <div className="relative w-full overflow-hidden corner-clip"
        style={{
          height: '480px',
          background: 'rgba(2,2,8,0.95)',
          border: '1px solid rgba(0,212,255,0.2)',
          boxShadow: '0 0 40px rgba(0,212,255,0.1)',
        }}>

        <div className="absolute top-3 left-3 z-10 px-3 py-1 font-mono text-xs font-bold tracking-widest corner-clip-sm"
          style={{ background: 'rgba(0,212,255,0.15)', border: '1px solid rgba(0,212,255,0.4)', color: '#00d4ff' }}>
          3D FORGE VIEWER
        </div>

        <div className="absolute top-3 right-3 z-10 flex gap-2">
          <button onClick={handleReset}
            className="p-2 rounded transition-all hover:scale-110"
            style={{ background: 'rgba(0,212,255,0.1)', border: '1px solid rgba(0,212,255,0.3)', color: '#00d4ff' }}
            title="Reset view">
            <RotateCcw className="w-4 h-4" />
          </button>
          <button onClick={() => setZoom(z => Math.max(2, z - 1))}
            className="p-2 rounded transition-all hover:scale-110"
            style={{ background: 'rgba(0,212,255,0.1)', border: '1px solid rgba(0,212,255,0.3)', color: '#00d4ff' }}
            title="Zoom in">
            <ZoomIn className="w-4 h-4" />
          </button>
          <button onClick={() => setZoom(z => Math.min(10, z + 1))}
            className="p-2 rounded transition-all hover:scale-110"
            style={{ background: 'rgba(0,212,255,0.1)', border: '1px solid rgba(0,212,255,0.3)', color: '#00d4ff' }}
            title="Zoom out">
            <ZoomOut className="w-4 h-4" />
          </button>
        </div>

        <div className="absolute bottom-3 left-3 z-10 font-mono text-xs" style={{ color: '#303060' }}>
          DRAG TO ROTATE &bull; SCROLL TO ZOOM &bull; RIGHT-CLICK TO PAN
        </div>

        <Canvas
          camera={{ position: [0, 0, zoom], fov: 50 }}
          style={{ background: 'transparent' }}
          shadows
        >
          <SceneSetup />
          <color attach="background" args={['#020208']} />
          <fog attach="fog" args={['#020208', 8, 25]} />

          <ambientLight intensity={0.3} />
          <pointLight position={[5, 5, 5]} intensity={1} color="#00d4ff" castShadow />
          <pointLight position={[-5, -5, -5]} intensity={0.5} color="#bf00ff" />
          <spotLight
            position={[0, 8, 0]}
            angle={0.6}
            penumbra={0.8}
            intensity={2}
            color="#ffffff"
            castShadow
          />

          <Suspense fallback={
            <Html center>
              <div className="font-mono text-sm" style={{ color: '#00d4ff' }}>Loading model...</div>
            </Html>
          }>
            <Model url={modelUrl} />
            <Environment preset="city" />
            <ContactShadows
              position={[0, -1.5, 0]}
              opacity={0.4}
              scale={10}
              blur={2}
              far={4}
              color="#00d4ff"
            />
          </Suspense>

          <CyberGrid />
          <OrbitControls
            ref={controlsRef}
            enableDamping
            dampingFactor={0.05}
            minDistance={2}
            maxDistance={12}
            autoRotate={false}
          />
        </Canvas>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={onDownload}
          disabled={isDownloading}
          className="flex items-center justify-center gap-3 py-4 px-6 font-display font-bold tracking-wider text-sm corner-clip transition-all"
          style={{
            background: 'linear-gradient(135deg, rgba(0,212,255,0.15), rgba(191,0,255,0.15))',
            border: '1px solid rgba(0,212,255,0.4)',
            color: '#00d4ff',
            opacity: isDownloading ? 0.6 : 1,
          }}
        >
          <Download className="w-5 h-5" />
          DOWNLOAD GLB
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={onDownloadOptimized}
          disabled={isDownloading}
          className="flex items-center justify-center gap-3 py-4 px-6 font-display font-bold tracking-wider text-sm corner-clip transition-all"
          style={{
            background: 'linear-gradient(135deg, #00d4ff, #bf00ff)',
            color: '#fff',
            opacity: isDownloading ? 0.6 : 1,
            boxShadow: '0 0 20px rgba(0,212,255,0.4)',
          }}
        >
          <Printer className="w-5 h-5" />
          DOWNLOAD FOR 3D PRINTING
        </motion.button>
      </div>

      <div className="px-4 py-3 corner-clip-sm font-mono text-xs"
        style={{ background: 'rgba(191,0,255,0.06)', border: '1px solid rgba(191,0,255,0.2)', color: '#706080' }}>
        <span style={{ color: '#bf00ff' }}>PRINT NOTE: </span>
        GLB output includes PBR textures and is compatible with all major FDM slicers.
        Import directly into PrusaSlicer, Bambu Studio, Cura, or any GLTF-compatible tool.
      </div>
    </motion.div>
  )
}
