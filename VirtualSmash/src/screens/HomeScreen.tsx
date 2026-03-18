import React, { useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
  Dimensions,
  SafeAreaView,
} from 'react-native';
import { COLORS, FONTS, SPACING, BORDER_RADIUS } from '../constants/theme';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

interface HomeScreenProps {
  navigation: any;
}

export const HomeScreen: React.FC<HomeScreenProps> = ({ navigation }) => {
  const titleScale = useRef(new Animated.Value(0.5)).current;
  const titleOpacity = useRef(new Animated.Value(0)).current;
  const buttonSlide = useRef(new Animated.Value(100)).current;
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const bgParticles = useRef(
    Array.from({ length: 15 }).map(() => ({
      x: new Animated.Value(Math.random() * SCREEN_WIDTH),
      y: new Animated.Value(Math.random() * 800),
      opacity: new Animated.Value(Math.random() * 0.3 + 0.1),
    }))
  ).current;

  useEffect(() => {
    // Title entrance
    Animated.parallel([
      Animated.spring(titleScale, {
        toValue: 1,
        friction: 4,
        tension: 100,
        useNativeDriver: true,
      }),
      Animated.timing(titleOpacity, {
        toValue: 1,
        duration: 600,
        useNativeDriver: true,
      }),
      Animated.timing(buttonSlide, {
        toValue: 0,
        duration: 800,
        delay: 400,
        useNativeDriver: true,
      }),
    ]).start();

    // Pulse animation for main button
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.05,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    ).start();
  }, []);

  return (
    <SafeAreaView style={styles.container}>
      {/* Background floating debris */}
      {bgParticles.map((particle, i) => (
        <Animated.View
          key={i}
          style={[
            styles.bgParticle,
            {
              left: particle.x as any,
              top: particle.y as any,
              opacity: particle.opacity as any,
            },
          ]}
        >
          <Text style={styles.bgParticleEmoji}>
            {['💥', '🔨', '💣', '⚡', '🧨', '🔥'][i % 6]}
          </Text>
        </Animated.View>
      ))}

      <View style={styles.content}>
        {/* Title */}
        <Animated.View
          style={[
            styles.titleContainer,
            {
              transform: [{ scale: titleScale }],
              opacity: titleOpacity,
            },
          ]}
        >
          <Text style={styles.titleIcon}>💥</Text>
          <Text style={styles.title}>VIRTUAL</Text>
          <Text style={styles.titleAccent}>SMASH</Text>
          <Text style={styles.subtitle}>Break stuff. Feel better.</Text>
        </Animated.View>

        {/* Buttons */}
        <Animated.View
          style={[
            styles.buttonsContainer,
            { transform: [{ translateY: buttonSlide }] },
          ]}
        >
          <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
            <TouchableOpacity
              style={styles.smashButton}
              onPress={() => navigation.navigate('ObjectSelect')}
              activeOpacity={0.8}
            >
              <Text style={styles.smashButtonEmoji}>👊</Text>
              <Text style={styles.smashButtonText}>START SMASHING</Text>
            </TouchableOpacity>
          </Animated.View>

          <TouchableOpacity
            style={styles.quickSmashButton}
            onPress={() => navigation.navigate('Arena', { objectId: null })}
            activeOpacity={0.8}
          >
            <Text style={styles.quickSmashEmoji}>⚡</Text>
            <Text style={styles.quickSmashText}>Quick Smash (Random)</Text>
          </TouchableOpacity>

          <View style={styles.secondaryButtons}>
            <TouchableOpacity
              style={styles.secondaryButton}
              onPress={() => navigation.navigate('Stats')}
              activeOpacity={0.8}
            >
              <Text style={styles.secondaryEmoji}>📊</Text>
              <Text style={styles.secondaryText}>Stats</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.secondaryButton}
              onPress={() => navigation.navigate('Settings')}
              activeOpacity={0.8}
            >
              <Text style={styles.secondaryEmoji}>⚙️</Text>
              <Text style={styles.secondaryText}>Settings</Text>
            </TouchableOpacity>
          </View>
        </Animated.View>

        {/* Tagline */}
        <Text style={styles.tagline}>
          No objects were harmed in real life. 😈
        </Text>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  bgParticle: {
    position: 'absolute',
  },
  bgParticleEmoji: {
    fontSize: 24,
    opacity: 0.15,
  },
  content: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: SPACING.lg,
  },
  titleContainer: {
    alignItems: 'center',
    marginBottom: SPACING.xxl,
  },
  titleIcon: {
    fontSize: 64,
    marginBottom: SPACING.sm,
  },
  title: {
    fontSize: 48,
    fontWeight: '900',
    color: COLORS.text,
    letterSpacing: 6,
  },
  titleAccent: {
    fontSize: 56,
    fontWeight: '900',
    color: COLORS.primary,
    letterSpacing: 8,
    marginTop: -8,
  },
  subtitle: {
    fontSize: 16,
    color: COLORS.textSecondary,
    marginTop: SPACING.sm,
    fontStyle: 'italic',
  },
  buttonsContainer: {
    width: '100%',
    alignItems: 'center',
  },
  smashButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.primary,
    paddingVertical: SPACING.lg,
    paddingHorizontal: SPACING.xxl,
    borderRadius: BORDER_RADIUS.xl,
    width: SCREEN_WIDTH * 0.85,
    elevation: 8,
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 12,
  },
  smashButtonEmoji: {
    fontSize: 28,
    marginRight: SPACING.sm,
  },
  smashButtonText: {
    ...FONTS.button,
    color: COLORS.text,
    fontSize: 20,
  },
  quickSmashButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.surfaceLight,
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.xl,
    borderRadius: BORDER_RADIUS.lg,
    marginTop: SPACING.md,
    width: SCREEN_WIDTH * 0.85,
    borderWidth: 1,
    borderColor: COLORS.accent,
  },
  quickSmashEmoji: {
    fontSize: 20,
    marginRight: SPACING.sm,
  },
  quickSmashText: {
    color: COLORS.accent,
    fontSize: 16,
    fontWeight: '600',
  },
  secondaryButtons: {
    flexDirection: 'row',
    marginTop: SPACING.lg,
    gap: SPACING.md,
  },
  secondaryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.surface,
    paddingVertical: SPACING.sm,
    paddingHorizontal: SPACING.lg,
    borderRadius: BORDER_RADIUS.md,
  },
  secondaryEmoji: {
    fontSize: 18,
    marginRight: SPACING.xs,
  },
  secondaryText: {
    color: COLORS.textSecondary,
    fontSize: 14,
    fontWeight: '600',
  },
  tagline: {
    position: 'absolute',
    bottom: 30,
    color: COLORS.textMuted,
    fontSize: 12,
  },
});
