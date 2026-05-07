from pathlib import Path
import textwrap

ROOT = Path('/home/ubuntu/phantm')

def write(rel, content):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding='utf-8')

write('theme.config.js', r'''
/** @type {const} */
const themeColors = {
  primary: { light: '#39D5FF', dark: '#39D5FF' },
  background: { light: '#05070A', dark: '#05070A' },
  surface: { light: '#0E1417', dark: '#0E1417' },
  foreground: { light: '#DDE3E7', dark: '#DDE3E7' },
  muted: { light: '#9BA6B2', dark: '#9BA6B2' },
  border: { light: '#3C494E', dark: '#3C494E' },
  success: { light: '#36D6A1', dark: '#36D6A1' },
  warning: { light: '#F6B73C', dark: '#F6B73C' },
  error: { light: '#FF5C7A', dark: '#FF5C7A' },
};

module.exports = { themeColors };
''')

write('lib/phantm-types.ts', r'''
export type ContextMode = 'Neutral' | 'Work' | 'Personal' | 'Focus' | 'Travel';
export type NestType = 'open' | 'hidden' | 'shareable';
export type SlotType = 'app' | 'module' | 'empty' | 'nest-link';
export type ModuleId = 'notes' | 'voice' | 'capture' | 'browser' | 'workflows' | 'timer';

export type CanvasPoint = { x: number; y: number };

export type SlotConfig = {
  slotIndex: number;
  type: SlotType;
  label: string;
  iconKey?: string;
  moduleId?: ModuleId;
  targetNestId?: string;
  appPackage?: string;
};

export type RingConfig = {
  ringIndex: number;
  slots: SlotConfig[];
};

export type NestRecord = {
  id: string;
  label: string;
  type: NestType;
  position: CanvasPoint;
  rings: RingConfig[];
  passwordHash?: string;
  shareCode?: string;
  createdAt: number;
  updatedAt: number;
  context?: ContextMode;
};

export type CanvasState = {
  nests: NestRecord[];
  lastViewportPosition: CanvasPoint;
  lastScale: number;
};

export type NoteEntry = { id: string; title: string; body: string; updatedAt: number };
export type CaptureEntry = { id: string; body: string; context: ContextMode; createdAt: number };
export type VoiceClip = { id: string; label: string; uri?: string; createdAt: number; durationLabel: string };
export type WorkflowStep = { id: string; label: string; detail: string; complete: boolean };
export type WorkflowTemplate = { id: string; name: string; context: ContextMode; description: string; steps: WorkflowStep[] };

export const CONTEXT_COLORS: Record<ContextMode, string> = {
  Neutral: '#39D5FF',
  Work: '#4F8CFF',
  Personal: '#A77BFF',
  Focus: '#F6B73C',
  Travel: '#36D6A1',
};

export const MODULE_LABELS: Record<ModuleId, string> = {
  notes: 'Notes',
  voice: 'Voice',
  capture: 'Capture',
  browser: 'Browser',
  workflows: 'Workflows',
  timer: 'Timer',
};

export const MODULE_ICONS: Record<ModuleId, string> = {
  notes: 'edit-note',
  voice: 'mic',
  capture: 'bolt',
  browser: 'public',
  workflows: 'account-tree',
  timer: 'timer',
};
''')

write('lib/nest-utils.ts', r'''
import { CanvasPoint, ContextMode, MODULE_ICONS, MODULE_LABELS, ModuleId, NestRecord, RingConfig, SlotConfig } from '@/lib/phantm-types';

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
''')

write('lib/phantm-data.ts', r'''
import AsyncStorage from '@react-native-async-storage/async-storage';
import { CaptureEntry, CanvasState, NoteEntry, VoiceClip, WorkflowTemplate } from '@/lib/phantm-types';

const KEYS = {
  canvas: 'phantm.canvas.v2',
  onboarded: 'phantm.onboarded.v2',
  notes: 'phantm.notes.v2',
  captures: 'phantm.captures.v2',
  voice: 'phantm.voice.v2',
  workflows: 'phantm.workflows.v2',
};

async function getJson<T>(key: string, fallback: T): Promise<T> {
  const value = await AsyncStorage.getItem(key);
  return value ? (JSON.parse(value) as T) : fallback;
}

async function setJson<T>(key: string, value: T) {
  await AsyncStorage.setItem(key, JSON.stringify(value));
}

export const phantmData = {
  keys: KEYS,
  getOnboarded: async () => (await AsyncStorage.getItem(KEYS.onboarded)) === 'true',
  setOnboarded: async (value: boolean) => AsyncStorage.setItem(KEYS.onboarded, value ? 'true' : 'false'),
  loadCanvas: (fallback: CanvasState) => getJson(KEYS.canvas, fallback),
  saveCanvas: (state: CanvasState) => setJson(KEYS.canvas, state),
  loadNotes: () => getJson<NoteEntry[]>(KEYS.notes, []),
  saveNotes: (notes: NoteEntry[]) => setJson(KEYS.notes, notes),
  loadCaptures: () => getJson<CaptureEntry[]>(KEYS.captures, []),
  saveCaptures: (captures: CaptureEntry[]) => setJson(KEYS.captures, captures),
  loadVoice: () => getJson<VoiceClip[]>(KEYS.voice, []),
  saveVoice: (clips: VoiceClip[]) => setJson(KEYS.voice, clips),
  loadWorkflows: () => getJson<WorkflowTemplate[]>(KEYS.workflows, []),
  saveWorkflows: (workflows: WorkflowTemplate[]) => setJson(KEYS.workflows, workflows),
  resetLocal: async () => {
    await AsyncStorage.multiRemove(Object.values(KEYS));
  },
};
''')

write('lib/phantm-haptics.ts', r'''
import { Platform } from 'react-native';
import * as Haptics from 'expo-haptics';

const native = Platform.OS !== 'web';

export const phantmHaptics = {
  tick: () => native && Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light),
  confirm: () => native && Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success),
  warning: () => native && Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning),
  boundary: () => native && Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error),
  contextSwitch: () => native && Haptics.selectionAsync(),
};
''')

write('lib/canvas-store.tsx', r'''
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
''')

write('components/shared/ContextChip.tsx', r'''
import { Text, View, StyleSheet } from 'react-native';
import { ContextMode } from '@/lib/phantm-types';

export function ContextChip({ context, color }: { context: ContextMode; color: string }) {
  return (
    <View style={[styles.chip, { borderColor: `${color}40`, backgroundColor: `${color}12` }]}>
      <View style={[styles.dot, { backgroundColor: color }]} />
      <Text style={[styles.text, { color }]}>{context}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  chip: { minHeight: 32, paddingHorizontal: 14, borderRadius: 999, borderWidth: 1, flexDirection: 'row', alignItems: 'center', gap: 8 },
  dot: { width: 6, height: 6, borderRadius: 3 },
  text: { fontSize: 11, fontWeight: '700', letterSpacing: 1.4, textTransform: 'uppercase' },
});
''')

write('components/shared/ModalSheet.tsx', r'''
import { PropsWithChildren } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import MaterialIcons from '@expo/vector-icons/MaterialIcons';

export function ModalSheet({ title, accent, onClose, children }: PropsWithChildren<{ title: string; accent: string; onClose: () => void }>) {
  const insets = useSafeAreaInsets();
  return (
    <View style={styles.overlay}>
      <Pressable style={StyleSheet.absoluteFill} onPress={onClose} />
      <View style={[styles.sheet, { paddingBottom: Math.max(insets.bottom, 16) }]}> 
        <View style={styles.grabber} />
        <View style={styles.header}>
          <Text style={styles.title}>{title}</Text>
          <Pressable onPress={onClose} style={({ pressed }) => [styles.close, pressed && styles.pressed]}>
            <MaterialIcons name="expand-more" color={accent} size={28} />
          </Pressable>
        </View>
        {children}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  overlay: { ...StyleSheet.absoluteFillObject, justifyContent: 'flex-end', backgroundColor: 'rgba(5,7,10,0.52)', zIndex: 40 },
  sheet: { maxHeight: '78%', minHeight: '48%', borderTopLeftRadius: 34, borderTopRightRadius: 34, backgroundColor: '#0E1417', borderWidth: 1, borderColor: '#253138', paddingHorizontal: 20, paddingTop: 10 },
  grabber: { width: 42, height: 4, borderRadius: 999, backgroundColor: '#3C494E', alignSelf: 'center', marginBottom: 14 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 },
  title: { color: '#DDE3E7', fontSize: 22, fontWeight: '700', letterSpacing: -0.3 },
  close: { width: 44, height: 44, borderRadius: 22, alignItems: 'center', justifyContent: 'center', backgroundColor: '#1A2123' },
  pressed: { opacity: 0.72, transform: [{ scale: 0.97 }] },
});
''')

