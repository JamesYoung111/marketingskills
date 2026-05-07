import React from 'react';
import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
  interpolate, spring, Img,
} from 'remotion';
import { C, grad, AnimatedBg, Logo } from '../shared/Brand';

const ft = { fontFamily: "'Arial', sans-serif" };
const RAW = 'https://raw.githubusercontent.com/JamesYoung111/marketingskills/main/launch/app-screenshots';

const SCREENS = {
  dashboard:   `${RAW}/IMG_1617.jpeg`,
  classDetail: `${RAW}/IMG_1618.jpeg`,
  clubs:       `${RAW}/IMG_1619.jpeg`,
  feed:        `${RAW}/IMG_1621.jpeg`,
  calendar:    `${RAW}/IMG_1622.jpeg`,
  search:      `${RAW}/IMG_1623.jpeg`,
};

// Words rendered in blue gradient
const HIGHLIGHTS = new Set([
  'campusclip', 'gpa', 'automatically', 'automatically.', 'free', 'free.',
  'western', 'western.', 'clubs', 'clubs.', 'deadlines', 'deadlines.',
  'grades', 'grades…', 'target', 'automatically.',
  'one', 'automatically,', 'automatically—', 'real-time',
]);

// ── Shared primitives ─────────────────────────────────────────────────────────

