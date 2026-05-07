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
    onStartShouldSetPanResponder: () => true,
    onMoveShouldSetPanResponder: (_, gesture) => Math.hypot(gesture.dx, gesture.dy) > 6,
    onPanResponderGrant: () => { start.current = store.canvasOffset; store.setNavigating(true, { x: 0, y: 0 }); },
    onPanResponderMove: (_, gesture) => {
      const speed = 1 + Math.min(2.4, Math.hypot(gesture.dx, gesture.dy) / 160);
      store.setCanvasOffset({ x: start.current.x - gesture.dx * speed, y: start.current.y - gesture.dy * speed });
      store.setNavigating(true, { x: gesture.dx, y: gesture.dy });
    },
    onPanResponderRelease: (_, gesture) => {
      const projected = { x: start.current.x - gesture.dx, y: start.current.y - gesture.dy };
      const hit = nearestNest(store.nests.filter((nest) => nest.type !== 'hidden'), projected, 260);
      if (hit && hit.id !== store.activeNestId) {
        store.setActiveNest(hit.id);
        setStatus(`Focused ${hit.label}`);
        phantmHaptics.confirm();
      } else if (hit) {
        setStatus(`At ${hit.label}`);
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
