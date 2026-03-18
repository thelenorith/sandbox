import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
  Dimensions,
} from 'react-native';
import { SMASH_OBJECTS, CATEGORIES, SmashObject } from '../constants/objects';
import { COLORS, SPACING, BORDER_RADIUS, FONTS } from '../constants/theme';

const { width: SCREEN_WIDTH } = Dimensions.get('window');
const CARD_WIDTH = (SCREEN_WIDTH - SPACING.lg * 2 - SPACING.md) / 2;

interface ObjectSelectScreenProps {
  navigation: any;
  route: any;
}

export const ObjectSelectScreen: React.FC<ObjectSelectScreenProps> = ({ navigation }) => {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const playerLevel = 10; // TODO: get from game state

  const filteredObjects =
    selectedCategory === 'all'
      ? SMASH_OBJECTS
      : SMASH_OBJECTS.filter((obj) => obj.category === selectedCategory);

  const renderObjectCard = (object: SmashObject) => {
    const isLocked = object.unlockLevel > playerLevel;

    return (
      <TouchableOpacity
        key={object.id}
        style={[styles.card, isLocked && styles.cardLocked]}
        onPress={() => !isLocked && navigation.navigate('Arena', { objectId: object.id })}
        activeOpacity={isLocked ? 1 : 0.7}
      >
        <View style={[styles.cardInner, { borderColor: object.color }]}>
          {isLocked && (
            <View style={styles.lockOverlay}>
              <Text style={styles.lockEmoji}>🔒</Text>
              <Text style={styles.lockText}>Level {object.unlockLevel}</Text>
            </View>
          )}

          <Text style={styles.cardEmoji}>{object.emoji}</Text>
          <Text style={styles.cardName}>{object.name}</Text>

          {/* Satisfaction stars */}
          <View style={styles.starsRow}>
            {Array.from({ length: 5 }).map((_, i) => (
              <Text key={i} style={styles.star}>
                {i < object.satisfactionRating ? '⭐' : '☆'}
              </Text>
            ))}
          </View>

          {/* Info row */}
          <View style={styles.infoRow}>
            <View style={styles.infoBadge}>
              <Text style={styles.infoText}>HP: {object.hitPoints}</Text>
            </View>
            <View style={[styles.infoBadge, styles.categoryBadge]}>
              <Text style={styles.infoText}>{object.category}</Text>
            </View>
          </View>

          <Text style={styles.cardDescription} numberOfLines={2}>
            {object.description}
          </Text>
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Choose Your Target</Text>
        <View style={{ width: 60 }} />
      </View>

      {/* Category filter */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.categoryScroll}
        contentContainerStyle={styles.categoryContainer}
      >
        {CATEGORIES.map((cat) => (
          <TouchableOpacity
            key={cat.id}
            style={[
              styles.categoryChip,
              selectedCategory === cat.id && styles.categoryChipActive,
            ]}
            onPress={() => setSelectedCategory(cat.id)}
          >
            <Text style={styles.categoryEmoji}>{cat.emoji}</Text>
            <Text
              style={[
                styles.categoryText,
                selectedCategory === cat.id && styles.categoryTextActive,
              ]}
            >
              {cat.name}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Object grid */}
      <ScrollView
        contentContainerStyle={styles.grid}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.gridRow}>
          {filteredObjects.map((obj) => renderObjectCard(obj))}
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
  categoryScroll: {
    maxHeight: 50,
  },
  categoryContainer: {
    paddingHorizontal: SPACING.md,
    gap: SPACING.sm,
    flexDirection: 'row',
  },
  categoryChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.surface,
    paddingVertical: SPACING.xs,
    paddingHorizontal: SPACING.md,
    borderRadius: BORDER_RADIUS.round,
    borderWidth: 1,
    borderColor: 'transparent',
  },
  categoryChipActive: {
    backgroundColor: COLORS.surfaceLight,
    borderColor: COLORS.primary,
  },
  categoryEmoji: {
    fontSize: 16,
    marginRight: 4,
  },
  categoryText: {
    color: COLORS.textSecondary,
    fontSize: 13,
    fontWeight: '600',
  },
  categoryTextActive: {
    color: COLORS.text,
  },
  grid: {
    padding: SPACING.md,
  },
  gridRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.md,
  },
  card: {
    width: CARD_WIDTH,
    marginBottom: SPACING.sm,
  },
  cardLocked: {
    opacity: 0.5,
  },
  cardInner: {
    backgroundColor: COLORS.surface,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.md,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: COLORS.surface,
  },
  lockOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.6)',
    borderRadius: BORDER_RADIUS.md,
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 10,
  },
  lockEmoji: {
    fontSize: 30,
  },
  lockText: {
    color: COLORS.textMuted,
    fontSize: 12,
    fontWeight: '700',
    marginTop: 4,
  },
  cardEmoji: {
    fontSize: 48,
    marginBottom: SPACING.xs,
  },
  cardName: {
    color: COLORS.text,
    fontSize: 14,
    fontWeight: '700',
    textAlign: 'center',
  },
  starsRow: {
    flexDirection: 'row',
    marginVertical: 4,
  },
  star: {
    fontSize: 10,
  },
  infoRow: {
    flexDirection: 'row',
    gap: 4,
    marginVertical: 4,
  },
  infoBadge: {
    backgroundColor: 'rgba(255,255,255,0.1)',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  categoryBadge: {
    backgroundColor: 'rgba(233, 69, 96, 0.2)',
  },
  infoText: {
    color: COLORS.textMuted,
    fontSize: 10,
    fontWeight: '600',
  },
  cardDescription: {
    color: COLORS.textMuted,
    fontSize: 11,
    textAlign: 'center',
    marginTop: 4,
    lineHeight: 15,
  },
});
