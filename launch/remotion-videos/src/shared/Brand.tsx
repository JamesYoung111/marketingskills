import React from 'react';

export const C = {
  darkBg:   '#0A1628',
  cardBg:   'rgba(21, 34, 72, 0.85)',
  gradA:    '#5B9EF8',
  gradB:    '#4040F2',
  midBlue:  '#4D6FF5',
  orange:   '#F59E0B',
  white:    '#FFFFFF',
  offWhite: '#D2E4FF',
  dimBlue:  '#7896DC',
  danger:   'rgba(220, 50, 60, 0.85)',
};

export const grad = `linear-gradient(135deg, ${C.gradA} 0%, ${C.gradB} 100%)`;

export const Logo: React.FC<{ size?: number }> = ({ size = 80 }) => (
  <svg width={size} height={size} viewBox="0 0 80 80" style={{ flexShrink: 0 }}>
    <defs>
      <linearGradient id="lg" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stopColor={C.gradA} />
        <stop offset="100%" stopColor={C.gradB} />
      </linearGradient>
    </defs>
    <rect width="80" height="80" rx="16" fill="url(#lg)" />
    {/* Graduation cap (diamond) */}
    <polygon points="40,14 60,34 40,54 20,34" fill="white" />
    {/* Envelope body */}
    <rect x="22" y="50" width="36" height="22" rx="3" fill="white" />
    {/* V-notch on envelope */}
    <polygon points="22,50 40,64 58,50" fill="url(#lg)" />
  </svg>
);

export const GlassCard: React.FC<{
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ children, style }) => (
  <div style={{
    background: C.cardBg,
    border: `1px solid rgba(91, 158, 248, 0.18)`,
    borderRadius: 24,
    boxShadow: '0 8px 32px rgba(64, 64, 242, 0.2), inset 0 1px 0 rgba(255,255,255,0.06)',
    backdropFilter: 'blur(20px)',
    ...style,
  }}>
    {children}
  </div>
);

export const GradientButton: React.FC<{
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ children, style }) => (
  <div style={{
    background: grad,
    borderRadius: 60,
    padding: '26px 64px',
    color: C.white,
    fontWeight: 800,
    fontSize: 36,
    textAlign: 'center',
    boxShadow: `0 12px 48px rgba(64, 64, 242, 0.55)`,
    letterSpacing: -0.5,
    ...style,
  }}>
    {children}
  </div>
);

export const GradientText: React.FC<{
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ children, style }) => (
  <span style={{
    background: grad,
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
    ...style,
  }}>
    {children}
  </span>
);

export const AnimatedBg: React.FC<{ frame: number; darkOverlay?: number }> = ({
  frame,
  darkOverlay = 0,
}) => {
  const glow1X = Math.sin(frame * 0.005) * 80;
  const glow1Y = Math.cos(frame * 0.003) * 60;
  const glow2X = Math.cos(frame * 0.004) * 60;

  return (
    <div style={{ position: 'absolute', inset: 0, background: C.darkBg, overflow: 'hidden' }}>
      {/* Primary glow – top-left */}
      <div style={{
        position: 'absolute',
        top: -200 + glow1Y,
        left: -150 + glow1X,
        width: 900,
        height: 900,
        background: `radial-gradient(circle, rgba(64,64,242,0.38) 0%, transparent 65%)`,
      }} />
      {/* Secondary glow – bottom-right */}
      <div style={{
        position: 'absolute',
        bottom: -200,
        right: -100 + glow2X,
        width: 700,
        height: 700,
        background: `radial-gradient(circle, rgba(91,158,248,0.28) 0%, transparent 65%)`,
      }} />
      {/* Subtle grid */}
      <div style={{
        position: 'absolute',
        inset: 0,
        backgroundImage: `linear-gradient(rgba(91,158,248,0.04) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(91,158,248,0.04) 1px, transparent 1px)`,
        backgroundSize: '80px 80px',
      }} />
      {darkOverlay > 0 && (
        <div style={{
          position: 'absolute',
          inset: 0,
          background: `rgba(10,22,40,${darkOverlay})`,
        }} />
      )}
    </div>
  );
};
