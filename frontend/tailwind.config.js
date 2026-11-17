/**
 * BLOODLINK design system: "Urgency without panic. Hope without cliché. Premium without coldness."
 *
 * Theming: class names describe the DARK appearance (e.g. `bg-slate-900 text-slate-300`). Every themed palette is
 * backed by CSS variables; in light mode the scale is mirrored (slate fully, accents for their tint/text shades
 * while the solid 500-700 fills stay put), so each class gets a sensible light-mode counterpart automatically.
 * `blood`, `rarity`, `white` and `black` are fixed in both themes; use them (plus `dark:`) for literal colors.
 */
import defaults from 'tailwindcss/colors';
import plugin from 'tailwindcss/plugin';

const SHADES = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950];
// light-mode shade used for each class shade
const NEUTRAL = { 50: 950, 100: 900, 200: 800, 300: 700, 400: 600, 500: 500, 600: 400, 700: 300, 800: 200, 900: 100, 950: 50 };
const ACCENT = { 50: 950, 100: 900, 200: 800, 300: 700, 400: 600, 500: 500, 600: 600, 700: 700, 800: 200, 900: 100, 950: 50 };
const THEMED = {
  slate: NEUTRAL,
  ...Object.fromEntries(
    ['red', 'orange', 'amber', 'yellow', 'green', 'emerald', 'teal', 'cyan', 'sky', 'blue', 'indigo', 'violet', 'purple', 'fuchsia', 'pink', 'rose'].map(
      (f) => [f, ACCENT],
    ),
  ),
};
const rgb = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16)).join(' ');

const themedColors = Object.fromEntries(
  Object.keys(THEMED).map((f) => [f, Object.fromEntries(SHADES.map((s) => [s, `rgb(var(--${f}-${s}) / <alpha-value>)`]))]),
);

const themeVariables = plugin(({ addBase }) => {
  const light = {};
  const dark = {};
  for (const [family, map] of Object.entries(THEMED)) {
    for (const s of SHADES) {
      dark[`--${family}-${s}`] = rgb(defaults[family][s]);
      light[`--${family}-${s}`] = rgb(defaults[family][map[s]]);
    }
  }
  addBase({ ':root': { ...light, colorScheme: 'light' }, '.dark': { ...dark, colorScheme: 'dark' } });
});

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        ...themedColors,
        blood: {
          50: '#FEF2F2', 100: '#FEE2E2', 200: '#FECACA', 300: '#FCA5A5', 400: '#F87171', 500: '#EF4444',
          600: '#DC2626', 700: '#B91C1C', 800: '#991B1B', 900: '#7F1D1D', 950: '#450A0A',
        },
        rarity: { common: '#94A3B8', uncommon: '#10B981', rare: '#3B82F6', epic: '#8B5CF6', legendary: '#F59E0B', mythic: '#EF4444' },
      },
      fontFamily: {
        sans: ['Inter', 'SF Pro Text', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'SF Mono', 'ui-monospace', 'monospace'],
      },
      boxShadow: {
        'glow-red': '0 0 25px rgba(220, 38, 38, 0.4)',
        'glow-amber': '0 0 25px rgba(245, 158, 11, 0.5)',
        'glow-purple': '0 0 25px rgba(139, 92, 246, 0.5)',
        'card-hover': '0 8px 30px rgba(0, 0, 0, 0.08)',
      },
      keyframes: {
        pulseRing: { '0%': { transform: 'scale(.9)', opacity: '.7' }, '100%': { transform: 'scale(1.6)', opacity: '0' } },
        'pulse-sos': { '0%, 100%': { boxShadow: '0 0 0 0 rgba(220, 38, 38, 0.7)' }, '50%': { boxShadow: '0 0 0 15px rgba(220, 38, 38, 0)' } },
        heartbeat: { '0%, 100%': { transform: 'scale(1)' }, '14%': { transform: 'scale(1.1)' }, '28%': { transform: 'scale(1)' }, '42%': { transform: 'scale(1.1)' }, '70%': { transform: 'scale(1)' } },
        float: { '0%, 100%': { transform: 'translateY(0)' }, '50%': { transform: 'translateY(-10px)' } },
        glow: { '0%, 100%': { boxShadow: '0 0 5px rgba(245, 158, 11, 0.5)' }, '50%': { boxShadow: '0 0 25px rgba(245, 158, 11, 0.8)' } },
        'glow-red': { '0%, 100%': { boxShadow: '0 0 6px rgba(239, 68, 68, 0.5)' }, '50%': { boxShadow: '0 0 28px rgba(239, 68, 68, 0.85)' } },
        'slide-up': { from: { opacity: '0', transform: 'translateY(20px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
        shimmer: { '0%': { backgroundPosition: '-1000px 0' }, '100%': { backgroundPosition: '1000px 0' } },
      },
      animation: {
        'pulse-ring': 'pulseRing 1.6s ease-out infinite',
        'pulse-sos': 'pulse-sos 2s infinite',
        heartbeat: 'heartbeat 1.5s ease-in-out infinite',
        float: 'float 3s ease-in-out infinite',
        glow: 'glow 2s ease-in-out infinite',
        'glow-red': 'glow-red 2s ease-in-out infinite',
        'slide-up': 'slide-up 0.3s ease-out',
        shimmer: 'shimmer 2s linear infinite',
      },
      transitionTimingFunction: { spring: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)' },
      backdropBlur: { xs: '2px' },
    },
  },
  plugins: [themeVariables],
};
