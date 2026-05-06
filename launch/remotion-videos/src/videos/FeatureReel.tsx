import React from 'react';
import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
  interpolate, spring,
} from 'remotion';
import { C, grad, GlassCard, GradientButton, GradientText, AnimatedBg, Logo } from '../shared/Brand';

const ft = { fontFamily: "'Arial', sans-serif" };

const sections: { emoji: string; title: string; body: string; accent: string }[] = [
  { emoji: '📚', title: 'Syllabus Scanner',   body: 'Drop your PDF. Every deadline auto-imported in seconds.', accent: C.gradA },
  { emoji: '📊', title: 'Grade Tracker',      body: 'Enter a mark, see your GPA recalculate live.', accent: C.gradB },
  { emoji: '🏫', title: 'Class Communities',  body: 'Course-specific chats, notes, and study groups.', accent: C.midBlue },
  { emoji: '📅', title: 'Deadline Calendar',  body: '24-hour warnings. Never surprised. Never late.', accent: C.orange },
  { emoji: '🎉', title: 'Events & Clubs',     body: 'Everything happening at Western, in one feed.', accent: C.gradA },
];

const SEC_FRAMES = 120; // 5 seconds each section at 24fps

export const FeatureReel: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const secIdx = Math.min(Math.floor(frame / SEC_FRAMES), sections.length - 1);
  const secFrame = frame - secIdx * SEC_FRAMES;
  const sec = sections[secIdx];

  // Transition: fade out last 12 frames of section
  const sectionOp = secFrame < SEC_FRAMES - 12
    ? interpolate(secFrame, [0, 16], [0, 1], { extrapolateRight: 'clamp' })
    : interpolate(secFrame, [SEC_FRAMES - 12, SEC_FRAMES], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  const sp = (d = 0) => spring({ frame: secFrame - d, fps, config: { damping: 180, stiffness: 160, mass: 0.6 } });

  const titleSp = sp(8);
  const bodySp  = sp(20);
  const barSp   = sp(0);

  // Big background emoji
  const emojiFontSize = 480;

  // Progress dots
  const totalSec = sections.length;

  return (
    <AbsoluteFill style={{ ...ft, overflow: 'hidden' }}>
      <AnimatedBg frame={frame} />

      {/* Giant background emoji (watermark style) */}
      <div style={{
        position: 'absolute',
        top: '50%', left: '50%',
        transform: 'translate(-50%, -52%)',
        fontSize: emojiFontSize,
        opacity: 0.06,
        userSelect: 'none',
        filter: 'blur(2px)',
      }}>
        {sec.emoji}
      </div>

      {/* Accent top bar */}
      <div style={{
        position: 'absolute', top: 0, left: 0,
        height: 8,
        width: `${((secIdx + 1) / totalSec) * 100}%`,
        background: grad,
        transition: 'none',
      }} />

      {/* Section number */}
      <div style={{
        position: 'absolute', top: 60, left: 80,
        color: C.dimBlue, fontSize: 28, fontWeight: 600,
        letterSpacing: 3,
      }}>
        {String(secIdx + 1).padStart(2, '0')} / {String(totalSec).padStart(2, '0')}
      </div>

      {/* Logo */}
      <div style={{ position: 'absolute', top: 48, right: 60 }}>
        <Logo size={80} />
      </div>

      {/* Main content */}
      <div style={{
        position: 'absolute',
        top: '30%',
        left: 80, right: 80,
        opacity: sectionOp,
      }}>
        {/* Emoji badge */}
        <div style={{
          width: 130, height: 130, borderRadius: 32,
          background: grad,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 64,
          boxShadow: `0 16px 48px rgba(64,64,242,0.55)`,
          marginBottom: 48,
          transform: `scale(${0.5 + titleSp * 0.5})`,
          opacity: titleSp,
        }}>
          {sec.emoji}
        </div>

        {/* Title */}
        <div style={{
          fontSize: 96, fontWeight: 900,
          letterSpacing: -2, lineHeight: 1.05,
          transform: `translateY(${(1 - titleSp) * 50}px)`,
          opacity: titleSp,
        }}>
          <GradientText>{sec.title}</GradientText>
        </div>

        {/* Body */}
        <div style={{
          color: C.offWhite, fontSize: 42, fontWeight: 400,
          lineHeight: 1.5, marginTop: 32,
          transform: `translateY(${(1 - bodySp) * 40}px)`,
          opacity: bodySp,
        }}>
          {sec.body}
        </div>

        {/* Accent line */}
        <div style={{
          marginTop: 48,
          height: 5, borderRadius: 3,
          width: `${barSp * 200}px`,
          background: sec.accent,
          boxShadow: `0 0 20px ${sec.accent}`,
        }} />
      </div>

      {/* Progress dots */}
      <div style={{
        position: 'absolute',
        bottom: 180,
        left: 0, right: 0,
        display: 'flex', justifyContent: 'center', gap: 16,
      }}>
        {sections.map((_, i) => (
          <div key={i} style={{
            width: i === secIdx ? 40 : 12,
            height: 12, borderRadius: 6,
            background: i === secIdx ? C.gradA : 'rgba(120, 150, 220, 0.4)',
            transition: 'none',
          }} />
        ))}
      </div>

      {/* Final CTA after last section */}
      {frame > (sections.length - 1) * SEC_FRAMES + 60 && (
        <div style={{
          position: 'absolute', bottom: 90, left: 80, right: 80,
          opacity: interpolate(
            frame,
            [(sections.length - 1) * SEC_FRAMES + 60, (sections.length - 1) * SEC_FRAMES + 84],
            [0, 1], { extrapolateRight: 'clamp' }
          ),
        }}>
          <GradientButton>All this. Free. August 2026.</GradientButton>
        </div>
      )}
    </AbsoluteFill>
  );
};
