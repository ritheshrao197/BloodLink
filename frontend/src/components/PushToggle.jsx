import { useEffect, useState } from 'react';
import { Bell, BellOff, CheckCircle2 } from 'lucide-react';
import { useI18n } from '../i18n';
import { currentSubscription, disablePush, enablePush, permission, pushConfig, pushSupported } from '../lib/push';
import { ErrorBox, Spinner } from './ui';

const isIOS = () => /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);

/**
 * Turn browser notifications on or off. Without props: alerts for the signed-in account.
 * With { requestId, requestToken }: updates for that SOS only (requester without an account).
 * Renders nothing when the server has push switched off.
 */
export default function PushToggle({ requestId, requestToken, compact = false }) {
  const { t } = useI18n();
  const forRequest = requestId != null;
  const [state, setState] = useState('loading'); // loading | hidden | ios | off | on | denied | busy
  const [error, setError] = useState(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      const cfg = await pushConfig();
      if (!cfg.enabled) return 'hidden';
      if (!pushSupported()) return isIOS() ? 'ios' : 'hidden';
      if (permission() === 'denied') return 'denied';
      // a request follow is always a fresh choice; account alerts are on if this browser already subscribed
      return !forRequest && permission() === 'granted' && (await currentSubscription()) ? 'on' : 'off';
    })().then((s) => alive && setState(s));
    return () => {
      alive = false;
    };
  }, [forRequest]);

  const turnOn = async () => {
    setError(null);
    setState('busy');
    try {
      const res = await enablePush(forRequest ? { requestId, requestToken } : {});
      setState(res === 'on' ? 'on' : res === 'denied' ? 'denied' : 'hidden');
    } catch (e) {
      setError(e);
      setState('off');
    }
  };
  const turnOff = async () => {
    setState('busy');
    await disablePush();
    setState('off');
  };

  if (state === 'loading' || state === 'hidden') return null;
  return (
    <div className={compact ? 'space-y-2' : 'mt-8 space-y-2'}>
      {!compact && <h2 className="text-lg font-bold">{t('push.title')}</h2>}
      {state === 'ios' && <p className="text-sm text-slate-400">{t('push.ios')}</p>}
      {state === 'denied' && <p className="text-sm text-amber-500">{t('push.denied')}</p>}
      {state === 'on' && (
        <div className={`flex flex-wrap items-center gap-3 ${compact ? 'justify-center' : ''}`}>
          <p className="flex items-center gap-2 text-sm text-emerald-400">
            <CheckCircle2 className="h-4 w-4 shrink-0" /> {t(forRequest ? 'push.sosOn' : 'push.on')}
          </p>
          {!forRequest && (
            <button onClick={turnOff} className="btn-ghost text-sm">
              <BellOff className="h-4 w-4" /> {t('push.turnOff')}
            </button>
          )}
        </div>
      )}
      {(state === 'off' || state === 'busy') && (
        <>
          <p className="text-sm text-slate-400">{t(forRequest ? 'push.sosPrompt' : 'push.prompt')}</p>
          <button onClick={turnOn} className="btn-primary" disabled={state === 'busy'}>
            {state === 'busy' ? <Spinner className="h-4 w-4" /> : <Bell className="h-4 w-4" />} {t('push.turnOn')}
          </button>
        </>
      )}
      {error && <ErrorBox error={error} />}
    </div>
  );
}
