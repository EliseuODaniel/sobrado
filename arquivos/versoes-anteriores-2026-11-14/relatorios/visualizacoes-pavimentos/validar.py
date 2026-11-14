"""Confere as cópias salvas e os arquivos de imagem da entrega."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
results=[]
for key in ['original','atual','industrial']:
 receipt=json.loads((ROOT/'relatorios/visualizacoes-pavimentos'/(key+'-verificacao.json')).read_text(encoding='utf-8'))
 assert hashlib.sha256((ROOT/receipt['source']).read_bytes()).hexdigest()==receipt['source_sha256']
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/receipt['blend']))
 cameras=[]
 for job in receipt['jobs']:
  scene=bpy.data.scenes['VISUALIZACAO_'+key+'_'+job['mode']]
  bpy.context.window.scene=scene;bpy.context.view_layer.update()
  group=bpy.data.collections['APRESENTACAO_'+job['mode']]
  names={o.name.removeprefix('VISTA '+job['mode']+' ') for o in group.objects}
  assert names==set(job['included_objects'])
  walls=[o for o in group.objects if o.get('wall_id')]
  assert len(walls)==len(job['full_wall_objects']) and walls
  assert all('CORTE ' not in o.name and 'R07 Corte ' not in o.name for o in walls)
  if job['mode']=='terreo':assert all(o.get('level')!=1 for o in walls)
  cameras.append((tuple(round(v,5) for v in scene.camera.location),tuple(round(v,5) for v in scene.camera.rotation_euler),scene.camera.data.ortho_scale))
  png=ROOT/job['image'];assert png.is_file() and png.stat().st_size>10000
  assert scene.render.resolution_x==1600 and scene.render.resolution_y==1500
 assert cameras[0]==cameras[1]
 results.append({'variant':key,'source_hash_preserved':True,'saved_scene_objects_match_receipts':True,'complete_wall_counts':[len(j['full_wall_objects']) for j in receipt['jobs']],'same_camera':cameras[0],'images':2})
assert results[0]['same_camera']==results[1]['same_camera']==results[2]['same_camera']
(ROOT/'relatorios/visualizacoes-pavimentos/validacao-final.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print('VALIDACAO_FINAL_OK',results,flush=True)
