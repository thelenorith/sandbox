import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
  Switch,
  ScrollView,
} from 'react-native';
import { COLORS, SPACING, BORDER_RADIUS, FONTS } from '../constants/theme';

interface SettingsScreenProps {
  navigation: any;
}

export const SettingsScreen: React.FC<SettingsScreenProps> = ({ navigation }) => {
  const [hapticEnabled, setHapticEnabled] = useState(true);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [particlesEnabled, setParticlesEnabled] = useState(true);
  const [screenShake, setScreenShake] = useState(true);
  const [showDamageNumbers, setShowDamageNumbers] = useState(true);

  const SettingRow = ({
    emoji,
    title,
    subtitle,
    value,
    onToggle,
  }: {
    emoji: string;
    title: string;
    subtitle: string;
    value: boolean;
    onToggle: (val: boolean) => void;
  }) => (
    <View style={styles.settingRow}>
      <Text style={styles.settingEmoji}>{emoji}</Text>
      <View style={styles.settingInfo}>
        <Text style={styles.settingTitle}>{title}</Text>
        <Text style={styles.settingSubtitle}>{subtitle}</Text>
      </View>
      <Switch
        value={value}
        onValueChange={onToggle}
        trackColor={{ false: COLORS.surface, true: COLORS.primary }}
        thumbColor={COLORS.text}
      />
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Settings</Text>
        <View style={{ width: 60 }} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.sectionTitle}>Feedback</Text>
        <View style={styles.section}>
          <SettingRow
            emoji="📳"
            title="Haptic Feedback"
            subtitle="Vibrate on impact"
            value={hapticEnabled}
            onToggle={setHapticEnabled}
          />
          <SettingRow
            emoji="🔊"
            title="Sound Effects"
            subtitle="Crash, bang, tinkle sounds"
            value={soundEnabled}
            onToggle={setSoundEnabled}
          />
          <SettingRow
            emoji="📱"
            title="Screen Shake"
            subtitle="Shake screen on heavy hits"
            value={screenShake}
            onToggle={setScreenShake}
          />
        </View>

        <Text style={styles.sectionTitle}>Visuals</Text>
        <View style={styles.section}>
          <SettingRow
            emoji="✨"
            title="Particle Effects"
            subtitle="Shards, sparks, and debris"
            value={particlesEnabled}
            onToggle={setParticlesEnabled}
          />
          <SettingRow
            emoji="🔢"
            title="Damage Numbers"
            subtitle="Show damage on impact"
            value={showDamageNumbers}
            onToggle={setShowDamageNumbers}
          />
        </View>

        <Text style={styles.sectionTitle}>Data</Text>
        <View style={styles.section}>
          <TouchableOpacity style={styles.actionRow}>
            <Text style={styles.settingEmoji}>🗑️</Text>
            <View style={styles.settingInfo}>
              <Text style={[styles.settingTitle, { color: COLORS.destructionRed }]}>
                Reset All Progress
              </Text>
              <Text style={styles.settingSubtitle}>
                Clear all stats, levels, and achievements
              </Text>
            </View>
          </TouchableOpacity>
        </View>

        <View style={styles.aboutSection}>
          <Text style={styles.aboutTitle}>Virtual Smash v1.0.0</Text>
          <Text style={styles.aboutText}>
            A virtual destruction sandbox for stress relief.{'\n'}
            No real objects were harmed. 💥
          </Text>
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
  sectionTitle: {
    color: COLORS.textMuted,
    fontSize: 13,
    fontWeight: '700',
    letterSpacing: 1,
    textTransform: 'uppercase',
    marginBottom: SPACING.sm,
    marginTop: SPACING.lg,
  },
  section: {
    backgroundColor: COLORS.surface,
    borderRadius: BORDER_RADIUS.md,
    overflow: 'hidden',
  },
  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: SPACING.md,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.05)',
  },
  actionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: SPACING.md,
  },
  settingEmoji: {
    fontSize: 22,
    marginRight: SPACING.md,
  },
  settingInfo: {
    flex: 1,
  },
  settingTitle: {
    color: COLORS.text,
    fontSize: 15,
    fontWeight: '600',
  },
  settingSubtitle: {
    color: COLORS.textMuted,
    fontSize: 12,
    marginTop: 2,
  },
  aboutSection: {
    alignItems: 'center',
    marginTop: SPACING.xxl,
    padding: SPACING.lg,
  },
  aboutTitle: {
    color: COLORS.textMuted,
    fontSize: 14,
    fontWeight: '700',
  },
  aboutText: {
    color: COLORS.textMuted,
    fontSize: 12,
    textAlign: 'center',
    marginTop: SPACING.xs,
    lineHeight: 18,
  },
});
