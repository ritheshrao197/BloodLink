import { useState } from 'react';
import { LogIn } from 'lucide-react';
import { api } from '../lib/api';
import { useSession } from '../lib/session';
import { useI18n } from '../i18n';
import { ErrorBox, Spinner } from './ui';

/** Hackathon "login": look yourself up by your referral code (no passwords, per the blueprint). */
export default function SignInByCode({ onSignedIn }) {
  const { signIn } = useSession();
  const { t } = useI18n();
  const [code, setCode] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const u = await api.userByCode(code.trim());
      signIn(u);
      onSignedIn?.(u);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  };

  return (
    <form onSubmit={submit} className="space-y-2">
      <div className="flex gap-2">
        <input
          className="input font-mono uppercase"
          placeholder={t('signin.placeholder')}
          aria-label={t('register.yourCode')}
          value={code}
          onChange={(e) => setCode(e.target.value)}
          required
        />
        <button className="btn-ghost shrink-0" disabled={busy}>
          {busy ? <Spinner className="h-4 w-4" /> : <LogIn className="h-4 w-4" />} {t('common.signIn')}
        </button>
      </div>
      <ErrorBox error={error} />
    </form>
  );
}
