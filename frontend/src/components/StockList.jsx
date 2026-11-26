import { Building2, Phone } from 'lucide-react';
import { useI18n } from '../i18n';
import { BloodTag } from './ui';

/** Blood banks with stock a patient of `group` can receive (rows from /api/stock or an SOS response). */
export default function StockList({ rows, group }) {
  const { t, ago } = useI18n();
  return (
    <ul className="divide-y divide-slate-800">
      {rows.map((s) => (
        <li key={s.bank.id} className="flex flex-wrap items-center gap-3 py-3 text-left">
          <Building2 className="h-5 w-5 shrink-0 text-slate-400" />
          <div className="min-w-0 flex-1">
            <p className="font-semibold">{s.bank.name}</p>
            <p className="text-xs text-slate-500">
              {s.distance_km != null ? t('geo.away', { km: s.distance_km }) : s.bank.city} · {t('stock.updated', { ago: ago(s.updated_at) })}
            </p>
            <div className="mt-1.5 flex flex-wrap items-center gap-2 text-sm">
              {s.units > 0 && (
                <span className="flex items-center gap-1.5 font-bold">
                  <BloodTag group={group} size="sm" /> × {s.units}
                </span>
              )}
              {Object.keys(s.compatible).length > 0 && (
                <span className="text-xs text-slate-400">
                  {t(s.units > 0 ? 'stock.alsoSuitable' : 'stock.suitable')}{' '}
                  {Object.entries(s.compatible)
                    .map(([g, n]) => `${g} × ${n}`)
                    .join(', ')}
                </span>
              )}
            </div>
          </div>
          {s.bank.phone && (
            <a href={`tel:${s.bank.phone.replace(/[^\d+]/g, '')}`} className="btn-secondary px-3 py-2 text-sm">
              <Phone className="h-4 w-4" /> {t('stock.call')}
            </a>
          )}
        </li>
      ))}
    </ul>
  );
}
