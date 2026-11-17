import QRCode from 'qrcode';

/** The five royal card designs (BLOODLINK v6 spec §7.1). Colours are [r, g, b]. */
export const CARD_VARIANTS = {
  blood_royalty: { bg: [[127, 29, 29], [69, 10, 10], [0, 0, 0]], primary: [212, 175, 55], light: [244, 228, 188], dark: [184, 134, 11], accent: [220, 38, 38] },
  achievement_crown: { bg: [[76, 29, 149], [46, 16, 101], [0, 0, 0]], primary: [232, 180, 160], light: [245, 213, 200], dark: [184, 134, 122], accent: [139, 92, 246] },
  diamond_elite: { bg: [[12, 74, 110], [8, 47, 73], [0, 0, 0]], primary: [229, 228, 226], light: [245, 245, 245], dark: [168, 168, 168], accent: [34, 211, 238] },
  emerald_guardian: { bg: [[6, 78, 59], [2, 44, 34], [0, 0, 0]], primary: [212, 175, 55], light: [244, 228, 188], dark: [184, 134, 11], accent: [16, 185, 129] },
  midnight_hero: { bg: [[30, 58, 138], [15, 23, 42], [0, 0, 0]], primary: [192, 192, 192], light: [232, 232, 232], dark: [128, 128, 128], accent: [59, 130, 246] },
};

// Which designs fit which story
export const VARIANTS_FOR = {
  donation: ['blood_royalty', 'midnight_hero'],
  achievement: ['achievement_crown', 'diamond_elite'],
  referral: ['emerald_guardian'],
};

const rgb = (c, a = 1) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;
const INDIC = '"Noto Sans Kannada", "Noto Sans Devanagari", "Noto Sans Malayalam", "Noto Sans Tamil", "Noto Sans Telugu", "Noto Sans Bengali"';
const SERIF = `"Playfair Display", ${INDIC}, Georgia, "Times New Roman", serif`;
const SANS = `Inter, ${INDIC}, system-ui, sans-serif`;

/** Largest font size (<= size) at which text fits maxWidth. */
function fit(ctx, text, weight, size, family, maxWidth) {
  let s = size;
  do {
    ctx.font = `${weight} ${s}px ${family}`;
    if (ctx.measureText(text).width <= maxWidth) break;
    s -= 2;
  } while (s > 14);
  return s;
}

function text(ctx, str, x, y, { weight = 600, size = 32, family = SANS, color, maxWidth = 900, letterSpacing = 0 }) {
  if (!str) return;
  fit(ctx, str, weight, size, family, maxWidth);
  ctx.fillStyle = color;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  if ('letterSpacing' in ctx) ctx.letterSpacing = `${letterSpacing}px`;
  ctx.fillText(str, x, y);
  if ('letterSpacing' in ctx) ctx.letterSpacing = '0px';
}

async function fontsReady(lang) {
  if (!document.fonts?.load) return;
  const loads = ['900 96px "Playfair Display"', '700 40px "Playfair Display"', '700 32px Inter', '500 24px Inter'];
  const indic = { kn: 'Kannada', tcy: 'Kannada', hi: 'Devanagari', kok: 'Devanagari', ml: 'Malayalam', ta: 'Tamil', te: 'Telugu', bn: 'Bengali', as: 'Bengali' }[lang];
  if (indic) loads.push(`700 40px "Noto Sans ${indic}"`);
  await Promise.all(loads.map((f) => document.fonts.load(f).catch(() => null)));
}

/**
 * Draw a 1080×1080 card. `card`: { variant, title, crest (blood group or emoji), crestIsEmoji, subtitle, lines[], quote,
 * name, meta, stats, serial, url (QR target), brandUrl, tagline, lang }
 */
