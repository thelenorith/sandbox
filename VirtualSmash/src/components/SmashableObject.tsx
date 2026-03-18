import React, { useState, useRef, useCallback, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableWithoutFeedback,
  Animated,
  Dimensions,
} from 'react-native';
import { SmashObject } from '../constants/objects';
import { COLORS } from '../constants/theme';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

interface SmashableObjectProps {
  object: SmashObject;
  currentHP: number;
  onSmash: (x: number, y: number) => void;
  isDestroyed: boolean;
  shakeIntensity: number;
}

export const SmashableObject: React.FC<SmashableObjectProps> = ({
  object,
  currentHP,
  onSmash,
  isDestroyed,
  shakeIntensity,
}) => {
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const shakeAnim = useRef(new Animated.Value(0)).current;
  const destroyAnim = useRef(new Animated.Value(1)).current;
  const glowAnim = useRef(new Animated.Value(0)).current;

  const sizeMap = { small: 120, medium: 160, large: 200 };
  const objectSize = sizeMap[object.size];

  const damagePercent = 1 - currentHP / object.hitPoints;

  useEffect(() => {
    if (isDestroyed) {
      Animated.parallel([
        Animated.timing(destroyAnim, {
          toValue: 0,
          duration: 300,
          useNativeDriver: true,
        }),
        Animated.timing(scaleAnim, {
          toValue: 1.5,
          duration: 300,
          useNativeDriver: true,
        }),
      ]).start();
    }
  }, [isDestroyed]);

  const handlePress = useCallback(
    (evt: any) => {
      if (isDestroyed) return;

      const { locationX, locationY, pageX, pageY } = evt.nativeEvent;

      // Smash animation
      Animated.sequence([
        Animated.timing(scaleAnim, {
          toValue: 0.85,
          duration: 50,
          useNativeDriver: true,
        }),
        Animated.spring(scaleAnim, {
          toValue: 1,
          friction: 3,
          tension: 200,
          useNativeDriver: true,
        }),
      ]).start();

      // Shake
      Animated.sequence([
        Animated.timing(shakeAnim, {
          toValue: shakeIntensity * 8,
          duration: 30,
          useNativeDriver: true,
        }),
        Animated.timing(shakeAnim, {
          toValue: -shakeIntensity * 8,
          duration: 30,
          useNativeDriver: true,
        }),
        Animated.timing(shakeAnim, {
          toValue: shakeIntensity * 4,
          duration: 30,
          useNativeDriver: true,
        }),
        Animated.timing(shakeAnim, {
          toValue: 0,
          duration: 30,
          useNativeDriver: true,
        }),
      ]).start();

      // Damage glow
      Animated.sequence([
        Animated.timing(glowAnim, {
          toValue: 1,
          duration: 50,
          useNativeDriver: false,
        }),
        Animated.timing(glowAnim, {
          toValue: 0,
          duration: 200,
          useNativeDriver: false,
        }),
      ]).start();

      onSmash(pageX, pageY);
    },
    [isDestroyed, onSmash, shakeIntensity]
  );

  const damageOverlayOpacity = glowAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [0, 0.6],
  });

  return (
    <View style={styles.container}>
      <TouchableWithoutFeedback onPress={handlePress}>
        <Animated.View
          style={[
            styles.objectContainer,
            {
              width: objectSize,
              height: objectSize,
              opacity: destroyAnim,
              transform: [
                { scale: scaleAnim },
                { translateX: shakeAnim },
              ],
            },
          ]}
        >
          {/* Object background with damage */}
          <View
            style={[
              styles.objectBg,
              {
                backgroundColor: object.color,
                borderColor: object.secondaryColor,
              },
            ]}
          >
            {/* Damage cracks overlay */}
            {damagePercent > 0 && (
              <View style={[styles.damageOverlay, { opacity: damagePercent * 0.5 }]}>
                {Array.from({ length: Math.ceil(damagePercent * 5) }).map((_, i) => (
                  <View
                    key={i}
                    style={[
                      styles.crackLine,
                      {
                        transform: [{ rotate: `${i * 72 + Math.random() * 30}deg` }],
                        width: 2,
                        height: objectSize * 0.3 + Math.random() * objectSize * 0.3,
                      },
                    ]}
                  />
                ))}
              </View>
            )}

            {/* Main emoji */}
            <Text style={[styles.emoji, { fontSize: objectSize * 0.45 }]}>
              {object.emoji}
            </Text>

            {/* Damage flash overlay */}
            <Animated.View
              style={[
                StyleSheet.absoluteFill,
                styles.flashOverlay,
                { opacity: damageOverlayOpacity },
              ]}
            />
          </View>

          {/* HP Bar */}
          {!isDestroyed && object.hitPoints > 1 && (
            <View style={styles.hpBarContainer}>
              <View style={styles.hpBarBg}>
                <View
                  style={[
                    styles.hpBarFill,
                    {
                      width: `${(currentHP / object.hitPoints) * 100}%`,
                      backgroundColor:
                        currentHP / object.hitPoints > 0.5
                          ? COLORS.success
                          : currentHP / object.hitPoints > 0.25
                          ? COLORS.warning
                          : COLORS.destructionRed,
                    },
                  ]}
                />
              </View>
            </View>
          )}

          {/* Object name */}
          <Text style={styles.objectName}>{object.name}</Text>
        </Animated.View>
      </TouchableWithoutFeedback>

      {/* "TAP TO SMASH" hint */}
      {!isDestroyed && currentHP === object.hitPoints && (
        <Text style={styles.tapHint}>TAP TO SMASH!</Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  objectContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  objectBg: {
    width: '100%',
    height: '100%',
    borderRadius: 20,
    borderWidth: 3,
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
    elevation: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 5 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
  },
  emoji: {
    textAlign: 'center',
  },
  damageOverlay: {
    ...StyleSheet.absoluteFillObject,
    alignItems: 'center',
    justifyContent: 'center',
  },
  crackLine: {
    position: 'absolute',
    backgroundColor: 'rgba(0,0,0,0.6)',
    borderRadius: 1,
  },
  flashOverlay: {
    backgroundColor: COLORS.destructionRed,
    borderRadius: 20,
  },
  hpBarContainer: {
    marginTop: 8,
    width: '80%',
    alignItems: 'center',
  },
  hpBarBg: {
    width: '100%',
    height: 6,
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 3,
    overflow: 'hidden',
  },
  hpBarFill: {
    height: '100%',
    borderRadius: 3,
  },
  objectName: {
    marginTop: 6,
    color: COLORS.text,
    fontSize: 14,
    fontWeight: '600',
  },
  tapHint: {
    marginTop: 12,
    color: COLORS.textMuted,
    fontSize: 13,
    fontWeight: '700',
    letterSpacing: 2,
    opacity: 0.7,
  },
});
