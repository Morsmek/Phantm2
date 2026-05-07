import { useState } from 'react';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { ScreenContainer } from '@/components/screen-container';
import { usePhantm } from '@/lib/canvas-store';
import { hashPassword } from '@/lib/nest-utils';

export default function UnlockNest() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const store = usePhantm();
  const nest = store.nests.find((item) => item.id === id);
  const [pw, setPw] = useState('');
  const [error, setError] = useState('');

  function unlock() {
    if (!nest) {
      setError('This nest no longer exists.');
      return;
    }
    if (!nest.passwordHash || nest.passwordHash === hashPassword(pw)) {
      store.setCanvasOffset(nest.position);
      store.setActiveNest(nest.id);
      router.replace('/');
      return;
    }
    setError('Password did not match. The demo Focus Vault password is 314159 unless changed in the editor.');
  }

  return (
    <ScreenContainer edges={['top', 'bottom', 'left', 'right']} className="p-6 justify-center" containerClassName="bg-background">
      <View style={styles.card}>
        <Text style={styles.kicker}>Hidden Nest</Text>
        <Text style={styles.title}>{nest?.label ?? 'Locked'}</Text>
        <Text style={styles.body}>Enter the local password to reveal this hidden nest on the canvas.</Text>
        <TextInput secureTextEntry value={pw} onChangeText={setPw} placeholder="Password" placeholderTextColor="#6B7880" style={styles.input} returnKeyType="done" onSubmitEditing={unlock} />
        {error ? <Text style={styles.error}>{error}</Text> : null}
        <Pressable onPress={unlock} style={styles.button}><Text style={styles.buttonText}>Unlock</Text></Pressable>
        <Pressable onPress={() => router.back()} style={styles.cancel}><Text style={styles.cancelText}>Cancel</Text></Pressable>
      </View>
    </ScreenContainer>
  );
}
const styles = StyleSheet.create({ card: { gap: 14, padding: 20, borderRadius: 28, backgroundColor: '#0E1417', borderWidth: 1, borderColor: '#FF5C7A44' }, kicker: { color: '#FF5C7A', fontSize: 11, fontWeight: '800', letterSpacing: 1.5, textTransform: 'uppercase' }, title: { color: '#DDE3E7', fontSize: 34, fontWeight: '300', letterSpacing: -1.4 }, body: { color: '#9BA6B2', lineHeight: 22 }, input: { height: 54, borderRadius: 18, borderWidth: 1, borderColor: '#3C494E', backgroundColor: '#1A2123', color: '#DDE3E7', paddingHorizontal: 16 }, error: { color: '#FF5C7A', lineHeight: 21 }, button: { height: 52, borderRadius: 26, alignItems: 'center', justifyContent: 'center', backgroundColor: '#FF5C7A' }, buttonText: { color: '#2B0007', fontWeight: '900' }, cancel: { height: 44, alignItems: 'center', justifyContent: 'center' }, cancelText: { color: '#9BA6B2', fontWeight: '800' } });
