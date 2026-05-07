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
