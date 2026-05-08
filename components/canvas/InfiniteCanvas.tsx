import { useRef, useState } from 'react';
import { Pressable, StyleSheet, Text, TextInput, View, useWindowDimensions } from 'react-native';
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

const ALL_MODULES: ModuleId[] = ['notes', 'capture', 'timer', 'voice', 'browser', 'workflows'];

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
  const storeRef = useRef(store);
  storeRef.current = store;

  // Navigation gesture state (all in refs to avoid stale closures in gesture callbacks)
  const navActivatedAbsPos = useRef({ x: 0, y: 0 });
  const navStartCanvasOffset = useRef({ x: 0, y: 0 });
  const isNavActive = useRef(false);
  const dragStartTime = useRef(0);
  const hapticInterval = useRef<ReturnType<typeof setInterval> | null>(null);

  const [newNestLabel, setNewNestLabel] = useState('');
  const [showAddNest, setShowAddNest] = useState(false);
  const [showModulePicker, setShowModulePicker] = useState(false);
  const [status, setStatus] = useState('Hold the center node to navigate');

  // Called from NestNode via runOnJS when LongPress activates
  function onNavStart(absX: number, absY: number) {
    navActivatedAbsPos.current = { x: absX, y: absY };
    navStartCanvasOffset.current = storeRef.current.canvasOffset;
    isNavActive.current = true;
    dragStartTime.current = Date.now();
    storeRef.current.setNavigating(true, { x: 0, y: 0 });
    phantmHaptics.tick();
    // Periodic haptic pulse every second during active navigation
    hapticInterval.current = setInterval(() => {
      if (isNavActive.current) phantmHaptics.tick();
    }, 1000);
  }

  // Called from NestNode Pan.onChange while navigating
  function onNavDrag(absX: number, absY: number) {
    if (!isNavActive.current) return;
    const dx = absX - navActivatedAbsPos.current.x;
    const dy = absY - navActivatedAbsPos.current.y;
    // Time-based acceleration: ramps from 1× to 8× over ~6 seconds of sustained drag
    const elapsed = (Date.now() - dragStartTime.current) / 1000;
    const accel = Math.min(8, 1 + Math.pow(elapsed, 1.4));
    storeRef.current.setCanvasOffset({
      x: navStartCanvasOffset.current.x - dx * accel,
      y: navStartCanvasOffset.current.y - dy * accel,
    });
    storeRef.current.setNavigating(true, { x: dx, y: dy });
  }

  // Called from NestNode Pan.onEnd when finger lifts
  function onNavEnd(absX: number, absY: number) {
    if (hapticInterval.current) { clearInterval(hapticInterval.current); hapticInterval.current = null; }
    if (!isNavActive.current) return;
    isNavActive.current = false;
    const dx = absX - navActivatedAbsPos.current.x;
    const dy = absY - navActivatedAbsPos.current.y;
    const elapsed = (Date.now() - dragStartTime.current) / 1000;
    const accel = Math.min(8, 1 + Math.pow(elapsed, 1.4));
    const projected = {
      x: navStartCanvasOffset.current.x - dx * accel,
      y: navStartCanvasOffset.current.y - dy * accel,
    };
    const hit = nearestNest(
      storeRef.current.nests.filter((n) => n.type !== 'hidden'),
      projected,
      260,
    );
    if (hit) {
      storeRef.current.setActiveNest(hit.id);
      setStatus(`Focused ${hit.label}`);
      phantmHaptics.confirm();
    } else {
      setStatus('No nest nearby — keep navigating');
    }
    storeRef.current.setNavigating(false, null);
  }

  function onCenterTap() {
    phantmHaptics.confirm();
    setStatus(`${storeRef.current.activeNest?.label ?? 'Nest'} active`);
  }

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
      <CanvasBackground offsetX={store.canvasOffset.x} offsetY={store.canvasOffset.y} />
      <NavigationTrail direction={store.navigationDirection} color={store.activeColor} />

      <View style={styles.header}>
        <View style={styles.brand}>
          <MaterialIcons name="blur-on" size={24} color={store.activeColor} />
          <Text style={[styles.wordmark, { color: store.activeColor }]}>PHANTM</Text>
        </View>
        <ContextChip context={store.context} color={store.activeColor} />
      </View>

      {/* Distant nest indicators — hidden nests excluded; viewport-culled */}
      {store.nests
        .filter((n) => n.id !== active?.id && n.type !== 'hidden')
        .map((nest) => {
          const sx = width / 2 + (nest.position.x - store.canvasOffset.x) * store.canvasScale;
          const sy = height / 2 + (nest.position.y - store.canvasOffset.y) * store.canvasScale;
          if (sx < -100 || sx > width + 100 || sy < -100 || sy > height + 100) return null;
          return (
            <NestDot
              key={nest.id}
              nest={nest}
              x={sx}
              y={sy}
              onPress={() => store.setActiveNest(nest.id)}
            />
          );
        })}

      <View style={styles.centerStage}>
        {active ? (
          <NestNode
            nest={active}
            accent={store.activeColor}
            scale={store.canvasScale * (store.isNavigating ? 0.86 : 1)}
            onNavStart={onNavStart}
            onNavDrag={onNavDrag}
            onNavEnd={onNavEnd}
            onCenterTap={onCenterTap}
            onSlotPress={slotPress}
          />
        ) : (
          <Text style={styles.empty}>No nest yet. Complete setup to begin.</Text>
        )}
      </View>

      <View style={styles.bottom}>
        <Text style={styles.hint}>
          {store.isNavigating
            ? 'Release to settle near a nest'
            : `${status} · hold center to navigate`}
        </Text>
        <View style={styles.nav}>
          <Pressable style={styles.navButton} onPress={() => store.setCanvasScale(store.canvasScale - 0.08)}>
            <MaterialIcons name="zoom-out" size={26} color="#9BA6B2" />
          </Pressable>
          <Pressable style={[styles.navButton, { shadowColor: store.activeColor, shadowOpacity: 0.35 }]} onPress={() => setShowAddNest(true)}>
            <MaterialIcons name="add-circle-outline" size={28} color={store.activeColor} />
          </Pressable>
          <Pressable style={styles.navButton} onPress={() => active && router.push(`/nest/${active.id}/edit`)}>
            <MaterialIcons name="tune" size={26} color="#9BA6B2" />
          </Pressable>
          <Pressable style={styles.navButton} onPress={() => setShowModulePicker(true)}>
            <MaterialIcons name="more-horiz" size={26} color="#9BA6B2" />
          </Pressable>
          <Pressable style={styles.navButton} onPress={() => router.push('/settings')}>
            <MaterialIcons name="settings" size={26} color="#9BA6B2" />
          </Pressable>
          <Pressable style={styles.navButton} onPress={() => store.setCanvasScale(store.canvasScale + 0.08)}>
            <MaterialIcons name="zoom-in" size={26} color="#9BA6B2" />
          </Pressable>
        </View>
      </View>

      {showAddNest ? (
        <ModalSheet title="Create Nest" accent={store.activeColor} onClose={() => setShowAddNest(false)}>
          <View style={styles.addForm}>
            <Text style={styles.addBody}>Create a working local nest near the current canvas position. It becomes active immediately.</Text>
            <TextInput
              value={newNestLabel}
              onChangeText={setNewNestLabel}
              placeholder="Nest name"
              placeholderTextColor="#6B7880"
              style={styles.input}
              returnKeyType="done"
              onSubmitEditing={createNest}
            />
            <Pressable onPress={createNest} style={[styles.primaryAction, { backgroundColor: store.activeColor }]}>
              <Text style={styles.primaryActionText}>Create and Focus</Text>
            </Pressable>
          </View>
        </ModalSheet>
      ) : null}

      {showModulePicker ? (
        <ModalSheet title="Modules" accent={store.activeColor} onClose={() => setShowModulePicker(false)}>
          <View style={styles.modulePicker}>
            {ALL_MODULES.map((id) => (
              <Pressable
                key={id}
                accessibilityRole="button"
                accessibilityLabel={`Open ${MODULE_LABELS[id]}`}
                onPress={() => { store.openModule(id); setShowModulePicker(false); setStatus(`Opened ${MODULE_LABELS[id]}`); }}
                style={({ pressed }) => [styles.modulePickerRow, pressed && styles.pressed]}
              >
                <MaterialIcons name={MODULE_ICONS[id] as never} size={22} color={store.activeColor} />
                <Text style={styles.modulePickerLabel}>{MODULE_LABELS[id]}</Text>
              </Pressable>
            ))}
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
  modulePicker: { gap: 4 },
  modulePickerRow: { flexDirection: 'row', alignItems: 'center', gap: 14, paddingVertical: 14, paddingHorizontal: 4, borderRadius: 16 },
  modulePickerLabel: { color: '#DDE3E7', fontSize: 15, fontWeight: '700' },
});
