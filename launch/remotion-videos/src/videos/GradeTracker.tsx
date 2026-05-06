import React from 'react';
import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
  interpolate, spring,
} from 'remotion';
import { C, grad, GlassCard, GradientButton, GradientText, AnimatedBg, Logo } from '../shared/Brand';

const ft = { fontFamily: "'Arial', sans-serif" };

const courses = [
  { code: 'CS 2211',   pct: 0.87, color: C.gradA,  label: '87%' },
  { code: 'MATH 1600', pct: 0.72, color: C.orange,  label: '72%' },
  { code: 'BIOL 1290', pct: 0.91, color: C.gradB,   label: '91%' },
];

const Ring: React.FC<{
  cx: number; cy: number; r: number;
  pct: number; color: string; label: string; code: string; opacity: number;
}> = ({ cx, cy, r, pct, color, label, code, opacity }) => {
  const size = (r + 30) * 2;
  const stroke = 20;
  const c = r;
  const circumference = 2 * Math.PI * r;
  const dash = circumference * pct;
  const gap  = circumference * (1 - pct);

  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      opacity,
      transform: `scale(${0.4 + opacity * 0.6})`,
    }}>
      <svg width={size} height={size} style={{ overflow: 'visible' }}>
        {/* Track */}
        <circle
          cx={c} cy={c} r={r}
          fill="none"
          stroke="rgba(21,34,72,0.9)"
          strokeWidth={stroke}
        />
        {/* Fill */}
        <circle
          cx={c} cy={c} r={r}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={`${dash} ${gap}`}
          strokeDashoffset={circumference * 0.25}
          style={{ filter: `drop-shadow(0 0 12px ${color})` }}
        />
        {/* Label */}
        <text
          x={c} y={c - 10}
          textAnchor="middle"
          fill="white"
          fontSize={44} fontWeight="900"
          fontFamily="Arial, sans-serif"
        >
          {label}
        </text>
      </svg>
      <div style={{ color: C.dimBlue, fontSize: 24, fontWeight: 600, marginTop: 8, letterSpacing: 1 }}>
        {code}
      </div>
    </div>
  );
};

export const GradeTracker: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Hook (0→36)
  const hookOp = interpolate(frame, [0, 20, 96, 120], [0, 1, 1, 0], { extrapolateRight: 'clamp' });

  // Rings appear (96→216)
  const ringOpacity = courses.map((_, i) =>
    spring({ frame: frame - (96 + i * 28), fps, config: { damping: 200, stiffness: 160 } })
  );

  // Animated percentages count up
  const ringPcts = courses.map((c, i) =>
    interpolate(frame, [96 + i * 28, 180 + i * 28], [0, c.pct], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: (t) => 1 - Math.pow(1 - t, 3),
    })
  );

  // GPA counter
  const gpaOp = interpolate(frame, [240, 264], [0, 1], { extrapolateRight: 'clamp' });
  const gpaVal = interpolate(frame, [240, 312], [0, 3.7], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: (t) => 1 - Math.pow(1 - t, 3),
  });

  return (
    <AbsoluteFill style={{ ...ft, overflow: 'hidden' }}>
      <AnimatedBg frame={frame} />

      {/* Hook */}
      <div style={{
        position: 'absolute', top: 240, left: 0, right: 0,
        textAlign: 'center', opacity: hookOp,
      }}>
        <div style={{ color: C.white, fontSize: 80, fontWeight: 900, letterSpacing: -2 }}>
          Know your grade.
        </div>
        <div style={{ fontSize: 76, fontWeight: 900, letterSpacing: -2, marginTop: 8 }}>
          <GradientText>Before it's too late.</GradientText>
        </div>
      </div>

      {/* Grade rings */}
      <div style={{
        position: 'absolute', top: 560, left: 0, right: 0,
        display: 'flex', justifyContent: 'space-around', paddingLeft: 40, paddingRight: 40,
      }}>
        {courses.map((c, i) => (
          <Ring
            key={c.code}
            cx={0} cy={0} r={110}
            pct={ringPcts[i]}
            color={c.color}
            label={`${Math.round(ringPcts[i] * 100)}%`}
            code={c.code}
            opacity={ringOpacity[i]}
          />
        ))}
      </div>

      {/* GPA summary card */}
      {frame > 240 && (
        <GlassCard style={{
          position: 'absolute', top: 1060, left: 100, right: 100,
          padding: '40px 50px',
          opacity: gpaOp,
          transform: `translateY(${interpolate(frame, [240, 264], [40, 0], { extrapolateRight: 'clamp' })}px)`,
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        }}>
          <div>
            <div style={{ color: C.dimBlue, fontSize: 28, fontWeight: 500, marginBottom: 8 }}>
              Current GPA
            </div>
            <div style={{
              fontSize: 88, fontWeight: 900, letterSpacing: -2,
              background: grad, WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent', backgroundClip: 'text',
            }}>
              {gpaVal.toFixed(1)}
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ color: C.offWhite, fontSize: 32, fontWeight: 500 }}>
              Target: 3.8
            </div>
            <div style={{
              marginTop: 12, padding: '10px 24px', borderRadius: 30,
              background: 'rgba(91, 158, 248, 0.15)',
              border: '1px solid rgba(91,158,248,0.3)',
              color: C.gradA, fontSize: 26, fontWeight: 600,
            }}>
              +0.1 to go 🎯
            </div>
          </div>
        </GlassCard>
      )}

      {/* Live update badge */}
      {frame > 288 && (
        <div style={{
          position: 'absolute', top: 1330, left: 0, right: 0,
          textAlign: 'center',
          opacity: interpolate(frame, [288, 312], [0, 1], { extrapolateRight: 'clamp' }),
        }}>
          <div style={{ color: C.dimBlue, fontSize: 30, fontWeight: 400 }}>
            Updates after every grade entry
          </div>
        </div>
      )}

      {/* CTA */}
      {frame > 312 && (
        <div style={{
          position: 'absolute', bottom: 100, left: 80, right: 80,
          opacity: interpolate(frame, [312, 336], [0, 1], { extrapolateRight: 'clamp' }),
          transform: `translateY(${interpolate(frame, [312, 336], [40, 0], { extrapolateRight: 'clamp' })}px)`,
        }}>
          <GradientButton>Track Your GPA Free →</GradientButton>
        </div>
      )}

      <div style={{ position: 'absolute', top: 60, right: 60 }}>
        <Logo size={80} />
      </div>
    </AbsoluteFill>
  );
};
