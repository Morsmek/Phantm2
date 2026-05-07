import { PropsWithChildren } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import MaterialIcons from '@expo/vector-icons/MaterialIcons';

export function ModalSheet({ title, accent, onClose, children }: PropsWithChildren<{ title: string; accent: string; onClose: () => void }>) {
  const insets = useSafeAreaInsets();
  return (
    <View style={styles.overlay}>
      <Pressable style={StyleSheet.absoluteFill} onPress={onClose} />
      <View style={[styles.sheet, { paddingBottom: Math.max(insets.bottom, 16) }]}> 
        <View style={styles.grabber} />
        <View style={styles.header}>
          <Text style={styles.title}>{title}</Text>
          <Pressable onPress={onClose} style={({ pressed }) => [styles.close, pressed && styles.pressed]}>
            <MaterialIcons name="expand-more" color={accent} size={28} />
          </Pressable>
        </View>
        {children}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  overlay: { ...StyleSheet.absoluteFillObject, justifyContent: 'flex-end', backgroundColor: 'rgba(5,7,10,0.52)', zIndex: 40 },
  sheet: { maxHeight: '78%', minHeight: '48%', borderTopLeftRadius: 34, borderTopRightRadius: 34, backgroundColor: '#0E1417', borderWidth: 1, borderColor: '#253138', paddingHorizontal: 20, paddingTop: 10 },
  grabber: { width: 42, height: 4, borderRadius: 999, backgroundColor: '#3C494E', alignSelf: 'center', marginBottom: 14 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 },
  title: { color: '#DDE3E7', fontSize: 22, fontWeight: '700', letterSpacing: -0.3 },
  close: { width: 44, height: 44, borderRadius: 22, alignItems: 'center', justifyContent: 'center', backgroundColor: '#1A2123' },
  pressed: { opacity: 0.72, transform: [{ scale: 0.97 }] },
});
