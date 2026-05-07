import Svg, { Line } from 'react-native-svg';
import { StyleSheet } from 'react-native';
import { CanvasPoint } from '@/lib/phantm-types';

export function NavigationTrail({ direction, color }: { direction: CanvasPoint | null; color: string }) {
  if (!direction) return null;
  return (
    <Svg pointerEvents="none" style={StyleSheet.absoluteFill}>
      <Line x1="50%" y1="50%" x2={`${50 + Math.max(-35, Math.min(35, direction.x / 4))}%`} y2={`${50 + Math.max(-35, Math.min(35, direction.y / 4))}%`} stroke={`${color}66`} strokeWidth={2} strokeDasharray="6 10" />
    </Svg>
  );
}
