/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        cyber: {
          blue: '#00d4ff',
          purple: '#bf00ff',
          pink: '#ff00aa',
          dark: '#050510',
          darker: '#020208',
          card: '#0a0a1a',
          border: '#1a1a3a',
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        display: ['Orbitron', 'sans-serif'],
      },
      animation: {
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'scan': 'scan 3s linear infinite',
        'float': 'float 6s ease-in-out infinite',
        'border-glow': 'borderGlow 2s ease-in-out infinite',
        'spin-slow': 'spin 8s linear infinite',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 20px #00d4ff44, 0 0 40px #00d4ff22' },
          '50%': { boxShadow: '0 0 40px #00d4ff88, 0 0 80px #00d4ff44' },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        borderGlow: {
          '0%, 100%': { borderColor: '#00d4ff' },
          '50%': { borderColor: '#bf00ff' },
        }
      },
      backgroundImage: {
        'cyber-grid': 'linear-gradient(rgba(0,212,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(0,212,255,0.05) 1px, transparent 1px)',
        'gradient-cyber': 'linear-gradient(135deg, #00d4ff, #bf00ff)',
        'gradient-dark': 'linear-gradient(180deg, #050510 0%, #020208 100%)',
      },
      backgroundSize: {
        'grid': '50px 50px',
      }
    }
  },
  plugins: []
}
