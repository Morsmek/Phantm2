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
