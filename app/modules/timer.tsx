import { Pressable, StyleSheet, Text } from 'react-native';
import { useRouter } from 'expo-router';
import { ScreenContainer } from '@/components/screen-container';
import { TimerModule } from '@/components/modules/TimerModule';

export default function ModuleScreen(){const router=useRouter();return <ScreenContainer edges={['top','bottom','left','right']} className="p-5" containerClassName="bg-background"><Pressable onPress={()=>router.back()} style={styles.back}><Text style={styles.backText}>Back</Text></Pressable><Text style={styles.title}>Timer</Text><TimerModule/></ScreenContainer>}
const styles=StyleSheet.create({back:{alignSelf:'flex-start',height:40,paddingHorizontal:16,borderRadius:20,backgroundColor:'#1A2123',justifyContent:'center',marginBottom:14},backText:{color:'#39D5FF',fontWeight:'800'},title:{color:'#DDE3E7',fontSize:34,fontWeight:'300',letterSpacing:-1.4,marginBottom:14}})