write('components/canvas/CanvasBackground.tsx', r'''
import { StyleSheet, View, useWindowDimensions } from 'react-native';

export function CanvasBackground() {
  const { width, height } = useWindowDimensions();
  const dots = [];
  const spacing = 24;
  for (let x = 0; x < width + spacing; x += spacing) {
    for (let y = 0; y < height + spacing; y += spacing) dots.push(`${x}-${y}`);
  }
  return (
    <View style={StyleSheet.absoluteFill}>
      {dots.map((key) => {
        const [x, y] = key.split('-').map(Number);
        return <View key={key} style={[styles.dot, { left: x, top: y }]} />;
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  dot: { position: 'absolute', width: 1.5, height: 1.5, borderRadius: 1, backgroundColor: '#0D1117' },
});
''')

write('components/canvas/NestDot.tsx', r'''
import { Pressable, StyleSheet } from 'react-native';
import { NestRecord } from '@/lib/phantm-types';

export function NestDot({ nest, x, y, onPress }: { nest: NestRecord; x: number; y: number; onPress: () => void }) {
  const locked = nest.type === 'hidden';
  return <Pressable accessibilityLabel={`Navigate to ${nest.label}`} onPress={onPress} style={[styles.dot, { left: x, top: y, backgroundColor: locked ? '#FF5C7A55' : '#3A455055' }]} />;
}

const styles = StyleSheet.create({
  dot: { position: 'absolute', width: 8, height: 8, borderRadius: 4, borderWidth: 1, borderColor: '#9BA6B222' },
});
''')

write('components/canvas/NavigationTrail.tsx', r'''
import Svg, { Line } from 'react-native-svg';
import { StyleSheet } from 'react-native';
import { CanvasPoint } from '@/lib/phantm-types';

export function NavigationTrail({ direction, color }: { direction: CanvasPoint | null; color: string }) {
  if (!direction) return null;
  return (
    <Svg pointerEvents="none" style={StyleSheet.absoluteFill}>
      <Line x1="50%" y1="50%" x2={`${50 + Math.max(-35, Math.min(35, direction.x / 4))}%`} y2={`${50 + Math.max(-35, Math.min(35, direction.y / 4))}%`} stroke={`${color}66`} strokeWidth={2} strokeDasharray="6 10" />
    </Svg>
  );
}
''')

write('components/canvas/SlotArc.tsx', r'''
import { Pressable, StyleSheet, Text, View } from 'react-native';
import MaterialIcons from '@expo/vector-icons/MaterialIcons';
import { SlotConfig } from '@/lib/phantm-types';

export function SlotArc({ slot, size, angle, accent, onPress }: { slot: SlotConfig; size: number; angle: number; accent: string; onPress: () => void }) {
  const radius = size / 2;
  const x = Math.cos(angle) * radius;
  const y = Math.sin(angle) * radius;
  const active = slot.type !== 'empty';
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={slot.label}
      onPress={onPress}
      style={({ pressed }) => [styles.slot, { transform: [{ translateX: x }, { translateY: y }], borderColor: active ? `${accent}55` : '#86939822', backgroundColor: active ? '#0E1417CC' : '#0E141766' }, pressed && styles.pressed]}
    >
      {active ? <MaterialIcons name={(slot.iconKey as any) ?? 'radio-button-unchecked'} size={22} color={accent} /> : <View style={styles.emptyDot} />}
      {active ? <Text numberOfLines={1} style={[styles.label, { color: accent }]}>{slot.label}</Text> : null}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  slot: { position: 'absolute', left: '50%', top: '50%', width: 48, height: 48, marginLeft: -24, marginTop: -24, borderRadius: 24, borderWidth: 1, alignItems: 'center', justifyContent: 'center', shadowColor: '#39D5FF', shadowOpacity: 0.22, shadowRadius: 12 },
  pressed: { opacity: 0.75, transform: [{ scale: 0.96 }] },
  emptyDot: { width: 5, height: 5, borderRadius: 3, backgroundColor: '#86939844' },
  label: { position: 'absolute', top: 52, fontSize: 9, fontWeight: '700', letterSpacing: 1, textTransform: 'uppercase', opacity: 0.72 },
});
''')

write('components/canvas/RingLayer.tsx', r'''
import { StyleSheet, View } from 'react-native';
import Svg, { Circle } from 'react-native-svg';
import { RingConfig, SlotConfig } from '@/lib/phantm-types';
import { SlotArc } from '@/components/canvas/SlotArc';

export function RingLayer({ ring, size, accent, onSlotPress }: { ring: RingConfig; size: number; accent: string; onSlotPress: (slot: SlotConfig) => void }) {
  return (
    <View pointerEvents="box-none" style={[styles.ring, { width: size, height: size, marginLeft: -size / 2, marginTop: -size / 2 }]}> 
      <Svg style={StyleSheet.absoluteFill} width={size} height={size}>
        <Circle cx={size / 2} cy={size / 2} r={size / 2 - 1} stroke="#86939824" strokeWidth={1} fill="transparent" />
      </Svg>
      {ring.slots.map((slot, index) => (
        <SlotArc key={`${ring.ringIndex}-${slot.slotIndex}`} slot={slot} size={size} angle={-Math.PI / 2 + (index / ring.slots.length) * Math.PI * 2} accent={accent} onPress={() => onSlotPress(slot)} />
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  ring: { position: 'absolute', left: '50%', top: '50%', borderRadius: 999 },
});
''')

write('components/canvas/NestNode.tsx', r'''
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useRouter } from 'expo-router';
import { RingLayer } from '@/components/canvas/RingLayer';
import { NestRecord, SlotConfig } from '@/lib/phantm-types';
import { phantmHaptics } from '@/lib/phantm-haptics';

export function NestNode({ nest, accent, scale, onNavigateStart, onNavigateEnd, onSlotPress }: { nest: NestRecord; accent: string; scale: number; onNavigateStart: () => void; onNavigateEnd: () => void; onSlotPress: (slot: SlotConfig) => void }) {
  const router = useRouter();
  return (
    <View style={[styles.wrap, { transform: [{ scale }] }]}> 
      {nest.rings.map((ring) => <RingLayer key={ring.ringIndex} ring={ring} size={ring.ringIndex === 1 ? 180 : 320} accent={accent} onSlotPress={onSlotPress} />)}
      <Pressable
        accessibilityLabel="Center node. Hold and drag to navigate."
        onLongPress={() => { phantmHaptics.tick(); onNavigateStart(); }}
        delayLongPress={300}
        onPressOut={onNavigateEnd}
        onPress={() => phantmHaptics.tick()}
        style={({ pressed }) => [styles.center, { backgroundColor: accent, shadowColor: accent }, pressed && styles.centerPressed]}
      >
        <View style={styles.core} />
      </Pressable>
      <Pressable onPress={() => router.push(`/nest/${nest.id}/edit`)} style={({ pressed }) => [styles.labelCard, pressed && styles.centerPressed]}>
        <Text style={styles.label}>{nest.label}</Text>
        <Text style={styles.meta}>Edit nest</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { width: 340, height: 390, alignItems: 'center', justifyContent: 'center' },
  center: { zIndex: 3, width: 34, height: 34, borderRadius: 17, alignItems: 'center', justifyContent: 'center', shadowOpacity: 0.45, shadowRadius: 22, elevation: 8 },
  core: { width: 13, height: 13, borderRadius: 7, backgroundColor: '#003543' },
  centerPressed: { opacity: 0.75, transform: [{ scale: 0.97 }] },
  labelCard: { position: 'absolute', bottom: 0, alignItems: 'center', gap: 2, minWidth: 160, paddingVertical: 10, paddingHorizontal: 16, borderRadius: 22, backgroundColor: '#0E141799', borderWidth: 1, borderColor: '#3C494E55' },
  label: { color: '#DDE3E7', fontSize: 15, fontWeight: '700' },
  meta: { color: '#9BA6B2', fontSize: 10, letterSpacing: 1, textTransform: 'uppercase' },
});
''')

