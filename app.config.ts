import './scripts/load-env.js';
import type { ExpoConfig } from 'expo/config';

const rawBundleId = 'io.stagic.phantm';
const bundleId = rawBundleId.replace(/[-_]/g, '.').replace(/[^a-zA-Z0-9.]/g, '').replace(/\.+/g, '.').replace(/^\.+|\.+$/g, '').toLowerCase().split('.').map((segment) => /^[a-zA-Z]/.test(segment) ? segment : 'x' + segment).join('.') || 'io.stagic.phantm';
const env = {
  appName: 'PHANTM',
  appSlug: 'phantm',
  logoUrl: '',
  scheme: 'phantm',
  iosBundleId: bundleId,
  androidPackage: bundleId,
};
const config: ExpoConfig = {name: env.appName, slug: env.appSlug, version: '1.0.0', orientation: 'portrait', icon: './assets/images/icon.png', scheme: env.scheme, userInterfaceStyle: 'dark', newArchEnabled: true, ios: {supportsTablet: false,bundleIdentifier: env.iosBundleId,infoPlist: {ITSAppUsesNonExemptEncryption: false}}, android: {adaptiveIcon: {backgroundColor: '#05070A',foregroundImage: './assets/images/android-icon-foreground.png',backgroundImage: './assets/images/android-icon-background.png',monochromeImage: './assets/images/android-icon-monochrome.png'},edgeToEdgeEnabled: true,predictiveBackGestureEnabled: false,package: env.androidPackage,permissions: ['POST_NOTIFICATIONS'],intentFilters: [{action: 'VIEW',autoVerify: true,data: [{scheme: env.scheme,host: '*'}],category: ['BROWSABLE', 'DEFAULT']}]}, web: {bundler: 'metro', output: 'static', favicon: './assets/images/favicon.png'}, plugins: ['expo-router',['expo-audio',{microphonePermission: 'Allow PHANTM to access your microphone.'}],['expo-video',{supportsBackgroundPlayback: true,supportsPictureInPicture: true}],['expo-splash-screen',{image: './assets/images/splash-icon.png',imageWidth: 200,resizeMode: 'contain',backgroundColor: '#05070A',dark: {backgroundColor: '#05070A'}}],['expo-build-properties',{android: {buildArchs: ['armeabi-v7a', 'arm64-v8a'],minSdkVersion: 24}}]], experiments: {typedRoutes: true, reactCompiler: true}};
export default config;
