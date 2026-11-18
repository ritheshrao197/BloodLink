import { useEffect, useRef, useState } from 'react';
import { KeyRound, Send } from 'lucide-react';
import { api } from '../lib/api';
import { useSession } from '../lib/session';
import { useI18n } from '../i18n';
import { ErrorBox, Spinner } from './ui';

/**
 * Runs the Telegram flow: get a one-time link, open the bot, poll until the bot confirms.
 * purpose 'login' → onDone({token, user}); purpose 'link' (signed in) → onDone({user}).
 */
function useTelegramFlow(purpose, onDone) {
  const [state, setState] = useState({ phase: 'idle', url: null, error: null });
  const timer = useRef(null);
  useEffect(() => () => clearInterval(timer.current), []);

  const start = async () => {
    clearInterval(timer.current);
    const win = window.open('', '_blank'); // open now (inside the click) so pop-up blockers allow it
    try {
      const { nonce, url } = await api.auth.telegramStart(purpose);
      if (win) win.location.href = url;
      setState({ phase: 'waiting', url, error: null });
      const started = Date.now();
      timer.current = setInterval(async () => {
        try {
          const res = await api.auth.telegramPoll(nonce);
          if (res.status === 'pending' && Date.now() - started < 10 * 60 * 1000) return;
          clearInterval(timer.current);
          if (res.status === 'ok' || res.status === 'linked') {
            setState({ phase: 'done', url: null, error: null });
            onDone(res);
          } else setState({ phase: res.status, url: null, error: null });
        } catch {
          /* keep polling through hiccups */
        }
      }, 2000);
    } catch (e) {
      win?.close();
      setState({ phase: 'idle', url: null, error: e });
    }
  };
  return [state, start];
}

export function TelegramLinkButton({ className = '' }) {
  const { setUser } = useSession();
  const { t } = useI18n();
  const [state, start] = useTelegramFlow('link', (res) => setUser(res.user));
  return (
    <div className="space-y-2">
      <button onClick={start} className={`btn-primary from-sky-600 to-sky-700 shadow-sky-900/40 ${className}`} disabled={state.phase === 'waiting'}>
        {state.phase === 'waiting' ? <Spinner className="h-4 w-4" /> : <Send className="h-4 w-4" />} {t('auth.linkBtn')}
      </button>
      <FlowStatus state={state} />
    </div>
  );
}

function FlowStatus({ state }) {
  const { t } = useI18n();
  if (state.error) return <ErrorBox error={state.error} />;
  if (state.phase === 'waiting')
    return (
      <p className="text-xs text-slate-400">
        {t('auth.waiting')}{' '}
        {state.url && (
          <a href={state.url} target="_blank" rel="noreferrer" className="font-semibold text-sky-500 hover:underline">
            {t('auth.openAgain')}
          </a>
        )}
      </p>
    );
  const msg = { not_registered: 'auth.notRegistered', expired: 'auth.expired', taken: 'auth.linkTaken' }[state.phase];
  return msg ? <p className="text-xs text-amber-500">{t(msg)}</p> : null;
}

/** Sign-in panel: Telegram (real accounts) and, while the server allows it, demo-account codes. */
export default function SignInByCode({ onSignedIn, demo = true }) {
  const { signIn, config } = useSession();
  const { t, num } = useI18n();
  const [code, setCode] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const done = (res) => {
    signIn(res.user, res.token);
    onSignedIn?.(res.user);
  };
  const [tg, startTelegram] = useTelegramFlow('login', done);

  const submitDemo = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      done(await api.auth.demo(code.trim()));
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-3">
      {config?.telegram_login !== false && (
        <>
          <button onClick={startTelegram} className="btn-primary w-full from-sky-600 to-sky-700 shadow-sky-900/40" disabled={tg.phase === 'waiting'}>
            {tg.phase === 'waiting' ? <Spinner className="h-4 w-4" /> : <Send className="h-4 w-4" />} {t('auth.telegram')}
          </button>
          <FlowStatus state={tg} />
        </>
      )}
      {demo && config?.demo_login && (
        <form onSubmit={submitDemo} className="space-y-2">
          <div className="flex items-center gap-3 text-[11px] uppercase tracking-wide text-slate-500">
            <span className="h-px flex-1 bg-slate-800" /> {t('auth.demoTitle')} <span className="h-px flex-1 bg-slate-800" />
          </div>
          <div className="flex gap-2">
            <input
              className="input font-mono uppercase"
              placeholder={t('signin.placeholder')}
              aria-label={t('auth.demoTitle')}
              value={code}
              onChange={(e) => setCode(e.target.value)}
              required
            />
            <button className="btn-ghost shrink-0" disabled={busy}>
              {busy ? <Spinner className="h-4 w-4" /> : <KeyRound className="h-4 w-4" />} {t('common.signIn')}
            </button>
          </div>
          <p className="text-[11px] text-slate-500">{t('auth.demoHint')}</p>
          {config.demo_heroes?.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {config.demo_heroes.map((h) => (
                <button
                  key={h.code}
                  type="button"
                  onClick={() => setCode(h.code)}
                  className="inline-flex min-h-8 items-center gap-1.5 rounded-full border border-amber-500/50 bg-amber-500/10 px-3 py-1 text-xs font-bold text-amber-500 hover:bg-amber-500/20"
                  title={`${h.code} · ${h.achievements}/${h.total}`}
                >
                  ⭐ {h.name} · {num(h.achievements)}/{num(h.total)} 🏅
                </button>
              ))}
            </div>
          )}
          <ErrorBox error={error} />
        </form>
      )}
    </div>
  );
}

/** Admin sign-in (password configured on the server, or an admin Telegram account via the panel above). */
export function AdminSignIn() {
  const { signIn, config, user } = useSession();
  const { t } = useI18n();
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const res = await api.auth.admin(password);
      signIn(res.user, res.token);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  };
  return (
    <div className="card mx-auto max-w-md space-y-4 p-6">
      <h2 className="text-lg font-bold">{t('auth.adminTitle')}</h2>
      {user && !user.is_admin && <p className="text-sm text-amber-500">{t('auth.adminDenied')}</p>}
      <p className="text-sm text-slate-400">{t('auth.adminHint')}</p>
      {config?.admin_password_login && (
        <form onSubmit={submit} className="space-y-2">
          <label className="label" htmlFor="admin-pw">
            {t('auth.adminPassword')}
          </label>
          <input id="admin-pw" type="password" autoComplete="current-password" className="input" value={password} onChange={(e) => setPassword(e.target.value)} required />
          <ErrorBox error={error} />
          <button className="btn-primary w-full" disabled={busy}>
            {busy ? <Spinner className="h-4 w-4" /> : <KeyRound className="h-4 w-4" />} {t('auth.adminBtn')}
          </button>
        </form>
      )}
      {!user && <SignInByCode demo={false} />}
    </div>
  );
}
