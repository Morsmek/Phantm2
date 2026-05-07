from pathlib import Path

ROOT = Path('/home/ubuntu/phantm')

def write(rel: str, content: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + '\n', encoding='utf-8')

write('lib/canvas-store.tsx', r'''
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
''')

write('components/canvas/InfiniteCanvas.tsx', r'''
import { useMemo, useRef, useState } from 'react';
import { PanResponder, Pressable, StyleSheet, Text, TextInput, View, useWindowDimensions } from 'react-native';
import { useRouter } from 'expo-router';
import MaterialIcons from '@expo/vector-icons/MaterialIcons';
import { CanvasBackground } from '@/components/canvas/CanvasBackground';
import { NestDot } from '@/components/canvas/NestDot';
import { NestNode } from '@/components/canvas/NestNode';
import { NavigationTrail } from '@/components/canvas/NavigationTrail';
import { ContextChip } from '@/components/shared/ContextChip';
import { ModalSheet } from '@/components/shared/ModalSheet';
import { NotesModule } from '@/components/modules/NotesModule';
import { VoiceModule } from '@/components/modules/VoiceModule';
import { CaptureModule } from '@/components/modules/CaptureModule';
import { BrowserModule } from '@/components/modules/BrowserModule';
import { WorkflowModule } from '@/components/modules/WorkflowModule';
import { TimerModule } from '@/components/modules/TimerModule';
import { usePhantm } from '@/lib/canvas-store';
import { phantmHaptics } from '@/lib/phantm-haptics';
import { nearestNest } from '@/lib/nest-utils';
import { MODULE_ICONS, MODULE_LABELS, ModuleId, SlotConfig } from '@/lib/phantm-types';

const QUICK_MODULES: ModuleId[] = ['notes', 'capture', 'timer', 'voice', 'browser', 'workflows'];

function ModuleContent({ id }: { id: ModuleId }) {
  if (id === 'notes') return <NotesModule />;
  if (id === 'voice') return <VoiceModule />;
  if (id === 'capture') return <CaptureModule />;
  if (id === 'browser') return <BrowserModule />;
  if (id === 'workflows') return <WorkflowModule />;
  return <TimerModule />;
}

export function InfiniteCanvas() {
  const router = useRouter();
  const { width, height } = useWindowDimensions();
  const store = usePhantm();
  const start = useRef(store.canvasOffset);
  const [newNestLabel, setNewNestLabel] = useState('');
  const [showAddNest, setShowAddNest] = useState(false);
  const [status, setStatus] = useState('Ready');

  const pan = useMemo(() => PanResponder.create({
    onMoveShouldSetPanResponder: (_, gesture) => store.isNavigating || Math.hypot(gesture.dx, gesture.dy) > 18,
    onPanResponderGrant: () => { start.current = store.canvasOffset; store.setNavigating(true, { x: 0, y: 0 }); },
    onPanResponderMove: (_, gesture) => {
      const speed = 1 + Math.min(2.4, Math.hypot(gesture.dx, gesture.dy) / 160);
      store.setCanvasOffset({ x: start.current.x - gesture.dx * speed, y: start.current.y - gesture.dy * speed });
      store.setNavigating(true, { x: gesture.dx, y: gesture.dy });
    },
    onPanResponderRelease: (_, gesture) => {
      const projected = { x: start.current.x - gesture.dx, y: start.current.y - gesture.dy };
      const hit = nearestNest(store.nests.filter((nest) => nest.type !== 'hidden'), projected, 260);
      if (hit) {
        store.setActiveNest(hit.id);
        setStatus(`Focused ${hit.label}`);
        phantmHaptics.confirm();
      } else {
        setStatus('Canvas moved');
      }
      store.setNavigating(false, null);
    },
    onPanResponderTerminate: () => store.setNavigating(false, null),
  }), [store]);

  function slotPress(slot: SlotConfig) {
    phantmHaptics.confirm();
    if (slot.type === 'module' && slot.moduleId) {
      store.openModule(slot.moduleId);
      setStatus(`Opened ${MODULE_LABELS[slot.moduleId]}`);
    }
    if (slot.type === 'nest-link' && slot.targetNestId) {
      store.setActiveNest(slot.targetNestId);
      setStatus('Opened linked nest');
    }
  }

  function nudge(x: number, y: number) {
    store.moveCanvasBy({ x, y });
    setStatus('Canvas nudged');
    const hit = nearestNest(store.nests.filter((nest) => nest.type !== 'hidden'), { x: store.canvasOffset.x + x, y: store.canvasOffset.y + y }, 180);
    if (hit) store.setActiveNest(hit.id);
  }

  function createNest() {
    const created = store.createNestFromCanvas(newNestLabel || `Nest ${store.nests.length + 1}`);
    setNewNestLabel('');
    setShowAddNest(false);
    setStatus(`Created ${created.label}`);
    phantmHaptics.confirm();
  }

  const active = store.activeNest;
  const moduleTitle = store.activeModuleId ? MODULE_LABELS[store.activeModuleId] : 'Module';

  return (
    <View style={styles.root}>
      <CanvasBackground />
      <NavigationTrail direction={store.navigationDirection} color={store.activeColor} />
      <View style={styles.header}>
        <View style={styles.brand}>
          <MaterialIcons name="blur-on" size={24} color={store.activeColor} />
          <Text style={[styles.wordmark, { color: store.activeColor }]}>PHANTM</Text>
        </View>
        <ContextChip context={store.context} color={store.activeColor} />
      </View>

      {store.nests.filter((nest) => nest.id !== active?.id).map((nest, index) => (
        <NestDot
          key={nest.id}
          nest={nest}
          x={width / 2 + (nest.position.x - store.canvasOffset.x) * 0.22 + (index % 2) * 20}
          y={height / 2 + (nest.position.y - store.canvasOffset.y) * 0.22}
          onPress={() => nest.type === 'hidden' ? router.push(`/nest/${nest.id}/unlock`) : store.setActiveNest(nest.id)}
        />
      ))}

      <View style={styles.centerStage} {...pan.panHandlers}>
        {active ? (
          <NestNode
            nest={active}
            accent={store.activeColor}
            scale={store.canvasScale * (store.isNavigating ? 0.86 : 1)}
            onNavigateStart={() => { store.setNavigating(true, { x: 0, y: 0 }); setStatus('Drag anywhere to move canvas'); }}
            onNavigateEnd={() => store.setNavigating(false, null)}
            onSlotPress={slotPress}
          />
        ) : <Text style={styles.empty}>No nest yet. Complete setup to begin.</Text>}
      </View>

      <View style={styles.sidePanel}>
        <Text style={styles.panelTitle}>Nests</Text>
        {store.nests.slice(0, 5).map((nest) => (
          <Pressable key={nest.id} onPress={() => nest.type === 'hidden' ? router.push(`/nest/${nest.id}/unlock`) : store.setActiveNest(nest.id)} style={[styles.nestPill, nest.id === active?.id && { borderColor: store.activeColor }]}> 
            <Text numberOfLines={1} style={[styles.nestPillText, nest.id === active?.id && { color: store.activeColor }]}>{nest.type === 'hidden' ? 'Locked' : nest.label}</Text>
          </Pressable>
        ))}
      </View>

      <View style={styles.moduleDock}>
        {QUICK_MODULES.map((id) => (
          <Pressable key={id} accessibilityRole="button" accessibilityLabel={`Open ${MODULE_LABELS[id]}`} onPress={() => { store.openModule(id); setStatus(`Opened ${MODULE_LABELS[id]}`); }} style={({ pressed }) => [styles.moduleButton, { borderColor: `${store.activeColor}55` }, pressed && styles.pressed]}> 
            <MaterialIcons name={MODULE_ICONS[id] as never} size={22} color={store.activeColor} />
          </Pressable>
        ))}
      </View>

      <View style={styles.compass}>
        <Pressable onPress={() => nudge(0, -160)} style={styles.compassButton}><MaterialIcons name="keyboard-arrow-up" size={24} color="#DDE3E7" /></Pressable>
        <View style={styles.compassRow}>
          <Pressable onPress={() => nudge(-160, 0)} style={styles.compassButton}><MaterialIcons name="keyboard-arrow-left" size={24} color="#DDE3E7" /></Pressable>
          <Pressable onPress={() => nudge(160, 0)} style={styles.compassButton}><MaterialIcons name="keyboard-arrow-right" size={24} color="#DDE3E7" /></Pressable>
        </View>
        <Pressable onPress={() => nudge(0, 160)} style={styles.compassButton}><MaterialIcons name="keyboard-arrow-down" size={24} color="#DDE3E7" /></Pressable>
      </View>

      <View style={styles.bottom}>
        <Text style={styles.hint}>{store.isNavigating ? 'Release to settle near a nest' : `${status} · drag center space or use controls`}</Text>
        <View style={styles.nav}>
          <Pressable style={styles.navButton} onPress={() => store.setCanvasScale(store.canvasScale - 0.08)}><MaterialIcons name="zoom-out" size={26} color="#9BA6B2" /></Pressable>
          <Pressable style={[styles.navButton, { shadowColor: store.activeColor, shadowOpacity: 0.35 }]} onPress={() => setShowAddNest(true)}><MaterialIcons name="add-circle-outline" size={28} color={store.activeColor} /></Pressable>
          <Pressable style={styles.navButton} onPress={() => active && router.push(`/nest/${active.id}/edit`)}><MaterialIcons name="tune" size={26} color="#9BA6B2" /></Pressable>
          <Pressable style={styles.navButton} onPress={() => router.push('/settings')}><MaterialIcons name="settings" size={26} color="#9BA6B2" /></Pressable>
          <Pressable style={styles.navButton} onPress={() => store.setCanvasScale(store.canvasScale + 0.08)}><MaterialIcons name="zoom-in" size={26} color="#9BA6B2" /></Pressable>
        </View>
      </View>

      {showAddNest ? (
        <ModalSheet title="Create Nest" accent={store.activeColor} onClose={() => setShowAddNest(false)}>
          <View style={styles.addForm}>
            <Text style={styles.addBody}>Create a working local nest near the current canvas position. It becomes active immediately.</Text>
            <TextInput value={newNestLabel} onChangeText={setNewNestLabel} placeholder="Nest name" placeholderTextColor="#6B7880" style={styles.input} returnKeyType="done" onSubmitEditing={createNest} />
            <Pressable onPress={createNest} style={[styles.primaryAction, { backgroundColor: store.activeColor }]}><Text style={styles.primaryActionText}>Create and Focus</Text></Pressable>
          </View>
        </ModalSheet>
      ) : null}

      {store.activeModuleId ? (
        <ModalSheet title={moduleTitle} accent={store.activeColor} onClose={store.closeModule}>
          <ModuleContent id={store.activeModuleId} />
        </ModalSheet>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#05070A', overflow: 'hidden' },
  header: { position: 'absolute', top: 0, left: 0, right: 0, zIndex: 10, paddingTop: 52, paddingHorizontal: 24, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  brand: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  wordmark: { fontSize: 20, fontWeight: '800', letterSpacing: -0.8 },
  centerStage: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  empty: { color: '#9BA6B2' },
  sidePanel: { position: 'absolute', top: 112, left: 16, zIndex: 8, gap: 8, maxWidth: 132 },
  panelTitle: { color: '#BBC9CE88', fontSize: 10, fontWeight: '900', letterSpacing: 1.3, textTransform: 'uppercase' },
  nestPill: { minHeight: 34, justifyContent: 'center', paddingHorizontal: 10, borderRadius: 17, backgroundColor: '#0E141799', borderWidth: 1, borderColor: '#3C494E55' },
  nestPillText: { color: '#DDE3E7', fontSize: 11, fontWeight: '800' },
  moduleDock: { position: 'absolute', top: 118, right: 16, zIndex: 8, gap: 8 },
  moduleButton: { width: 44, height: 44, borderRadius: 22, alignItems: 'center', justifyContent: 'center', backgroundColor: '#0E1417CC', borderWidth: 1 },
  compass: { position: 'absolute', left: 18, bottom: 128, zIndex: 8, alignItems: 'center', gap: 2 },
  compassRow: { flexDirection: 'row', gap: 38 },
  compassButton: { width: 38, height: 38, borderRadius: 19, alignItems: 'center', justifyContent: 'center', backgroundColor: '#0E1417CC', borderWidth: 1, borderColor: '#3C494E55' },
  bottom: { position: 'absolute', left: 0, right: 0, bottom: 28, alignItems: 'center', paddingHorizontal: 28, gap: 12 },
  hint: { color: '#BBC9CE99', fontSize: 11, fontWeight: '700', letterSpacing: 1.1, textTransform: 'uppercase', textAlign: 'center' },
  nav: { minHeight: 64, width: '100%', flexDirection: 'row', alignItems: 'center', justifyContent: 'space-around' },
  navButton: { width: 48, height: 48, borderRadius: 24, alignItems: 'center', justifyContent: 'center', backgroundColor: '#0E141766', shadowRadius: 10 },
  pressed: { opacity: 0.75, transform: [{ scale: 0.96 }] },
  addForm: { gap: 14 },
  addBody: { color: '#9BA6B2', lineHeight: 22 },
  input: { height: 54, borderRadius: 18, borderWidth: 1, borderColor: '#3C494E', backgroundColor: '#1A2123', color: '#DDE3E7', paddingHorizontal: 16 },
  primaryAction: { height: 52, borderRadius: 26, alignItems: 'center', justifyContent: 'center' },
  primaryActionText: { color: '#001F28', fontWeight: '900' },
});
''')

