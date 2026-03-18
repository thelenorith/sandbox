import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
  ScrollView,
} from 'react-native';
import { COLORS, SPACING, BORDER_RADIUS, FONTS } from '../constants/theme';
import { getLevelTitle } from '../engine/GameState';
import { SMASH_OBJECTS } from '../constants/objects';

interface StatsScreenProps {
  navigation: any;
}

export const StatsScreen: React.FC<StatsScreenProps> = ({ navigation }) => {
  // In a real app these would come from persistent storage
  const stats = {
    totalSmashes: 0,
    totalObjectsDestroyed: 0,
    favoriteObject: null as string | null,
    biggestCombo: 0,
    level: 1,
    xp: 0,
    xpToNextLevel: 100,
    totalTimePlayed: '0m',
  };

  const achievements = [
    { emoji: '👊', name: 'First Blood', desc: 'Smash your first object', unlocked: false },
    { emoji: '💯', name: 'Century', desc: 'Destroy 100 objects', unlocked: false },
    { emoji: '⚡', name: 'Speed Demon', desc: 'Get a 5x combo', unlocked: false },
    { emoji: '🔨', name: 'Hammer Time', desc: 'Unlock the hammer', unlocked: false },
    { emoji: '🏏', name: 'Batter Up', desc: 'Unlock the baseball bat', unlocked: false },
    { emoji: '⚒️', name: 'Sledge Lord', desc: 'Unlock the sledgehammer', unlocked: false },
    { emoji: '💻', name: 'Tech Wrecker', desc: 'Destroy all electronics', unlocked: false },
    { emoji: '🏆', name: 'Completionist', desc: 'Destroy every object type', unlocked: false },
    { emoji: '👑', name: 'God Mode', desc: 'Reach level 20', unlocked: false },
    { emoji: '🔥', name: 'Unstoppable', desc: '10x combo', unlocked: false },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Destruction Stats</Text>
        <View style={{ width: 60 }} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* Level Card */}
        <View style={styles.levelCard}>
          <View style={styles.levelBadgeLarge}>
            <Text style={styles.levelNumberLarge}>{stats.level}</Text>
          </View>
          <Text style={styles.levelTitleLarge}>{getLevelTitle(stats.level)}</Text>
          <View style={styles.xpBarLarge}>
            <View
              style={[
                styles.xpFillLarge,
                { width: `${(stats.xp / stats.xpToNextLevel) * 100}%` },
              ]}
            />
          </View>
          <Text style={styles.xpTextLarge}>
            {stats.xp} / {stats.xpToNextLevel} XP to next level
          </Text>
        </View>

        {/* Stats Grid */}
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Text style={styles.statEmoji}>👊</Text>
            <Text style={styles.statValue}>{stats.totalSmashes}</Text>
            <Text style={styles.statLabel}>Total Hits</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statEmoji}>💥</Text>
            <Text style={styles.statValue}>{stats.totalObjectsDestroyed}</Text>
            <Text style={styles.statLabel}>Destroyed</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statEmoji}>🔥</Text>
            <Text style={styles.statValue}>{stats.biggestCombo}x</Text>
            <Text style={styles.statLabel}>Best Combo</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statEmoji}>⏱️</Text>
            <Text style={styles.statValue}>{stats.totalTimePlayed}</Text>
            <Text style={styles.statLabel}>Time Played</Text>
          </View>
        </View>

        {/* Achievements */}
        <Text style={styles.sectionTitle}>Achievements</Text>
        <View style={styles.achievementsGrid}>
          {achievements.map((ach, i) => (
            <View
              key={i}
              style={[styles.achievementCard, !ach.unlocked && styles.achievementLocked]}
            >
              <Text style={styles.achievementEmoji}>
                {ach.unlocked ? ach.emoji : '🔒'}
              </Text>
              <Text style={styles.achievementName}>{ach.name}</Text>
              <Text style={styles.achievementDesc}>{ach.desc}</Text>
            </View>
          ))}
        </View>

        {/* Object catalog progress */}
        <Text style={styles.sectionTitle}>Smash Catalog</Text>
        <View style={styles.catalogGrid}>
          {SMASH_OBJECTS.map((obj) => (
            <View key={obj.id} style={styles.catalogItem}>
              <Text style={styles.catalogEmoji}>{obj.emoji}</Text>
              <Text style={styles.catalogName}>{obj.name}</Text>
            </View>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.md,
  },
  backButton: {
    padding: SPACING.sm,
  },
  backText: {
    color: COLORS.textSecondary,
    fontSize: 16,
    fontWeight: '600',
  },
  headerTitle: {
    ...FONTS.heading,
    color: COLORS.text,
    fontSize: 22,
  },
  content: {
    padding: SPACING.md,
    paddingBottom: SPACING.xxl,
  },
  levelCard: {
    backgroundColor: COLORS.surface,
    borderRadius: BORDER_RADIUS.lg,
    padding: SPACING.xl,
    alignItems: 'center',
    marginBottom: SPACING.lg,
    borderWidth: 1,
    borderColor: COLORS.primary,
  },
  levelBadgeLarge: {
    width: 70,
    height: 70,
    borderRadius: 35,
    backgroundColor: COLORS.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: SPACING.sm,
  },
  levelNumberLarge: {
    color: COLORS.text,
    fontSize: 28,
    fontWeight: '900',
  },
  levelTitleLarge: {
    color: COLORS.text,
    fontSize: 20,
    fontWeight: '800',
    marginBottom: SPACING.sm,
  },
  xpBarLarge: {
    width: '80%',
    height: 8,
    backgroundColor: 'rgba(255,255,255,0.15)',
    borderRadius: 4,
    overflow: 'hidden',
  },
  xpFillLarge: {
    height: '100%',
    backgroundColor: COLORS.accent,
    borderRadius: 4,
  },
  xpTextLarge: {
    color: COLORS.textMuted,
    fontSize: 12,
    marginTop: SPACING.xs,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.sm,
    marginBottom: SPACING.lg,
  },
  statCard: {
    width: '48%',
    backgroundColor: COLORS.surface,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.md,
    alignItems: 'center',
    flexGrow: 1,
    flexBasis: '45%',
  },
  statEmoji: {
    fontSize: 28,
    marginBottom: SPACING.xs,
  },
  statValue: {
    color: COLORS.text,
    fontSize: 28,
    fontWeight: '900',
  },
  statLabel: {
    color: COLORS.textMuted,
    fontSize: 12,
    fontWeight: '600',
    marginTop: 2,
  },
  sectionTitle: {
    color: COLORS.text,
    fontSize: 20,
    fontWeight: '800',
    marginBottom: SPACING.md,
  },
  achievementsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.sm,
    marginBottom: SPACING.lg,
  },
  achievementCard: {
    width: '48%',
    backgroundColor: COLORS.surface,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.md,
    alignItems: 'center',
    flexGrow: 1,
    flexBasis: '45%',
  },
  achievementLocked: {
    opacity: 0.4,
  },
  achievementEmoji: {
    fontSize: 24,
    marginBottom: 4,
  },
  achievementName: {
    color: COLORS.text,
    fontSize: 13,
    fontWeight: '700',
    textAlign: 'center',
  },
  achievementDesc: {
    color: COLORS.textMuted,
    fontSize: 11,
    textAlign: 'center',
    marginTop: 2,
  },
  catalogGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.sm,
  },
  catalogItem: {
    backgroundColor: COLORS.surface,
    borderRadius: BORDER_RADIUS.sm,
    padding: SPACING.sm,
    alignItems: 'center',
    width: 80,
  },
  catalogEmoji: {
    fontSize: 28,
  },
  catalogName: {
    color: COLORS.textMuted,
    fontSize: 9,
    textAlign: 'center',
    marginTop: 2,
  },
});
