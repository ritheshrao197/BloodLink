import { useEffect, useState } from 'react';
import { LocateFixed, Package } from 'lucide-react';
import { api } from '../lib/api';
import { useSession } from '../lib/session';
import { BLOOD_GROUPS, cx } from '../lib/utils';
import { useI18n } from '../i18n';
import { Empty, ErrorBox, Loading, PageHeader, Spinner } from '../components/ui';
import LocationPicker from '../components/LocationPicker';
import StockList from '../components/StockList';
import { currentPosition } from '../components/Nearby';

/** Public: which blood banks nearby hold the group a patient needs (or one they can receive). */
export default function Stock() {
  const { user } = useSession();
  const { t } = useI18n();
  const [group, setGroup] = useState(() => new URLSearchParams(window.location.search).get('group') || user?.blood_group || 'O+');
  const [place, setPlace] = useState({ state: user?.state || '', city: user?.city || '' });
  const [point, setPoint] = useState(null);
  const [locating, setLocating] = useState(false);
  const [rows, setRows] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!point && !place.city) return undefined;
    let alive = true;
    setRows(null);
    setError(null);
    const where = point ? { lat: point.lat, lng: point.lng } : { district: place.city, state: place.state };
    api.stock
      .search({ blood_group: group, ...where })
      .then((r) => alive && setRows(r))
      .catch((e) => alive && setError(e));
    return () => {
      alive = false;
    };
  }, [group, place.city, place.state, point]);

  const nearMe = async () => {
    setLocating(true);
    setError(null);
    try {
      setPoint(await currentPosition());
    } catch (e) {
      setError(new Error(t(e.message === 'denied' ? 'stock.locDenied' : 'stock.locFailed')));
    } finally {
      setLocating(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl">
      <PageHeader icon={Package} title={t('stock.title')} subtitle={t('stock.subtitle')} />
      <div className="card space-y-4 p-5">
        <div>
          <div className="mb-2 text-sm font-semibold">{t('stock.group')}</div>
          <div className="grid grid-cols-4 gap-2 sm:grid-cols-8">
            {BLOOD_GROUPS.map((g) => (
              <button
                key={g}
                type="button"
                aria-pressed={group === g}
                onClick={() => setGroup(g)}
                className={cx(
                  'rounded-xl border px-2 py-2 font-bold transition',
                  group === g ? 'border-red-500 bg-red-600/15 text-red-500' : 'border-slate-700 hover:border-slate-500',
                )}
              >
                {g}
              </button>
            ))}
          </div>
        </div>
        <LocationPicker
          idPrefix="stock"
          value={place}
          onChange={(v) => {
            setPoint(null);
            setPlace({ state: v.state, city: v.city });
          }}
        />
        <button type="button" onClick={nearMe} className={cx('btn-secondary', point && 'border-emerald-500 text-emerald-500')} disabled={locating}>
          {locating ? <Spinner className="h-4 w-4" /> : <LocateFixed className="h-4 w-4" />} {t('stock.nearMe')}
        </button>
      </div>

      <div className="mt-6 space-y-3">
        <ErrorBox error={error} />
        {!point && !place.city ? (
          <Empty icon={Package} title={t('stock.pickPlace')} />
        ) : !rows && !error ? (
          <Loading rows={3} />
        ) : rows?.length ? (
          <div className="card px-5 py-2">
            <StockList rows={rows} group={group} />
          </div>
        ) : rows ? (
          <Empty icon={Package} title={t('stock.empty', { group })}>
            {t('stock.emptyHint')}
          </Empty>
        ) : null}
      </div>
      <p className="mt-4 text-xs text-slate-500">{t('stock.disclaimer')}</p>
    </div>
  );
}
