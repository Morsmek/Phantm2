import { describe, expect, it } from 'vitest';
import { applySlot, createFocusedNest, makeEmptyAssignment, makeModuleAssignment, makeNestLinkAssignment } from './phantm-actions';
import { createNest } from './nest-utils';

describe('PHANTM functional actions', () => {
  it('creates a new nest near the current viewport so add-nest has visible behaviour', () => {
    const nest = createFocusedNest('', 'Work', 'notes', { x: 10, y: -20 }, 3);
    expect(nest.label).toBe('Nest 4');
    expect(nest.context).toBe('Work');
    expect(nest.position).toEqual({ x: 270, y: 100 });
  });

  it('assigns a module to a selected ring slot without changing unrelated slots', () => {
    const nest = createNest('Main', 'Neutral', 'notes', { x: 0, y: 0 });
    const updated = applySlot(nest, 1, 1, makeModuleAssignment(1, 'timer'));
    expect(updated.rings[0].slots[1].type).toBe('module');
    expect(updated.rings[0].slots[1].moduleId).toBe('timer');
    expect(updated.rings[0].slots[0].moduleId).toBe('notes');
  });

  it('supports nest-link and empty slot assignments for the editor flow', () => {
    const source = createNest('Source', 'Neutral', 'notes', { x: 0, y: 0 });
    const target = createNest('Target', 'Focus', 'timer', { x: 80, y: 20 });
    const linked = applySlot(source, 2, 2, makeNestLinkAssignment(2, target));
    expect(linked.rings[1].slots[2].type).toBe('nest-link');
    expect(linked.rings[1].slots[2].targetNestId).toBe(target.id);
    const emptied = applySlot(linked, 2, 2, makeEmptyAssignment(2));
    expect(emptied.rings[1].slots[2].type).toBe('empty');
  });
});
