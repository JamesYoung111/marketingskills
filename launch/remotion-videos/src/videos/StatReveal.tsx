import React from 'react';
import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
  interpolate, spring, Sequence,
} from 'remotion';
import { C, grad, GlassCard, GradientButton, GradientText, AnimatedBg, Logo } from '../shared/Brand';

const ft = { fontFamily: "'Arial', sans-serif" };

const checks = [
  'Auto-parsed from your syllabus',
  'Synced to your calendar instantly',
  'Smart reminders — 3 days early',
];

export const StatReveal: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Phase 1: "Real talk." 0→36 frames
  const intro = spring({ frame, fps, config: { damping: 200, stiffness: 160 } });

  // Phase 2: stat number counts up  48 → 168
  const statProg = interpolate(frame, [48, 168], [0, 70], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: (t) => t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2,
  });
  const statNum = Math.round(statProg);
  const statOp = interpolate(frame, [48, 72, 200, 228], [0, 1, 1, 0], { extrapolateRight: 'clamp' });

  // Phase 3: solution  240 → end
  const solOp = interpolate(frame, [240, 270], [0, 1], { extrapolateRight: 'clamp' });
  const solY = interpolate(frame, [240, 270], [40, 0], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ ...ft, overflow: 'hidden' }}>
      <AnimatedBg frame={frame} />

      {/* Phase 1 – intro hook */}
      <div style={{
        position: 'absolute', top: 300, left: 0, right: 0,
        textAlign: 'center',
        opacity: interpolate(frame, [0, 24, 180, 228], [0, 1, 1, 0], { extrapolateRight: 'clamp' }),
        transform: `scale(${0.7 + intro * 0.3})`,
      }}>
        <div style={{ color: C.offWhite, fontSize: 72, fontWeight: 800, letterSpacing: -2 }}>
          Real talk.
        </div>
      </div>

      {/* Phase 2 – big stat */}
      <div style={{
        position: 'absolute', top: 500, left: 0, right: 0,
        textAlign: 'center', opacity: statOp,
      }}>
        <div style={{
          fontSize: 280, fontWeight: 900, lineHeight: 1, letterSpacing: -8,
          background: grad,
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
        }}>
          {statNum}%
        </div>
        <div style={{ color: C.offWhite, fontSize: 46, fontWeight: 600, marginTop: 16 }}>
          of students miss at least one
        </div>
        <div style={{ color: C.dimBlue, fontSize: 40, fontWeight: 400, marginTop: 8 }}>
          deadline per semester
        </div>

        {/* Underline rule */}
        <div style={{
          margin: '48px auto 0',
          width: interpolate(frame, [140, 180], [0, 360], { extrapolateRight: 'clamp' }),
          height: 4, borderRadius: 2,
          background: grad,
        }} />
      </div>

      {/* Phase 3 – solution */}
      <div style={{
        position: 'absolute', top: 460, left: 60, right: 60,
        opacity: solOp,
        transform: `translateY(${solY}px)`,
      }}>
        <div style={{
          color: C.white, fontSize: 80, fontWeight: 900,
          letterSpacing: -2, lineHeight: 1.1, textAlign: 'center',
        }}>
          CampusClip sees every deadline{' '}
          <GradientText>before you do.</GradientText>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 22, marginTop: 64 }}>
          {checks.map((text, i) => {
            const cp = spring({
              frame: frame - (270 + i * 20),
              fps,
              config: { damping: 200, stiffness: 180 },
            });
            return (
              <GlassCard key={text} style={{
                padding: '28px 36px',
                display: 'flex', alignItems: 'center', gap: 24,
                opacity: cp,
                transform: `translateX(${(1 - cp) * 60}px)`,
              }}>
                <div style={{
                  width: 44, height: 44, borderRadius: '50%',
                  background: grad, flexShrink: 0,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 22, color: 'white', fontWeight: 900,
                  boxShadow: '0 4px 16px rgba(64,64,242,0.5)',
                }}>
                  ✓
                </div>
                <div style={{ color: C.offWhite, fontSize: 34, fontWeight: 500 }}>
                  {text}
                </div>
              </GlassCard>
            );
          })}
        </div>
      </div>

      {/* CTA */}
      <Sequence from={336}>
        <div style={{
          position: 'absolute', bottom: 100, left: 80, right: 80,
          opacity: interpolate(frame, [336, 360], [0, 1], { extrapolateRight: 'clamp' }),
          transform: `translateY(${interpolate(frame, [336, 360], [40, 0], { extrapolateRight: 'clamp' })}px)`,
        }}>
          <GradientButton>Never Miss a Deadline →</GradientButton>
        </div>
      </Sequence>

      <div style={{ position: 'absolute', top: 60, right: 60 }}>
        <Logo size={80} />
      </div>
    </AbsoluteFill>
  );
};
