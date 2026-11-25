import { useState } from 'react';
import { LocateFixed, MapPin } from 'lucide-react';
import { cx } from '../lib/utils';
import { useI18n } from '../i18n';
import { useToast } from './Toast';
import { currentPosition } from './Nearby';
import LocationPicker from './LocationPicker';
import { Spinner } from './ui';

export const SCOPES = ['25', '50', 'state', 'all'];

/** "Near Mysuru · change · use my current position", plus the district picker for visitors. */
export function AreaBar({ area, choose, setHere, signedIn }) {
  const { t } = useI18n();
  const toast = useToast();
  const [picking, setPicking] = useState(!area);
  const [where, setWhere] = useState({ state: area?.state || null, city: area?.district || '' });
  const [busy, setBusy] = useState(false);

  const locate = async () => {
    setBusy(true);
    try {
      setHere(await currentPosition());
      setPicking(false);
    } catch (e) {
      toast(t(e.message === 'denied' ? 'geo.denied' : 'geo.unsupported'), 'error');
    } finally {
      setBusy(false);
    }
  };
  const pick = async (v) => {
    setWhere(v);
    if (!v.city) return;
    try {
      await choose(v);
      setPicking(false);
    } catch {
      /* a district we can't place (e.g. still typing an "Other" name): keep the picker open */
    }
  };

  return (
    <div className="mb-4 space-y-3">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm">
        <span className="flex items-center gap-1.5 font-semibold text-slate-200">
          <MapPin className="h-4 w-4 text-brand-600" aria-hidden />
          {area ? (area.source === 'here' ? t('area.here') : t('area.near', { place: area.label })) : t('area.pickTitle')}
        </span>
        {!signedIn && area && (
          <button onClick={() => setPicking(!picking)} className="text-xs font-semibold text-brand-600 hover:underline">
            {t('area.change')}
          </button>
        )}
        <button onClick={locate} disabled={busy} className="flex items-center gap-1 text-xs font-semibold text-brand-600 hover:underline">
          {busy ? <Spinner className="h-3.5 w-3.5" /> : <LocateFixed className="h-3.5 w-3.5" />} {t('area.useHere')}
        </button>
      </div>
      {!signedIn && picking && (
        <div className="card p-4">
          {!area && <p className="mb-3 text-sm text-slate-400">{t('area.pickBody')}</p>}
          <LocationPicker idPrefix="area" value={where} onChange={pick} />
        </div>
      )}
    </div>
  );
}

/** 25 km · 50 km · My state · All */
export function ScopeChips({ scope, onChange }) {
  const { t } = useI18n();
  return (
    <div className="flex gap-1 rounded-lg bg-slate-800 p-1 text-xs font-semibold" role="group" aria-label={t('area.scopeLabel')}>
      {SCOPES.map((s) => (
        <button
          key={s}
          onClick={() => onChange(s)}
          aria-pressed={scope === s}
          className={cx('min-h-8 rounded-md px-2.5', scope === s ? 'bg-brand-700 text-white' : 'text-slate-300 hover:text-slate-50')}
        >
          {t(`area.scope.s${s}`)}
        </button>
      ))}
    </div>
  );
}
