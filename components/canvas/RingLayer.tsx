import { StyleSheet, View } from 'react-native';
import Svg, { Circle } from 'react-native-svg';
import { RingConfig, SlotConfig } from '@/lib/phantm-types';
import { SlotArc } from '@/components/canvas/SlotArc';

// Maximum non-overlapping slots per ring to prevent visual crowding
const MAX_VISIBLE_SLOTS: Record<number, number> = { 1: 5, 2: 8 };

export function RingLayer({ ring, size, accent, onSlotPress }: { ring: RingConfig; size: number; accent: string; onSlotPress: (slot: SlotConfig) => void }) {
  const maxSlots = MAX_VISIBLE_SLOTS[ring.ringIndex] ?? 8;
  const visibleSlots = ring.slots.slice(0, maxSlots);

  return (
    <View pointerEvents="box-none" style={[styles.ring, { width: size, height: size, marginLeft: -size / 2, marginTop: -size / 2 }]}>
      <Svg style={StyleSheet.absoluteFill} width={size} height={size}>
        <Circle cx={size / 2} cy={size / 2} r={size / 2 - 1} stroke="#86939824" strokeWidth={1} fill="transparent" />
      </Svg>
      {visibleSlots.map((slot, index) => (
        <SlotArc
          key={`${ring.ringIndex}-${slot.slotIndex}`}
          slot={slot}
          size={size}
          angle={-Math.PI / 2 + (index / visibleSlots.length) * Math.PI * 2}
          accent={accent}
          onPress={() => onSlotPress(slot)}
        />
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  ring: { position: 'absolute', left: '50%', top: '50%', borderRadius: 999 },
});
