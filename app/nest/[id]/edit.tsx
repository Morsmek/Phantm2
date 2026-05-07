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

  const currentNest = nest;

  function saveMeta() {
    store.updateNest(currentNest.id, {
      label: label.trim() || 'Untitled Nest',
      context,
      type,
      passwordHash: type === 'hidden' ? (password ? hashPassword(password) : currentNest.passwordHash ?? hashPassword('314159')) : undefined,
    });
    store.setActiveNest(currentNest.id);
    setStatus('Nest details saved.');
  }

  function assignModule(moduleId: ModuleId) {
    const next = moduleSlot(selected.slotIndex, moduleId);
    store.assignSlot(currentNest.id, selected.ringIndex, selected.slotIndex, next);
    setStatus(`${MODULE_LABELS[moduleId]} assigned to ring ${selected.ringIndex}, slot ${selected.slotIndex + 1}.`);
  }

  function assignNestLink(targetNestId: string) {
    const target = store.nests.find((item) => item.id === targetNestId);
    const next: SlotConfig = { slotIndex: selected.slotIndex, type: 'nest-link', targetNestId, label: target?.label ?? 'Linked Nest', iconKey: 'hub' };
    store.assignSlot(currentNest.id, selected.ringIndex, selected.slotIndex, next);
    setStatus(`Linked slot to ${target?.label ?? 'another nest'}.`);
  }

  function clearSlot() {
    store.assignSlot(currentNest.id, selected.ringIndex, selected.slotIndex, emptySlot(selected.slotIndex));
    setStatus('Slot cleared.');
  }

  return (
    <ScreenContainer edges={['top', 'bottom', 'left', 'right']} className="p-5" containerClassName="bg-background">
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        <View style={styles.header}>
          <Pressable onPress={() => router.back()} style={styles.back}><Text style={styles.backText}>Back</Text></Pressable>
          <Text style={styles.kicker}>Nest Editor</Text>
          <Text style={styles.title}>{currentNest.label}</Text>
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
          {currentNest.rings.map((ring) => (
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
          <View style={styles.grid}>{store.nests.filter((item) => item.id !== currentNest.id && item.type !== 'hidden').map((item) => <Pressable key={item.id} onPress={() => assignNestLink(item.id)} style={styles.choice}><Text numberOfLines={1} style={styles.choiceText}>{item.label}</Text></Pressable>)}</View>
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
