import { SmashObject, Tool, TOOLS, SMASH_OBJECTS } from '../constants/objects';

export interface GameStats {
  totalSmashes: number;
  totalObjectsDestroyed: number;
  favoriteObject: string | null;
  biggestCombo: number;
  currentStreak: number;
  level: number;
  xp: number;
  xpToNextLevel: number;
}

const XP_PER_LEVEL = 100;
const XP_PER_SMASH = 5;
const XP_PER_DESTROY = 25;
const XP_COMBO_BONUS = 10;

export function createInitialStats(): GameStats {
  return {
    totalSmashes: 0,
    totalObjectsDestroyed: 0,
    favoriteObject: null,
    biggestCombo: 0,
    currentStreak: 0,
    level: 1,
    xp: 0,
    xpToNextLevel: XP_PER_LEVEL,
  };
}

export function addXP(stats: GameStats, amount: number): GameStats {
  let newXP = stats.xp + amount;
  let newLevel = stats.level;
  let newXPToNext = stats.xpToNextLevel;

  while (newXP >= newXPToNext) {
    newXP -= newXPToNext;
    newLevel++;
    newXPToNext = XP_PER_LEVEL + (newLevel - 1) * 50;
  }

  return {
    ...stats,
    xp: newXP,
    level: newLevel,
    xpToNextLevel: newXPToNext,
  };
}

export function recordSmash(stats: GameStats): GameStats {
  return addXP(
    {
      ...stats,
      totalSmashes: stats.totalSmashes + 1,
    },
    XP_PER_SMASH
  );
}

export function recordDestroy(stats: GameStats, objectId: string): GameStats {
  const newStreak = stats.currentStreak + 1;
  const comboBonus = newStreak > 1 ? XP_COMBO_BONUS * newStreak : 0;

  return addXP(
    {
      ...stats,
      totalObjectsDestroyed: stats.totalObjectsDestroyed + 1,
      currentStreak: newStreak,
      biggestCombo: Math.max(stats.biggestCombo, newStreak),
      favoriteObject: objectId,
    },
    XP_PER_DESTROY + comboBonus
  );
}

export function getUnlockedObjects(level: number): SmashObject[] {
  return SMASH_OBJECTS.filter((obj) => obj.unlockLevel <= level);
}

export function getUnlockedTools(level: number): Tool[] {
  const tools = [TOOLS[0]]; // fist always available
  if (level >= 2) tools.push(TOOLS[1]); // hammer
  if (level >= 4) tools.push(TOOLS[2]); // bat
  if (level >= 6) tools.push(TOOLS[3]); // sledgehammer
  return tools;
}

export function getLevelTitle(level: number): string {
  if (level <= 2) return 'Novice Smasher';
  if (level <= 5) return 'Destruction Apprentice';
  if (level <= 8) return 'Chaos Specialist';
  if (level <= 12) return 'Master of Mayhem';
  if (level <= 16) return 'Demolition Expert';
  if (level <= 20) return 'Wrecking Ball';
  return 'God of Destruction';
}
