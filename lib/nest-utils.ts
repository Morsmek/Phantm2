import { CanvasPoint, ContextMode, MODULE_ICONS, MODULE_LABELS, ModuleId, NestRecord, RingConfig, SlotConfig } from './phantm-types';

export function makeId(prefix: string) {
  return `${prefix}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
}

export function distance(a: CanvasPoint, b: CanvasPoint) {
  const dx = a.x - b.x;
  const dy = a.y - b.y;
  return Math.sqrt(dx * dx + dy * dy);
}

export function nearestNest(nests: NestRecord[], point: CanvasPoint, threshold = 180) {
  let best: NestRecord | null = null;
  let bestDistance = Number.POSITIVE_INFINITY;
  for (const nest of nests) {
    const d = distance(nest.position, point);
    if (d < bestDistance) {
      best = nest;
      bestDistance = d;
    }
  }
  return best && bestDistance <= threshold ? best : null;
}

export function emptySlot(slotIndex: number): SlotConfig {
  return { slotIndex, type: 'empty', label: 'Empty' };
}

export function moduleSlot(slotIndex: number, moduleId: ModuleId): SlotConfig {
  return { slotIndex, type: 'module', moduleId, iconKey: MODULE_ICONS[moduleId], label: MODULE_LABELS[moduleId] };
}

export function createDefaultRings(primaryModule: ModuleId = 'notes'): RingConfig[] {
  return [
    { ringIndex: 1, slots: [moduleSlot(0, primaryModule), moduleSlot(1, 'voice'), moduleSlot(2, 'timer'), moduleSlot(3, 'capture')] },
    { ringIndex: 2, slots: [moduleSlot(0, 'browser'), moduleSlot(1, 'workflows'), emptySlot(2), emptySlot(3), emptySlot(4), emptySlot(5)] },
  ];
}

export function createNest(label: string, context: ContextMode = 'Neutral', primaryModule: ModuleId = 'notes', position: CanvasPoint = { x: 0, y: 0 }): NestRecord {
  const now = Date.now();
  return {
    id: makeId('nest'),
    label: label.trim() || 'Main Nest',
    type: 'open',
    position,
    rings: createDefaultRings(primaryModule),
    createdAt: now,
    updatedAt: now,
    context,
  };
}

export function exportNest(nest: NestRecord) {
  return JSON.stringify({ phantmNestVersion: 2, nest }, null, 2);
}

export function parseNestImport(value: string): NestRecord | null {
  try {
    const parsed = JSON.parse(value);
    const nest = parsed.nest ?? parsed;
    if (!nest?.id || !nest?.label || !Array.isArray(nest?.rings)) return null;
    return { ...nest, id: makeId('nest'), position: nest.position ?? { x: 260, y: 160 }, createdAt: Date.now(), updatedAt: Date.now() };
  } catch {
    return null;
  }
}

export function hashPassword(value: string) {
  let hash = 0;
  for (let i = 0; i < value.length; i += 1) hash = (hash << 5) - hash + value.charCodeAt(i);
  return `local_${Math.abs(hash)}`;
}