const AnimWord: React.FC<{
  word: string; frame: number; delay: number; fps: number; size: number;
}> = ({ word, frame, delay, fps, size }) => {
  const sp = spring({ frame: frame - delay, fps, config: { damping: 200, stiffness: 420, mass: 0.4 } });
  const c = Math.max(0, Math.min(1, sp));
  const isHl = HIGHLIGHTS.has(word.toLowerCase().replace(/[.,!?…'"]/g, ''));
  return (
    <span style={{
      display: 'inline-block',
      marginRight: size * 0.26,
      transform: `translateY(${(1 - c) * 28}px) scale(${0.55 + c * 0.45})`,
      opacity: c,
      textShadow: '0 2px 20px rgba(0,0,0,0.95), 0 4px 40px rgba(0,0,0,0.6)',
      ...(isHl
        ? { background: grad, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }
        : { color: '#fff' }),
    }}>
      {word}
    </span>
  );
};

const CaptionLine: React.FC<{
  text: string; startF: number; fps: number;
  size?: number; bold?: boolean; color?: string;
}> = ({ text, startF, fps, size = 78, bold = true, color }) => {
  const frame = useCurrentFrame();
  if (frame < startF) return null;
  const words = text.split(' ');
  return (
    <div style={{
      ...ft, fontSize: size, fontWeight: bold ? 900 : 500,
      lineHeight: 1.18, letterSpacing: size > 70 ? -1.5 : -0.5,
      display: 'flex', flexWrap: 'wrap', justifyContent: 'center',
      padding: '0 52px', marginBottom: 4,
      color: color || undefined,
    }}>
      {words.map((w, i) => (
        color
          ? <span key={i} style={{ marginRight: size * 0.26 }}>{w}</span>
          : <AnimWord key={i} word={w} frame={frame} delay={startF + i * 4} fps={fps} size={size} />
      ))}
    </div>
  );
};

interface SceneDef {
  startF: number;
  endF: number;
  broll?: string;
  lines: Array<{ text: string; size?: number; delay?: number; bold?: boolean; color?: string }>;
}

const Scene: React.FC<{ s: SceneDef; fps: number }> = ({ s, fps }) => {
  const frame = useCurrentFrame();
  if (frame < s.startF || frame >= s.endF) return null;

  const fadeIn  = interpolate(frame, [s.startF, s.startF + 6], [0, 1], { extrapolateRight: 'clamp' });
  const fadeOut = interpolate(frame, [s.endF - 8, s.endF], [1, 0], { extrapolateRight: 'clamp' });
  const op = Math.min(fadeIn, fadeOut);

  return (
    <>
      {s.broll && (
        <AbsoluteFill style={{ opacity: op }}>
          <Img src={s.broll} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          <div style={{
            position: 'absolute', inset: 0,
            background: 'linear-gradient(to bottom, rgba(8,18,38,0.55) 0%, rgba(8,18,38,0.1) 40%, rgba(8,18,38,0.1) 60%, rgba(8,18,38,0.82) 100%)',
          }} />
        </AbsoluteFill>
      )}
      <div style={{
        position: 'absolute', inset: 0, opacity: op,
        display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center', gap: 6,
      }}>
        {s.lines.map((ln, i) => (
          <CaptionLine
            key={i} text={ln.text} fps={fps}
            startF={s.startF + (ln.delay ?? i * 18)}
            size={ln.size} bold={ln.bold} color={ln.color}
          />
        ))}
      </div>
    </>
  );
};

const Handle: React.FC = () => {
  const frame = useCurrentFrame();
  const op = interpolate(frame, [24, 48], [0, 1], { extrapolateRight: 'clamp' });
  return (
    <div style={{
      position: 'absolute', bottom: 72, left: 0, right: 0,
      display: 'flex', justifyContent: 'center', opacity: op,
    }}>
      <span style={{ ...ft, fontSize: 32, fontWeight: 500, color: 'rgba(180,205,245,0.72)', letterSpacing: 1 }}>
        @campusclipapp
      </span>
    </div>
  );
};

const ProgBar: React.FC<{ total: number }> = ({ total }) => {
  const frame = useCurrentFrame();
  return (
    <div style={{
      position: 'absolute', top: 0, left: 0, height: 5,
      width: `${(frame / total) * 100}%`,
      background: grad, boxShadow: '0 0 10px rgba(91,158,248,0.7)',
    }} />
  );
};

const CTASlate: React.FC<{ startF: number }> = ({ startF }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (frame < startF) return null;
  const sp = spring({ frame: frame - startF, fps, config: { damping: 200, stiffness: 180 } });
  const op = interpolate(frame, [startF, startF + 16], [0, 1], { extrapolateRight: 'clamp' });
  return (
    <div style={{
      position: 'absolute', inset: 0, opacity: op,
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center', gap: 24,
    }}>
      <div style={{ transform: `scale(${0.4 + sp * 0.6})`, opacity: sp }}>
        <Logo size={100} />
      </div>
      <div style={{
        ...ft, fontSize: 72, fontWeight: 900, letterSpacing: -2,
        background: grad, WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent', backgroundClip: 'text',
        opacity: sp,
      }}>
        CampusClip
      </div>
      <div style={{
        ...ft, fontSize: 36, fontWeight: 500, color: C.offWhite,
        textAlign: 'center', paddingInline: 80, lineHeight: 1.5,
        opacity: interpolate(frame, [startF + 14, startF + 30], [0, 1], { extrapolateRight: 'clamp' }),
      }}>
        Free for Western Students
      </div>
      <div style={{
        marginTop: 8, paddingInline: 52, paddingBlock: 20,
        background: grad, borderRadius: 60,
        ...ft, color: '#fff', fontSize: 32, fontWeight: 700, letterSpacing: 0.5,
        transform: `translateY(${(1 - sp) * 40}px)`, opacity: sp,
        boxShadow: '0 10px 50px rgba(64,64,242,0.55)',
      }}>
        Download Coming August 2026
      </div>
    </div>
  );
};

// ── Script 1: Grade Tracker (15s = 360 frames) ────────────────────────────────
const S1_SCENES: SceneDef[] = [
  {
    startF: 0, endF: 88,
    lines: [
      { text: "If you're at Western", size: 92, delay: 0 },
      { text: "and still using a spreadsheet", size: 68, delay: 24 },
      { text: "to track your grades…", size: 68, delay: 52 },
    ],
  },
  {
    startF: 88, endF: 185,
    lines: [
      { text: "you're wasting", size: 96, delay: 0 },
      { text: "so much time.", size: 96, delay: 20 },
    ],
  },
  {
    startF: 185, endF: 295,
    broll: SCREENS.dashboard,
    lines: [
      { text: "CampusClip does it", size: 84, delay: 8 },
      { text: "automatically.", size: 84, delay: 32 },
      { text: "See your GPA update in real time.", size: 52, delay: 60, bold: false },
    ],
  },
  {
    startF: 295, endF: 340,
    lines: [
      { text: "It's free.", size: 96, delay: 0 },
    ],
  },
];

export const UGCGradeTracker: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ ...ft, overflow: 'hidden', background: C.darkBg }}>
      <AnimatedBg frame={useCurrentFrame()} />
      {S1_SCENES.map((s, i) => <Scene key={i} s={s} fps={fps} />)}
      <CTASlate startF={340} />
      <Handle />
      <ProgBar total={360} />
    </AbsoluteFill>
  );
};
export const UGCGradeTrackerFrames = 360;

