import { createContext, useCallback, useContext, useState } from 'react';
import { AlertTriangle, CheckCircle2 } from 'lucide-react';
import { cx } from '../lib/utils';

const ToastContext = createContext(() => {});

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const toast = useCallback((message, type = 'success') => {
    const id = Math.random();
    setToasts((t) => [...t, { id, message, type }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 4500);
  }, []);

  return (
    <ToastContext.Provider value={toast}>
      {children}
      <div className="pointer-events-none fixed bottom-4 right-4 z-[60] flex w-[min(24rem,calc(100vw-2rem))] flex-col gap-2">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={cx(
              'pointer-events-auto flex items-start gap-2 rounded-xl border px-4 py-3 text-sm shadow-xl',
              t.type === 'error' ? 'border-red-500/50 bg-red-950 text-red-100' : 'border-emerald-500/40 bg-slate-900 text-slate-100',
            )}
          >
            {t.type === 'error' ? (
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-red-400" />
            ) : (
              <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
            )}
            {t.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export const useToast = () => useContext(ToastContext);
