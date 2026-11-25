import { Droplets } from 'lucide-react';
import { cx } from '../lib/utils';
import { useI18n } from '../i18n';

const BAND_STYLE = {
  good: 'bg-emerald-500/15 text-emerald-300',
  borderline: 'bg-amber-500/15 text-amber-300',
  low: 'bg-red-500/15 text-red-300',
};

/** The donor's haemoglobin readings (recorded by hospital staff), newest first. Private to the donor. */
export default function HaemoglobinCard({ readings }) {
  const { t, date } = useI18n();
  if (!readings) return null;
  return (
    <div className="card p-6">
      <h2 className="flex items-center gap-2 text-lg font-bold">
        <Droplets className="h-5 w-5 text-brand-600" aria-hidden /> {t('hb.title')}
      </h2>
      <p className="mt-1 text-xs text-slate-400">{t('hb.intro')}</p>
      {readings.length === 0 ? (
        <p className="mt-4 text-sm text-slate-400">{t('hb.empty')}</p>
      ) : (
        <ul className="mt-4 divide-y divide-slate-800">
          {readings.map((r) => (
            <li key={`${r.at}-${r.hb_g_dl}`} className="flex items-center justify-between gap-3 py-2.5 text-sm">
              <span className="min-w-0">
                <span className="block font-semibold tabular-nums text-slate-100">{r.hb_g_dl} g/dL</span>
                <span className="block truncate text-xs text-slate-500">
                  {date(r.at)} · {r.hospital}
                </span>
              </span>
              <span className={cx('shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold', BAND_STYLE[r.band])}>{t(`hb.${r.band}`)}</span>
            </li>
          ))}
        </ul>
      )}
      <p className="mt-3 text-xs text-slate-500">{t('hb.tip')}</p>
    </div>
  );
}
