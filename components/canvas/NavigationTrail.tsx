import { useEffect, useRef } from 'react';
import { Animated, StyleSheet, useWindowDimensions } from 'react-native';
import Svg, { Line } from 'react-native-svg';
import { CanvasPoint } from '@/lib/phantm-types';

export function NavigationTrail({ direction, color }: { direction: CanvasPoint | null; color: string }) {
  const { width, height } = useWindowDimensions();
  const opacity = useRef(new Animated.Value(0)).current;
  const lastDir = useRef<CanvasPoint | null>(null);

  // Keep last non-null direction so the trail doesn't snap away during fade-out
  if (direction) lastDir.current = direction;

  useEffect(() => {
    Animated.timing(opacity, {
      toValue: direction ? 1 : 0,
      duration: direction ? 150 : 600,
      useNativeDriver: true,
    }).start();
  }, [direction !== null]); // eslint-disable-line react-hooks/exhaustive-deps

  const dir = direction ?? lastDir.current;
  if (!dir) return null;

  const cx = width / 2;
  const cy = height / 2;
  const dist = Math.min(Math.hypot(dir.x, dir.y), height * 0.4);
  const angle = Math.atan2(dir.y, dir.x);
  const ex = cx + Math.cos(angle) * dist;
  const ey = cy + Math.sin(angle) * dist;

  return (
    <Animated.View style={[StyleSheet.absoluteFill, { opacity }]} pointerEvents="none">
      <Svg width={width} height={height}>
        <Line
          x1={cx} y1={cy} x2={ex} y2={ey}
          stroke={`${color}55`}
          strokeWidth={1.5}
          strokeDasharray="6 8"
        />
      </Svg>
    </Animated.View>
  );
}
