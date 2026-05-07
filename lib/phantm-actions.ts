import { CanvasPoint, ContextMode, ModuleId, NestRecord, SlotConfig } from './phantm-types';
import { createNest, emptySlot, moduleSlot } from './nest-utils';

export function applySlot(nest: NestRecord, ringIndex: number, slotIndex: number, slot: SlotConfig): NestRecord {
  return {
    ...nest,
    updatedAt: Date.now(),
    rings: nest.rings.map((ring) => ring.ringIndex !== ringIndex ? ring : {
      ...ring,
      slots: ring.slots.map((existing) => existing.slotIndex === slotIndex ? { ...slot, slotIndex } : existing),
    }),
  };
}

export function makeModuleAssignment(slotIndex: number, moduleId: ModuleId): SlotConfig {
  return moduleSlot(slotIndex, moduleId);
}

export function makeNestLinkAssignment(slotIndex: number, target: NestRecord): SlotConfig {
  return { slotIndex, type: 'nest-link', targetNestId: target.id, label: target.label, iconKey: 'hub' };
}

export function makeEmptyAssignment(slotIndex: number): SlotConfig {
  return emptySlot(slotIndex);
}

export function createFocusedNest(label: string, context: ContextMode, moduleId: ModuleId, currentOffset: CanvasPoint, count: number): NestRecord {
  return createNest(label.trim() || `Nest ${count + 1}`, context, moduleId, { x: currentOffset.x + 260, y: currentOffset.y + 120 });
}
