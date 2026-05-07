import { createContext, PropsWithChildren, useContext, useEffect, useMemo, useState } from 'react';
import { phantmData } from '@/lib/phantm-data';
import { CanvasPoint, CanvasState, CaptureEntry, ContextMode, CONTEXT_COLORS, ModuleId, NestRecord, NoteEntry, VoiceClip, WorkflowTemplate } from '@/lib/phantm-types';
import { createNest, makeId } from '@/lib/nest-utils';

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
  setCanvasScale: (scale: number) => void;
  setActiveNest: (id: string) => void;
  createMainNest: (label: string, moduleId: ModuleId, ctx: ContextMode) => Promise<void>;
  createNestFromCanvas: (label?: string) => void;
  updateNest: (id: string, updates: Partial<NestRecord>) => void;
  deleteNest: (id: string) => void;
  importNest: (nest: NestRecord) => void;
  openModule: (id: ModuleId) => void;
  closeModule: () => void;
  setContext: (ctx: ContextMode) => void;
  addNote: (title: string, body: string) => void;
  addCapture: (body: string) => void;
  addVoiceClip: (clip: VoiceClip) => void;
  updateWorkflows: (items: WorkflowTemplate[]) => void;
  setNavigating: (value: boolean, direction?: CanvasPoint | null) => void;
  resetAll: () => Promise<void>;
};

const defaultCanvas: CanvasState = {
  nests: [],
  lastViewportPosition: { x: 0, y: 0 },
  lastScale: 1,
};

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
      setOnboardingComplete(onboarded);
      setCanvasOffsetState(canvas.lastViewportPosition);
      setCanvasScaleState(canvas.lastScale);
      setNests(canvas.nests);
      setActiveNestId(canvas.nests[0]?.id ?? '');
      setContextState(canvas.nests[0]?.context ?? 'Neutral');
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

  const store = useMemo<PhantmStore>(() => ({
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
    setCanvasScale: (scale) => setCanvasScaleState(Math.max(0.72, Math.min(1.35, scale))),
    setActiveNest: (id) => {
      setActiveNestId(id);
      const nest = nests.find((item) => item.id === id);
      if (nest) {
        setContextState(nest.context ?? 'Neutral');
        setCanvasOffsetState(nest.position);
      }
    },
    createMainNest: async (label, moduleId, ctx) => {
      const main = createNest(label, ctx, moduleId, { x: 0, y: 0 });
      const satellite = createNest('Focus Vault', 'Focus', 'timer', { x: 360, y: -180 });
      const travel = createNest('Travel Cache', 'Travel', 'capture', { x: -300, y: 260 });
      setNests([main, { ...satellite, type: 'hidden', passwordHash: 'local_3149094' }, travel]);
      setActiveNestId(main.id);
      setContextState(ctx);
      setCanvasOffsetState(main.position);
      await phantmData.setOnboarded(true);
      setOnboardingComplete(true);
    },
    createNestFromCanvas: (label = 'New Nest') => {
      const next = createNest(label, context, 'notes', { x: canvasOffset.x + 220, y: canvasOffset.y + 80 });
      setNests((items) => [...items, next]);
    },
    updateNest: (id, updates) => setNests((items) => items.map((nest) => nest.id === id ? { ...nest, ...updates, updatedAt: Date.now() } : nest)),
    deleteNest: (id) => setNests((items) => items.filter((nest) => nest.id !== id)),
    importNest: (nest) => setNests((items) => [...items, nest]),
    openModule: setActiveModuleId,
    closeModule: () => setActiveModuleId(null),
    setContext: (ctx) => setContextState(ctx),
    addNote: (title, body) => {
      const next = [{ id: makeId('note'), title: title.trim() || 'Untitled note', body, updatedAt: Date.now() }, ...notes];
      setNotes(next);
      phantmData.saveNotes(next);
    },
    addCapture: (body) => {
      const next = [{ id: makeId('capture'), body, context, createdAt: Date.now() }, ...captures];
      setCaptures(next);
      phantmData.saveCaptures(next);
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
      setNotes([]); setCaptures([]); setVoiceClips([]); setWorkflows(defaultWorkflows);
    },
  }), [hydrated, onboardingComplete, canvasOffset, canvasScale, nests, activeNestId, activeNest, context, activeColor, activeModuleId, isNavigating, navigationDirection, notes, captures, voiceClips, workflows]);

  return <Ctx.Provider value={store}>{children}</Ctx.Provider>;
}

export function usePhantm() {
  const store = useContext(Ctx);
  if (!store) throw new Error('usePhantm must be used inside PhantmProvider');
  return store;
}