write('app/nest/[id]/edit.tsx', r'''
import { useMemo, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import MaterialIcons from '@expo/vector-icons/MaterialIcons';
import { ScreenContainer } from '@/components/screen-container';
import { usePhantm } from '@/lib/canvas-store';
import { emptySlot, hashPassword, moduleSlot } from '@/lib/nest-utils';
import { CONTEXT_COLORS, ContextMode, MODULE_ICONS, MODULE_LABELS, ModuleId, NestType, SlotConfig } from '@/lib/phantm-types';

const modules: ModuleId[] = ['notes', 'capture', 'timer', 'voice', 'browser', 'workflows'];
const contexts: ContextMode[] = ['Neutral', 'Work', 'Personal', 'Focus', 'Travel'];
const types: NestType[] = ['open', 'hidden', 'shareable'];

type SelectedSlot = { ringIndex: number; slotIndex: number };

export default function EditNestScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const store = usePhantm();
  const nest = store.nests.find((item) => item.id === id);
  const [label, setLabel] = useState(nest?.label ?? '');
  const [context, setContext] = useState<ContextMode>(nest?.context ?? 'Neutral');
  const [type, setType] = useState<NestType>(nest?.type ?? 'open');
  const [password, setPassword] = useState('');
  const [selected, setSelected] = useState<SelectedSlot>({ ringIndex: 1, slotIndex: 0 });
  const [status, setStatus] = useState('Select a slot, then assign a module, nest link, or empty state.');

  const selectedSlot = useMemo(() => nest?.rings.find((ring) => ring.ringIndex === selected.ringIndex)?.slots.find((slot) => slot.slotIndex === selected.slotIndex), [nest, selected]);

  if (!nest) {
    return (
      <ScreenContainer edges={['top', 'bottom', 'left', 'right']} className="p-6" containerClassName="bg-background">
        <View style={styles.card}><Text style={styles.title}>Nest not found</Text><Pressable onPress={() => router.back()} style={styles.secondary}><Text style={styles.secondaryText}>Back</Text></Pressable></View>
      </ScreenContainer>
    );
  }

  function saveMeta() {
    store.updateNest(nest.id, {
      label: label.trim() || 'Untitled Nest',
      context,
      type,
      passwordHash: type === 'hidden' ? (password ? hashPassword(password) : nest.passwordHash ?? hashPassword('314159')) : undefined,
    });
    store.setActiveNest(nest.id);
    setStatus('Nest details saved.');
  }

  function assignModule(moduleId: ModuleId) {
    const next = moduleSlot(selected.slotIndex, moduleId);
    store.assignSlot(nest.id, selected.ringIndex, selected.slotIndex, next);
    setStatus(`${MODULE_LABELS[moduleId]} assigned to ring ${selected.ringIndex}, slot ${selected.slotIndex + 1}.`);
  }

  function assignNestLink(targetNestId: string) {
    const target = store.nests.find((item) => item.id === targetNestId);
    const next: SlotConfig = { slotIndex: selected.slotIndex, type: 'nest-link', targetNestId, label: target?.label ?? 'Linked Nest', iconKey: 'hub' };
    store.assignSlot(nest.id, selected.ringIndex, selected.slotIndex, next);
    setStatus(`Linked slot to ${target?.label ?? 'another nest'}.`);
  }

  function clearSlot() {
    store.assignSlot(nest.id, selected.ringIndex, selected.slotIndex, emptySlot(selected.slotIndex));
    setStatus('Slot cleared.');
  }

  return (
    <ScreenContainer edges={['top', 'bottom', 'left', 'right']} className="p-5" containerClassName="bg-background">
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        <View style={styles.header}>
          <Pressable onPress={() => router.back()} style={styles.back}><Text style={styles.backText}>Back</Text></Pressable>
          <Text style={styles.kicker}>Nest Editor</Text>
          <Text style={styles.title}>{nest.label}</Text>
          <Text style={styles.body}>Edit the nest identity and configure real ring slots. Changes write directly to the local canvas.</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>Nest Details</Text>
          <TextInput value={label} onChangeText={setLabel} placeholder="Nest label" placeholderTextColor="#6B7880" style={styles.input} />
          <View style={styles.grid}>{contexts.map((item) => <Pressable key={item} onPress={() => setContext(item)} style={[styles.choice, context === item && { borderColor: CONTEXT_COLORS[item], backgroundColor: `${CONTEXT_COLORS[item]}18` }]}><Text style={[styles.choiceText, { color: CONTEXT_COLORS[item] }]}>{item}</Text></Pressable>)}</View>
          <View style={styles.grid}>{types.map((item) => <Pressable key={item} onPress={() => setType(item)} style={[styles.choice, type === item && { borderColor: '#39D5FF', backgroundColor: '#39D5FF18' }]}><Text style={styles.choiceText}>{item}</Text></Pressable>)}</View>
          {type === 'hidden' ? <TextInput secureTextEntry value={password} onChangeText={setPassword} placeholder="Hidden nest password" placeholderTextColor="#6B7880" style={styles.input} /> : null}
          <Pressable onPress={saveMeta} style={[styles.primary, { backgroundColor: CONTEXT_COLORS[context] }]}><Text style={styles.primaryText}>Save Details</Text></Pressable>
        </View>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>Ring Slots</Text>
          <Text style={styles.cardBody}>Selected: ring {selected.ringIndex}, slot {selected.slotIndex + 1}. Current: {selectedSlot?.label ?? 'Empty'}.</Text>
          {nest.rings.map((ring) => (
            <View key={ring.ringIndex} style={styles.ringBlock}>
              <Text style={styles.section}>Ring {ring.ringIndex}</Text>
              <View style={styles.slotGrid}>{ring.slots.map((slot) => {
                const isSelected = selected.ringIndex === ring.ringIndex && selected.slotIndex === slot.slotIndex;
                return <Pressable key={`${ring.ringIndex}-${slot.slotIndex}`} onPress={() => setSelected({ ringIndex: ring.ringIndex, slotIndex: slot.slotIndex })} style={[styles.slotChoice, isSelected && { borderColor: CONTEXT_COLORS[context], backgroundColor: `${CONTEXT_COLORS[context]}18` }]}>
                  <MaterialIcons name={(slot.iconKey || 'radio-button-unchecked') as never} size={18} color={isSelected ? CONTEXT_COLORS[context] : '#9BA6B2'} />
                  <Text numberOfLines={1} style={[styles.slotText, isSelected && { color: CONTEXT_COLORS[context] }]}>{slot.label || `Slot ${slot.slotIndex + 1}`}</Text>
                </Pressable>;
              })}</View>
            </View>
          ))}
        </View>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>Assign Selected Slot</Text>
          <Text style={styles.section}>Modules</Text>
          <View style={styles.grid}>{modules.map((moduleId) => <Pressable key={moduleId} onPress={() => assignModule(moduleId)} style={styles.moduleChoice}><MaterialIcons name={MODULE_ICONS[moduleId] as never} size={20} color={CONTEXT_COLORS[context]} /><Text style={styles.choiceText}>{MODULE_LABELS[moduleId]}</Text></Pressable>)}</View>
          <Text style={styles.section}>Nest Link</Text>
          <View style={styles.grid}>{store.nests.filter((item) => item.id !== nest.id && item.type !== 'hidden').map((item) => <Pressable key={item.id} onPress={() => assignNestLink(item.id)} style={styles.choice}><Text numberOfLines={1} style={styles.choiceText}>{item.label}</Text></Pressable>)}</View>
          <Pressable onPress={clearSlot} style={styles.danger}><Text style={styles.dangerText}>Clear Selected Slot</Text></Pressable>
          <Text style={styles.status}>{status}</Text>
        </View>
      </ScrollView>
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  content: { gap: 16, paddingBottom: 36 },
  header: { gap: 9 },
  back: { alignSelf: 'flex-start', height: 40, paddingHorizontal: 16, borderRadius: 20, backgroundColor: '#1A2123', justifyContent: 'center' },
  backText: { color: '#39D5FF', fontWeight: '800' },
  kicker: { color: '#39D5FF', fontSize: 11, fontWeight: '800', letterSpacing: 1.5, textTransform: 'uppercase' },
  title: { color: '#DDE3E7', fontSize: 38, fontWeight: '300', letterSpacing: -1.8 },
  body: { color: '#9BA6B2', lineHeight: 23 },
  card: { padding: 16, borderRadius: 24, backgroundColor: '#0E1417', borderWidth: 1, borderColor: '#2F3638', gap: 12 },
  cardTitle: { color: '#DDE3E7', fontSize: 18, fontWeight: '800' },
  cardBody: { color: '#9BA6B2', lineHeight: 21 },
  input: { height: 54, borderRadius: 18, borderWidth: 1, borderColor: '#3C494E', backgroundColor: '#1A2123', color: '#DDE3E7', paddingHorizontal: 16 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  choice: { minHeight: 42, paddingHorizontal: 13, borderRadius: 21, borderWidth: 1, borderColor: '#3C494E', backgroundColor: '#1A2123', alignItems: 'center', justifyContent: 'center' },
  choiceText: { color: '#DDE3E7', fontWeight: '800' },
  primary: { height: 50, borderRadius: 25, alignItems: 'center', justifyContent: 'center' },
  primaryText: { color: '#001F28', fontWeight: '900' },
  section: { color: '#9BA6B2', fontSize: 11, fontWeight: '900', letterSpacing: 1.2, textTransform: 'uppercase' },
  ringBlock: { gap: 8 },
  slotGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  slotChoice: { width: '30%', minWidth: 88, height: 58, paddingHorizontal: 8, borderRadius: 18, borderWidth: 1, borderColor: '#3C494E', backgroundColor: '#1A2123', alignItems: 'center', justifyContent: 'center', gap: 4 },
  slotText: { color: '#9BA6B2', fontSize: 10, fontWeight: '800', textAlign: 'center' },
  moduleChoice: { minHeight: 46, paddingHorizontal: 13, borderRadius: 23, borderWidth: 1, borderColor: '#3C494E', backgroundColor: '#1A2123', flexDirection: 'row', alignItems: 'center', gap: 8 },
  danger: { height: 46, borderRadius: 23, alignItems: 'center', justifyContent: 'center', backgroundColor: '#FF5C7A22', borderWidth: 1, borderColor: '#FF5C7A55' },
  dangerText: { color: '#FF5C7A', fontWeight: '900' },
  secondary: { height: 46, borderRadius: 23, alignItems: 'center', justifyContent: 'center', backgroundColor: '#1A2123' },
  secondaryText: { color: '#DDE3E7', fontWeight: '800' },
  status: { color: '#39D5FF', lineHeight: 21 },
});
''')

