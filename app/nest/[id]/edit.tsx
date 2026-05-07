import { useEffect, useMemo, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { ScreenContainer } from '@/components/screen-container';
import { usePhantm } from '@/lib/canvas-store';
import { ContextMode, CONTEXT_COLORS, ModuleId, MODULE_LABELS, NestRecord, NestType } from '@/lib/phantm-types';
import { createDefaultRings, hashPassword } from '@/lib/nest-utils';

const contexts: ContextMode[] = ['Neutral', 'Work', 'Personal', 'Focus', 'Travel'];
const modules: ModuleId[] = ['notes', 'voice', 'capture', 'browser', 'workflows', 'timer'];
const types: NestType[] = ['open', 'hidden', 'shareable'];

function NotFound() {
  return (
    <ScreenContainer edges={['top', 'bottom', 'left', 'right']} className="p-6" containerClassName="bg-background">
      <Text style={styles.title}>Nest not found.</Text>
    </ScreenContainer>
  );
}

function EditNestContent({ nest }: { nest: NestRecord }) {
  const router = useRouter();
  const { nests, updateNest, deleteNest, setActiveNest } = usePhantm();
  const [label, setLabel] = useState(nest.label);
  const [ctx, setCtx] = useState<ContextMode>(nest.context ?? 'Neutral');
  const [type, setType] = useState<NestType>(nest.type);
  const [pw, setPw] = useState('');

  useEffect(() => {
    setLabel(nest.label);
    setCtx(nest.context ?? 'Neutral');
    setType(nest.type);
  }, [nest]);

  function save() {
    updateNest(nest.id, {
      label,
      context: ctx,
      type,
      rings: nest.rings.length ? nest.rings : createDefaultRings(),
      passwordHash: type === 'hidden' ? (pw ? hashPassword(pw) : nest.passwordHash ?? hashPassword('phantm')) : undefined,
    });
    setActiveNest(nest.id);
    router.back();
  }

  return (
    <ScreenContainer edges={['top', 'bottom', 'left', 'right']} className="p-5" containerClassName="bg-background">
      <ScrollView contentContainerStyle={styles.content}>
        <Pressable onPress={() => router.back()} style={styles.back}>
          <Text style={styles.backText}>Back</Text>
        </Pressable>
        <Text style={styles.title}>Nest Editor</Text>
        <Text style={styles.body}>Configure the nest label, visibility type, context accent, and module slots.</Text>
        <TextInput value={label} onChangeText={setLabel} style={styles.input} />
        <Text style={styles.section}>Type</Text>
        <View style={styles.grid}>
          {types.map((item) => (
            <Pressable key={item} onPress={() => setType(item)} style={[styles.choice, type === item && styles.selected]}>
              <Text style={styles.choiceText}>{item}</Text>
            </Pressable>
          ))}
        </View>
        {type === 'hidden' ? (
          <TextInput secureTextEntry value={pw} onChangeText={setPw} placeholder="New password, optional" placeholderTextColor="#6B7880" style={styles.input} />
        ) : null}
        <Text style={styles.section}>Context</Text>
        <View style={styles.grid}>
          {contexts.map((item) => (
            <Pressable key={item} onPress={() => setCtx(item)} style={[styles.choice, ctx === item && { borderColor: CONTEXT_COLORS[item], backgroundColor: `${CONTEXT_COLORS[item]}18` }]}>
              <Text style={[styles.choiceText, { color: CONTEXT_COLORS[item] }]}>{item}</Text>
            </Pressable>
          ))}
        </View>
        <Text style={styles.section}>Module Slots</Text>
        {modules.map((moduleId, index) => (
          <View key={moduleId} style={styles.slot}>
            <Text style={styles.slotTitle}>Slot {index + 1}</Text>
            <Text style={styles.slotModule}>{MODULE_LABELS[moduleId]}</Text>
          </View>
        ))}
        <Pressable onPress={save} style={[styles.button, { backgroundColor: CONTEXT_COLORS[ctx] }]}>
          <Text style={styles.buttonText}>Save Nest</Text>
        </Pressable>
        {nests.length > 1 ? (
          <Pressable onPress={() => { deleteNest(nest.id); router.replace('/'); }} style={styles.danger}>
            <Text style={styles.dangerText}>Delete Nest</Text>
          </Pressable>
        ) : null}
      </ScrollView>
    </ScreenContainer>
  );
}

export default function EditNest() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { nests } = usePhantm();
  const nest = useMemo(() => nests.find((item) => item.id === id), [nests, id]);
  return nest ? <EditNestContent nest={nest} /> : <NotFound />;
}

const styles = StyleSheet.create({
  content: { gap: 14, paddingBottom: 32 },
  back: { alignSelf: 'flex-start', height: 40, paddingHorizontal: 16, borderRadius: 20, backgroundColor: '#1A2123', justifyContent: 'center' },
  backText: { color: '#39D5FF', fontWeight: '800' },
  title: { color: '#DDE3E7', fontSize: 38, fontWeight: '300', letterSpacing: -1.8 },
  body: { color: '#9BA6B2', lineHeight: 23 },
  input: { height: 54, borderRadius: 18, borderWidth: 1, borderColor: '#3C494E', backgroundColor: '#1A2123', color: '#DDE3E7', paddingHorizontal: 16 },
  section: { color: '#DDE3E7', fontWeight: '900', marginTop: 4 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  choice: { minHeight: 44, paddingHorizontal: 14, borderRadius: 22, borderWidth: 1, borderColor: '#3C494E', backgroundColor: '#0E1417', justifyContent: 'center' },
  selected: { borderColor: '#39D5FF', backgroundColor: '#39D5FF18' },
  choiceText: { color: '#DDE3E7', fontWeight: '800', textTransform: 'capitalize' },
  slot: { padding: 14, borderRadius: 18, backgroundColor: '#0E1417', borderWidth: 1, borderColor: '#2F3638', flexDirection: 'row', justifyContent: 'space-between' },
  slotTitle: { color: '#9BA6B2' },
  slotModule: { color: '#39D5FF', fontWeight: '800' },
  button: { height: 54, borderRadius: 27, alignItems: 'center', justifyContent: 'center' },
  buttonText: { color: '#001F28', fontWeight: '900' },
  danger: { height: 50, borderRadius: 25, alignItems: 'center', justifyContent: 'center', backgroundColor: '#FF5C7A22', borderWidth: 1, borderColor: '#FF5C7A55' },
  dangerText: { color: '#FF5C7A', fontWeight: '900' },
});
