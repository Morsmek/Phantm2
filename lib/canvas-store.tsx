import { createContext, PropsWithChildren, useContext, useEffect, useMemo, useState } from 'react';
import { phantmData } from './phantm-data';
import { CanvasPoint, CanvasState, CaptureEntry, ContextMode, CONTEXT_COLORS, ModuleId, NestRecord, NoteEntry, SlotConfig, VoiceClip, WorkflowTemplate } from './phantm-types';
import { createNest, makeId, moduleSlot } from './nest-utils';

type PhantmStore = {
  hydrated: boolean;
  onboardingComplete: boolean;
  completeOnboarding: () => Promise<void>;
  canvasOffset: CanvasPoint;
  canvasScale: number;
  nests: NestRecord[];
  activeNestId: string;
  activeNest?: NestRecord;
  context: ContextMode;
  activeColor: string;
  activeModuleId: ModuleId | null;
  isNavigating: boolean;
  navigationDirection: CanvasPoint | null;
  notes: NoteEntry[];
  captures: CaptureEntry[];
  voiceClips: VoiceClip[];
  workflows: WorkflowTemplate[];
  setCanvasOffset: (offset: CanvasPoint) => void;
  moveCanvasBy: (delta: CanvasPoint) => void;
  setCanvasScale: (scale: number) => void;
  setActiveNest: (id: string) => void;
  createMainNest: (label: string, moduleId: ModuleId, ctx: ContextMode) => Promise<void>;
  createNestFromCanvas: (label?: string) => NestRecord;
  updateNest: (id: string, updates: Partial<NestRecord>) => void;
  assignSlot: (nestId: string, ringIndex: number, slotIndex: number, slot: SlotConfig) => void;
  deleteNest: (id: string) => void;
  importNest: (nest: NestRecord) => void;
  openModule: (id: ModuleId) => void;
  closeModule: () => void;
  setContext: (ctx: ContextMode) => void;
  addNote: (title: string, body: string) => NoteEntry | null;
  addCapture: (body: string) => CaptureEntry | null;
  addVoiceClip: (clip: VoiceClip) => void;
  updateWorkflows: (items: WorkflowTemplate[]) => void;
  setNavigating: (value: boolean, direction?: CanvasPoint | null) => void;
  resetAll: () => Promise<void>;
};

const defaultCanvas: CanvasState = { nests: [], lastViewportPosition: { x: 0, y: 0 }, lastScale: 1 };

const defaultWorkflows: WorkflowTemplate[] = [
  {
    id: 'morning-focus',
    name: 'Morning Focus',
    context: 'Focus',
    description: 'Silence noise, capture intent, and start a focus block.',
    steps: [
      { id: '1', label: 'Switch context', detail: 'Move PHANTM into Focus mode.', complete: false },
      { id: '2', label: 'Open Capture', detail: 'Write today’s first intention.', complete: false },
      { id: '3', label: 'Start Timer', detail: 'Begin a 25 minute focus interval.', complete: false },
    ],
  },
];

const Ctx = createContext<PhantmStore | null>(null);

function withTimestamp(nest: NestRecord): NestRecord {
  return { ...nest, updatedAt: Date.now() };
}

