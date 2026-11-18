import { useEffect, useState } from 'react';
import { PartyPopper, Share2, XCircle } from 'lucide-react';
import { api } from '../lib/api';
import { Link } from '../lib/router';
import { useSession } from '../lib/session';
import { canDonate } from '../lib/utils';
import { useI18n } from '../i18n';
import { BloodTag, CopyField, ErrorBox, Modal, Spinner } from './ui';
import SignInByCode from './SignInByCode';
import { RarityTag, achText } from './Achievements';
import { EligibilityForm, ReasonList } from './Eligibility';
import ShareCardModal from './ShareCard';

export default function DonateModal({ request, onClose, onDone }) {
  const { user, setUser } = useSession();
  const i18n = useI18n();
  const { t } = i18n;
  const [confirmed, setConfirmed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [screening, setScreening] = useState(null); // set once the health check passes
  const [sharing, setSharing] = useState(false);

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
            <p className="mt-2 text-2xl font-extrabold text-emerald-300">+{result.points_awarded} BLP</p>
            <ul className="mt-2 space-y-0.5 text-sm text-slate-300">
              {result.breakdown.map((b) => (
                <li key={b.reason}>
                  +{b.points} · {t(`donate.breakdown.${b.code}`)}
                </li>
              ))}
            </ul>
          </div>
          {result.achievements?.length > 0 && (
            <div className="rounded-xl border border-amber-400/40 bg-amber-950/20 p-4">
              <p className="text-xs font-bold uppercase tracking-wider text-amber-300">{t('donate.unlocked')}</p>
              <ul className="mt-2 space-y-2">
                {result.achievements.map((a) => (
                  <li key={a.key} className="flex items-center gap-3">
                    <span className="text-3xl">{a.icon}</span>
                    <span className="min-w-0 flex-1">
                      <span className="block font-bold">
                        {a.name}
                        {a.tier && ` (${t(`achievements.tier.${a.tier}`)})`}
                      </span>
                      <RarityTag rarity={a.rarity} />
                      <span className="block text-xs text-slate-400">{achText(i18n, a).description}</span>
                    </span>
                    <span className="text-sm font-bold text-emerald-400">+{a.points}</span>
                  </li>
                ))}
              </ul>
              <Link to="/achievements" onClick={onClose} className="mt-3 block text-center text-xs text-amber-300 hover:underline">
                {t('donate.viewCollection')}
              </Link>
            </div>
          )}
          <p className="text-sm text-slate-300">
            {t('donate.headTo', { place: `${request.hospital}, ${request.city}` })}
            {request.contact_phone && <> {t('donate.contact', { phone: request.contact_phone })}</>}
          </p>
          {request.contact_phone && (
            <div className="grid grid-cols-2 gap-2">
              <a href={`tel:${request.contact_phone.replace(/[^\d+]/g, '')}`} className="btn-ghost">
                📞 {request.contact_phone}
              </a>
              <a href={`https://wa.me/${request.contact_phone.replace(/\D/g, '')}`} target="_blank" rel="noreferrer" className="btn-ghost text-emerald-500">
                💬 WhatsApp
              </a>
            </div>
          )}
          <button onClick={() => setSharing(true)} className="btn-primary w-full from-amber-500 to-amber-700 shadow-amber-900/30">
            <Share2 className="h-4 w-4" /> {t('card.cta')}
          </button>
          <CopyField label={t('donate.invite')} value={result.donor.web_referral_link} />
          <button onClick={onClose} className="btn-ghost w-full">
            {t('common.done')}
          </button>
          <ShareCardModal
            open={sharing}
            onClose={() => setSharing(false)}
            kind="donation"
            user={result.donor}
            donation={{ hospital: request.hospital, city: request.city, created_at: new Date().toISOString() }}
          />
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
                <input type="checkbox" className="mt-0.5 h-4 w-4 shrink-0 accent-red-600" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} />
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
