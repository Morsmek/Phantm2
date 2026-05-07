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
