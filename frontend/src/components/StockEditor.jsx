import { useEffect, useState } from 'react';
import { Package, Save } from 'lucide-react';
import { api } from '../lib/api';
import { BLOOD_GROUPS } from '../lib/utils';
import { useI18n } from '../i18n';
import { useToast } from './Toast';
import { BloodTag, ErrorBox, Spinner } from './ui';

/** A blood bank's own sheet: units held per group. Families see it until it is `fresh_hours` old. */
export default function StockEditor() {
  const { t, ago } = useI18n();
  const toast = useToast();
  const [sheet, setSheet] = useState(null);
  const [units, setUnits] = useState({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const load = (s) => {
    setSheet(s);
    setUnits(Object.fromEntries(BLOOD_GROUPS.map((g) => [g, String(s.units[g] ?? 0)])));
  };
  useEffect(() => {
    api.stock.mine().then(load).catch(setError);
  }, []);

  const save = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      load(await api.stock.save(Object.fromEntries(BLOOD_GROUPS.map((g) => [g, Number(units[g]) || 0]))));
      toast(t('stock.saved'));
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  };

  const hours = sheet?.fresh_hours ?? 48;
  const stale = sheet?.updated_at && Date.now() - new Date(sheet.updated_at).getTime() > hours * 3600 * 1000;
  const status = !sheet
    ? null
    : !sheet.updated_at
      ? t('stock.mineNever')
      : stale
        ? t('stock.mineStale', { hours })
        : t('stock.mineUpdated', { ago: ago(sheet.updated_at) });
  return (
    <form onSubmit={save} className="card mb-6 space-y-4 p-5">
      <div>
        <h2 className="flex items-center gap-2 text-lg font-bold">
          <Package className="h-5 w-5 text-brand-400" /> {t('stock.mineTitle')}
        </h2>
        <p className="mt-1 text-sm text-slate-400">{t('stock.mineHint', { hours })}</p>
      </div>
      {!sheet && !error ? (
        <Spinner className="h-5 w-5" />
      ) : (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {BLOOD_GROUPS.map((g) => (
            <label key={g} className="flex items-center gap-2 rounded-xl bg-slate-800/50 p-2">
              <BloodTag group={g} size="sm" />
              <input
                type="number"
                inputMode="numeric"
                min="0"
                max="9999"
                aria-label={t('stock.unitsOf', { group: g })}
                value={units[g] ?? ''}
                onChange={(e) => setUnits({ ...units, [g]: e.target.value })}
                className="input w-full min-w-0"
              />
            </label>
          ))}
        </div>
      )}
      <div className="flex flex-wrap items-center gap-3">
        <button type="submit" className="btn-primary" disabled={busy || !sheet}>
          {busy ? <Spinner className="h-4 w-4" /> : <Save className="h-4 w-4" />} {t('stock.save')}
        </button>
        {status && <p className={stale || !sheet.updated_at ? 'text-sm text-amber-500' : 'text-sm text-slate-400'}>{status}</p>}
      </div>
      <ErrorBox error={error} />
    </form>
  );
}