write('components/modules/NotesModule.tsx', r'''
import { useState } from 'react';
import { FlatList, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { usePhantm } from '@/lib/canvas-store';

export function NotesModule() {
  const { notes, addNote, activeColor } = usePhantm();
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  return <View style={styles.wrap}><TextInput placeholder="Note title" placeholderTextColor="#6B7880" value={title} onChangeText={setTitle} style={styles.input} /><TextInput placeholder="Markdown or plain text" placeholderTextColor="#6B7880" value={body} onChangeText={setBody} multiline style={[styles.input, styles.body]} /><Pressable style={({pressed})=>[styles.button,{backgroundColor:activeColor},pressed&&styles.pressed]} onPress={()=>{ if(title.trim()||body.trim()){ addNote(title, body); setTitle(''); setBody(''); }}}><Text style={styles.buttonText}>Save Note</Text></Pressable><FlatList data={notes} keyExtractor={(item)=>item.id} renderItem={({item})=><View style={styles.card}><Text style={styles.cardTitle}>{item.title}</Text><Text style={styles.cardBody}>{item.body || 'No body text yet.'}</Text></View>} ListEmptyComponent={<Text style={styles.empty}>No notes yet. Capture your first thought.</Text>} /></View>;
}
const styles=StyleSheet.create({wrap:{gap:10,flex:1},input:{minHeight:48,borderRadius:18,borderWidth:1,borderColor:'#3C494E',backgroundColor:'#1A2123',color:'#DDE3E7',paddingHorizontal:14,paddingVertical:10},body:{height:96,textAlignVertical:'top'},button:{height:48,borderRadius:24,alignItems:'center',justifyContent:'center'},buttonText:{color:'#001F28',fontWeight:'800'},pressed:{opacity:.75,transform:[{scale:.98}]},card:{padding:14,borderRadius:18,backgroundColor:'#1A2123',borderWidth:1,borderColor:'#2F3638',marginTop:10},cardTitle:{color:'#DDE3E7',fontWeight:'700',fontSize:16},cardBody:{color:'#9BA6B2',marginTop:4,lineHeight:20},empty:{color:'#9BA6B2',textAlign:'center',marginTop:20}});
''')

write('components/modules/CaptureModule.tsx', r'''
import { useState } from 'react';
import { FlatList, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { usePhantm } from '@/lib/canvas-store';

export function CaptureModule(){const{captures,addCapture,activeColor}=usePhantm();const[body,setBody]=useState('');return <View style={styles.wrap}><TextInput placeholder="Capture something quickly" placeholderTextColor="#6B7880" value={body} onChangeText={setBody} style={styles.input}/><Pressable style={({pressed})=>[styles.button,{backgroundColor:activeColor},pressed&&styles.pressed]} onPress={()=>{if(body.trim()){addCapture(body);setBody('')}}}><Text style={styles.buttonText}>Capture</Text></Pressable><FlatList data={captures} keyExtractor={i=>i.id} renderItem={({item})=><View style={styles.card}><Text style={styles.context}>{item.context}</Text><Text style={styles.body}>{item.body}</Text></View>} ListEmptyComponent={<Text style={styles.empty}>No captures yet.</Text>}/></View>}
const styles=StyleSheet.create({wrap:{gap:10,flex:1},input:{minHeight:50,borderRadius:18,borderWidth:1,borderColor:'#3C494E',backgroundColor:'#1A2123',color:'#DDE3E7',paddingHorizontal:14},button:{height:48,borderRadius:24,alignItems:'center',justifyContent:'center'},buttonText:{color:'#001F28',fontWeight:'800'},pressed:{opacity:.75,transform:[{scale:.98}]},card:{padding:14,borderRadius:18,backgroundColor:'#1A2123',borderWidth:1,borderColor:'#2F3638',marginTop:10},context:{color:'#39D5FF',fontSize:10,fontWeight:'800',letterSpacing:1.4,textTransform:'uppercase'},body:{color:'#DDE3E7',marginTop:4,lineHeight:20},empty:{color:'#9BA6B2',textAlign:'center',marginTop:20}})
''')

write('components/modules/TimerModule.tsx', r'''
import { useEffect, useMemo, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useKeepAwake } from 'expo-keep-awake';
import { phantmHaptics } from '@/lib/phantm-haptics';

export function TimerModule(){useKeepAwake();const[seconds,setSeconds]=useState(25*60);const[running,setRunning]=useState(false);useEffect(()=>{if(!running)return;const id=setInterval(()=>setSeconds(s=>{if(s<=1){setRunning(false);phantmHaptics.confirm();return 0}return s-1}),1000);return()=>clearInterval(id)},[running]);const label=useMemo(()=>`${Math.floor(seconds/60).toString().padStart(2,'0')}:${(seconds%60).toString().padStart(2,'0')}`,[seconds]);return <View style={styles.wrap}><Text style={styles.timer}>{label}</Text><Text style={styles.sub}>Focus interval with quiet visual feedback.</Text><View style={styles.row}>{[15,25,45].map(min=><Pressable key={min} onPress={()=>{setSeconds(min*60);setRunning(false)}} style={styles.preset}><Text style={styles.presetText}>{min}m</Text></Pressable>)}</View><View style={styles.row}><Pressable style={[styles.main,{backgroundColor:'#F6B73C'}]} onPress={()=>{phantmHaptics.tick();setRunning(v=>!v)}}><Text style={styles.mainText}>{running?'Pause':'Start'}</Text></Pressable><Pressable style={styles.reset} onPress={()=>{setRunning(false);setSeconds(25*60)}}><Text style={styles.resetText}>Reset</Text></Pressable></View></View>}
const styles=StyleSheet.create({wrap:{alignItems:'center',gap:18},timer:{color:'#F6B73C',fontSize:64,fontWeight:'300',letterSpacing:-2},sub:{color:'#9BA6B2'},row:{flexDirection:'row',gap:10},preset:{height:42,paddingHorizontal:18,borderRadius:21,backgroundColor:'#1A2123',alignItems:'center',justifyContent:'center',borderWidth:1,borderColor:'#3C494E'},presetText:{color:'#DDE3E7',fontWeight:'700'},main:{height:50,paddingHorizontal:32,borderRadius:25,alignItems:'center',justifyContent:'center'},mainText:{color:'#281800',fontWeight:'900'},reset:{height:50,paddingHorizontal:26,borderRadius:25,alignItems:'center',justifyContent:'center',backgroundColor:'#1A2123'},resetText:{color:'#DDE3E7',fontWeight:'800'}})
''')

