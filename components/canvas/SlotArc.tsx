import { Pressable, StyleSheet, Text, View } from 'react-native';
import MaterialIcons from '@expo/vector-icons/MaterialIcons';
import { SlotConfig } from '@/lib/phantm-types';

// size = ring diameter; inner ring (≤180) uses smaller targets to avoid center overlap
export function SlotArc({ slot, size, angle, accent, onPress }: { slot: SlotConfig; size: number; angle: number; accent: string; onPress: () => void }) {
  const isInner = size <= 180;
  const touchSize = isInner ? 60 : 72;
  const visualSize = isInner ? 52 : 56;
  const radius = size / 2;
  const x = Math.cos(angle) * radius;
  const y = Math.sin(angle) * radius;
  const active = slot.type !== 'empty';

  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={slot.label}
      onPress={onPress}
      style={{
        position: 'absolute',
        left: '50%',
        top: '50%',
        width: touchSize,
        height: touchSize,
        marginLeft: -touchSize / 2,
        marginTop: -touchSize / 2,
        alignItems: 'center',
        justifyContent: 'center',
        transform: [{ translateX: x }, { translateY: y }],
      }}
    >
      {({ pressed }) => (
        <View
          style={[
            styles.visual,
            {
              width: visualSize,
              height: visualSize,
              borderRadius: visualSize / 2,
              borderColor: active ? `${accent}55` : '#86939822',
              backgroundColor: active ? (pressed ? '#1A2428CC' : '#0E1417CC') : '#0E141766',
              opacity: pressed ? 0.78 : 1,
              transform: pressed ? [{ scale: 0.94 }] : [],
            },
          ]}
        >
          {active ? (
            <>
              <MaterialIcons name={(slot.iconKey as any) ?? 'radio-button-unchecked'} size={18} color={accent} />
              <Text numberOfLines={1} style={[styles.label, { color: accent }]}>{slot.label}</Text>
            </>
          ) : (
            <View style={styles.emptyDot} />
          )}
        </View>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  visual: { alignItems: 'center', justifyContent: 'center', borderWidth: 1, gap: 2, shadowColor: '#39D5FF', shadowOpacity: 0.18, shadowRadius: 10 },
  emptyDot: { width: 5, height: 5, borderRadius: 3, backgroundColor: '#86939844' },
  label: { fontSize: 8, fontWeight: '700', letterSpacing: 0.5, textTransform: 'uppercase', textAlign: 'center', opacity: 0.82 },
});
