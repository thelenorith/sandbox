import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import { COLORS, SPACING } from '../constants/theme';
import { GameStats, getLevelTitle } from '../engine/GameState';

interface DestructionCounterProps {
  stats: GameStats;
  combo: number;
}

export const DestructionCounter: React.FC<DestructionCounterProps> = ({ stats, combo }) => {
  const comboScale = useRef(new Animated.Value(1)).current;
  const comboPulse = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (combo > 1) {
      Animated.sequence([
        Animated.spring(comboScale, {
          toValue: 1.4,
          friction: 3,
          tension: 200,
          useNativeDriver: true,
        }),
        Animated.spring(comboScale, {
          toValue: 1,
          friction: 5,
          useNativeDriver: true,
        }),
      ]).start();
    }
  }, [combo]);

  const xpProgress = stats.xp / stats.xpToNextLevel;

  return (
    <View style={styles.container}>
      <View style={styles.levelRow}>
        <View style={styles.levelBadge}>
          <Text style={styles.levelNumber}>{stats.level}</Text>
        </View>
        <View style={styles.levelInfo}>
          <Text style={styles.levelTitle}>{getLevelTitle(stats.level)}</Text>
          <View style={styles.xpBar}>
            <View style={[styles.xpFill, { width: `${xpProgress * 100}%` }]} />
          </View>
          <Text style={styles.xpText}>
            {stats.xp} / {stats.xpToNextLevel} XP
          </Text>
        </View>
      </View>

      <View style={styles.statsRow}>
        <View style={styles.statItem}>
          <Text style={styles.statValue}>{stats.totalSmashes}</Text>
          <Text style={styles.statLabel}>HITS</Text>
        </View>
        <View style={styles.statDivider} />
        <View style={styles.statItem}>
          <Text style={styles.statValue}>{stats.totalObjectsDestroyed}</Text>
          <Text style={styles.statLabel}>DESTROYED</Text>
        </View>
        <View style={styles.statDivider} />
        <View style={styles.statItem}>
          <Text style={styles.statValue}>{stats.biggestCombo}x</Text>
          <Text style={styles.statLabel}>BEST COMBO</Text>
        </View>
      </View>

      {combo > 1 && (
        <Animated.View style={[styles.comboContainer, { transform: [{ scale: comboScale }] }]}>
          <Text style={styles.comboText}>{combo}x COMBO!</Text>
          <Text style={styles.comboBonus}>+{combo * 10} XP BONUS</Text>
        </Animated.View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: SPACING.md,
  },
  levelRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.sm,
  },
  levelBadge: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: COLORS.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: SPACING.sm,
  },
  levelNumber: {
    color: COLORS.text,
    fontSize: 18,
    fontWeight: '900',
  },
  levelInfo: {
    flex: 1,
  },
  levelTitle: {
    color: COLORS.text,
    fontSize: 14,
    fontWeight: '700',
    marginBottom: 4,
  },
  xpBar: {
    height: 4,
    backgroundColor: 'rgba(255,255,255,0.15)',
    borderRadius: 2,
    overflow: 'hidden',
  },
  xpFill: {
    height: '100%',
    backgroundColor: COLORS.accent,
    borderRadius: 2,
  },
  xpText: {
    color: COLORS.textMuted,
    fontSize: 10,
    marginTop: 2,
  },
  statsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.surface,
    borderRadius: 12,
    paddingVertical: SPACING.sm,
    paddingHorizontal: SPACING.md,
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statValue: {
    color: COLORS.text,
    fontSize: 20,
    fontWeight: '800',
  },
  statLabel: {
    color: COLORS.textMuted,
    fontSize: 9,
    fontWeight: '700',
    letterSpacing: 1,
    marginTop: 2,
  },
  statDivider: {
    width: 1,
    height: 30,
    backgroundColor: 'rgba(255,255,255,0.1)',
  },
  comboContainer: {
    alignItems: 'center',
    marginTop: SPACING.sm,
    backgroundColor: COLORS.primary,
    borderRadius: 20,
    paddingVertical: 6,
    paddingHorizontal: 20,
    alignSelf: 'center',
  },
  comboText: {
    color: COLORS.text,
    fontSize: 22,
    fontWeight: '900',
    letterSpacing: 2,
  },
  comboBonus: {
    color: 'rgba(255,255,255,0.8)',
    fontSize: 11,
    fontWeight: '600',
  },
});