write('app/nest/[id]/unlock.tsx', r'''
import { useState } from 'react';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { ScreenContainer } from '@/components/screen-container';
import { usePhantm } from '@/lib/canvas-store';
import { hashPassword } from '@/lib/nest-utils';

export default function UnlockNest() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const store = usePhantm();
  const nest = store.nests.find((item) => item.id === id);
  const [pw, setPw] = useState('');
  const [error, setError] = useState('');

  function unlock() {
    if (!nest) {
      setError('This nest no longer exists.');
      return;
    }
    if (!nest.passwordHash || nest.passwordHash === hashPassword(pw)) {
      store.setActiveNest(nest.id);
      router.replace('/');
      return;
    }
    setError('Password did not match. The demo Focus Vault password is 314159 unless changed in the editor.');
  }

  return (
    <ScreenContainer edges={['top', 'bottom', 'left', 'right']} className="p-6 justify-center" containerClassName="bg-background">
      <View style={styles.card}>
        <Text style={styles.kicker}>Hidden Nest</Text>
        <Text style={styles.title}>{nest?.label ?? 'Locked'}</Text>
        <Text style={styles.body}>Enter the local password to reveal this hidden nest on the canvas.</Text>
        <TextInput secureTextEntry value={pw} onChangeText={setPw} placeholder="Password" placeholderTextColor="#6B7880" style={styles.input} returnKeyType="done" onSubmitEditing={unlock} />
        {error ? <Text style={styles.error}>{error}</Text> : null}
        <Pressable onPress={unlock} style={styles.button}><Text style={styles.buttonText}>Unlock</Text></Pressable>
        <Pressable onPress={() => router.back()} style={styles.cancel}><Text style={styles.cancelText}>Cancel</Text></Pressable>
      </View>
    </ScreenContainer>
  );
}
const styles = StyleSheet.create({ card: { gap: 14, padding: 20, borderRadius: 28, backgroundColor: '#0E1417', borderWidth: 1, borderColor: '#FF5C7A44' }, kicker: { color: '#FF5C7A', fontSize: 11, fontWeight: '800', letterSpacing: 1.5, textTransform: 'uppercase' }, title: { color: '#DDE3E7', fontSize: 34, fontWeight: '300', letterSpacing: -1.4 }, body: { color: '#9BA6B2', lineHeight: 22 }, input: { height: 54, borderRadius: 18, borderWidth: 1, borderColor: '#3C494E', backgroundColor: '#1A2123', color: '#DDE3E7', paddingHorizontal: 16 }, error: { color: '#FF5C7A', lineHeight: 21 }, button: { height: 52, borderRadius: 26, alignItems: 'center', justifyContent: 'center', backgroundColor: '#FF5C7A' }, buttonText: { color: '#2B0007', fontWeight: '900' }, cancel: { height: 44, alignItems: 'center', justifyContent: 'center' }, cancelText: { color: '#9BA6B2', fontWeight: '800' } });
''')

write('lib/phantm-actions.ts', r'''
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
''')

write('lib/phantm-actions.test.ts', r'''
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
''')
print('PHANTM functionality repair files written.')