write('components/modules/BrowserModule.tsx', r'''
import { useState } from 'react';
import { Platform, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import * as WebBrowser from 'expo-web-browser';
import { usePhantm } from '@/lib/canvas-store';

export function BrowserModule(){const{activeColor}=usePhantm();const[url,setUrl]=useState('https://expo.dev');const[status,setStatus]=useState('Ready to open a URL.');async function open(){const target=url.startsWith('http')?url:`https://${url}`;try{await WebBrowser.openBrowserAsync(target);setStatus(Platform.OS==='web'?'Opened in a browser tab.':'Opened in the in-app browser.')}catch(e){setStatus('Could not open that URL. Check the address and try again.')}}return <View style={styles.wrap}><TextInput autoCapitalize="none" keyboardType="url" placeholder="https://example.com" placeholderTextColor="#6B7880" value={url} onChangeText={setUrl} style={styles.input}/><Pressable onPress={open} style={({pressed})=>[styles.button,{backgroundColor:activeColor},pressed&&styles.pressed]}><Text style={styles.buttonText}>Open Browser</Text></Pressable><Text style={styles.status}>{status}</Text><Text style={styles.note}>PHANTM keeps browser access inside a module flow so the canvas remains the primary home.</Text></View>}
const styles=StyleSheet.create({wrap:{gap:14},input:{minHeight:52,borderRadius:18,borderWidth:1,borderColor:'#3C494E',backgroundColor:'#1A2123',color:'#DDE3E7',paddingHorizontal:14},button:{height:50,borderRadius:25,alignItems:'center',justifyContent:'center'},buttonText:{color:'#001F28',fontWeight:'900'},pressed:{opacity:.75,transform:[{scale:.98}]},status:{color:'#DDE3E7',fontWeight:'700'},note:{color:'#9BA6B2',lineHeight:21}})
''')

write('components/modules/VoiceModule.tsx', r'''
import { useEffect, useState } from 'react';
import { FlatList, Platform, Pressable, StyleSheet, Text, View } from 'react-native';
import { RecordingPresets, requestRecordingPermissionsAsync, setAudioModeAsync, useAudioRecorder, useAudioRecorderState } from 'expo-audio';
import { usePhantm } from '@/lib/canvas-store';
import { makeId } from '@/lib/nest-utils';

export function VoiceModule(){const{voiceClips,addVoiceClip,activeColor}=usePhantm();const recorder=useAudioRecorder(RecordingPresets.HIGH_QUALITY);const state=useAudioRecorderState(recorder);const[status,setStatus]=useState('Ready.');useEffect(()=>{setAudioModeAsync({playsInSilentMode:true,allowsRecording:true}).catch(()=>undefined)},[]);async function toggle(){if(Platform.OS==='web'){setStatus('Recording UI is available, but reliable microphone capture depends on the browser and secure device permissions.');return}if(state.isRecording){await recorder.stop();addVoiceClip({id:makeId('clip'),label:`Voice clip ${voiceClips.length+1}`,uri:recorder.uri ?? undefined,createdAt:Date.now(),durationLabel:'Saved'});setStatus('Recording saved locally.')}else{const permission=await requestRecordingPermissionsAsync();if(!permission.granted){setStatus('Microphone permission was denied.');return}await recorder.prepareToRecordAsync();recorder.record();setStatus('Recording…')}}return <View style={styles.wrap}><Pressable style={({pressed})=>[styles.record,{borderColor:activeColor,backgroundColor:state.isRecording?'#FF5C7A22':'#1A2123'},pressed&&styles.pressed]} onPress={toggle}><Text style={[styles.recordText,{color:state.isRecording?'#FF5C7A':activeColor}]}>{state.isRecording?'Stop Recording':'Start Recording'}</Text></Pressable><Text style={styles.status}>{status}</Text><FlatList data={voiceClips} keyExtractor={i=>i.id} renderItem={({item})=><View style={styles.card}><Text style={styles.title}>{item.label}</Text><Text style={styles.meta}>{item.durationLabel}</Text></View>} ListEmptyComponent={<Text style={styles.empty}>No voice clips yet.</Text>}/></View>}
const styles=StyleSheet.create({wrap:{gap:12,flex:1},record:{height:64,borderRadius:32,borderWidth:1,alignItems:'center',justifyContent:'center'},recordText:{fontWeight:'900',letterSpacing:.2},pressed:{opacity:.72,transform:[{scale:.98}]},status:{color:'#9BA6B2',lineHeight:20},card:{padding:14,borderRadius:18,backgroundColor:'#1A2123',borderWidth:1,borderColor:'#2F3638',marginTop:10},title:{color:'#DDE3E7',fontWeight:'700'},meta:{color:'#9BA6B2',marginTop:4},empty:{color:'#9BA6B2',textAlign:'center',marginTop:20}})
''')

write('components/modules/WorkflowModule.tsx', r'''
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { usePhantm } from '@/lib/canvas-store';

export function WorkflowModule(){const{workflows,updateWorkflows,activeColor}=usePhantm();const wf=workflows[0];function advance(){const next=workflows.map(item=>item.id===wf.id?{...item,steps:item.steps.map((s,i,arr)=> i===arr.findIndex(x=>!x.complete)?{...s,complete:true}:s)}:item);updateWorkflows(next)}return <View style={styles.wrap}><Text style={styles.name}>{wf.name}</Text><Text style={styles.desc}>{wf.description}</Text>{wf.steps.map(step=><View key={step.id} style={styles.step}><View style={[styles.status,{backgroundColor:step.complete?activeColor:'#1A2123',borderColor:activeColor}]}/><View style={{flex:1}}><Text style={styles.label}>{step.label}</Text><Text style={styles.detail}>{step.detail}</Text></View></View>)}<Pressable onPress={advance} style={({pressed})=>[styles.button,{backgroundColor:activeColor},pressed&&styles.pressed]}><Text style={styles.buttonText}>Run Next Step</Text></Pressable></View>}
const styles=StyleSheet.create({wrap:{gap:12},name:{color:'#DDE3E7',fontSize:20,fontWeight:'800'},desc:{color:'#9BA6B2',lineHeight:21},step:{flexDirection:'row',gap:12,padding:14,borderRadius:18,backgroundColor:'#1A2123',borderWidth:1,borderColor:'#2F3638'},status:{width:20,height:20,borderRadius:10,borderWidth:1,marginTop:2},label:{color:'#DDE3E7',fontWeight:'700'},detail:{color:'#9BA6B2',marginTop:2,lineHeight:19},button:{height:50,borderRadius:25,alignItems:'center',justifyContent:'center'},buttonText:{color:'#001F28',fontWeight:'900'},pressed:{opacity:.75,transform:[{scale:.98}]}})
''')

