import React from 'react';
import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
  interpolate, spring, Img,
} from 'remotion';
import { C, grad, GradientText, AnimatedBg, Logo } from '../shared/Brand';

const ft = { fontFamily: "'Arial', sans-serif" };

const RAW = 'https://raw.githubusercontent.com/JamesYoung111/marketingskills/main/launch/app-screenshots';

// 6 key screens — ordered for maximum impact
const SCREENS = [
  { src: `${RAW}/IMG_1617.jpeg`, label: '📊 Grade Tracking',      sub: 'Set your goal. Watch your GPA climb.' },
  { src: `${RAW}/IMG_1622.jpeg`, label: '📅 Deadline Calendar',   sub: 'Track your academic journey.' },
  { src: `${RAW}/IMG_1619.jpeg`, label: '🏫 Clubs & Communities', sub: 'Investment Club. Sigma Chi. Find yours.' },
  { src: `${RAW}/IMG_1621.jpeg`, label: '🏠 Campus Feed',         sub: 'Everything happening at Western.' },
  { src: `${RAW}/IMG_1623.jpeg`, label: '🔍 Explore',             sub: 'Discover trending students & clubs.' },
  { src: `${RAW}/IMG_1618.jpeg`, label: '📚 Your Classes',        sub: 'Every grade. Every weight. One place.' },
];

const SPF = 40; // frames per screen (1.67s each at 24fps)

// ── Timing constants ──────────────────────────────────────────────────────────
const HOOK_END       = 52;
const MONTAGE_START  = HOOK_END;
const MONTAGE_END    = MONTAGE_START + SCREENS.length * SPF; // 292
const PAUSE_END      = MONTAGE_END + 10;                     // 302
const COUNTDOWN_START = PAUSE_END;                           // 302
const CTA_START      = COUNTDOWN_START + 90;                 // 392
export const TOTAL_FRAMES = CTA_START + 80;                  // 472  ≈ 19.7s

// ── Single screen card ────────────────────────────────────────────────────────
const ScreenCard: React.FC<{
  screen: (typeof SCREENS)[0];
  localFrame: number;
  fps: number;
}> = ({ screen, localFrame, fps }) => {
  const imgOp = interpolate(
    localFrame,
    [0, 5, SPF - 5, SPF],
    [0, 1, 1, 0],
    { extrapolateRight: 'clamp' },
  );
  const imgScale = interpolate(localFrame, [0, SPF], [1.07, 1.0], { extrapolateRight: 'clamp' });
  const labelSp  = spring({ frame: localFrame - 6, fps, config: { damping: 200, stiffness: 220 } });
  const subOp    = interpolate(localFrame, [16, 28], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ opacity: imgOp }}>
      {/* Full-bleed screenshot with subtle zoom */}
      <div style={{
        position: 'absolute', inset: 0,
        transform: `scale(${imgScale})`,
        transformOrigin: 'center center',
      }}>
        <Img src={screen.src} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
      </div>

      {/* Gradient overlays for readability */}
      <div style={{
        position: 'absolute', inset: 0,
        background: 'linear-gradient(to bottom, rgba(8,18,38,0.78) 0%, transparent 30%, transparent 58%, rgba(8,18,38,0.72) 100%)',
      }} />

      {/* Feature label — top area */}
      <div style={{
        position: 'absolute', top: 130, left: 64, right: 64,
        transform: `translateY(${(1 - labelSp) * 44}px)`,
        opacity: labelSp,
      }}>
        <div style={{ ...ft, fontSize: 58, fontWeight: 900, color: '#fff', letterSpacing: -1, lineHeight: 1.1 }}>
          {screen.label}
        </div>
        <div style={{ ...ft, fontSize: 34, fontWeight: 400, color: 'rgba(180,205,245,0.9)', marginTop: 10, opacity: subOp, lineHeight: 1.4 }}>
          {screen.sub}
        </div>
      </div>

      {/* Blue flash on screen entry */}
      <div style={{
        position: 'absolute', inset: 0,
        background: 'rgba(64,64,242,1)',
        opacity: interpolate(localFrame, [0, 4], [0.9, 0], { extrapolateRight: 'clamp' }),
        pointerEvents: 'none',
      }} />
    </AbsoluteFill>
  );
};

