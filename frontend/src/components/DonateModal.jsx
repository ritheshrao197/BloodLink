import { useEffect, useState } from 'react';
import { PartyPopper, XCircle } from 'lucide-react';
import { api } from '../lib/api';
import { Link } from '../lib/router';
import { useSession } from '../lib/session';
import { canDonate } from '../lib/utils';
import { useI18n } from '../i18n';
import { BloodTag, CopyField, ErrorBox, Modal, Spinner } from './ui';
import SignInByCode from './SignInByCode';
import { EligibilityForm, ReasonList } from './Eligibility';
import GettingThere from './Travel';

export default function DonateModal({ request, onClose, onDone }) {
  const { user, setUser } = useSession();
  const { t } = useI18n();
  const [confirmed, setConfirmed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [screening, setScreening] = useState(null); // set once the health check passes

  useEffect(() => {
    setScreening(null);
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
      const res = await api.donate(request.id, user.id, screening);
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
    <Modal open onClose={onClose} title={result ? t('donate.thanks') : t('donate.title')}>
      {result ? (
        <div className="space-y-4">
          <div className="flex flex-col items-center rounded-xl bg-emerald-950/40 p-5 text-center ring-1 ring-emerald-500/30">
            <PartyPopper className="h-10 w-10 text-emerald-400" />
            <p className="mt-2 text-lg font-extrabold text-emerald-300">{t('donate.pledgedTitle')}</p>
            <p className="mt-1 text-sm text-slate-300">{t('donate.pledgedBody', { points: result.expected_points })}</p>
            <ul className="mt-2 space-y-0.5 text-sm text-slate-400">
              {result.breakdown.map((b) => (
                <li key={b.code}>
                  +{b.points} · {t(`donate.breakdown.${b.code}`)}
                </li>
              ))}
            </ul>
            <p className="mt-2 text-xs text-slate-500">{t('donate.expires', { hours: result.pledge_hours })}</p>
          </div>
          <GettingThere request={result.request || request} donationId={result.donation_id} />
          <CopyField label={t('donate.invite')} value={result.donor.web_referral_link} />
          <button onClick={onClose} className="btn-ghost w-full">
            {t('common.done')}
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center gap-3 rounded-xl bg-slate-800/60 p-4">
            <BloodTag group={request.blood_group} size="lg" />
            <div>
              <p className="font-bold">{request.hospital}</p>
              <p className="text-sm text-slate-400">
                {t('donate.stillNeeded', { city: request.city, n: request.units_needed - request.units_fulfilled })}
              </p>
            </div>
          </div>

          {!user ? (
            <div className="space-y-3">
              <p className="text-sm text-slate-300">{t('donate.signInPrompt')}</p>
              <SignInByCode />
              <Link to="/register" onClick={onClose} className="btn-ghost w-full">
                {t('donate.registerCta')}
              </Link>
            </div>
          ) : !compatible ? (
            <div className="flex gap-2 rounded-lg border border-amber-500/40 bg-amber-950/30 p-3 text-sm text-amber-200">
              <XCircle className="h-5 w-5 shrink-0" />
              <span>
                {t('donate.incompatible', {
                  mine: user.blood_group,
                  theirs: request.blood_group,
                  groups: request.compatible_donor_groups.join(', '),
                })}
              </span>
            </div>
          ) : !screening ? (
            <EligibilityForm user={user} onEligible={setScreening} />
          ) : (
            <>
              <p className="flex items-center gap-2 rounded-lg bg-emerald-950/40 px-3 py-2 text-sm font-semibold text-emerald-300">{t('elig.ok')}</p>
              <p className="text-sm text-slate-300">{t('donate.donatingAs', { name: user.name, group: user.blood_group })}</p>
              <label className="flex cursor-pointer items-start gap-2 text-sm text-slate-300">
                <input type="checkbox" className="mt-0.5 h-4 w-4 shrink-0 accent-brand-600" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} />
                {t('donate.confirm')}
              </label>
              {error?.data?.eligibility ? (
                <div className="rounded-lg border border-amber-500/40 bg-amber-950/30 p-3 text-amber-200">
                  <ReasonList reasons={error.data.eligibility.reasons} />
                </div>
              ) : (
                <ErrorBox error={error} />
              )}
              <button className="btn-primary w-full" disabled={!confirmed || busy} onClick={submit}>
                {busy ? <Spinner /> : '🩸'} {t('donate.confirmBtn')}
              </button>
            </>
          )}
        </div>
      )}
    </Modal>
  );
}
