import { useEffect, useState } from 'react';
import { PartyPopper, XCircle } from 'lucide-react';
import { api } from '../lib/api';
import { Link } from '../lib/router';
import { useSession } from '../lib/session';
import { canDonate } from '../lib/utils';
import { BloodTag, CopyField, ErrorBox, Modal, Spinner } from './ui';
import SignInByCode from './SignInByCode';

export default function DonateModal({ request, onClose, onDone }) {
  const { user, setUser } = useSession();
  const [confirmed, setConfirmed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  useEffect(() => {
    setConfirmed(false);
    setError(null);
    setResult(null);
  }, [request?.id]);

  if (!request) return null;
  const compatible = user && canDonate(user.blood_group, request.blood_group);

  const submit = async () => {
    setBusy(true);
    setError(null);
    try {
      const res = await api.donate(request.id, user.id);
      setResult(res);
      setUser(res.donor);
      onDone?.(res);
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal open onClose={onClose} title={result ? 'Thank you, hero!' : 'Respond to SOS'}>
      {result ? (
        <div className="space-y-4">
          <div className="flex flex-col items-center rounded-xl bg-emerald-950/40 p-5 text-center ring-1 ring-emerald-500/30">
            <PartyPopper className="h-10 w-10 text-emerald-400" />
            <p className="mt-2 text-2xl font-extrabold text-emerald-300">+{result.points_awarded} BLP</p>
            <ul className="mt-2 space-y-0.5 text-sm text-slate-300">
              {result.breakdown.map((b) => (
                <li key={b.reason}>
                  +{b.points} · {b.reason}
                </li>
              ))}
            </ul>
          </div>
          <p className="text-sm text-slate-300">
            Please head to <b>{request.hospital}, {request.city}</b> with a photo ID.
            {request.contact_phone && <> Contact: <b>{request.contact_phone}</b>.</>}
          </p>
          <CopyField label="Invite a friend — earn +200 BLP when they donate" value={result.donor.web_referral_link} />
          <button onClick={onClose} className="btn-primary w-full">
            Done
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center gap-3 rounded-xl bg-slate-800/60 p-4">
            <BloodTag group={request.blood_group} size="lg" />
            <div>
              <p className="font-bold">{request.hospital}</p>
              <p className="text-sm text-slate-400">
                {request.city} · {request.units_needed - request.units_fulfilled} unit(s) still needed
              </p>
            </div>
          </div>

          {!user ? (
            <div className="space-y-3">
              <p className="text-sm text-slate-300">Sign in with your referral code, or register in 20 seconds.</p>
              <SignInByCode />
              <Link to="/register" onClick={onClose} className="btn-ghost w-full">
                Register as a donor (+50 BLP)
              </Link>
            </div>
          ) : !compatible ? (
            <div className="flex gap-2 rounded-lg border border-amber-500/40 bg-amber-950/30 p-3 text-sm text-amber-200">
              <XCircle className="h-5 w-5 shrink-0" />
              <span>
                Your blood group <b>{user.blood_group}</b> isn't compatible with a <b>{request.blood_group}</b> patient. This request
                accepts {request.compatible_donor_groups.join(', ')}. Share it with friends who can help!
              </span>
            </div>
          ) : (
            <>
              <p className="text-sm text-slate-300">
                Donating as <b>{user.name}</b> ({user.blood_group}). You'll earn <b>+100 BLP</b>, plus +20 if you respond within 5
                minutes.
              </p>
              <label className="flex cursor-pointer items-start gap-2 text-sm text-slate-300">
                <input type="checkbox" className="mt-0.5 h-4 w-4 accent-red-600" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} />I
                confirm I'm able to donate and will go to the hospital. (Final eligibility is checked by hospital staff.)
              </label>
              <ErrorBox error={error} />
              <button className="btn-primary w-full" disabled={!confirmed || busy} onClick={submit}>
                {busy ? <Spinner /> : '🩸'} Confirm Donation
              </button>
            </>
          )}
        </div>
      )}
    </Modal>
  );
}
