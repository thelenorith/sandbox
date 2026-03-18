export interface Particle {
  id: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  color: string;
  opacity: number;
  rotation: number;
  rotationSpeed: number;
  life: number;
  maxLife: number;
  type: 'shard' | 'spark' | 'dust' | 'debris' | 'smoke';
  shape: 'triangle' | 'rect' | 'circle';
}

export interface CrackLine {
  id: number;
  points: { x: number; y: number }[];
  width: number;
  opacity: number;
}

let nextParticleId = 0;

export function createExplosion(
  x: number,
  y: number,
  count: number,
  colors: string[],
  intensity: number = 1
): Particle[] {
  const particles: Particle[] = [];

  // Shards - main debris
  for (let i = 0; i < count; i++) {
    const angle = (Math.PI * 2 * i) / count + (Math.random() - 0.5) * 0.5;
    const speed = (3 + Math.random() * 8) * intensity;
    const life = 40 + Math.random() * 40;

    particles.push({
      id: nextParticleId++,
      x,
      y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed - 2,
      size: 4 + Math.random() * 12,
      color: colors[Math.floor(Math.random() * colors.length)],
      opacity: 1,
      rotation: Math.random() * 360,
      rotationSpeed: (Math.random() - 0.5) * 15,
      life,
      maxLife: life,
      type: 'shard',
      shape: Math.random() > 0.5 ? 'triangle' : 'rect',
    });
  }

  // Sparks
  const sparkCount = Math.floor(count * 0.6);
  for (let i = 0; i < sparkCount; i++) {
    const angle = Math.random() * Math.PI * 2;
    const speed = (5 + Math.random() * 12) * intensity;
    const life = 15 + Math.random() * 20;

    particles.push({
      id: nextParticleId++,
      x: x + (Math.random() - 0.5) * 20,
      y: y + (Math.random() - 0.5) * 20,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      size: 2 + Math.random() * 3,
      color: '#ffff00',
      opacity: 1,
      rotation: 0,
      rotationSpeed: 0,
      life,
      maxLife: life,
      type: 'spark',
      shape: 'circle',
    });
  }

  // Dust cloud
  const dustCount = Math.floor(count * 0.4);
  for (let i = 0; i < dustCount; i++) {
    const angle = Math.random() * Math.PI * 2;
    const speed = 1 + Math.random() * 3;
    const life = 30 + Math.random() * 30;

    particles.push({
      id: nextParticleId++,
      x: x + (Math.random() - 0.5) * 30,
      y: y + (Math.random() - 0.5) * 30,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed - 1,
      size: 8 + Math.random() * 15,
      color: '#888888',
      opacity: 0.6,
      rotation: Math.random() * 360,
      rotationSpeed: (Math.random() - 0.5) * 3,
      life,
      maxLife: life,
      type: 'dust',
      shape: 'circle',
    });
  }

  return particles;
}

export function createCrack(
  startX: number,
  startY: number,
  objectWidth: number,
  objectHeight: number
): CrackLine[] {
  const cracks: CrackLine[] = [];
  const branchCount = 2 + Math.floor(Math.random() * 4);

  for (let b = 0; b < branchCount; b++) {
    const angle = (Math.PI * 2 * b) / branchCount + (Math.random() - 0.5) * 1.0;
    const points: { x: number; y: number }[] = [{ x: startX, y: startY }];
    const segmentCount = 3 + Math.floor(Math.random() * 5);

    let cx = startX;
    let cy = startY;

    for (let s = 0; s < segmentCount; s++) {
      const segLen = 10 + Math.random() * 25;
      const jitter = (Math.random() - 0.5) * 0.8;
      cx += Math.cos(angle + jitter) * segLen;
      cy += Math.sin(angle + jitter) * segLen;

      // Keep within object bounds (rough)
      cx = Math.max(startX - objectWidth / 2, Math.min(startX + objectWidth / 2, cx));
      cy = Math.max(startY - objectHeight / 2, Math.min(startY + objectHeight / 2, cy));

      points.push({ x: cx, y: cy });
    }

    cracks.push({
      id: nextParticleId++,
      points,
      width: 1 + Math.random() * 2,
      opacity: 0.8 + Math.random() * 0.2,
    });
  }

  return cracks;
}

export function updateParticles(particles: Particle[], gravity: number = 0.3): Particle[] {
  return particles
    .map((p) => ({
      ...p,
      x: p.x + p.vx,
      y: p.y + p.vy,
      vy: p.vy + gravity,
      vx: p.vx * 0.98,
      rotation: p.rotation + p.rotationSpeed,
      life: p.life - 1,
      opacity: Math.max(0, p.life / p.maxLife),
      size: p.type === 'dust' ? p.size * 1.02 : p.size * 0.99,
    }))
    .filter((p) => p.life > 0);
}

export function createImpactRipple(x: number, y: number): Particle[] {
  const ripples: Particle[] = [];
  for (let i = 0; i < 3; i++) {
    const life = 20 + i * 8;
    ripples.push({
      id: nextParticleId++,
      x,
      y,
      vx: 0,
      vy: 0,
      size: 10 + i * 5,
      color: '#ffffff',
      opacity: 0.5 - i * 0.15,
      rotation: 0,
      rotationSpeed: 0,
      life,
      maxLife: life,
      type: 'dust',
      shape: 'circle',
    });
  }
  return ripples;
}
