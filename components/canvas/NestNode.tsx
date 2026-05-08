import { StyleSheet, Text, View } from 'react-native';
import { useRouter } from 'expo-router';
import { Gesture, GestureDetector } from 'react-native-gesture-handler';
import { runOnJS } from 'react-native-reanimated';
import { RingLayer } from '@/components/canvas/RingLayer';
import { NestRecord, SlotConfig } from '@/lib/phantm-types';

export function NestNode({
  nest,
  accent,
  scale,
  onNavStart,
  onNavDrag,
  onNavEnd,
  onCenterTap,
  onSlotPress,
}: {
  nest: NestRecord;
  accent: string;
  scale: number;
  onNavStart: (absX: number, absY: number) => void;
  onNavDrag: (absX: number, absY: number) => void;
  onNavEnd: (absX: number, absY: number) => void;
  onCenterTap: () => void;
  onSlotPress: (slot: SlotConfig) => void;
}) {
  const router = useRouter();

  // Short tap activates nest; long press + drag navigates canvas
  const tap = Gesture.Tap()
    .maxDuration(250)
    .onEnd(() => runOnJS(onCenterTap)());

  const longPress = Gesture.LongPress()
    .minDuration(300)
    .onStart((e) => runOnJS(onNavStart)(e.absoluteX, e.absoluteY));

  const pan = Gesture.Pan()
    .onChange((e) => runOnJS(onNavDrag)(e.absoluteX, e.absoluteY))
    .onEnd((e) => runOnJS(onNavEnd)(e.absoluteX, e.absoluteY));

  // Tap and (LongPress + Pan) are mutually exclusive — whichever activates first wins
  const centerGesture = Gesture.Exclusive(tap, Gesture.Simultaneous(longPress, pan));

  return (
    <View style={[styles.wrap, { transform: [{ scale }] }]}>
      {nest.rings.map((ring) => (
        <RingLayer
          key={ring.ringIndex}
          ring={ring}
          size={ring.ringIndex === 1 ? 180 : 320}
          accent={accent}
          onSlotPress={onSlotPress}
        />
      ))}
      <GestureDetector gesture={centerGesture}>
        <View style={[styles.center, { backgroundColor: accent, shadowColor: accent }]}>
          <View style={styles.core} />
        </View>
      </GestureDetector>
      <View style={styles.labelCard}>
        <Text style={styles.label}>{nest.label}</Text>
        <Text onPress={() => router.push(`/nest/${nest.id}/edit`)} style={styles.meta}>
          Edit nest
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { width: 340, height: 390, alignItems: 'center', justifyContent: 'center' },
  center: { zIndex: 3, width: 44, height: 44, borderRadius: 22, alignItems: 'center', justifyContent: 'center', shadowOpacity: 0.55, shadowRadius: 26, elevation: 8 },
  core: { width: 14, height: 14, borderRadius: 7, backgroundColor: '#003543' },
  labelCard: { position: 'absolute', bottom: 0, alignItems: 'center', gap: 4, minWidth: 160, paddingVertical: 10, paddingHorizontal: 16, borderRadius: 22, backgroundColor: '#0E141799', borderWidth: 1, borderColor: '#3C494E55' },
  label: { color: '#DDE3E7', fontSize: 15, fontWeight: '700' },
  meta: { color: '#9BA6B2', fontSize: 10, letterSpacing: 1, textTransform: 'uppercase' },
});
