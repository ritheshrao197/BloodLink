import { useEffect, useState } from 'react';
import { AlertTriangle, Check, Copy, Loader2, X } from 'lucide-react';
import { BADGES, cx } from '../lib/utils';

export function BloodTag({ group, size = 'md', className }) {
  const sizes = { sm: 'h-7 min-w-7 text-xs', md: 'h-9 min-w-9 text-sm', lg: 'h-14 min-w-14 text-xl' };
  return (
    <span
      className={cx(
        'inline-flex items-center justify-center rounded-lg bg-red-600/15 px-1.5 font-extrabold text-red-400 ring-1 ring-red-500/40',
        sizes[size],
        className,
      )}
    >
      {group}
    </span>
  );
}

export function BadgeChip({ badge, showTitle = false }) {
  const b = BADGES[badge] || BADGES.Bronze;
  return (
    <span className={cx('inline-flex items-center gap-1 text-sm font-semibold', b.text)} title={b.title}>
      <span className="text-base leading-none">{b.icon}</span>
      {badge}
      {showTitle && <span className="font-normal text-slate-400">· {b.title}</span>}
    </span>
  );
}

export function Spinner({ className }) {
  return <Loader2 className={cx('animate-spin', className || 'h-5 w-5')} />;
}

export function Loading({ label = 'Loading…' }) {
  return (
    <div className="flex items-center justify-center gap-2 py-16 text-slate-400">
      <Spinner /> {label}
    </div>
  );
}

export function ErrorBox({ error }) {
  if (!error) return null;
  return (
    <div className="flex items-start gap-2 rounded-lg border border-red-500/40 bg-red-950/40 px-3 py-2.5 text-sm text-red-200">
      <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
      <span>{error.message || String(error)}</span>
    </div>
  );
}

export function Empty({ icon: Icon, title, children }) {
  return (
    <div className="card flex flex-col items-center px-6 py-12 text-center">
      {Icon && <Icon className="mb-3 h-10 w-10 text-slate-600" />}
      <p className="font-semibold text-slate-200">{title}</p>
      {children && <div className="mt-1 text-sm text-slate-400">{children}</div>}
    </div>
  );
}

export function PageHeader({ icon: Icon, title, subtitle, children }) {
  return (
    <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="flex items-center gap-3 text-3xl font-extrabold tracking-tight sm:text-4xl">
          {Icon && <Icon className="h-8 w-8 text-red-500" />}
          {title}
        </h1>
        {subtitle && <p className="mt-2 max-w-2xl text-slate-400">{subtitle}</p>}
      </div>
      {children}
    </div>
  );
}

export function StatCard({ icon: Icon, label, value, hint, accent = 'text-red-400' }) {
  return (
    <div className="card p-5">
      <div className="flex items-center justify-between text-sm text-slate-400">
        {label}
        {Icon && <Icon className={cx('h-5 w-5', accent)} />}
      </div>
      <div className="mt-2 text-3xl font-extrabold tabular-nums">{value ?? '—'}</div>
      {hint && <div className="mt-1 text-xs text-slate-500">{hint}</div>}
    </div>
  );
}

export function Modal({ open, onClose, title, children }) {
  useEffect(() => {
    if (!open) return undefined;
    const onKey = (e) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, onClose]);
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/70 p-4 sm:items-center" onClick={onClose}>
      <div
        className="card w-full max-w-md border-slate-700 bg-slate-900 p-6 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-bold">{title}</h2>
          <button onClick={onClose} className="rounded-lg p-1 text-slate-400 hover:bg-slate-800 hover:text-white" aria-label="Close">
            <X className="h-5 w-5" />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

export function CopyField({ value, label }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard blocked: the text is selectable anyway */
    }
  };
  return (
    <div>
      {label && <div className="label">{label}</div>}
      <div className="flex gap-2">
        <input readOnly value={value} className="input font-mono text-sm" onFocus={(e) => e.target.select()} />
        <button type="button" onClick={copy} className="btn-ghost shrink-0 px-3" aria-label="Copy">
          {copied ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
        </button>
      </div>
    </div>
  );
}

export function Toggle({ checked, onChange, disabled }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      disabled={disabled}
      onClick={() => onChange(!checked)}
      className={cx(
        'relative h-6 w-11 rounded-full transition disabled:opacity-50',
        checked ? 'bg-emerald-500' : 'bg-slate-700',
      )}
    >
      <span className={cx('absolute top-0.5 h-5 w-5 rounded-full bg-white transition', checked ? 'left-[22px]' : 'left-0.5')} />
    </button>
  );
}