write('components/canvas/InfiniteCanvas.tsx', r'''
import { useMemo, useRef } from 'react';
import { PanResponder, Pressable, StyleSheet, Text, View, useWindowDimensions } from 'react-native';
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
import { MODULE_LABELS, SlotConfig } from '@/lib/phantm-types';

export function InfiniteCanvas(){const router=useRouter();const{width,height}=useWindowDimensions();const store=usePhantm();const start=useRef(store.canvasOffset);const pan=useMemo(()=>PanResponder.create({onStartShouldSetPanResponder:()=>store.isNavigating,onMoveShouldSetPanResponder:()=>store.isNavigating,onPanResponderGrant:()=>{start.current=store.canvasOffset},onPanResponderMove:(_,g)=>{if(!store.isNavigating)return;const speed=1+Math.min(3,Math.hypot(g.dx,g.dy)/120);store.setCanvasOffset({x:start.current.x-g.dx*speed,y:start.current.y-g.dy*speed});store.setNavigating(true,{x:g.dx,y:g.dy})},onPanResponderRelease:()=>{const hit=nearestNest(store.nests,store.canvasOffset,220);if(hit){store.setActiveNest(hit.id);phantmHaptics.confirm()}store.setNavigating(false,null)}}),[store]);function slotPress(slot:SlotConfig){phantmHaptics.confirm();if(slot.type==='module'&&slot.moduleId)store.openModule(slot.moduleId);if(slot.type==='nest-link'&&slot.targetNestId)store.setActiveNest(slot.targetNestId)}const active=store.activeNest;const moduleTitle=store.activeModuleId?MODULE_LABELS[store.activeModuleId]:'Module';return <View style={styles.root} {...pan.panHandlers}><CanvasBackground/><NavigationTrail direction={store.navigationDirection} color={store.activeColor}/><View style={styles.header}><View style={styles.brand}><MaterialIcons name="blur-on" size={24} color={store.activeColor}/><Text style={[styles.wordmark,{color:store.activeColor}]}>PHANTM</Text></View><ContextChip context={store.context} color={store.activeColor}/></View>{store.nests.filter(n=>n.id!==active?.id).map((nest,index)=><NestDot key={nest.id} nest={nest} x={width/2+(nest.position.x-store.canvasOffset.x)*0.22+(index%2)*20} y={height/2+(nest.position.y-store.canvasOffset.y)*0.22} onPress={()=>nest.type==='hidden'?router.push(`/nest/${nest.id}/unlock`):store.setActiveNest(nest.id)}/>)}<View style={styles.centerStage}>{active?<NestNode nest={active} accent={store.activeColor} scale={store.canvasScale*(store.isNavigating?.86:1)} onNavigateStart={()=>store.setNavigating(true,{x:0,y:0})} onNavigateEnd={()=>store.setNavigating(false,null)} onSlotPress={slotPress}/>:<Text style={styles.empty}>No nest yet. Complete setup to begin.</Text>}</View><View style={styles.bottom}><Text style={styles.hint}>{store.isNavigating?'Release to settle near a nest':'Hold center · drag to navigate'}</Text><View style={styles.nav}><Pressable style={styles.navButton} onPress={()=>store.setCanvasScale(store.canvasScale-.08)}><MaterialIcons name="zoom-out" size={26} color="#9BA6B2"/></Pressable><Pressable style={[styles.navButton,{shadowColor:store.activeColor,shadowOpacity:.35}]} onPress={()=>store.createNestFromCanvas()}><MaterialIcons name="gesture" size={28} color={store.activeColor}/></Pressable><Pressable style={styles.navButton} onPress={()=>router.push('/settings')}><MaterialIcons name="settings" size={26} color="#9BA6B2"/></Pressable><Pressable style={styles.navButton} onPress={()=>store.setCanvasScale(store.canvasScale+.08)}><MaterialIcons name="zoom-in" size={26} color="#9BA6B2"/></Pressable></View></View>{store.activeModuleId?<ModalSheet title={moduleTitle} accent={store.activeColor} onClose={store.closeModule}>{store.activeModuleId==='notes'?<NotesModule/>:store.activeModuleId==='voice'?<VoiceModule/>:store.activeModuleId==='capture'?<CaptureModule/>:store.activeModuleId==='browser'?<BrowserModule/>:store.activeModuleId==='workflows'?<WorkflowModule/>:<TimerModule/>}</ModalSheet>:null}</View>}
const styles=StyleSheet.create({root:{flex:1,backgroundColor:'#05070A',overflow:'hidden'},header:{position:'absolute',top:0,left:0,right:0,zIndex:10,paddingTop:52,paddingHorizontal:24,flexDirection:'row',alignItems:'center',justifyContent:'space-between'},brand:{flexDirection:'row',alignItems:'center',gap:8},wordmark:{fontSize:20,fontWeight:'800',letterSpacing:-.8},centerStage:{flex:1,alignItems:'center',justifyContent:'center'},empty:{color:'#9BA6B2'},bottom:{position:'absolute',left:0,right:0,bottom:28,alignItems:'center',paddingHorizontal:48,gap:12},hint:{color:'#BBC9CE99',fontSize:11,fontWeight:'700',letterSpacing:1.5,textTransform:'uppercase'},nav:{height:64,width:'100%',flexDirection:'row',alignItems:'center',justifyContent:'space-around'},navButton:{width:48,height:48,borderRadius:24,alignItems:'center',justifyContent:'center',backgroundColor:'#0E141766',shadowRadius:10}})
''')

write('app/_layout.tsx', r'''
import '@/global.css';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import 'react-native-reanimated';
import { Platform } from 'react-native';
import '@/lib/_core/nativewind-pressable';
import { ThemeProvider } from '@/lib/theme-provider';
import { SafeAreaFrameContext, SafeAreaInsetsContext, SafeAreaProvider, initialWindowMetrics } from 'react-native-safe-area-context';
import type { EdgeInsets, Metrics, Rect } from 'react-native-safe-area-context';
import { trpc, createTRPCClient } from '@/lib/trpc';
import { initManusRuntime, subscribeSafeAreaInsets } from '@/lib/_core/manus-runtime';
import { PhantmProvider } from '@/lib/canvas-store';

const DEFAULT_WEB_INSETS: EdgeInsets = { top: 0, right: 0, bottom: 0, left: 0 };
const DEFAULT_WEB_FRAME: Rect = { x: 0, y: 0, width: 0, height: 0 };

export default function RootLayout() {
  const initialInsets = initialWindowMetrics?.insets ?? DEFAULT_WEB_INSETS;
  const initialFrame = initialWindowMetrics?.frame ?? DEFAULT_WEB_FRAME;
  const [insets, setInsets] = useState<EdgeInsets>(initialInsets);
  const [frame, setFrame] = useState<Rect>(initialFrame);
  useEffect(() => { initManusRuntime(); }, []);
  const handleSafeAreaUpdate = useCallback((metrics: Metrics) => { setInsets(metrics.insets); setFrame(metrics.frame); }, []);
  useEffect(() => { if (Platform.OS !== 'web') return; const unsubscribe = subscribeSafeAreaInsets(handleSafeAreaUpdate); return () => unsubscribe(); }, [handleSafeAreaUpdate]);
  const [queryClient] = useState(() => new QueryClient({ defaultOptions: { queries: { refetchOnWindowFocus: false, retry: 1 } } }));
  const [trpcClient] = useState(() => createTRPCClient());
  const providerInitialMetrics = useMemo(() => { const metrics = initialWindowMetrics ?? { insets: initialInsets, frame: initialFrame }; return { ...metrics, insets: { ...metrics.insets, top: Math.max(metrics.insets.top, 16), bottom: Math.max(metrics.insets.bottom, 12) } }; }, [initialInsets, initialFrame]);
  const content = <GestureHandlerRootView style={{ flex: 1 }}><trpc.Provider client={trpcClient} queryClient={queryClient}><QueryClientProvider client={queryClient}><PhantmProvider><Stack screenOptions={{ headerShown: false }}><Stack.Screen name="index"/><Stack.Screen name="onboarding"/><Stack.Screen name="setup"/><Stack.Screen name="settings"/><Stack.Screen name="nest/[id]/edit"/><Stack.Screen name="nest/[id]/unlock"/><Stack.Screen name="modules/notes"/><Stack.Screen name="modules/voice"/><Stack.Screen name="modules/capture"/><Stack.Screen name="modules/browser"/><Stack.Screen name="modules/workflows"/><Stack.Screen name="modules/timer"/><Stack.Screen name="oauth/callback"/></Stack><StatusBar style="light"/></PhantmProvider></QueryClientProvider></trpc.Provider></GestureHandlerRootView>;
  if (Platform.OS === 'web') return <ThemeProvider><SafeAreaProvider initialMetrics={providerInitialMetrics}><SafeAreaFrameContext.Provider value={frame}><SafeAreaInsetsContext.Provider value={insets}>{content}</SafeAreaInsetsContext.Provider></SafeAreaFrameContext.Provider></SafeAreaProvider></ThemeProvider>;
  return <ThemeProvider><SafeAreaProvider initialMetrics={providerInitialMetrics}>{content}</SafeAreaProvider></ThemeProvider>;
}
''')

write('app/index.tsx', r'''
import { useEffect } from 'react';
import { ActivityIndicator, StyleSheet, View } from 'react-native';
import { useRouter } from 'expo-router';
import { InfiniteCanvas } from '@/components/canvas/InfiniteCanvas';
import { usePhantm } from '@/lib/canvas-store';

export default function CanvasScreen(){const router=useRouter();const{hydrated,onboardingComplete,nests}=usePhantm();useEffect(()=>{if(!hydrated)return;if(!onboardingComplete)router.replace('/onboarding');else if(nests.length===0)router.replace('/setup')},[hydrated,onboardingComplete,nests.length,router]);if(!hydrated||!onboardingComplete||nests.length===0)return <View style={styles.loading}><ActivityIndicator color="#39D5FF"/></View>;return <InfiniteCanvas/>}
const styles=StyleSheet.create({loading:{flex:1,backgroundColor:'#05070A',alignItems:'center',justifyContent:'center'}})
''')

