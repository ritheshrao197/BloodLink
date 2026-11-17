/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] },
      keyframes: {
        pulseRing: { '0%': { transform: 'scale(.9)', opacity: '.7' }, '100%': { transform: 'scale(1.6)', opacity: '0' } },
        glow: { '0%, 100%': { filter: 'brightness(1)' }, '50%': { filter: 'brightness(1.25) saturate(1.2)' } },
      },
      animation: { 'pulse-ring': 'pulseRing 1.6s ease-out infinite', glow: 'glow 2.4s ease-in-out infinite' },
    },
  },
  plugins: [],
};