// ── Main component ────────────────────────────────────────────────────────────
export const LaunchCountdown: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const isMontage    = frame >= MONTAGE_START && frame < MONTAGE_END;
  const screenIdx    = isMontage ? Math.min(Math.floor((frame - MONTAGE_START) / SPF), SCREENS.length - 1) : -1;
  const localFrame   = isMontage ? (frame - MONTAGE_START) % SPF : 0;
  const barProgress  = isMontage
    ? (frame - MONTAGE_START) / (MONTAGE_END - MONTAGE_START)
    : frame >= MONTAGE_END ? 1 : 0;

  // Hook
  const hookOp  = interpolate(frame, [0, 18, 44, HOOK_END], [0, 1, 1, 0], { extrapolateRight: 'clamp' });
  const logoSp  = spring({ frame, fps, config: { damping: 180, stiffness: 200 } });

  // Countdown
  const cdOp     = interpolate(frame, [COUNTDOWN_START, COUNTDOWN_START + 18], [0, 1], { extrapolateRight: 'clamp' });
  const inSp     = spring({ frame: frame - (COUNTDOWN_START + 4),  fps, config: { damping: 200, stiffness: 180 } });
  const numSp    = spring({ frame: frame - (COUNTDOWN_START + 14), fps, config: { damping: 110, stiffness: 320, mass: 0.7 } });
  const monthsSp = spring({ frame: frame - (COUNTDOWN_START + 28), fps, config: { damping: 160, stiffness: 260 } });
  const augOp    = interpolate(frame, [COUNTDOWN_START + 56, COUNTDOWN_START + 70], [0, 1], { extrapolateRight: 'clamp' });
  const lineOp   = interpolate(frame, [COUNTDOWN_START + 44, COUNTDOWN_START + 58], [0, 1], { extrapolateRight: 'clamp' });

  // CTA
  const ctaOp = interpolate(frame, [CTA_START, CTA_START + 20], [0, 1], { extrapolateRight: 'clamp' });
  const ctaSp = spring({ frame: frame - CTA_START, fps, config: { damping: 200, stiffness: 180 } });
  const btnSp = spring({ frame: frame - (CTA_START + 16), fps, config: { damping: 200, stiffness: 200 } });

  return (
    <AbsoluteFill style={{ ...ft, overflow: 'hidden', background: '#0A1628' }}>

      {/* ── Hook ──────────────────────────────────────────── */}
      {frame < HOOK_END && (
        <AbsoluteFill style={{ opacity: hookOp }}>
          <AnimatedBg frame={frame} />
          <div style={{
            position: 'absolute', inset: 0,
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          }}>
            <div style={{ transform: `scale(${0.4 + logoSp * 0.6})`, opacity: logoSp }}>
              <Logo size={150} />
            </div>
            <div style={{
              color: '#fff', fontSize: 62, fontWeight: 900, letterSpacing: -1.5,
              marginTop: 36, textAlign: 'center', paddingInline: 60,
              transform: `translateY(${(1 - logoSp) * 30}px)`, opacity: logoSp,
            }}>
              CampusClip
            </div>
            <div style={{
              color: C.dimBlue, fontSize: 34, fontWeight: 400, marginTop: 14,
              textAlign: 'center', paddingInline: 80, lineHeight: 1.4,
              opacity: interpolate(frame, [20, 40], [0, 1], { extrapolateRight: 'clamp' }),
            }}>
              Western's campus app is almost here.
            </div>
          </div>
        </AbsoluteFill>
      )}

      {/* ── Montage ───────────────────────────────────────── */}
      {isMontage && screenIdx >= 0 && (
        <ScreenCard screen={SCREENS[screenIdx]} localFrame={localFrame} fps={fps} />
      )}

      {/* Progress bar */}
      {(isMontage || (frame >= MONTAGE_END && frame < PAUSE_END)) && (
        <div style={{
          position: 'absolute', top: 0, left: 0,
          height: 7,
          width: `${barProgress * 100}%`,
          background: grad,
          boxShadow: '0 0 12px rgba(91,158,248,0.8)',
        }} />
      )}

      {/* Logo watermark during montage */}
      {isMontage && (
        <div style={{ position: 'absolute', bottom: 64, right: 64, opacity: 0.9 }}>
          <Logo size={68} />
        </div>
      )}

      {/* ── Countdown ─────────────────────────────────────── */}
      {frame >= COUNTDOWN_START && frame < CTA_START && (
        <AbsoluteFill style={{ opacity: cdOp }}>
          <AnimatedBg frame={frame} />
          <div style={{
            position: 'absolute', inset: 0,
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          }}>
            {/* "Launching in" */}
            <div style={{
              color: C.dimBlue, fontSize: 38, fontWeight: 500, letterSpacing: 6,
              textTransform: 'uppercase',
              transform: `translateY(${(1 - inSp) * 32}px)`, opacity: inSp,
            }}>
              Launching in
            </div>

            {/* Giant "3" */}
            <div style={{
              fontSize: 340, fontWeight: 900, lineHeight: 0.82, letterSpacing: -20,
              background: grad,
              WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
              transform: `scale(${0.2 + numSp * 0.8})`,
              opacity: numSp,
              filter: `drop-shadow(0 0 60px rgba(91,158,248,${numSp * 0.6}))`,
            }}>
              3
            </div>

            {/* "MONTHS" */}
            <div style={{
              color: '#fff', fontSize: 92, fontWeight: 900, letterSpacing: 14,
              textTransform: 'uppercase',
              transform: `translateY(${(1 - monthsSp) * 44}px)`, opacity: monthsSp,
            }}>
              MONTHS
            </div>

            {/* Divider line */}
            <div style={{
              marginTop: 48, marginBottom: 40,
              width: `${lineOp * 320}px`, height: 3, borderRadius: 2,
              background: grad,
              boxShadow: '0 0 16px rgba(91,158,248,0.6)',
            }} />

            {/* "August 2026" */}
            <div style={{
              color: C.orange, fontSize: 46, fontWeight: 700, letterSpacing: 3,
              opacity: augOp,
              transform: `translateY(${(1 - augOp) * 20}px)`,
            }}>
              August 2026
            </div>
          </div>

          {/* CampusClip logo top-right */}
          <div style={{ position: 'absolute', top: 64, right: 64, opacity: augOp }}>
            <Logo size={72} />
          </div>
        </AbsoluteFill>
      )}

      {/* ── CTA ───────────────────────────────────────────── */}
      {frame >= CTA_START && (
        <AbsoluteFill style={{ opacity: ctaOp }}>
          <AnimatedBg frame={frame} />
          <div style={{
            position: 'absolute', inset: 0,
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            gap: 20,
          }}>
            {/* Logo */}
            <div style={{
              transform: `scale(${0.4 + ctaSp * 0.6})`, opacity: ctaSp,
            }}>
              <Logo size={120} />
            </div>

            {/* Wordmark */}
            <div style={{ fontSize: 80, fontWeight: 900, letterSpacing: -2, opacity: ctaSp }}>
              <GradientText>CampusClip</GradientText>
            </div>

            {/* Tagline */}
            <div style={{
              color: C.offWhite, fontSize: 36, fontWeight: 400,
              textAlign: 'center', paddingInline: 80, lineHeight: 1.5,
              opacity: interpolate(frame, [CTA_START + 12, CTA_START + 28], [0, 1], { extrapolateRight: 'clamp' }),
            }}>
              Free for Western Students
            </div>

            {/* CTA button */}
            <div style={{
              marginTop: 20,
              paddingInline: 52, paddingBlock: 22,
              background: grad,
              borderRadius: 60,
              color: '#fff', fontSize: 34, fontWeight: 700, letterSpacing: 0.5,
              transform: `translateY(${(1 - btnSp) * 40}px)`,
              opacity: btnSp,
              boxShadow: '0 10px 50px rgba(64,64,242,0.55)',
            }}>
              Download Coming August 2026
            </div>

            {/* Social handle */}
            <div style={{
              color: C.dimBlue, fontSize: 28, fontWeight: 400, letterSpacing: 1,
              opacity: interpolate(frame, [CTA_START + 32, CTA_START + 48], [0, 1], { extrapolateRight: 'clamp' }),
            }}>
              @campusclipapp
            </div>
          </div>
        </AbsoluteFill>
      )}

    </AbsoluteFill>
  );
};
