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
  slot: { position: 'absolute', left: '50%', top: '50%', width: 64, height: 64, marginLeft: -32, marginTop: -32, borderRadius: 32, borderWidth: 1.5, alignItems: 'center', justifyContent: 'center', shadowColor: '#39D5FF', shadowOpacity: 0.22, shadowRadius: 12 },
  pressed: { opacity: 0.75, transform: [{ scale: 0.93 }] },
  emptyDot: { width: 6, height: 6, borderRadius: 3, backgroundColor: '#86939844' },
  label: { position: 'absolute', top: 68, fontSize: 10, fontWeight: '700', letterSpacing: 0.8, textTransform: 'uppercase', opacity: 0.72 },
});