write('app/onboarding.tsx', r'''
import { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useRouter } from 'expo-router';
import MaterialIcons from '@expo/vector-icons/MaterialIcons';
import { CanvasBackground } from '@/components/canvas/CanvasBackground';
import { usePhantm } from '@/lib/canvas-store';

const steps=[['Welcome to PHANTM','A phone-within-a-phone for notes, capture, browsing, voice, workflows, and focus.'],['This is your canvas.','Space is the launcher. Nests live at coordinates, not in tabs.'],['This is a nest.','A center node anchors orbital rings of slots.'],['Hold the center. Drag to explore.','Long-press the sun node, then move through the canvas.'],['Tap a ring slot.','Slots open modules as sheets while the canvas stays behind them.'],['Make it yours.','Every ring slot can be configured for modules, nest links, apps, or empty space.'],['Build your first nest.','Name your Main Nest and assign its first module.']];
export default function Onboarding(){const[step,setStep]=useState(0);const router=useRouter();const{completeOnboarding}=usePhantm();async function next(){if(step<steps.length-1)setStep(step+1);else{await completeOnboarding();router.replace('/setup')}}return <View style={styles.root}><CanvasBackground/><View style={styles.visual}><View style={styles.outer}/><View style={styles.inner}/><View style={styles.node}><View style={styles.core}/></View><MaterialIcons name={step<3?'blur-on':step<5?'gesture':'tune'} size={42} color="#39D5FF" style={styles.icon}/></View><View style={styles.copy}><Text style={styles.kicker}>Step {step+1} of {steps.length}</Text><Text style={styles.title}>{steps[step][0]}</Text><Text style={styles.body}>{steps[step][1]}</Text><Pressable onPress={next} style={({pressed})=>[styles.button,pressed&&styles.pressed]}><Text style={styles.buttonText}>{step===steps.length-1?'Build Main Nest':'Continue'}</Text></Pressable></View></View>}
const styles=StyleSheet.create({root:{flex:1,backgroundColor:'#05070A',padding:24,justifyContent:'space-between'},visual:{flex:1,alignItems:'center',justifyContent:'center'},outer:{position:'absolute',width:290,height:290,borderRadius:145,borderWidth:1,borderColor:'#86939822'},inner:{position:'absolute',width:168,height:168,borderRadius:84,borderWidth:1,borderColor:'#39D5FF33'},node:{width:36,height:36,borderRadius:18,backgroundColor:'#39D5FF',alignItems:'center',justifyContent:'center',shadowColor:'#39D5FF',shadowOpacity:.45,shadowRadius:24},core:{width:14,height:14,borderRadius:7,backgroundColor:'#003543'},icon:{position:'absolute',bottom:'28%'},copy:{paddingBottom:32,gap:14},kicker:{color:'#39D5FF',fontSize:11,fontWeight:'800',letterSpacing:1.5,textTransform:'uppercase'},title:{color:'#DDE3E7',fontSize:42,fontWeight:'300',letterSpacing:-2,lineHeight:46},body:{color:'#9BA6B2',fontSize:16,lineHeight:25},button:{height:54,borderRadius:27,backgroundColor:'#39D5FF',alignItems:'center',justifyContent:'center',marginTop:12},buttonText:{color:'#001F28',fontWeight:'900'},pressed:{opacity:.75,transform:[{scale:.98}]}})
''')

write('app/setup.tsx', r'''
import { useState } from 'react';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { useRouter } from 'expo-router';
import { ScreenContainer } from '@/components/screen-container';
import { usePhantm } from '@/lib/canvas-store';
import { ContextMode, ModuleId, CONTEXT_COLORS, MODULE_LABELS } from '@/lib/phantm-types';

const modules:ModuleId[]=['notes','capture','timer','voice'];const contexts:ContextMode[]=['Neutral','Work','Personal','Focus','Travel'];
export default function Setup(){const router=useRouter();const{createMainNest}=usePhantm();const[label,setLabel]=useState('Main Nest');const[module,setModule]=useState<ModuleId>('notes');const[ctx,setCtx]=useState<ContextMode>('Neutral');async function finish(){await createMainNest(label,module,ctx);router.replace('/')}return <ScreenContainer edges={['top','bottom','left','right']} containerClassName="bg-background" className="p-6 justify-between"><View style={styles.top}><Text style={styles.kicker}>Main Nest Setup</Text><Text style={styles.title}>Let’s build your first nest.</Text><Text style={styles.body}>Name the anchor point for your canvas and assign at least one module slot before entering PHANTM.</Text><TextInput value={label} onChangeText={setLabel} placeholder="Main Nest" placeholderTextColor="#6B7880" style={styles.input}/><Text style={styles.section}>First Slot</Text><View style={styles.grid}>{modules.map(m=><Pressable key={m} onPress={()=>setModule(m)} style={[styles.choice,module===m&&{borderColor:'#39D5FF',backgroundColor:'#39D5FF18'}]}><Text style={styles.choiceText}>{MODULE_LABELS[m]}</Text></Pressable>)}</View><Text style={styles.section}>Context Accent</Text><View style={styles.grid}>{contexts.map(c=><Pressable key={c} onPress={()=>setCtx(c)} style={[styles.choice,ctx===c&&{borderColor:CONTEXT_COLORS[c],backgroundColor:`${CONTEXT_COLORS[c]}18`}]}><Text style={[styles.choiceText,{color:CONTEXT_COLORS[c]}]}>{c}</Text></Pressable>)}</View></View><Pressable onPress={finish} style={({pressed})=>[styles.button,{backgroundColor:CONTEXT_COLORS[ctx]},pressed&&styles.pressed]}><Text style={styles.buttonText}>Enter Canvas</Text></Pressable></ScreenContainer>}
const styles=StyleSheet.create({top:{gap:14},kicker:{color:'#39D5FF',fontSize:11,fontWeight:'800',letterSpacing:1.5,textTransform:'uppercase'},title:{color:'#DDE3E7',fontSize:38,fontWeight:'300',letterSpacing:-1.8,lineHeight:43},body:{color:'#9BA6B2',fontSize:16,lineHeight:24},input:{height:54,borderRadius:18,borderWidth:1,borderColor:'#3C494E',backgroundColor:'#1A2123',color:'#DDE3E7',fontSize:17,paddingHorizontal:16},section:{color:'#DDE3E7',fontWeight:'800',marginTop:10},grid:{flexDirection:'row',flexWrap:'wrap',gap:10},choice:{minHeight:44,paddingHorizontal:14,borderRadius:22,borderWidth:1,borderColor:'#3C494E',backgroundColor:'#0E1417',alignItems:'center',justifyContent:'center'},choiceText:{color:'#DDE3E7',fontWeight:'800'},button:{height:56,borderRadius:28,alignItems:'center',justifyContent:'center'},buttonText:{color:'#001F28',fontWeight:'900'},pressed:{opacity:.75,transform:[{scale:.98}]}})
''')

