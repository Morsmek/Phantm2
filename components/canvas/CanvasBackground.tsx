import { StyleSheet, View, useWindowDimensions } from 'react-native';
import { useMemo } from 'react';

const SPACING = 28;

export function CanvasBackground({ offsetX = 0, offsetY = 0 }: { offsetX?: number; offsetY?: number }) {
  const { width, height } = useWindowDimensions();

  // Shift the grid so it tiles seamlessly as the canvas scrolls
  const ox = -(((offsetX % SPACING) + SPACING) % SPACING);
  const oy = -(((offsetY % SPACING) + SPACING) % SPACING);

  const cols = Math.ceil(width / SPACING) + 2;
  const rows = Math.ceil(height / SPACING) + 2;

  const dots = useMemo(() => {
    const items: { key: string; x: number; y: number }[] = [];
    for (let c = 0; c < cols; c++) {
      for (let r = 0; r < rows; r++) {
        items.push({ key: `${c}-${r}`, x: c * SPACING, y: r * SPACING });
      }
    }
    return items;
  }, [cols, rows]);

  return (
    <View style={StyleSheet.absoluteFill} pointerEvents="none">
      <View style={{ transform: [{ translateX: ox }, { translateY: oy }] }}>
        {dots.map(({ key, x, y }) => (
          <View key={key} style={[styles.dot, { left: x, top: y }]} />
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  dot: { position: 'absolute', width: 2, height: 2, borderRadius: 1, backgroundColor: '#1C262E' },
});
