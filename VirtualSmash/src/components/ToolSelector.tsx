import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView } from 'react-native';
import { Tool, TOOLS } from '../constants/objects';

import { COLORS, BORDER_RADIUS, SPACING } from '../constants/theme';

interface ToolSelectorProps {
  selectedTool: Tool;
  unlockedTools: Tool[];
  onSelect: (tool: Tool) => void;
}

export const ToolSelector: React.FC<ToolSelectorProps> = ({
  selectedTool,
  unlockedTools,
  onSelect,
}) => {
  return (
    <View style={styles.container}>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        {TOOLS.map((tool) => {
          const isUnlocked = unlockedTools.some((t) => t.id === tool.id);
          const isSelected = selectedTool.id === tool.id;

          return (
            <TouchableOpacity
              key={tool.id}
              style={[
                styles.toolButton,
                isSelected && styles.toolButtonSelected,
                !isUnlocked && styles.toolButtonLocked,
              ]}
              onPress={() => isUnlocked && onSelect(tool)}
              disabled={!isUnlocked}
              activeOpacity={0.7}
            >
              <Text style={styles.toolEmoji}>{isUnlocked ? tool.emoji : '🔒'}</Text>
              <Text
                style={[
                  styles.toolName,
                  isSelected && styles.toolNameSelected,
                  !isUnlocked && styles.toolNameLocked,
                ]}
              >
                {tool.name}
              </Text>
              {isUnlocked && (
                <View style={styles.damageIndicator}>
                  {Array.from({ length: 5 }).map((_, i) => (
                    <View
                      key={i}
                      style={[
                        styles.damageDot,
                        { backgroundColor: i < tool.damage ? COLORS.primary : 'rgba(255,255,255,0.2)' },
                      ]}
                    />
                  ))}
                </View>
              )}
            </TouchableOpacity>
          );
        })}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingVertical: SPACING.sm,
  },
  toolButton: {
    alignItems: 'center',
    backgroundColor: COLORS.surface,
    borderRadius: BORDER_RADIUS.md,
    paddingVertical: SPACING.sm,
    paddingHorizontal: SPACING.md,
    marginHorizontal: SPACING.xs,
    minWidth: 80,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  toolButtonSelected: {
    borderColor: COLORS.primary,
    backgroundColor: COLORS.surfaceLight,
  },
  toolButtonLocked: {
    opacity: 0.4,
  },
  toolEmoji: {
    fontSize: 28,
  },
  toolName: {
    color: COLORS.textSecondary,
    fontSize: 11,
    fontWeight: '600',
    marginTop: 2,
  },
  toolNameSelected: {
    color: COLORS.text,
  },
  toolNameLocked: {
    color: COLORS.textMuted,
  },
  damageIndicator: {
    flexDirection: 'row',
    marginTop: 4,
    gap: 2,
  },
  damageDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
  },
});
