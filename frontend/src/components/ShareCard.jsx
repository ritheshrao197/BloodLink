import { useEffect, useRef, useState } from 'react';
import { Download, Share2 } from 'lucide-react';
import { CARD_VARIANTS, VARIANTS_FOR, drawCard, toBlob } from '../lib/cards';
import { cx } from '../lib/utils';
import { useI18n } from '../i18n';
import { achText } from './Achievements';
import { useToast } from './Toast';
import { Modal, Spinner } from './ui';

const PLATFORMS = [
  { name: 'WhatsApp', color: '#25D366', glyph: 'W', url: (text, link) => `https://wa.me/?text=${encodeURIComponent(`${text}\n${link}`)}` },
  { name: 'Telegram', color: '#229ED9', glyph: 'T', url: (text, link) => `https://t.me/share/url?url=${encodeURIComponent(link)}&text=${encodeURIComponent(text)}` },
  { name: 'X', color: '#000000', glyph: '𝕏', url: (text, link) => `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(link)}` },
  { name: 'LinkedIn', color: '#0A66C2', glyph: 'in', url: (text, link) => `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(link)}` },
  { name: 'Facebook', color: '#1877F2', glyph: 'f', url: (text, link) => `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(link)}` },
];

/** Builds the text content of a card in the current language. kind: donation | achievement | referral */
function buildCard(i18n, { kind, variant, user, donation, achievement }) {
  const { t, date, lang } = i18n;
  const base = {
    variant,
    lang,
    name: user.name,
    title: t(`card.title.${variant}`),
    serial: `BL-${new Date().getFullYear()}-${String(user.id).padStart(4, '0')}`,
    url: user.web_referral_link,
    brandUrl: window.location.host.toUpperCase(),
    tagline: t('footer.tagline'),
    scan: t('card.scan'),
  };
  if (kind === 'achievement') {
    const { description } = achText(i18n, achievement);
    return {
      ...base,
      crest: achievement.icon,
      crestIsEmoji: true,
      subtitle: `${achievement.name}${achievement.tier ? ` · ${t(`achievements.tier.${achievement.tier}`)}` : ''}`,
      lines: [],
      quote: description,
      meta: `${t(`achievements.rarityName.${achievement.rarity}`)} · ${user.blood_group}`,
    };
  }
  if (kind === 'referral') {
    const n = user.referrals?.total || 0;
    return {
      ...base,
      crest: '🤝',
      crestIsEmoji: true,
      subtitle: t('card.referred', { n }),
      lines: [],
      quote: t('card.referredLine', { n }),
      meta: `${t(`badge.${user.badge}`)} · ${user.blood_group}`,
    };
  }
  return {
    ...base,
    crest: user.blood_group,
    crestIsEmoji: false,
    subtitle: variant === 'midnight_hero' ? t('card.night') : null,
    lines: donation ? [t('card.at', { place: `${donation.hospital}, ${donation.city}` }), t('card.on', { date: date(donation.created_at) })] : [],
    meta: `${t(`badge.${user.badge}`)} · ${t('card.donations', { n: user.total_donations })}`,
  };
}

/** Night donations (midnight to 4 am IST) default to the Midnight Hero design; legendary achievements to Diamond Elite. */
export function defaultVariant({ kind, donation, achievement }) {
  if (kind === 'achievement') return ['Legendary', 'Mythic'].includes(achievement?.rarity) ? 'diamond_elite' : 'achievement_crown';
  if (kind === 'referral') return 'emerald_guardian';
  if (donation?.created_at) {
    const istHour = (new Date(donation.created_at).getUTCHours() + 5.5) % 24;
    if (istHour < 4) return 'midnight_hero';
  }
  return 'blood_royalty';
}

