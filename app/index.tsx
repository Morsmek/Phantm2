import { useEffect } from 'react';
import { ActivityIndicator, StyleSheet, View } from 'react-native';
import { useRouter } from 'expo-router';
import { InfiniteCanvas } from '@/components/canvas/InfiniteCanvas';
import { usePhantm } from '@/lib/canvas-store';

export default function CanvasScreen(){const router=useRouter();const{hydrated,onboardingComplete,nests}=usePhantm();useEffect(()=>{if(!hydrated)return;if(!onboardingComplete)router.replace('/onboarding');else if(nests.length===0)router.replace('/setup')},[hydrated,onboardingComplete,nests.length,router]);if(!hydrated||!onboardingComplete||nests.length===0)return <View style={styles.loading}><ActivityIndicator color="#39D5FF"/></View>;return <InfiniteCanvas/>}
const styles=StyleSheet.create({loading:{flex:1,backgroundColor:'#05070A',alignItems:'center',justifyContent:'center'}})
