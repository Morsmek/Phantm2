import { useState } from 'react';
import { FlatList, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { usePhantm } from '@/lib/canvas-store';

export function NotesModule() {
  const { notes, addNote, activeColor } = usePhantm();
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  return <View style={styles.wrap}><TextInput placeholder="Note title" placeholderTextColor="#6B7880" value={title} onChangeText={setTitle} style={styles.input} /><TextInput placeholder="Markdown or plain text" placeholderTextColor="#6B7880" value={body} onChangeText={setBody} multiline style={[styles.input, styles.body]} /><Pressable style={({pressed})=>[styles.button,{backgroundColor:activeColor},pressed&&styles.pressed]} onPress={()=>{ if(title.trim()||body.trim()){ addNote(title, body); setTitle(''); setBody(''); }}}><Text style={styles.buttonText}>Save Note</Text></Pressable><FlatList data={notes} keyExtractor={(item)=>item.id} renderItem={({item})=><View style={styles.card}><Text style={styles.cardTitle}>{item.title}</Text><Text style={styles.cardBody}>{item.body || 'No body text yet.'}</Text></View>} ListEmptyComponent={<Text style={styles.empty}>No notes yet. Capture your first thought.</Text>} /></View>;
}
const styles=StyleSheet.create({wrap:{gap:10,flex:1},input:{minHeight:48,borderRadius:18,borderWidth:1,borderColor:'#3C494E',backgroundColor:'#1A2123',color:'#DDE3E7',paddingHorizontal:14,paddingVertical:10},body:{height:96,textAlignVertical:'top'},button:{height:48,borderRadius:24,alignItems:'center',justifyContent:'center'},buttonText:{color:'#001F28',fontWeight:'800'},pressed:{opacity:.75,transform:[{scale:.98}]},card:{padding:14,borderRadius:18,backgroundColor:'#1A2123',borderWidth:1,borderColor:'#2F3638',marginTop:10},cardTitle:{color:'#DDE3E7',fontWeight:'700',fontSize:16},cardBody:{color:'#9BA6B2',marginTop:4,lineHeight:20},empty:{color:'#9BA6B2',textAlign:'center',marginTop:20}});
