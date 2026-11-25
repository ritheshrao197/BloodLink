import { useState } from 'react';
import { CheckCircle2, ClipboardCheck, Hospital, Phone, XCircle } from 'lucide-react';
import { api } from '../lib/api';
import { useSession } from '../lib/session';
import { usePoll } from '../lib/usePoll';
import { useI18n } from '../i18n';
import { useToast } from '../components/Toast';
import { BloodTag, Empty, ErrorBox, Loading, PageHeader, Spinner } from '../components/ui';
import SignInByCode from '../components/SignInByCode';

const STAFF_ROLES = ['hospital', 'blood_bank'];

/** One donor who pledged: staff confirm after the donation, or mark that they never came. */
function PledgeRow({ p, onDone }) {
  const { t, ago, date } = useI18n();
  const toast = useToast();
  const [hb, setHb] = useState('');
  const [busy, setBusy] = useState(null);
  const [error, setError] = useState(null);

  const act = async (kind) => {
    setBusy(kind);
    setError(null);
    try {
      if (kind === 'confirm') {
        const res = await api.staff.confirm(p.donation_id, hb === '' ? null : Number(hb));
        toast(t('staff.confirmed', { name: res.donor_name, points: res.points_awarded }));
      } else {
        await api.staff.noShow(p.donation_id);
        toast(t('staff.missed'));
      }
      onDone();
    } catch (e) {
      setError(e);
    } finally {
      setBusy(null);
    }
  };

  return (
    <li className="card space-y-3 p-4">
      <div className="flex flex-wrap items-center gap-3">
        <BloodTag group={p.donor.blood_group} />
        <div className="min-w-0 flex-1">
          <p className="font-bold">{p.donor.name}</p>
          <p className="flex items-center gap-1 text-sm text-slate-400">
            <Hospital className="h-4 w-4 shrink-0" />
            <span className="min-w-0">
              {p.request.hospital}, {p.request.city} · #{p.request.id} ({p.request.blood_group})
            </span>
          </p>
        </div>
        {p.donor.phone && (
          <a href={`tel:${p.donor.phone.replace(/[^\d+]/g, '')}`} className="flex items-center gap-1 text-sm text-slate-300">
            <Phone className="h-4 w-4" /> {p.donor.phone}
          </a>
        )}
      </div>
      <p className="text-xs text-slate-500">
        {t('staff.pledged', { ago: ago(p.pledged_at) })} · {t('staff.expires', { date: date(p.expires_at) })}
      </p>
      <div className="flex flex-wrap items-end gap-2">
        <label className="text-xs text-slate-400">
          {t('staff.hb')}
          <input
            type="number"
            inputMode="decimal"
            step="0.1"
            min="4"
            max="25"
            value={hb}
            onChange={(e) => setHb(e.target.value)}
            className="input mt-1 block w-32"
          />
        </label>
        <button className="btn-primary" disabled={!!busy} onClick={() => act('confirm')}>
          {busy === 'confirm' ? <Spinner /> : <CheckCircle2 className="h-4 w-4" />} {t('staff.donated')}
        </button>
        <button className="btn-ghost" disabled={!!busy} onClick={() => act('noShow')}>
          {busy === 'noShow' ? <Spinner /> : <XCircle className="h-4 w-4" />} {t('staff.noShow')}
        </button>
      </div>
      <ErrorBox error={error} />
    </li>
  );
}

export default function Staff() {
  const { user } = useSession();
  const { t } = useI18n();
  const allowed = !!user && (user.is_admin || STAFF_ROLES.includes(user.role));
  const { data, error, loading, reload } = usePoll(() => (allowed ? api.staff.pledges() : Promise.resolve([])), 10000, `${user?.id}`);

  return (
    <div className="mx-auto max-w-3xl">
      <PageHeader icon={ClipboardCheck} title={t('staff.title')} subtitle={t('staff.subtitle')} />
      {!user ? (
        <div className="card space-y-3 p-5">
          <p className="text-sm text-slate-300">{t('staff.signIn')}</p>
          <SignInByCode />
        </div>
      ) : !allowed ? (
        <Empty icon={ClipboardCheck} title={t('staff.notStaff')} />
      ) : loading && !data ? (
        <Loading rows={3} />
      ) : (
        <div className="space-y-3">
          <ErrorBox error={error} />
          {data?.length ? (
            <ul className="space-y-3">
              {data.map((p) => (
                <PledgeRow key={p.donation_id} p={p} onDone={reload} />
              ))}
            </ul>
          ) : (
            <Empty icon={ClipboardCheck} title={t('staff.empty')} />
          )}
        </div>
      )}
    </div>
  );
}
