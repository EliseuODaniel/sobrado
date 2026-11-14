import bpy,json
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
root=Path(__file__).resolve().parents[1];rows=[]
for key in ['original','atual','industrial']:
 p=root/'projeto'/key/'visualizacao-pavimentos.blend';bpy.ops.wm.open_mainfile(filepath=str(p));scene=bpy.context.window.scene
 assert scene.name=='VISUALIZACAO_'+key+'_COMPARACAO',(key,scene.name)
 assert len(bpy.data.scenes)==3
 scene.frame_set(scene.frame_current);bpy.context.view_layer.update()
 for mode in ['terreo','dois-pavimentos']:
  group=bpy.data.collections['COMPARACAO_'+mode]
  walls=[o for o in group.objects if o.get('wall_id')]
  assert walls
  for o in walls:
   for pt in o.bound_box:
    projected=world_to_camera_view(scene,scene.camera,o.matrix_world@Vector(pt))
    assert 0<=projected.x<=1 and 0<=projected.y<=1,(key,mode,o.name,tuple(projected))
  if mode=='terreo':assert all(o.get('level')!=1 for o in walls)
  assert not any('CORTE ' in o.name or 'R07 Corte ' in o.name for o in walls)
 rows.append({'version':key,'default_comparison_scene_verified':True,'three_scenes':True,'full_walls_in_frame':True,'new_images_rendered':False})
(root/'relatorios/comparacao-validacao-final.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print('COMPARACAO_REABERTA_VALIDADA_OK',rows,flush=True)
