import { motion } from 'framer-motion'
import { Cpu, ScanLine, Layers, CheckCircle } from 'lucide-react'

interface LoadingStateProps {
  progress: number
  status: string
}

const stages = [
  { icon: Cpu,         label: 'PREPROCESSING',      threshold: 0  },
  { icon: ScanLine,    label: 'SCENE ANALYSIS',      threshold: 25 },
  { icon: Layers,      label: 'MESH GENERATION',     threshold: 55 },
  { icon: CheckCircle, label: 'FINALIZING MODEL',    threshold: 85 },
]

export default function LoadingState({ progress, status }: LoadingStateProps) {
  const currentStageIdx = stages.reduce((acc, stage, i) => {
    return progress >= stage.threshold ? i : acc
  }, 0)
  const currentStage = stages[currentStageIdx]
  const Icon = currentStage.icon

  const displayStatus = status && status.length > 0 ? status : currentStage.label

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center gap-8 py-8"
    >
      <div className="relative">
        <motion.div
          className="w-32 h-32 rounded-full flex items-center justify-center"
          style={{
            background: 'rgba(0,212,255,0.05)',
            border: '1px solid rgba(0,212,255,0.2)',
          }}
        >
          <motion.div
            className="absolute inset-0 rounded-full"
            style={{
              background: 'conic-gradient(from 0deg, #00d4ff, #bf00ff, transparent)',
              mask: 'radial-gradient(farthest-side, transparent calc(100% - 3px), white calc(100% - 3px))',
              WebkitMask: 'radial-gradient(farthest-side, transparent calc(100% - 3px), white calc(100% - 3px))',
            }}
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
          />
          <motion.div
            animate={{ scale: [1, 1.15, 1], opacity: [0.7, 1, 0.7] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <Icon className="w-10 h-10" style={{ color: '#00d4ff' }} />
          </motion.div>
        </motion.div>

        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1.5 h-1.5 rounded-full"
            style={{
              background: i % 2 === 0 ? '#00d4ff' : '#bf00ff',
              top: '50%',
              left: '50%',
            }}
            animate={{
              x: Math.cos((i * Math.PI * 2) / 6) * 72,
              y: Math.sin((i * Math.PI * 2) / 6) * 72,
              opacity: [0.3, 1, 0.3],
              scale: [0.5, 1, 0.5],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              delay: i * 0.33,
              ease: 'easeInOut',
            }}
          />
        ))}
      </div>

      <div className="text-center">
        <motion.h3
          className="font-display text-xl font-bold tracking-widest mb-2"
          style={{ color: '#00d4ff' }}
          animate={{ opacity: [0.7, 1, 0.7] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          GENERATING WITH OPEN SOURCE AI ENGINE
        </motion.h3>
        <motion.p
          key={displayStatus}
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          className="font-mono text-sm tracking-wider"
          style={{ color: '#bf00ff' }}
        >
          {displayStatus}
        </motion.p>
      </div>

      <div className="w-full max-w-md">
        <div className="flex justify-between font-mono text-xs mb-2" style={{ color: '#606080' }}>
          <span>PROGRESS</span>
          <span style={{ color: '#00d4ff' }}>{progress}%</span>
        </div>
        <div className="w-full h-2 rounded-full overflow-hidden" style={{ background: 'rgba(0,212,255,0.1)' }}>
          <motion.div
            className="h-full rounded-full"
            style={{
              background: 'linear-gradient(90deg, #00d4ff, #bf00ff)',
              boxShadow: '0 0 10px rgba(0,212,255,0.8)',
            }}
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>

        <div className="grid grid-cols-4 gap-1 mt-4">
          {stages.map((stage, i) => {
            const StageIcon = stage.icon
            const done = i < currentStageIdx
            const active = i === currentStageIdx
            return (
              <div key={i} className="flex flex-col items-center gap-1">
                <div
                  className="w-8 h-8 rounded flex items-center justify-center transition-all duration-500"
                  style={{
                    background: done
                      ? 'rgba(0,212,255,0.2)'
                      : active
                      ? 'rgba(0,212,255,0.1)'
                      : 'rgba(255,255,255,0.03)',
                    border: `1px solid ${
                      done ? 'rgba(0,212,255,0.6)' : active ? 'rgba(0,212,255,0.3)' : 'rgba(255,255,255,0.07)'
                    }`,
                  }}
                >
                  <StageIcon
                    className="w-4 h-4"
                    style={{ color: done ? '#00d4ff' : active ? '#00d4ffaa' : '#30304050' }}
                  />
                </div>
                <span
                  className="font-mono text-center leading-tight"
                  style={{
                    fontSize: '8px',
                    color: active ? '#00d4ff' : done ? '#608080' : '#303050',
                  }}
                >
                  {stage.label.split(' ').slice(-1)[0]}
                </span>
              </div>
            )
          })}
        </div>
      </div>
    </motion.div>
  )
}
