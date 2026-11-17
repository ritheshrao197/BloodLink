import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import en from './en';
import kn from './kn';
import hi from './hi';
import ml from './ml';
import ta from './ta';
import te from './te';
import bn from './bn';
import as from './as';
import kok from './kok';
import tcy from './tcy';

export const LANGUAGES = [
  { code: 'en', label: 'English', short: 'EN', locale: 'en-IN' },
  { code: 'kn', label: 'ಕನ್ನಡ', short: 'ಕ', locale: 'kn-IN' },
  { code: 'hi', label: 'हिन्दी', short: 'हि', locale: 'hi-IN' },
  { code: 'ml', label: 'മലയാളം', short: 'മ', locale: 'ml-IN' },
  { code: 'ta', label: 'தமிழ்', short: 'த', locale: 'ta-IN' },
  { code: 'te', label: 'తెలుగు', short: 'తె', locale: 'te-IN' },
  { code: 'bn', label: 'বাংলা', short: 'বা', locale: 'bn-IN' },
  { code: 'as', label: 'অসমীয়া', short: 'অ', locale: 'as-IN' },
  { code: 'kok', label: 'कोंकणी', short: 'को', locale: 'kok-IN' },
  { code: 'tcy', label: 'ತುಳು', short: 'ತು', locale: 'kn-IN' }, // Tulu is written in Kannada script
];
const DICTS = { en, kn, hi, ml, ta, te, bn, as, kok, tcy };
const KEY = 'bloodlink-lang';

function lookup(dict, key) {
  return key.split('.').reduce((node, part) => (node == null ? undefined : node[part]), dict);
}

function interpolate(str, vars) {
  return vars ? str.replace(/\{(\w+)\}/g, (m, k) => (vars[k] ?? m)) : str;
}

function initialLang() {
  try {
    const saved = localStorage.getItem(KEY);
    if (saved && DICTS[saved]) return saved;
  } catch {
    /* storage blocked */
  }
  const nav = (navigator.language || 'en').toLowerCase().split('-')[0];
  return DICTS[nav] ? nav : 'en';
}

const I18nContext = createContext(null);

export function I18nProvider({ children }) {
  const [lang, setLangState] = useState(initialLang);
  const [explicit, setExplicit] = useState(() => {
    try {
      return !!localStorage.getItem(KEY);
    } catch {
      return false;
    }
  });

  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  const setLang = useCallback((code, { remember = true } = {}) => {
    if (!DICTS[code]) return;
    setLangState(code);
    if (remember) {
      setExplicit(true);
      try {
        localStorage.setItem(KEY, code);
      } catch {
        /* storage blocked: applies for this visit */
      }
    }
  }, []);

  const value = useMemo(() => {
    const dict = DICTS[lang];
    const locale = LANGUAGES.find((l) => l.code === lang).locale;

    /** t('home.title', {n: 3}). Falls back to English, then to the key itself. */
    const t = (key, vars) => {
      const s = lookup(dict, key) ?? lookup(en, key);
      if (typeof s !== 'string') {
        if (import.meta.env.DEV) console.warn(`[i18n] missing key ${key}`);
        return key;
      }
      return interpolate(s, vars);
    };
    /** Translated text if this language has it, else `fallback` (e.g. English text from the API). */
    const tOr = (key, fallback, vars) => {
      const s = lookup(dict, key);
      return typeof s === 'string' ? interpolate(s, vars) : fallback;
    };
    const num = (n) => (n == null ? '—' : Number(n).toLocaleString(locale));
    const date = (iso) => (iso ? new Date(iso).toLocaleDateString(locale, { day: 'numeric', month: 'short', year: 'numeric' }) : '');
    const ago = (iso) => {
      if (!iso) return '';
      const s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
      if (s < 60) return t('time.now');
      if (s < 3600) return t('time.min', { n: Math.floor(s / 60) });
      if (s < 86400) return t('time.hour', { n: Math.floor(s / 3600) });
      return t('time.day', { n: Math.floor(s / 86400) });
    };
    /** Point-ledger reasons are stored in English by the API; translate the known shapes. */
    const reason = (text) => {
      if (lang === 'en' || !text) return text;
      const rules = [
        [/^Registration bonus$/, () => t('reason.register')],
        [/^Welcome bonus \(invited by (.+)\)$/, (m) => t('reason.welcome', { name: m[1] })],
        [/^Referral: (.+) registered$/, (m) => t('reason.refJoined', { name: m[1] })],
        [/^Referral: (.+) donated$/, (m) => t('reason.refDonated', { name: m[1] })],
        [/^Successful donation — request #(\d+)$/, (m) => t('reason.donation', { id: m[1] })],
        [/^Quick response \(< 5 min\) — request #(\d+)$/, (m) => t('reason.quick', { id: m[1] })],
        [/^Streak bonus \(3-month return\) — request #(\d+)$/, (m) => t('reason.streak', { id: m[1] })],
        [/^Redeemed (.+)$/, (m) => t('reason.redeemed', { reward: m[1] })],
        [/^Achievement unlocked: (.+)$/, (m) => t('reason.achievement', { name: m[1] })],
        [/^Seeded demo balance$/, () => t('reason.seed')],
      ];
      for (const [re, fn] of rules) {
        const m = text.match(re);
        if (m) return fn(m);
      }
      return text;
    };
    return { lang, setLang, explicit, t, tOr, num, date, ago, reason, locale };
  }, [lang, setLang, explicit]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export const useI18n = () => useContext(I18nContext);
