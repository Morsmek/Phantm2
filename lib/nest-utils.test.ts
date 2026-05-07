import { describe, expect, it } from 'vitest';
import { createNest, exportNest, parseNestImport, nearestNest } from './nest-utils';

describe('PHANTM nest utilities', () => {
  it('creates a default nest with two rings and a module slot', () => {
    const nest = createNest('Main', 'Neutral', 'notes');
    expect(nest.rings).toHaveLength(2);
    expect(nest.rings[0].slots[0].moduleId).toBe('notes');
  });
  it('round-trips shareable nest JSON', () => {
    const nest = createNest('Share', 'Work', 'capture');
    const imported = parseNestImport(exportNest(nest));
    expect(imported?.label).toBe('Share');
    expect(imported?.id).not.toBe(nest.id);
  });
  it('finds the nearest nest within a threshold', () => {
    const nest = createNest('Near', 'Neutral', 'notes', { x: 10, y: 20 });
    expect(nearestNest([nest], { x: 12, y: 18 }, 10)?.label).toBe('Near');
  });
});
