import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Particle, CrackLine } from '../engine/ParticleSystem';

interface ParticleRendererProps {
  particles: Particle[];
  cracks: CrackLine[];
}

export const ParticleRenderer: React.FC<ParticleRendererProps> = ({ particles, cracks }) => {
  return (
    <View style={StyleSheet.absoluteFill} pointerEvents="none">
      {/* Render crack lines as thin views */}
      {cracks.map((crack) =>
        crack.points.slice(1).map((point, idx) => {
          const prev = crack.points[idx];
          const dx = point.x - prev.x;
          const dy = point.y - prev.y;
          const length = Math.sqrt(dx * dx + dy * dy);
          const angle = Math.atan2(dy, dx) * (180 / Math.PI);

          return (
            <View
              key={`crack-${crack.id}-${idx}`}
              style={{
                position: 'absolute',
                left: prev.x,
                top: prev.y,
                width: length,
                height: crack.width,
                backgroundColor: `rgba(30, 30, 30, ${crack.opacity})`,
                transform: [{ rotate: `${angle}deg` }],
                transformOrigin: 'left center',
              }}
            />
          );
        })
      )}

      {/* Render particles */}
      {particles.map((p) => {
        const style: any = {
          position: 'absolute' as const,
          left: p.x - p.size / 2,
          top: p.y - p.size / 2,
          width: p.size,
          height: p.size,
          backgroundColor: p.color,
          opacity: p.opacity,
          transform: [{ rotate: `${p.rotation}deg` }],
        };

        if (p.shape === 'circle') {
          style.borderRadius = p.size / 2;
        } else if (p.shape === 'triangle') {
          style.width = 0;
          style.height = 0;
          style.backgroundColor = 'transparent';
          style.borderLeftWidth = p.size / 2;
          style.borderRightWidth = p.size / 2;
          style.borderBottomWidth = p.size;
          style.borderLeftColor = 'transparent';
          style.borderRightColor = 'transparent';
          style.borderBottomColor = p.color;
          style.opacity = p.opacity;
        }

        // Glow effect for sparks
        if (p.type === 'spark') {
          style.shadowColor = p.color;
          style.shadowOffset = { width: 0, height: 0 };
          style.shadowOpacity = 1;
          style.shadowRadius = 4;
        }

        return <View key={p.id} style={style} />;
      })}
    </View>
  );
};
