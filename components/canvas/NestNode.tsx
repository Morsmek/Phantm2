import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useRouter } from 'expo-router';
import { RingLayer } from '@/components/canvas/RingLayer';
import { NestRecord, SlotConfig } from '@/lib/phantm-types';
import { phantmHaptics } from '@/lib/phantm-haptics';

export function NestNode({ nest, accent, scale, onSlotPress }: { nest: NestRecord; accent: string; scale: number; onSlotPress: (slot: SlotConfig) => void }) {
  const router = useRouter();
  return (
    <View style={[styles.wrap, { transform: [{ scale }] }]} pointerEvents="box-none">
      {nest.rings.map((ring) => <RingLayer key={ring.ringIndex} ring={ring} size={ring.ringIndex === 1 ? 180 : 320} accent={accent} onSlotPress={onSlotPress} />)}
      <View
        accessibilityLabel="Active nest center"
        style={[styles.center, { backgroundColor: accent, shadowColor: accent }]}
      >
        <View style={styles.core} />
      </View>
      <Pressable onPress={() => { phantmHaptics.tick(); router.push(`/nest/${nest.id}/edit`); }} style={({ pressed }) => [styles.labelCard, pressed && styles.centerPressed]}>
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