export async function drawCard(canvas, card) {
  await fontsReady(card.lang);
  const cfg = CARD_VARIANTS[card.variant] || CARD_VARIANTS.blood_royalty;
  const W = 1080;
  const H = 1080;
  canvas.width = W;
  canvas.height = H;
  const ctx = canvas.getContext('2d');

  // background: three-stop vertical gradient + soft accent glow
  const g = ctx.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, rgb(cfg.bg[0]));
  g.addColorStop(0.55, rgb(cfg.bg[1]));
  g.addColorStop(1, rgb(cfg.bg[2]));
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);
  const glow = ctx.createRadialGradient(W / 2, 520, 40, W / 2, 520, 520);
  glow.addColorStop(0, rgb(cfg.accent, 0.28));
  glow.addColorStop(1, rgb(cfg.accent, 0));
  ctx.fillStyle = glow;
  ctx.fillRect(0, 0, W, H);

  // ornamental double border with diamond corners
  const m = 40;
  ctx.strokeStyle = rgb(cfg.primary);
  ctx.lineWidth = 3;
  ctx.strokeRect(m, m, W - 2 * m, H - 2 * m);
  ctx.lineWidth = 1;
  ctx.strokeStyle = rgb(cfg.dark);
  ctx.strokeRect(m + 12, m + 12, W - 2 * (m + 12), H - 2 * (m + 12));
  ctx.fillStyle = rgb(cfg.primary);
  for (const [cx, cy] of [[m, m], [W - m, m], [m, H - m], [W - m, H - m]]) {
    ctx.beginPath();
    ctx.moveTo(cx, cy - 12);
    ctx.lineTo(cx + 12, cy);
    ctx.lineTo(cx, cy + 12);
    ctx.lineTo(cx - 12, cy);
    ctx.closePath();
    ctx.fill();
  }
  text(ctx, '✦', 110, 110, { size: 28, color: rgb(cfg.primary) });
  text(ctx, '✦', W - 110, 110, { size: 28, color: rgb(cfg.primary) });

  // brand + title
  text(ctx, '🩸  BLOODLINK  🩸', W / 2, 128, { weight: 700, size: 34, family: SERIF, color: rgb(cfg.primary), letterSpacing: 6 });
  ctx.strokeStyle = rgb(cfg.dark);
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(W * 0.3, 172);
  ctx.lineTo(W * 0.7, 172);
  ctx.stroke();
  text(ctx, card.title, W / 2, 262, { weight: 900, size: 88, family: SERIF, color: rgb(cfg.light), maxWidth: 880 });

  // crest
  const cx0 = W / 2 - 115;
  const cy0 = 330;
  const roundRect = (x, y, w, h, r) => {
    ctx.beginPath();
    ctx.roundRect ? ctx.roundRect(x, y, w, h, r) : ctx.rect(x, y, w, h);
  };
  const crestFill = ctx.createLinearGradient(cx0, cy0, cx0 + 230, cy0 + 230);
  crestFill.addColorStop(0, rgb(cfg.accent, 0.35));
  crestFill.addColorStop(1, rgb([0, 0, 0], 0.35));
  roundRect(cx0, cy0, 230, 230, 26);
  ctx.fillStyle = crestFill;
  ctx.fill();
  ctx.lineWidth = 4;
  ctx.strokeStyle = rgb(cfg.primary);
  ctx.stroke();
  roundRect(cx0 + 9, cy0 + 9, 212, 212, 18);
  ctx.lineWidth = 1;
  ctx.strokeStyle = rgb(cfg.dark);
  ctx.stroke();
  if (card.crestIsEmoji) text(ctx, card.crest, W / 2, cy0 + 120, { size: 120, color: rgb(cfg.light), family: 'system-ui, sans-serif' });
  else text(ctx, card.crest, W / 2, cy0 + 118, { weight: 800, size: 118, color: rgb(cfg.primary), maxWidth: 200 });

  // story lines
  let y = 620;
  if (card.subtitle) {
    text(ctx, card.subtitle, W / 2, y, { weight: 700, size: 40, family: SERIF, color: rgb(cfg.primary), maxWidth: 860 });
    y += 52;
  }
  for (const line of card.lines || []) {
    text(ctx, line, W / 2, y, { weight: 500, size: 30, color: rgb(cfg.light), maxWidth: 860 });
    y += 42;
  }
  if (card.quote) {
    text(ctx, `“${card.quote}”`, W / 2, y + 4, { weight: 500, size: 26, color: rgb(cfg.primary), maxWidth: 860 });
    y += 46;
  }

  // divider + donor
  ctx.strokeStyle = rgb(cfg.dark);
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(W * 0.15, y + 6);
  ctx.lineTo(W * 0.85, y + 6);
  ctx.stroke();
  y += 56;
  text(ctx, (card.name || '').toUpperCase(), W / 2, y, { weight: 700, size: 50, family: SERIF, color: rgb(cfg.light), maxWidth: 640, letterSpacing: 2 });
  y += 50;
  text(ctx, card.meta, W / 2, y, { weight: 600, size: 28, color: rgb(cfg.primary), maxWidth: 640 });

  // QR code (bottom right) pointing at the donor's invite link
  if (card.url) {
    const q = document.createElement('canvas');
    await QRCode.toCanvas(q, card.url, { margin: 1, width: 150, errorCorrectionLevel: 'M', color: { dark: '#000000', light: '#ffffff' } });
    ctx.drawImage(q, W - 92 - 150, H - 92 - 150, 150, 150);
    ctx.strokeStyle = rgb(cfg.primary);
    ctx.lineWidth = 2;
    ctx.strokeRect(W - 92 - 154, H - 92 - 154, 158, 158);
    text(ctx, card.scan, W - 92 - 75, H - 72, { weight: 600, size: 16, color: rgb(cfg.light), maxWidth: 190 });
  }

  // footer
  text(ctx, card.brandUrl, 250, H - 150, { weight: 700, size: 26, color: rgb(cfg.primary), maxWidth: 360 });
  text(ctx, card.serial, 250, H - 114, { weight: 500, size: 18, family: 'ui-monospace, monospace', color: rgb(cfg.dark), maxWidth: 360 });
  text(ctx, card.tagline, 250, H - 80, { weight: 500, size: 17, color: rgb(cfg.light, 0.85), maxWidth: 380 });

  // holographic sheen
  const sheen = ctx.createLinearGradient(0, 0, W, H);
  sheen.addColorStop(0, 'rgba(255,255,255,0.10)');
  sheen.addColorStop(0.35, 'rgba(255,255,255,0)');
  sheen.addColorStop(0.65, 'rgba(255,255,255,0)');
  sheen.addColorStop(1, 'rgba(255,255,255,0.06)');
  ctx.fillStyle = sheen;
  ctx.fillRect(0, 0, W, H);
  return canvas;
}

export const toBlob = (canvas) => new Promise((resolve) => canvas.toBlob(resolve, 'image/png'));
