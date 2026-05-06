import React from 'react';
import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
  interpolate, spring, Sequence,
} from 'remotion';
import { C, grad, Logo, GlassCard, GradientButton, GradientText, AnimatedBg } from '../shared/Brand';

const features = [
  { icon: '📚', label: 'Syllabus Scanner',   sub: 'Auto-import every deadline' },
  { icon: '📊', label: 'Grade Tracker',      sub: 'Know your GPA in real time' },
  { icon: '🏫', label: 'Class Communities',  sub: 'Study groups that work' },
  { icon: '📅', label: 'Deadline Calendar',  sub: '3-day smart reminders' },
  { icon: '🎉', label: 'Events & Clubs',     sub: 'Campus life in one place' },
];

const ft = { fontFamily: "'Arial', sans-serif" };

export const LaunchHero: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const sp = (delay = 0, config = { damping: 180, stiffness: 160, mass: 0.6 }) =>
    spring({ frame: frame - delay, fps, config });

  // Logo
  const logoScale = sp(0);
  const logoOp = interpolate(frame, [0, 18], [0, 1], { extrapolateRight: 'clamp' });

  // Headline words
  const word1 = sp(28, { damping: 200, stiffness: 180, mass: 0.5 });
  const word2 = sp(44, { damping: 200, stiffness: 180, mass: 0.5 });

  // Tagline
  const tagOp = interpolate(frame, [72, 96], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ ...ft, overflow: 'hidden' }}>
      <AnimatedBg frame={frame} />

      {/* Logo + brand name */}
      <div style={{
        position: 'absolute',
        top: 180,
        left: 0, right: 0,
        display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20,
        opacity: logoOp,
        transform: `scale(${0.7 + logoScale * 0.3})`,
      }}>
        <Logo size={110} />
        <div style={{ color: C.white, fontSize: 48, fontWeight: 800, letterSpacing: -1 }}>
          CampusClip
        </div>
        <div style={{ color: C.dimBlue, fontSize: 28, fontWeight: 400, letterSpacing: 3 }}>
          WESTERN UNIVERSITY
        </div>
      </div>

      {/* Main headline */}
      <div style={{
        position: 'absolute',
        top: 560,
        left: 0, right: 0,
        paddingLeft: 80, paddingRight: 80,
        display: 'flex', flexDirection: 'column', gap: 8,
      }}>
        <div style={{
          fontSize: 108, fontWeight: 900, color: C.white,
          lineHeight: 1.05, letterSpacing: -3,
          transform: `translateY(${(1 - word1) * 60}px)`,
          opacity: word1,
        }}>
          Your campus.
        </div>
        <div style={{
          fontSize: 108, fontWeight: 900, lineHeight: 1.05, letterSpacing: -3,
          transform: `translateY(${(1 - word2) * 60}px)`,
          opacity: word2,
        }}>
          <GradientText>Organised.</GradientText>
        </div>
        <div style={{
          marginTop: 20, color: C.offWhite, fontSize: 36, fontWeight: 400,
          lineHeight: 1.5, opacity: tagOp,
        }}>
          The all-in-one platform for Western students.
        </div>
      </div>

      {/* Feature cards */}
      <div style={{
        position: 'absolute',
        top: 980,
        left: 60, right: 60,
        display: 'flex', flexDirection: 'column', gap: 20,
      }}>
        {features.map((f, i) => {
          const p = spring({
            frame: frame - (96 + i * 28),
            fps,
            config: { damping: 200, stiffness: 160, mass: 0.5 },
          });
          return (
            <GlassCard key={f.label} style={{
              padding: '24px 32px',
              display: 'flex', alignItems: 'center', gap: 28,
              transform: `translateX(${(1 - p) * 80}px)`,
              opacity: p,
            }}>
              <div style={{
                width: 72, height: 72, borderRadius: 18,
                background: grad,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 32, flexShrink: 0,
                boxShadow: '0 4px 20px rgba(64,64,242,0.4)',
              }}>
                {f.icon}
              </div>
              <div>
                <div style={{ color: C.white, fontSize: 34, fontWeight: 700, letterSpacing: -0.5 }}>
                  {f.label}
                </div>
                <div style={{ color: C.dimBlue, fontSize: 26, fontWeight: 400, marginTop: 4 }}>
                  {f.sub}
                </div>
              </div>
            </GlassCard>
          );
        })}
      </div>

      {/* CTA */}
      <Sequence from={480}>
        <div style={{
          position: 'absolute',
          bottom: 100,
          left: 80, right: 80,
          opacity: interpolate(frame, [480, 510], [0, 1], { extrapolateRight: 'clamp' }),
          transform: `translateY(${interpolate(frame, [480, 510], [40, 0], { extrapolateRight: 'clamp' })}px)`,
        }}>
          <GradientButton>Download Free — Aug 2026</GradientButton>
        </div>
      </Sequence>
    </AbsoluteFill>
  );
};