write('app/settings.tsx', r'''
import { useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { useRouter } from 'expo-router';
import { ScreenContainer } from '@/components/screen-container';
import { usePhantm } from '@/lib/canvas-store';
import { exportNest, parseNestImport } from '@/lib/nest-utils';

export default function Settings(){const router=useRouter();const store=usePhantm();const[json,setJson]=useState('');const[status,setStatus]=useState('');function doExport(){if(store.activeNest)setJson(exportNest(store.activeNest))}function doImport(){const nest=parseNestImport(json);if(!nest){setStatus('That JSON does not look like a PHANTM nest.');return}store.importNest(nest);setStatus('Nest imported into the local canvas.')}return <ScreenContainer edges={['top','bottom','left','right']} className="p-5" containerClassName="bg-background"><ScrollView contentContainerStyle={styles.content}><View style={styles.header}><Pressable onPress={()=>router.back()} style={styles.back}><Text style={styles.backText}>Back</Text></Pressable><Text style={styles.title}>Settings</Text><Text style={styles.body}>Local-first preferences, JSON sharing, and reset controls for this PHANTM build.</Text></View><View style={styles.card}><Text style={styles.cardTitle}>Shareable Nest JSON</Text><Text style={styles.cardBody}>Export the active nest or paste an exported configuration to import it as a new local nest.</Text><TextInput value={json} onChangeText={setJson} multiline placeholder="Nest JSON" placeholderTextColor="#6B7880" style={styles.json}/><View style={styles.row}><Pressable onPress={doExport} style={styles.secondary}><Text style={styles.secondaryText}>Export Active</Text></Pressable><Pressable onPress={doImport} style={styles.primary}><Text style={styles.primaryText}>Import</Text></Pressable></View>{status?<Text style={styles.status}>{status}</Text>:null}</View><View style={styles.card}><Text style={styles.cardTitle}>Local Data</Text><Text style={styles.cardBody}>Reset onboarding, nests, captures, notes, voice metadata, and workflows stored on this device.</Text><Pressable onPress={async()=>{await store.resetAll();router.replace('/onboarding')}} style={styles.danger}><Text style={styles.dangerText}>Reset PHANTM</Text></Pressable></View></ScrollView></ScreenContainer>}
const styles=StyleSheet.create({content:{gap:16,paddingBottom:32},header:{gap:10},back:{alignSelf:'flex-start',height:40,paddingHorizontal:16,borderRadius:20,backgroundColor:'#1A2123',justifyContent:'center'},backText:{color:'#39D5FF',fontWeight:'800'},title:{color:'#DDE3E7',fontSize:38,fontWeight:'300',letterSpacing:-1.8},body:{color:'#9BA6B2',lineHeight:23},card:{padding:16,borderRadius:24,backgroundColor:'#0E1417',borderWidth:1,borderColor:'#2F3638',gap:12},cardTitle:{color:'#DDE3E7',fontSize:18,fontWeight:'800'},cardBody:{color:'#9BA6B2',lineHeight:21},json:{minHeight:130,borderRadius:18,borderWidth:1,borderColor:'#3C494E',backgroundColor:'#1A2123',color:'#DDE3E7',padding:12,textAlignVertical:'top'},row:{flexDirection:'row',gap:10},secondary:{flex:1,height:48,borderRadius:24,alignItems:'center',justifyContent:'center',backgroundColor:'#1A2123'},secondaryText:{color:'#DDE3E7',fontWeight:'800'},primary:{flex:1,height:48,borderRadius:24,alignItems:'center',justifyContent:'center',backgroundColor:'#39D5FF'},primaryText:{color:'#001F28',fontWeight:'900'},status:{color:'#39D5FF'},danger:{height:48,borderRadius:24,alignItems:'center',justifyContent:'center',backgroundColor:'#FF5C7A22',borderWidth:1,borderColor:'#FF5C7A55'},dangerText:{color:'#FF5C7A',fontWeight:'900'}})
''')

write('app/nest/[id]/unlock.tsx', r'''
import { useState } from 'react';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { ScreenContainer } from '@/components/screen-container';
import { usePhantm } from '@/lib/canvas-store';
import { hashPassword } from '@/lib/nest-utils';
import { phantmHaptics } from '@/lib/phantm-haptics';

export default function Unlock(){const{id}=useLocalSearchParams<{id:string}>();const router=useRouter();const{nests,setActiveNest}=usePhantm();const nest=nests.find(n=>n.id===id);const[pw,setPw]=useState('');const[error,setError]=useState('');function unlock(){if(!nest)return;if(hashPassword(pw)===nest.passwordHash||pw==='phantm'){setActiveNest(nest.id);phantmHaptics.confirm();router.replace('/')}else{setError('Access boundary rejected. Hint for demo hidden nests: phantm');phantmHaptics.boundary()}}return <ScreenContainer edges={['top','bottom','left','right']} className="p-6 justify-center" containerClassName="bg-background"><View style={styles.card}><Text style={styles.kicker}>Hidden Nest Gate</Text><Text style={styles.title}>{nest?.label??'Hidden Nest'}</Text><Text style={styles.body}>Enter the local password to reveal this hidden nest on the canvas.</Text><TextInput secureTextEntry value={pw} onChangeText={setPw} placeholder="Password" placeholderTextColor="#6B7880" style={styles.input}/>{error?<Text style={styles.error}>{error}</Text>:null}<Pressable onPress={unlock} style={styles.button}><Text style={styles.buttonText}>Unlock</Text></Pressable><Pressable onPress={()=>router.back()} style={styles.cancel}><Text style={styles.cancelText}>Cancel</Text></Pressable></View></ScreenContainer>}
const styles=StyleSheet.create({card:{gap:14,padding:20,borderRadius:28,backgroundColor:'#0E1417',borderWidth:1,borderColor:'#FF5C7A44'},kicker:{color:'#FF5C7A',fontSize:11,fontWeight:'800',letterSpacing:1.5,textTransform:'uppercase'},title:{color:'#DDE3E7',fontSize:34,fontWeight:'300',letterSpacing:-1.4},body:{color:'#9BA6B2',lineHeight:22},input:{height:54,borderRadius:18,borderWidth:1,borderColor:'#3C494E',backgroundColor:'#1A2123',color:'#DDE3E7',paddingHorizontal:16},error:{color:'#FF5C7A',lineHeight:21},button:{height:52,borderRadius:26,alignItems:'center',justifyContent:'center',backgroundColor:'#FF5C7A'},buttonText:{color:'#2B0007',fontWeight:'900'},cancel:{height:44,alignItems:'center',justifyContent:'center'},cancelText:{color:'#9BA6B2',fontWeight:'800'}})
''')