export default function ShareCardModal({ open, onClose, kind = 'donation', user, donation, achievement }) {
  const i18n = useI18n();
  const { t } = i18n;
  const toast = useToast();
  const canvasRef = useRef(null);
  const [variant, setVariant] = useState(() => defaultVariant({ kind, donation, achievement }));
  const [preview, setPreview] = useState(null);
  const [downloaded, setDownloaded] = useState(false);

  useEffect(() => {
    if (open) setVariant(defaultVariant({ kind, donation, achievement }));
  }, [open, kind, donation?.created_at, achievement?.key]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!open || !user) return undefined;
    let cancelled = false;
    setPreview(null);
    const canvas = canvasRef.current || document.createElement('canvas');
    canvasRef.current = canvas;
    drawCard(canvas, buildCard(i18n, { kind, variant, user, donation, achievement })).then((c) => {
      if (!cancelled) setPreview(c.toDataURL('image/png'));
    });
    return () => {
      cancelled = true;
    };
  }, [open, variant, i18n.lang, user?.id, user?.points, kind, donation, achievement]); // eslint-disable-line react-hooks/exhaustive-deps

  if (!open || !user) return null;
  const text = t('card.shareText');
  const link = user.web_referral_link;
  const fileName = `bloodlink-${variant}-${user.referral_code}.png`;

  const download = () => {
    const a = document.createElement('a');
    a.href = preview;
    a.download = fileName;
    a.click();
    setDownloaded(true);
  };

  const shareNative = async () => {
    const blob = await toBlob(canvasRef.current);
    const file = new File([blob], fileName, { type: 'image/png' });
    try {
      if (navigator.canShare?.({ files: [file] })) await navigator.share({ files: [file], text: `${text}\n${link}` });
      else if (navigator.share) await navigator.share({ text, url: link });
      else {
        download();
        toast(t('card.instagram'));
      }
    } catch {
      /* user closed the share sheet */
    }
  };

  const options = VARIANTS_FOR[kind];
  return (
    <Modal open onClose={onClose} title={t('card.shareTitle')}>
      <div className="space-y-4">
        <div className="relative aspect-square overflow-hidden rounded-xl border-2 border-amber-500/30 bg-slate-900">
          {preview ? (
            <img src={preview} alt={t(`card.title.${variant}`)} className="h-full w-full" />
          ) : (
            <div className="flex h-full items-center justify-center text-slate-400">
              <Spinner />
            </div>
          )}
        </div>

        {options.length > 1 && (
          <div className="flex flex-wrap gap-2" role="radiogroup" aria-label={t('card.design')}>
            {options.map((v) => {
              const c = CARD_VARIANTS[v];
              return (
                <button
                  key={v}
                  role="radio"
                  aria-checked={variant === v}
                  onClick={() => setVariant(v)}
                  className={cx('flex min-h-9 items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold', variant === v ? 'border-amber-400 text-amber-300' : 'border-slate-700 text-slate-400')}
                >
                  <span className="h-3 w-3 rounded-full" style={{ background: `linear-gradient(135deg, rgb(${c.bg[0]}), rgb(${c.primary}))` }} />
                  {t(`card.variant.${v}`)}
                </button>
              );
            })}
          </div>
        )}

        <div className="grid grid-cols-2 gap-2">
          <button onClick={shareNative} className="btn-primary" disabled={!preview}>
            <Share2 className="h-4 w-4" /> {t('card.share')}
          </button>
          <button onClick={download} className="btn-ghost" disabled={!preview}>
            <Download className="h-4 w-4" /> {downloaded ? t('card.downloaded') : t('card.download')}
          </button>
        </div>

        <div className="grid grid-cols-5 gap-2">
          {PLATFORMS.map((p) => (
            <a
              key={p.name}
              href={p.url(text, link)}
              target="_blank"
              rel="noreferrer"
              className="flex flex-col items-center gap-1 rounded-lg p-1.5 text-[10px] text-slate-400 hover:bg-slate-800"
              title={p.name}
            >
              <span className="flex h-10 w-10 items-center justify-center rounded-full text-sm font-black text-white" style={{ backgroundColor: p.color }}>
                {p.glyph}
              </span>
              {p.name}
            </a>
          ))}
        </div>
        <p className="text-center text-xs text-slate-500">{t('card.note')}</p>
      </div>
    </Modal>
  );
}
