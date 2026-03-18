import React, { useState, useCallback, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  SafeAreaView,
  TouchableOpacity,
  Animated,
} from 'react-native';
import { SMASH_OBJECTS, TOOLS, SmashObject, Tool } from '../constants/objects';
import { COLORS, SPACING, BORDER_RADIUS } from '../constants/theme';
import {
  Particle,
  CrackLine,
  createExplosion,
  createCrack,
  updateParticles,
  createImpactRipple,
} from '../engine/ParticleSystem';
import {
  GameStats,
  createInitialStats,
  recordSmash,
  recordDestroy,
  getUnlockedTools,
} from '../engine/GameState';
import { SmashableObject } from '../components/SmashableObject';
import { ParticleRenderer } from '../components/ParticleRenderer';
import { ToolSelector } from '../components/ToolSelector';
import { DestructionCounter } from '../components/DestructionCounter';
import { useHaptics } from '../hooks/useHaptics';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

interface ArenaScreenProps {
  navigation: any;
  route: any;
}

export const ArenaScreen: React.FC<ArenaScreenProps> = ({ navigation, route }) => {
  const objectId = route.params?.objectId;
  const initialObject =
    objectId
      ? SMASH_OBJECTS.find((o) => o.id === objectId) || SMASH_OBJECTS[0]
      : SMASH_OBJECTS[Math.floor(Math.random() * SMASH_OBJECTS.length)];

  const [currentObject, setCurrentObject] = useState<SmashObject>(initialObject);
  const [currentHP, setCurrentHP] = useState(initialObject.hitPoints);
  const [isDestroyed, setIsDestroyed] = useState(false);
  const [particles, setParticles] = useState<Particle[]>([]);
  const [cracks, setCracks] = useState<CrackLine[]>([]);
  const [selectedTool, setSelectedTool] = useState<Tool>(TOOLS[0]);
  const [stats, setStats] = useState<GameStats>(createInitialStats());
  const [combo, setCombo] = useState(0);
  const [showDestroyedMessage, setShowDestroyedMessage] = useState(false);
  const [screenShake, setScreenShake] = useState(false);

  const haptics = useHaptics();
  const animFrame = useRef<number | null>(null);
  const destroyedScale = useRef(new Animated.Value(0)).current;
  const shakeX = useRef(new Animated.Value(0)).current;

  // Particle animation loop
  useEffect(() => {
    let running = true;

    const tick = () => {
      if (!running) return;
      setParticles((prev) => {
        if (prev.length === 0) return prev;
        return updateParticles(prev);
      });
      animFrame.current = requestAnimationFrame(tick);
    };

    animFrame.current = requestAnimationFrame(tick);
    return () => {
      running = false;
      if (animFrame.current) cancelAnimationFrame(animFrame.current);
    };
  }, []);

  const handleSmash = useCallback(
    (x: number, y: number) => {
      if (isDestroyed) return;

      const damage = selectedTool.damage;
      const newHP = Math.max(0, currentHP - damage);

      // Haptic feedback
      haptics.smash(damage);

      // Screen shake
      Animated.sequence([
        Animated.timing(shakeX, { toValue: damage * 3, duration: 30, useNativeDriver: true }),
        Animated.timing(shakeX, { toValue: -damage * 3, duration: 30, useNativeDriver: true }),
        Animated.timing(shakeX, { toValue: damage * 1.5, duration: 20, useNativeDriver: true }),
        Animated.timing(shakeX, { toValue: 0, duration: 20, useNativeDriver: true }),
      ]).start();

      // Create impact particles
      const impactParticles = createExplosion(
        x,
        y,
        4 + damage * 2,
        [currentObject.color, currentObject.secondaryColor, '#ffffff'],
        damage * 0.5
      );
      const ripples = createImpactRipple(x, y);
      setParticles((prev) => [...prev, ...impactParticles, ...ripples]);

      // Add cracks
      if (currentObject.hitPoints > 1) {
        const newCracks = createCrack(x, y, 150, 150);
        setCracks((prev) => [...prev, ...newCracks]);
      }

      // Update stats
      setStats((prev) => recordSmash(prev));

      if (newHP <= 0) {
        // DESTROYED!
        setIsDestroyed(true);
        setCurrentHP(0);
        haptics.destruction();

        // Big explosion
        const destroyParticles = createExplosion(
          SCREEN_WIDTH / 2,
          SCREEN_HEIGHT / 2 - 50,
          currentObject.shardCount + 10,
          [
            currentObject.color,
            currentObject.secondaryColor,
            COLORS.destructionRed,
            COLORS.destructionOrange,
            COLORS.destructionYellow,
            '#ffffff',
          ],
          2
        );
        setParticles((prev) => [...prev, ...destroyParticles]);

        // Update stats
        setStats((prev) => recordDestroy(prev, currentObject.id));
        setCombo((prev) => prev + 1);

        // Show destroyed message
        setShowDestroyedMessage(true);
        Animated.spring(destroyedScale, {
          toValue: 1,
          friction: 4,
          tension: 100,
          useNativeDriver: true,
        }).start();

        // Auto-dismiss after 2 seconds
        setTimeout(() => {
          setShowDestroyedMessage(false);
          destroyedScale.setValue(0);
        }, 2500);
      } else {
        setCurrentHP(newHP);
      }
    },
    [currentHP, currentObject, isDestroyed, selectedTool, haptics]
  );

  const handleNextObject = useCallback(() => {
    const available = SMASH_OBJECTS.filter((o) => o.id !== currentObject.id);
    const next = available[Math.floor(Math.random() * available.length)];
    setCurrentObject(next);
    setCurrentHP(next.hitPoints);
    setIsDestroyed(false);
    setCracks([]);
    setShowDestroyedMessage(false);
    destroyedScale.setValue(0);
  }, [currentObject]);

  const handleReset = useCallback(() => {
    setCurrentHP(currentObject.hitPoints);
    setIsDestroyed(false);
    setCracks([]);
    setParticles([]);
    setCombo(0);
  }, [currentObject]);

  const unlockedTools = getUnlockedTools(stats.level);

  return (
    <SafeAreaView style={styles.container}>
      <Animated.View style={[styles.innerContainer, { transform: [{ translateX: shakeX }] }]}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
            <Text style={styles.backText}>← Exit</Text>
          </TouchableOpacity>
          <Text style={styles.headerTitle}>SMASH ARENA</Text>
          <TouchableOpacity onPress={handleReset} style={styles.resetButton}>
            <Text style={styles.resetText}>🔄</Text>
          </TouchableOpacity>
        </View>

        {/* Stats */}
        <DestructionCounter stats={stats} combo={combo} />

        {/* Arena area */}
        <View style={styles.arenaArea}>
          <SmashableObject
            object={currentObject}
            currentHP={currentHP}
            onSmash={handleSmash}
            isDestroyed={isDestroyed}
            shakeIntensity={selectedTool.damage}
          />

          {/* Particle effects */}
          <ParticleRenderer particles={particles} cracks={cracks} />

          {/* Destroyed overlay */}
          {showDestroyedMessage && (
            <Animated.View
              style={[styles.destroyedOverlay, { transform: [{ scale: destroyedScale }] }]}
            >
              <Text style={styles.destroyedEmoji}>💥</Text>
              <Text style={styles.destroyedText}>DESTROYED!</Text>
              <Text style={styles.destroyedSubtext}>
                {currentObject.name} has been obliterated
              </Text>
              <TouchableOpacity style={styles.nextButton} onPress={handleNextObject}>
                <Text style={styles.nextButtonText}>SMASH ANOTHER →</Text>
              </TouchableOpacity>
            </Animated.View>
          )}
        </View>

        {/* Tool selector */}
        <ToolSelector
          selectedTool={selectedTool}
          unlockedTools={unlockedTools}
          onSelect={setSelectedTool}
        />

        {/* Current tool indicator */}
        <View style={styles.toolIndicator}>
          <Text style={styles.toolIndicatorText}>
            {selectedTool.emoji} {selectedTool.name} • DMG: {selectedTool.damage} • {selectedTool.speed}
          </Text>
        </View>
      </Animated.View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  innerContainer: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.sm,
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
    color: COLORS.primary,
    fontSize: 18,
    fontWeight: '900',
    letterSpacing: 3,
  },
  resetButton: {
    padding: SPACING.sm,
  },
  resetText: {
    fontSize: 22,
  },
  arenaArea: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  destroyedOverlay: {
    position: 'absolute',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(0,0,0,0.75)',
    borderRadius: BORDER_RADIUS.lg,
    padding: SPACING.xl,
    paddingHorizontal: SPACING.xxl,
  },
  destroyedEmoji: {
    fontSize: 64,
    marginBottom: SPACING.sm,
  },
  destroyedText: {
    color: COLORS.destructionRed,
    fontSize: 36,
    fontWeight: '900',
    letterSpacing: 4,
  },
  destroyedSubtext: {
    color: COLORS.textSecondary,
    fontSize: 14,
    marginTop: SPACING.xs,
    marginBottom: SPACING.lg,
  },
  nextButton: {
    backgroundColor: COLORS.primary,
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.xl,
    borderRadius: BORDER_RADIUS.lg,
  },
  nextButtonText: {
    color: COLORS.text,
    fontSize: 16,
    fontWeight: '800',
    letterSpacing: 1,
  },
  toolIndicator: {
    alignItems: 'center',
    paddingBottom: SPACING.md,
  },
  toolIndicatorText: {
    color: COLORS.textMuted,
    fontSize: 12,
    fontWeight: '600',
  },
});
