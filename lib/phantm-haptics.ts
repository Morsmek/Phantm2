import { Platform } from 'react-native';
import * as Haptics from 'expo-haptics';

const native = Platform.OS !== 'web';

export const phantmHaptics = {
  tick: () => native && Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light),
  confirm: () => native && Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success),
  warning: () => native && Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning),
  boundary: () => native && Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error),
  contextSwitch: () => native && Haptics.selectionAsync(),
};