export function PhantmProvider({ children }: PropsWithChildren) {
  const [hydrated, setHydrated] = useState(false);
  const [onboardingComplete, setOnboardingComplete] = useState(false);
  const [canvasOffset, setCanvasOffsetState] = useState(defaultCanvas.lastViewportPosition);
  const [canvasScale, setCanvasScaleState] = useState(defaultCanvas.lastScale);
  const [nests, setNests] = useState<NestRecord[]>([]);
  const [activeNestId, setActiveNestId] = useState('');
  const [context, setContextState] = useState<ContextMode>('Neutral');
  const [activeModuleId, setActiveModuleId] = useState<ModuleId | null>(null);
  const [isNavigating, setIsNavigating] = useState(false);
  const [navigationDirection, setNavigationDirection] = useState<CanvasPoint | null>(null);
  const [notes, setNotes] = useState<NoteEntry[]>([]);
  const [captures, setCaptures] = useState<CaptureEntry[]>([]);
  const [voiceClips, setVoiceClips] = useState<VoiceClip[]>([]);
  const [workflows, setWorkflows] = useState<WorkflowTemplate[]>(defaultWorkflows);

  useEffect(() => {
    let mounted = true;
    async function hydrate() {
      const [onboarded, canvas, savedNotes, savedCaptures, savedVoice, savedWorkflows] = await Promise.all([
        phantmData.getOnboarded(),
        phantmData.loadCanvas(defaultCanvas),
        phantmData.loadNotes(),
        phantmData.loadCaptures(),
        phantmData.loadVoice(),
        phantmData.loadWorkflows(),
      ]);
      if (!mounted) return;
      const firstNest = canvas.nests[0];
      setOnboardingComplete(onboarded);
      setCanvasOffsetState(canvas.lastViewportPosition);
      setCanvasScaleState(canvas.lastScale);
      setNests(canvas.nests);
      setActiveNestId(firstNest?.id ?? '');
      setContextState(firstNest?.context ?? 'Neutral');
      setNotes(savedNotes);
      setCaptures(savedCaptures);
      setVoiceClips(savedVoice);
      setWorkflows(savedWorkflows.length ? savedWorkflows : defaultWorkflows);
      setHydrated(true);
    }
    hydrate();
    return () => { mounted = false; };
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    phantmData.saveCanvas({ nests, lastViewportPosition: canvasOffset, lastScale: canvasScale });
  }, [hydrated, nests, canvasOffset, canvasScale]);

  const activeNest = nests.find((nest) => nest.id === activeNestId) ?? nests[0];
  const activeColor = CONTEXT_COLORS[context];

  const store = useMemo<PhantmStore>(() => {
    const focusNest = (id: string, list = nests) => {
      const nest = list.find((item) => item.id === id);
      if (!nest) return;
      setActiveNestId(nest.id);
      setContextState(nest.context ?? 'Neutral');
      setCanvasOffsetState(nest.position);
      setActiveModuleId(null);
    };

    return {
      hydrated,
      onboardingComplete,
      completeOnboarding: async () => { setOnboardingComplete(true); await phantmData.setOnboarded(true); },
      canvasOffset,
      canvasScale,
      nests,
      activeNestId,
      activeNest,
      context,
      activeColor,
      activeModuleId,
      isNavigating,
      navigationDirection,
      notes,
      captures,
      voiceClips,
      workflows,
      setCanvasOffset: setCanvasOffsetState,
      moveCanvasBy: (delta) => setCanvasOffsetState((current) => ({ x: current.x + delta.x, y: current.y + delta.y })),
      setCanvasScale: (scale) => setCanvasScaleState(Math.max(0.72, Math.min(1.35, scale))),
      setActiveNest: (id) => focusNest(id),
      createMainNest: async (label, moduleId, ctx) => {
        const main = createNest(label.trim() || 'Main Nest', ctx, moduleId, { x: 0, y: 0 });
        const satellite = createNest('Focus Vault', 'Focus', 'timer', { x: 360, y: -180 });
        const travel = createNest('Travel Cache', 'Travel', 'capture', { x: -300, y: 260 });
        const next = [main, { ...satellite, type: 'hidden' as const, passwordHash: 'local_3149094' }, travel];
        setNests(next);
        focusNest(main.id, next);
        await phantmData.setOnboarded(true);
        setOnboardingComplete(true);
      },
      createNestFromCanvas: (label = 'New Nest') => {
        const name = label.trim() || `Nest ${nests.length + 1}`;
        const nextNest = createNest(name, context, 'notes', { x: canvasOffset.x + 260, y: canvasOffset.y + 120 });
        setNests((items) => [...items, nextNest]);
        focusNest(nextNest.id, [...nests, nextNest]);
        return nextNest;
      },
      updateNest: (id, updates) => setNests((items) => items.map((nest) => nest.id === id ? withTimestamp({ ...nest, ...updates }) : nest)),
      assignSlot: (nestId, ringIndex, slotIndex, slot) => setNests((items) => items.map((nest) => {
        if (nest.id !== nestId) return nest;
        return withTimestamp({
          ...nest,
          rings: nest.rings.map((ring) => ring.ringIndex !== ringIndex ? ring : {
            ...ring,
            slots: ring.slots.map((existing) => existing.slotIndex === slotIndex ? { ...slot, slotIndex } : existing),
          }),
        });
      })),
      deleteNest: (id) => setNests((items) => {
        const next = items.filter((nest) => nest.id !== id);
        if (activeNestId === id && next[0]) focusNest(next[0].id, next);
        return next;
      }),
      importNest: (nest) => {
        const primary = nest.rings[0]?.slots[0]?.moduleId ?? 'notes';
        const normalized = { ...nest, rings: nest.rings.length ? nest.rings : createNest(nest.label, nest.context ?? 'Neutral', primary, nest.position).rings };
        setNests((items) => [...items, normalized]);
        focusNest(normalized.id, [...nests, normalized]);
      },
      openModule: (id) => setActiveModuleId(id),
      closeModule: () => setActiveModuleId(null),
      setContext: (ctx) => setContextState(ctx),
      addNote: (title, body) => {
        if (!title.trim() && !body.trim()) return null;
        const entry = { id: makeId('note'), title: title.trim() || 'Untitled note', body: body.trim(), updatedAt: Date.now() };
        const next = [entry, ...notes];
        setNotes(next);
        phantmData.saveNotes(next);
        return entry;
      },
      addCapture: (body) => {
        if (!body.trim()) return null;
        const entry = { id: makeId('capture'), body: body.trim(), context, createdAt: Date.now() };
        const next = [entry, ...captures];
        setCaptures(next);
        phantmData.saveCaptures(next);
        return entry;
      },
      addVoiceClip: (clip) => {
        const next = [clip, ...voiceClips];
        setVoiceClips(next);
        phantmData.saveVoice(next);
      },
      updateWorkflows: (items) => {
        setWorkflows(items);
        phantmData.saveWorkflows(items);
      },
      setNavigating: (value, direction = null) => { setIsNavigating(value); setNavigationDirection(direction); },
      resetAll: async () => {
        await phantmData.resetLocal();
        setOnboardingComplete(false); setNests([]); setActiveNestId(''); setCanvasOffsetState({ x: 0, y: 0 }); setCanvasScaleState(1);
        setNotes([]); setCaptures([]); setVoiceClips([]); setWorkflows(defaultWorkflows); setActiveModuleId(null); setContextState('Neutral');
      },
    };
  }, [hydrated, onboardingComplete, canvasOffset, canvasScale, nests, activeNestId, activeNest, context, activeColor, activeModuleId, isNavigating, navigationDirection, notes, captures, voiceClips, workflows]);

  return <Ctx.Provider value={store}>{children}</Ctx.Provider>;
}

export function usePhantm() {
  const store = useContext(Ctx);
  if (!store) throw new Error('usePhantm must be used inside PhantmProvider');
  return store;
}