// ── Script 3: Transformation (25s = 600 frames) ───────────────────────────────
const S3_SCENES: SceneDef[] = [
  {
    startF: 0, endF: 110,
    lines: [
      { text: "First year I didn't know", size: 82, delay: 0 },
      { text: "my grade in 3 of my 5 classes", size: 62, delay: 24 },
      { text: "until the week before finals.", size: 62, delay: 52 },
    ],
  },
  {
    startF: 110, endF: 230,
    lines: [
      { text: "Canvas shows marks.", size: 80, delay: 0 },
      { text: "Not your actual average.", size: 80, delay: 28 },
      { text: "Every exam I was calculating", size: 56, delay: 62, bold: false },
      { text: "in the hallway.", size: 56, delay: 80, bold: false },
    ],
  },
  {
    startF: 230, endF: 360,
    broll: SCREENS.classDetail,
    lines: [
      { text: "CampusClip tracks it all.", size: 86, delay: 8 },
      { text: "Set your target GPA.", size: 70, delay: 40 },
      { text: "It tells you exactly what you", size: 54, delay: 72, bold: false },
      { text: "need on every upcoming test.", size: 54, delay: 94, bold: false },
    ],
  },
  {
    startF: 360, endF: 470,
    broll: SCREENS.dashboard,
    lines: [
      { text: "No spreadsheet.", size: 90, delay: 0 },
      { text: "No guessing.", size: 90, delay: 24 },
    ],
  },
  {
    startF: 470, endF: 555,
    lines: [
      { text: "Built for Western.", size: 88, delay: 0 },
      { text: "Your actual courses.", size: 66, delay: 28 },
      { text: "Your actual clubs.", size: 66, delay: 50 },
    ],
  },
];

export const UGCTransformation: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ ...ft, overflow: 'hidden', background: C.darkBg }}>
      <AnimatedBg frame={useCurrentFrame()} />
      {S3_SCENES.map((s, i) => <Scene key={i} s={s} fps={fps} />)}
      <CTASlate startF={555} />
      <Handle />
      <ProgBar total={600} />
    </AbsoluteFill>
  );
};
export const UGCTransformationFrames = 600;

// ── Script 5: Peer Recommendation (15s = 360 frames) ─────────────────────────
const S5_SCENES: SceneDef[] = [
  {
    startF: 0, endF: 88,
    lines: [
      { text: "If you're starting at Western", size: 82, delay: 0 },
      { text: "in September—", size: 82, delay: 28 },
      { text: "download CampusClip", size: 68, delay: 52, color: C.gradA },
    ],
  },
  {
    startF: 88, endF: 170,
    broll: SCREENS.dashboard,
    lines: [
      { text: "Tracks your grades", size: 80, delay: 0 },
      { text: "automatically.", size: 80, delay: 20 },
    ],
  },
  {
    startF: 170, endF: 252,
    broll: SCREENS.clubs,
    lines: [
      { text: "Shows you every club", size: 80, delay: 0 },
      { text: "on campus.", size: 80, delay: 20 },
    ],
  },
  {
    startF: 252, endF: 320,
    broll: SCREENS.calendar,
    lines: [
      { text: "Syncs deadlines", size: 80, delay: 0 },
      { text: "with your courses.", size: 80, delay: 20 },
    ],
  },
  {
    startF: 320, endF: 360,
    lines: [
      { text: "The one app I wish I had", size: 72, delay: 0 },
      { text: "in first year.", size: 72, delay: 24 },
    ],
  },
];

export const UGCPeerRec: React.FC = () => {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ ...ft, overflow: 'hidden', background: C.darkBg }}>
      <AnimatedBg frame={frame} />
      {S5_SCENES.map((s, i) => <Scene key={i} s={s} fps={fps} />)}
      <Handle />
      <ProgBar total={360} />
    </AbsoluteFill>
  );
};
export const UGCPeerRecFrames = 360;
