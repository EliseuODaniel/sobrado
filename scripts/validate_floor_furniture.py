"""Confere posições reais dos objetos contra cada fonte avaliada pelo Blender."""
from pathlib import Path
import bpy,json,sys
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[1]
items=[('original','casa-07.blend','R07_volumetria'),('atual','casa-07-atual-fiel.blend','FIEL2_volumetria'),('industrial','casa-industrial-fotorrealista.blend','PHOTO6_volumetria')]
receipts=[]
for key,base,scene_name in items:
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/'projeto'/key/base))
 bpy.context.window.scene=bpy.data.scenes[scene_name];bpy.context.scene.frame_set(bpy.context.scene.frame_current);bpy.context.view_layer.update()
 graph=bpy.context.evaluated_depsgraph_get();graph.update()
 expected={o.name:o.evaluated_get(graph).matrix_world.copy() for o in bpy.context.scene.objects}
 path=ROOT/('.tools/floor-repair' if '--repair' in sys.argv else 'projeto')/key/'visualizacao-pavimentos.blend'
 bpy.ops.wm.open_mainfile(filepath=str(path))
 assert bpy.context.window.scene.name=='VISUALIZACAO_'+key+'_COMPARACAO'
 checks=0;upper_beds=[]
 for mode in ['terreo','dois-pavimentos']:
  bpy.context.window.scene=bpy.data.scenes['VISUALIZACAO_'+key+'_'+mode];bpy.context.scene.frame_set(bpy.context.scene.frame_current);bpy.context.view_layer.update()
  prefix='VISTA '+mode+' '
  for o in bpy.data.collections['APRESENTACAO_'+mode].objects:
   name=o.name.removeprefix(prefix);assert name in expected,(key,name)
   error=max(abs(o.matrix_world[i][j]-expected[name][i][j]) for i in range(4) for j in range(4))
   assert error<1e-4,(key,mode,name,error)
   if mode=='dois-pavimentos' and any(t in name.lower() for t in ['cama','colch','beliche']) and expected[name].translation.z>=2.7:
    upper_beds.append({'object':name,'z_m':round(o.matrix_world.translation.z,3)})
   checks+=1
  bpy.context.window.scene=bpy.data.scenes['VISUALIZACAO_'+key+'_COMPARACAO'];bpy.context.scene.frame_set(bpy.context.scene.frame_current);bpy.context.view_layer.update()
  transform=Matrix.Translation((-5.2 if mode=='terreo' else 5.2,0,0))
  for o in bpy.data.collections['COMPARACAO_'+mode].objects:
   if o.type=='FONT':continue
   name=o.name.removeprefix('COMPARACAO '+mode+' '+prefix)
   target=transform@expected[name]
   error=max(abs(o.matrix_world[i][j]-target[i][j]) for i in range(4) for j in range(4))
   assert error<1e-4,(key,'comparison',name,error)
   checks+=1
 assert upper_beds,(key,'Nenhuma cama no nível superior')
 receipts.append({'version':key,'object_transforms_compared_to_evaluated_source':checks,'maximum_allowed_matrix_error':.0001,'upper_bed_objects_verified':upper_beds,'status':'passed'})
(ROOT/'relatorios/validacao-moveis-pavimentos.json').write_text(json.dumps(receipts,ensure_ascii=False,indent=2),encoding='utf-8')
print('MOVEIS_E_TRANSFORMACOES_OK',[(r['version'],r['object_transforms_compared_to_evaluated_source'],len(r['upper_bed_objects_verified'])) for r in receipts],flush=True)
