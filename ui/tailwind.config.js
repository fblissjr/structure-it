export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Rajdhani', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
        display: ['Orbitron', 'sans-serif'],
      },
      colors: {
        slate: { 950: '#020617' }, // Deep background
        violet: { 500: '#8b5cf6' }, // Primary accent
        
        // Cyberpunk Palette
        'neon-blue': '#00f3ff',
        'neon-purple': '#bc13fe',
        'neon-pink': '#ff00ff',
        'neon-green': '#0aff00',
        'neon-yellow': '#faff00',
      },
      backgroundImage: {
        'glass-gradient': 'linear-gradient(rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.01))',
        'cyber-grid': 'linear-gradient(transparent 0%, rgba(0, 243, 255, 0.1) 1%, transparent 2%), linear-gradient(90deg, transparent 0%, rgba(0, 243, 255, 0.1) 1%, transparent 2%)',
      },
      boxShadow: {
        'glow-blue': '0 0 15px rgba(0, 243, 255, 0.3), 0 0 30px rgba(0, 243, 255, 0.1)',
        'glow-purple': '0 0 15px rgba(188, 19, 254, 0.3), 0 0 30px rgba(188, 19, 254, 0.1)',
        'glow-pink': '0 0 15px rgba(255, 0, 255, 0.3), 0 0 30px rgba(255, 0, 255, 0.1)',
        'glow-green': '0 0 15px rgba(10, 255, 0, 0.3), 0 0 30px rgba(10, 255, 0, 0.1)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
