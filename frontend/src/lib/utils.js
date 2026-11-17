export const BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];

// Recipient -> donor groups it can receive from (mirrors backend logic.COMPATIBILITY)
export const COMPATIBILITY = {
  'A+': ['A+', 'A-', 'O+', 'O-'],
  'A-': ['A-', 'O-'],
  'B+': ['B+', 'B-', 'O+', 'O-'],
  'B-': ['B-', 'O-'],
  'AB+': BLOOD_GROUPS,
  'AB-': ['AB-', 'A-', 'B-', 'O-'],
  'O+': ['O+', 'O-'],
  'O-': ['O-'],
};

export const canDonate = (donor, recipient) => (COMPATIBILITY[recipient] || []).includes(donor);

export const BADGES = {
  Bronze: { icon: '🥉', title: 'First Responder', text: 'text-amber-500', min: 0 },
  Silver: { icon: '🥈', title: 'Life Saver', text: 'text-slate-300', min: 101 },
  Gold: { icon: '🥇', title: 'Guardian Angel', text: 'text-yellow-400', min: 501 },
  Platinum: { icon: '💎', title: 'Legendary Hero', text: 'text-cyan-300', min: 1000 },
};

export const URGENCY = {
  Critical: { chip: 'bg-red-600 text-white', border: 'border-red-500/60', dot: 'bg-red-500' },
  High: { chip: 'bg-orange-500 text-white', border: 'border-orange-500/40', dot: 'bg-orange-400' },
  Normal: { chip: 'bg-amber-400 text-slate-950', border: 'border-amber-400/30', dot: 'bg-amber-300' },
};

export function timeAgo(iso) {
  if (!iso) return '';
  const s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
  if (s < 60) return 'just now';
  if (s < 3600) return `${Math.floor(s / 60)} min ago`;
  if (s < 86400) return `${Math.floor(s / 3600)} h ago`;
  return `${Math.floor(s / 86400)} d ago`;
}

export const cx = (...classes) => classes.filter(Boolean).join(' ');