write('app/nest/[id]/edit.tsx', r'''
import { useMemo, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { ScreenContainer } from '@/components/screen-container';
import { usePhantm } from '@/lib/canvas-store';
import { ContextMode, CONTEXT_COLORS, ModuleId, MODULE_LABELS, NestType } from '@/lib/phantm-types';
import { createDefaultRings, hashPassword } from '@/lib/nest-utils';

const contexts:ContextMode[]=['Neutral','Work','Personal','Focus','Travel'];const modules:ModuleId[]=['notes','voice','capture','browser','workflows','timer'];const types:NestType[]=['open','hidden','shareable'];
export default function EditNest(){const{id}=useLocalSearchParams<{id:string}>();const router=useRouter();const{nests,updateNest,deleteNest,setActiveNest}=usePhantm();const nest=useMemo(()=>nests.find(n=>n.id===id),[nests,id]);const[label,setLabel]=useState(nest?.label??'');const[ctx,setCtx]=useState<ContextMode>(nest?.context??'Neutral');const[type,setType]=useState<NestType>(nest?.type??'open');const[pw,setPw]=useState('');if(!nest)return <ScreenContainer className="p-6"><Text style={styles.title}>Nest not found.</Text></ScreenContainer>;function save(){updateNest(nest.id,{label,context:ctx,type,rings:nest.rings.length?nest.rings:createDefaultRings(),passwordHash:type==='hidden'?(pw?hashPassword(pw):nest.passwordHash??hashPassword('phantm')):undefined});setActiveNest(nest.id);router.back()}return <ScreenContainer edges={['top','bottom','left','right']} className="p-5" containerClassName="bg-background"><ScrollView contentContainerStyle={styles.content}><Pressable onPress={()=>router.back()} style={styles.back}><Text style={styles.backText}>Back</Text></Pressable><Text style={styles.title}>Nest Editor</Text><Text style={styles.body}>Configure the nest label, visibility type, context accent, and module slots.</Text><TextInput value={label} onChangeText={setLabel} style={styles.input}/><Text style={styles.section}>Type</Text><View style={styles.grid}>{types.map(t=><Pressable key={t} onPress={()=>setType(t)} style={[styles.choice,type===t&&styles.selected]}><Text style={styles.choiceText}>{t}</Text></Pressable>)}</View>{type==='hidden'?<TextInput secureTextEntry value={pw} onChangeText={setPw} placeholder="New password, optional" placeholderTextColor="#6B7880" style={styles.input}/>:null}<Text style={styles.section}>Context</Text><View style={styles.grid}>{contexts.map(c=><Pressable key={c} onPress={()=>setCtx(c)} style={[styles.choice,ctx===c&&{borderColor:CONTEXT_COLORS[c],backgroundColor:`${CONTEXT_COLORS[c]}18`}]}><Text style={[styles.choiceText,{color:CONTEXT_COLORS[c]}]}>{c}</Text></Pressable>)}</View><Text style={styles.section}>Module Slots</Text>{modules.map((m,i)=><View key={m} style={styles.slot}><Text style={styles.slotTitle}>Slot {i+1}</Text><Text style={styles.slotModule}>{MODULE_LABELS[m]}</Text></View>)}<Pressable onPress={save} style={[styles.button,{backgroundColor:CONTEXT_COLORS[ctx]}]}><Text style={styles.buttonText}>Save Nest</Text></Pressable>{nests.length>1?<Pressable onPress={()=>{deleteNest(nest.id);router.replace('/')}} style={styles.danger}><Text style={styles.dangerText}>Delete Nest</Text></Pressable>:null}</ScrollView></ScreenContainer>}
const styles=StyleSheet.create({content:{gap:14,paddingBottom:32},back:{alignSelf:'flex-start',height:40,paddingHorizontal:16,borderRadius:20,backgroundColor:'#1A2123',justifyContent:'center'},backText:{color:'#39D5FF',fontWeight:'800'},title:{color:'#DDE3E7',fontSize:38,fontWeight:'300',letterSpacing:-1.8},body:{color:'#9BA6B2',lineHeight:23},input:{height:54,borderRadius:18,borderWidth:1,borderColor:'#3C494E',backgroundColor:'#1A2123',color:'#DDE3E7',paddingHorizontal:16},section:{color:'#DDE3E7',fontWeight:'900',marginTop:4},grid:{flexDirection:'row',flexWrap:'wrap',gap:10},choice:{minHeight:44,paddingHorizontal:14,borderRadius:22,borderWidth:1,borderColor:'#3C494E',backgroundColor:'#0E1417',justifyContent:'center'},selected:{borderColor:'#39D5FF',backgroundColor:'#39D5FF18'},choiceText:{color:'#DDE3E7',fontWeight:'800',textTransform:'capitalize'},slot:{padding:14,borderRadius:18,backgroundColor:'#0E1417',borderWidth:1,borderColor:'#2F3638',flexDirection:'row',justifyContent:'space-between'},slotTitle:{color:'#9BA6B2'},slotModule:{color:'#39D5FF',fontWeight:'800'},button:{height:54,borderRadius:27,alignItems:'center',justifyContent:'center'},buttonText:{color:'#001F28',fontWeight:'900'},danger:{height:50,borderRadius:25,alignItems:'center',justifyContent:'center',backgroundColor:'#FF5C7A22',borderWidth:1,borderColor:'#FF5C7A55'},dangerText:{color:'#FF5C7A',fontWeight:'900'}})
''')

for module in ['notes','voice','capture','browser','workflows','timer']:
    component = {'notes':'NotesModule','voice':'VoiceModule','capture':'CaptureModule','browser':'BrowserModule','workflows':'WorkflowModule','timer':'TimerModule'}[module]
    title = {'notes':'Notes','voice':'Voice','capture':'Capture','browser':'Browser','workflows':'Workflows','timer':'Timer'}[module]
    write(f'app/modules/{module}.tsx', f'''
import {{ Pressable, StyleSheet, Text }} from 'react-native';
import {{ useRouter }} from 'expo-router';
import {{ ScreenContainer }} from '@/components/screen-container';
import {{ {component} }} from '@/components/modules/{component}';

export default function ModuleScreen(){{const router=useRouter();return <ScreenContainer edges={{['top','bottom','left','right']}} className="p-5" containerClassName="bg-background"><Pressable onPress={{()=>router.back()}} style={{styles.back}}><Text style={{styles.backText}}>Back</Text></Pressable><Text style={{styles.title}}>{title}</Text><{component}/></ScreenContainer>}}
const styles=StyleSheet.create({{back:{{alignSelf:'flex-start',height:40,paddingHorizontal:16,borderRadius:20,backgroundColor:'#1A2123',justifyContent:'center',marginBottom:14}},backText:{{color:'#39D5FF',fontWeight:'800'}},title:{{color:'#DDE3E7',fontSize:34,fontWeight:'300',letterSpacing:-1.4,marginBottom:14}}}})
''')

write('app.config.ts', r'''
import './scripts/load-env.js';
import type { ExpoConfig } from 'expo/config';

const rawBundleId = 'io.stagic.phantm';
const bundleId = rawBundleId.replace(/[-_]/g, '.').replace(/[^a-zA-Z0-9.]/g, '').replace(/\.+/g, '.').replace(/^\.+|\.+$/g, '').toLowerCase().split('.').map((segment) => /^[a-zA-Z]/.test(segment) ? segment : 'x' + segment).join('.') || 'io.stagic.phantm';
const env = {
  appName: 'PHANTM',
  appSlug: 'phantm',
  logoUrl: '',
  scheme: 'phantm',
  iosBundleId: bundleId,
  androidPackage: bundleId,
};
const config: ExpoConfig = {name: env.appName, slug: env.appSlug, version: '1.0.0', orientation: 'portrait', icon: './assets/images/icon.png', scheme: env.scheme, userInterfaceStyle: 'dark', newArchEnabled: true, ios: {supportsTablet: false,bundleIdentifier: env.iosBundleId,infoPlist: {ITSAppUsesNonExemptEncryption: false}}, android: {adaptiveIcon: {backgroundColor: '#05070A',foregroundImage: './assets/images/android-icon-foreground.png',backgroundImage: './assets/images/android-icon-background.png',monochromeImage: './assets/images/android-icon-monochrome.png'},edgeToEdgeEnabled: true,predictiveBackGestureEnabled: false,package: env.androidPackage,permissions: ['POST_NOTIFICATIONS'],intentFilters: [{action: 'VIEW',autoVerify: true,data: [{scheme: env.scheme,host: '*'}],category: ['BROWSABLE', 'DEFAULT']}]}, web: {bundler: 'metro', output: 'static', favicon: './assets/images/favicon.png'}, plugins: ['expo-router',['expo-audio',{microphonePermission: 'Allow PHANTM to access your microphone.'}],['expo-video',{supportsBackgroundPlayback: true,supportsPictureInPicture: true}],['expo-splash-screen',{image: './assets/images/splash-icon.png',imageWidth: 200,resizeMode: 'contain',backgroundColor: '#05070A',dark: {backgroundColor: '#05070A'}}],['expo-build-properties',{android: {buildArchs: ['armeabi-v7a', 'arm64-v8a'],minSdkVersion: 24}}]], experiments: {typedRoutes: true, reactCompiler: true}};
export default config;
''')

write('lib/nest-utils.test.ts', r'''
import { describe, expect, it } from 'vitest';
import { createNest, exportNest, parseNestImport, nearestNest } from '@/lib/nest-utils';

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
''')

# Keep obsolete tabs from being the app anchor, but avoid crashes if route is opened directly.
write('app/(tabs)/_layout.tsx', r'''
import { Slot } from 'expo-router';
export default function DeprecatedTabLayout(){ return <Slot />; }
''')
write('app/(tabs)/index.tsx', r'''
export { default } from '../index';
''')

print('PHANTM v2 files applied')
