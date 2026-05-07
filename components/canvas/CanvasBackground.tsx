import { StyleSheet, View, useWindowDimensions } from 'react-native';

export function CanvasBackground() {
  const { width, height } = useWindowDimensions();
  const dots = [];
  const spacing = 24;
  for (let x = 0; x < width + spacing; x += spacing) {
    for (let y = 0; y < height + spacing; y += spacing) dots.push(`${x}-${y}`);
  }
  return (
    <View style={StyleSheet.absoluteFill}>
      {dots.map((key) => {
        const [x, y] = key.split('-').map(Number);
        return <View key={key} style={[styles.dot, { left: x, top: y }]} />;
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  dot: { position: 'absolute', width: 1.5, height: 1.5, borderRadius: 1, backgroundColor: '#0D1117' },
});
