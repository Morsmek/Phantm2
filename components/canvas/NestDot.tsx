import { Pressable, StyleSheet } from 'react-native';
import { NestRecord } from '@/lib/phantm-types';

export function NestDot({ nest, x, y, onPress }: { nest: NestRecord; x: number; y: number; onPress: () => void }) {
  const locked = nest.type === 'hidden';
  return <Pressable accessibilityLabel={`Navigate to ${nest.label}`} onPress={onPress} style={[styles.dot, { left: x, top: y, backgroundColor: locked ? '#FF5C7A55' : '#3A455055' }]} />;
}

const styles = StyleSheet.create({
  dot: { position: 'absolute', width: 8, height: 8, borderRadius: 4, borderWidth: 1, borderColor: '#9BA6B222' },
});
