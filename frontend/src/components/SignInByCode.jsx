import { useState } from 'react';
import { LogIn } from 'lucide-react';
import { api } from '../lib/api';
import { useSession } from '../lib/session';
import { ErrorBox, Spinner } from './ui';

/** Hackathon "login": look yourself up by your referral code (no passwords, per the blueprint). */
export default function SignInByCode({ onSignedIn }) {
  const { signIn } = useSession();
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
        <input className="input font-mono uppercase" placeholder="USER_12345" value={code} onChange={(e) => setCode(e.target.value)} required />
        <button className="btn-ghost shrink-0" disabled={busy}>
          {busy ? <Spinner className="h-4 w-4" /> : <LogIn className="h-4 w-4" />} Sign in
        </button>
      </div>
      <ErrorBox error={error} />
    </form>
  );
}
