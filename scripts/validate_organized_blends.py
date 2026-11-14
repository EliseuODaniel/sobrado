"""Atualiza caminhos de saída das cópias e valida Blender sem renderizar."""
from pathlib import Path
import bpy,json,re,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'relatorios/organizacao-movimentos.json').read_text(encoding='utf-8-sig'))
pairs={m['source']:m['destination'] for m in manifest['moves']}
pattern=re.compile('|'.join(re.escape(k) for k in sorted(pairs,key=len,reverse=True)))
def remap(value):return pattern.sub(lambda m:pairs[m.group()],value.replace('\\','/'))
results=[];camera_receipts=[]
for key in ['original','atual','industrial','atico']:
 path=ROOT/'projeto'/key/('atico-caixa-canto-escada.blend' if key=='atico' else 'visualizacao-pavimentos.blend')
 bpy.ops.wm.open_mainfile(filepath=str(path))
 bpy.context.preferences.filepaths.save_version=0
 geometry_before={o.name:(tuple(o.matrix_world),len(o.data.vertices)) for o in bpy.data.objects if o.type=='MESH'}
 updates=0
 for scene in bpy.data.scenes:
  old=scene.render.filepath
  if key!='atico' and scene.name.startswith('VISUALIZACAO_'):
   mode=scene.name.removeprefix('VISUALIZACAO_'+key+'_');scene.render.filepath=str(ROOT/'renders'/key/'vistas-pavimentos'/(mode+'.png'))
  elif key=='atico':scene.render.filepath=remap(old)
  updates+=old!=scene.render.filepath
 missing=[]
 for image in bpy.data.images:
  if image.source not in {'FILE','TILED'} or image.packed_file:continue
  if not image.filepath:continue
  resolved=Path(bpy.path.abspath(image.filepath))
  if not resolved.exists():
   candidate=Path(remap(str(resolved)))
   if candidate.exists():image.filepath=str(candidate)
   else:missing.append(image.name)
 assert not missing,(key,missing)
 if key!='atico':
  r=json.loads((ROOT/'relatorios'/key/'verificacao-pavimentos.json').read_text(encoding='utf-8'))
  assert hashlib.sha256((ROOT/r['source']).read_bytes()).hexdigest()==r['source_sha256']
  cams=[]
  for job in r['jobs']:
   scene=bpy.data.scenes['VISUALIZACAO_'+key+'_'+job['mode']]
   group=bpy.data.collections['APRESENTACAO_'+job['mode']]
   walls=[o for o in group.objects if o.get('wall_id')]
   assert len(walls)==len(job['full_wall_objects']) and walls
   assert not any('CORTE ' in o.name or 'R07 Corte ' in o.name for o in walls)
   if job['mode']=='terreo':assert all(o.get('level')!=1 for o in walls)
   cams.append((tuple(round(v,5) for v in scene.camera.location),tuple(round(v,5) for v in scene.camera.rotation_euler),scene.camera.data.ortho_scale))
  assert cams[0]==cams[1];camera_receipts.append(cams[0])
 assert {o.name:(tuple(o.matrix_world),len(o.data.vertices)) for o in bpy.data.objects if o.type=='MESH'}==geometry_before
 bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
 results.append({'variant':key,'blend':path.relative_to(ROOT).as_posix(),'output_paths_updated':updates,'missing_external_images':missing,'geometry_preserved':True,'render_status':'Pendente por solicitação do usuário; imagens existentes preservadas'})
assert camera_receipts[0]==camera_receipts[1]==camera_receipts[2]
(ROOT/'relatorios/validacao-blender-final.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print('QUATRO_VERSOES_BLENDER_OK',results,flush=True)
