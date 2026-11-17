import { useEffect, useState } from 'react';

const KEY = 'bloodlink-theme'; // 'light' | 'dark' | 'system'
const media = () => window.matchMedia('(prefers-color-scheme: dark)');

function read() {
  try {
    return localStorage.getItem(KEY) || 'system';
  } catch {
    return 'system';
  }
}

function apply(mode) {
  const dark = mode === 'dark' || (mode === 'system' && media().matches);
  document.documentElement.classList.toggle('dark', dark);
}

/** Theme preference: light, dark or follow the OS. */
export function useTheme() {
  const [mode, setMode] = useState(read);

  useEffect(() => {
    apply(mode);
    try {
      if (mode === 'system') localStorage.removeItem(KEY);
      else localStorage.setItem(KEY, mode);
    } catch {
      /* storage blocked: still works for this visit */
    }
    if (mode !== 'system') return undefined;
    const m = media();
    const onChange = () => apply('system');
    m.addEventListener('change', onChange);
    return () => m.removeEventListener('change', onChange);
  }, [mode]);

  const cycle = () => setMode((m) => (m === 'light' ? 'dark' : m === 'dark' ? 'system' : 'light'));
  return { mode, setMode, cycle };
}
