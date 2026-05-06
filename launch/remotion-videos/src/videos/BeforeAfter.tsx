import React from 'react';
import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
  interpolate, spring,
} from 'remotion';
import { C, grad, GlassCard, GradientButton, GradientText, AnimatedBg, Logo } from '../shared/Brand';

const ft = { fontFamily: "'Arial', sans-serif" };

const beforeItems = [
  { text: 'When was the midterm again??', emoji: '😰' },
  { text: 'I have THREE things due tomorrow', emoji: '😭' },
  { text: 'Which prof posted the notes?', emoji: '🤯' },
  { text: 'Did I even submit that assignment?', emoji: '💀' },
];

const afterItems = [
  { text: 'All deadlines auto-imported', emoji: '✅' },
  { text: 'Grade sitting at 89% — on track', emoji: '📊' },
  { text: 'Smart reminder 3 days early', emoji: '🔔' },
  { text: 'Class notes synced to community', emoji: '🤝' },
];

export const BeforeAfter: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const PHASE_BEFORE = 216; // 9s
  const PHASE_PIVOT  = 264; // 11s
  const PHASE_AFTER  = 288; // 12s

  const isAfterPhase = frame >= PHASE_PIVOT;

  return (
    <AbsoluteFill style={{ ...ft, overflow: 'hidden' }}>
      <AnimatedBg frame={frame} darkOverlay={isAfterPhase ? 0 : 0.1} />

      {/* ── BEFORE phase ── */}
      {frame < PHASE_PIVOT && (
        <div style={{
          position: 'absolute', inset: 0,
          opacity: interpolate(frame, [PHASE_BEFORE, PHASE_PIVOT], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }),
        }}>
          {/* Hook */}
          <div style={{
            position: 'absolute', top: 220, left: 0, right: 0, textAlign: 'center',
            opacity: interpolate(frame, [0, 20], [0, 1], { extrapolateRight: 'clamp' }),
          }}>
            <div style={{ fontSize: 72, marginBottom: 12 }}>😬</div>
            <div style={{ color: C.white, fontSize: 68, fontWeight: 800, letterSpacing: -2 }}>
              Sound familiar?
            </div>
            <div style={{ color: C.dimBlue, fontSize: 36, fontWeight: 400, marginTop: 12 }}>
              Every. Single. Semester.
            </div>
          </div>

          {/* Before cards */}
          <div style={{
            position: 'absolute', top: 560, left: 60, right: 60,
            display: 'flex', flexDirection: 'column', gap: 22,
          }}>
            {beforeItems.map((item, i) => {
              const p = spring({
                frame: frame - (36 + i * 22),
                fps,
                config: { damping: 200, stiffness: 160 },
              });
              return (
                <div key={item.text} style={{
                  display: 'flex', alignItems: 'center', gap: 22,
                  padding: '26px 32px', borderRadius: 20,
                  background: 'rgba(180, 30, 50, 0.2)',
                  border: '1px solid rgba(220, 60, 80, 0.25)',
                  boxShadow: '0 4px 24px rgba(180,30,50,0.15)',
                  opacity: p,
                  transform: `translateX(${(1 - p) * 60}px)`,
                }}>
                  <span style={{ fontSize: 36, flexShrink: 0 }}>{item.emoji}</span>
                  <div style={{ color: C.offWhite, fontSize: 34, fontWeight: 500 }}>
                    {item.text}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ── PIVOT text ── */}
      {frame >= PHASE_BEFORE && frame < PHASE_AFTER + 24 && (
        <div style={{
          position: 'absolute', inset: 0,
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          opacity: interpolate(
            frame,
            [PHASE_BEFORE, PHASE_PIVOT, PHASE_AFTER, PHASE_AFTER + 24],
            [0, 1, 1, 0],
            { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
          ),
        }}>
          <div style={{
            color: C.white, fontSize: 86, fontWeight: 900,
            letterSpacing: -2, textAlign: 'center', lineHeight: 1.1,
          }}>
            There's a<br />
            <GradientText>better way.</GradientText>
          </div>
        </div>
      )}

      {/* ── AFTER phase ── */}
      {frame >= PHASE_AFTER && (
        <div style={{
          position: 'absolute', inset: 0,
          opacity: interpolate(frame, [PHASE_AFTER, PHASE_AFTER + 24], [0, 1], { extrapolateRight: 'clamp' }),
        }}>
          <div style={{
            position: 'absolute', top: 200, left: 0, right: 0, textAlign: 'center',
          }}>
            <div style={{ color: C.white, fontSize: 68, fontWeight: 800, letterSpacing: -2 }}>
              With CampusClip
            </div>
            <div style={{ color: C.dimBlue, fontSize: 36, fontWeight: 400, marginTop: 12 }}>
              Western students are organised.
            </div>
          </div>

          <div style={{
            position: 'absolute', top: 480, left: 60, right: 60,
            display: 'flex', flexDirection: 'column', gap: 22,
          }}>
            {afterItems.map((item, i) => {
              const p = spring({
                frame: frame - (PHASE_AFTER + 12 + i * 20),
                fps,
                config: { damping: 200, stiffness: 160 },
              });
              return (
                <GlassCard key={item.text} style={{
                  display: 'flex', alignItems: 'center', gap: 22,
                  padding: '26px 32px',
                  opacity: p,
                  transform: `translateX(${(1 - p) * 60}px)`,
                }}>
                  <div style={{
                    width: 52, height: 52, borderRadius: '50%',
                    background: grad, flexShrink: 0,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 24,
                    boxShadow: '0 4px 16px rgba(64,64,242,0.5)',
                  }}>
                    {item.emoji}
                  </div>
                  <div style={{ color: C.offWhite, fontSize: 34, fontWeight: 500 }}>
                    {item.text}
                  </div>
                </GlassCard>
              );
            })}
          </div>
        </div>
      )}

      {/* CTA */}
      {frame > 396 && (
        <div style={{
          position: 'absolute', bottom: 100, left: 80, right: 80,
          opacity: interpolate(frame, [396, 420], [0, 1], { extrapolateRight: 'clamp' }),
          transform: `translateY(${interpolate(frame, [396, 420], [40, 0], { extrapolateRight: 'clamp' })}px)`,
        }}>
          <GradientButton>Download Free — Aug 2026</GradientButton>
        </div>
      )}

      <div style={{ position: 'absolute', top: 60, right: 60 }}>
        <Logo size={80} />
      </div>
    </AbsoluteFill>
  );
};
