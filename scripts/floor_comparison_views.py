"""Seis vistas comparáveis, com paredes integrais e sem coberturas."""
from pathlib import Path
import bpy,sys,json,hashlib,time
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
key=sys.argv[-1]
SOURCES={'original':'R07_volumetria','atual':'FIEL2_volumetria','industrial':'PHOTO6_volumetria'}
OUT=ROOT/'renders'/key/'vistas-pavimentos';OUT.mkdir(parents=True,exist_ok=True)
DEST=ROOT/'projeto'/key/'visualizacao-pavimentos.blend';DEST.parent.mkdir(exist_ok=True)
if '--repair' in sys.argv:
 DEST=ROOT/'.tools/floor-repair'/key/'visualizacao-pavimentos.blend';DEST.parent.mkdir(parents=True,exist_ok=True)
assert not DEST.exists(),DEST
src=Path(bpy.data.filepath);sha=hashlib.sha256(src.read_bytes()).hexdigest()
source=bpy.data.scenes[SOURCES[key]];bpy.context.window.scene=source
source.frame_set(source.frame_current)
bpy.context.view_layer.update()
depsgraph=bpy.context.evaluated_depsgraph_get();depsgraph.update()
exclude={'R07_Teto_Superior','R07_Teto_Terreo','R07_Cobertura','ATUAL_Cobertura_Fundos','FIEL2_Detalhes_Cobertura','FIEL2_Vizinhos_Apenas_Fachada','FIEL2_Vizinho_Contexto','PHOTO6_Entorno','R07_Contexto','FIEL2_Contexto','PHOTO6_Contexto_Apresentacao'}
geometry=set()
for col in source.collection.children:
 if col.name in exclude:continue
 for o in col.all_objects:
  if o.type in {'MESH','CURVE','SURFACE','FONT','META'} or o.type=='EMPTY' and o.instance_type=='COLLECTION':geometry.add(o)
# Fechamentos laterais dos anexos são preservados mesmo sem a cobertura.
if key=='atual':
 for o in bpy.data.collections['FIEL2_Detalhes_Cobertura'].objects:
  if 'Fechamento lateral' in o.name:geometry.add(o)
worlds={o:o.evaluated_get(depsgraph).matrix_world.copy() for o in geometry}
def limits(o):
 p=[worlds[o]@Vector(v) for v in o.bound_box]
 return min(v.z for v in p),max(v.z for v in p)
world=bpy.data.worlds.new('APRESENTACAO_Ceu');world.use_nodes=True
background=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND')
background.inputs['Color'].default_value=(.72,.78,.85,1)
background.inputs['Strength'].default_value=.55
lightcol=bpy.data.collections.new('APRESENTACAO_Luzes')
for name,pos,power,size in [('Principal',(-4,-5,15),2300,9),('Fundos',(9,12,15),1800,8)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size
 o=bpy.data.objects.new(name,d);lightcol.objects.link(o);o.location=pos;o.rotation_euler=(Vector((3.175,4.5,1.5))-o.location).to_track_quat('-Z','Y').to_euler()
scenes=[];receipts=[]
for mode in ['terreo','dois-pavimentos']:
 scene=bpy.data.scenes.new('VISUALIZACAO_'+key+'_'+mode);scene.use_fake_user=True;scene.world=world
 group=bpy.data.collections.new('APRESENTACAO_'+mode);scene.collection.children.link(group);scene.collection.children.link(lightcol)
 included=[];wallnames=[];excluded=[]
 for o in sorted(geometry,key=lambda o:o.name):
  low,high=limits(o)
  if mode=='terreo' and (o.get('level')==1 or low>=2.55-1e-4):excluded.append(o.name);continue
  clone=o.copy();clone.name='VISTA '+mode+' '+o.name;clone.parent=None;clone.matrix_world=worlds[o];group.objects.link(clone)
  included.append(o.name)
  if o.get('wall_id'):wallnames.append(o.name)
 # Garante que todas as paredes documentais deste recorte estão presentes.
 required={o.name for o in geometry if o.get('wall_id') and (mode!='terreo' or o.get('level')!=1 and limits(o)[0]<2.55-1e-4)}
 assert required and required<=set(included)
 assert not any('CORTE ' in n or 'R07 Corte ' in n for n in wallnames)
 camera_data=bpy.data.cameras.new(scene.name);camera=bpy.data.objects.new(scene.name,camera_data);scene.collection.objects.link(camera);scene.camera=camera
 camera.location=(15,-16,30);camera.rotation_euler=(Vector((3.175,4.4,1.8))-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.type='ORTHO';camera_data.ortho_scale=16.5
 camera_data.clip_start=.1;camera_data.clip_end=200
 scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True;scene.cycles.adaptive_threshold=.04
 scene.cycles.transparent_max_bounces=24
 scene.render.resolution_x=1600;scene.render.resolution_y=1500;scene.render.resolution_percentage=100
 scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.filepath=str(OUT/(mode+'.png'))
 scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=.2
 scene.unit_settings.system='METRIC';scene['scope']='Paredes integrais e opacas; sem telhado, forro superior ou cobertura dos anexos.'
 receipts.append({'mode':mode,'objects':len(included),'full_wall_objects':wallnames,'included_objects':included,'excluded_upper_objects':excluded,'image':str(Path(scene.render.filepath).relative_to(ROOT))})
 scenes.append(scene)
# Remove cenas antigas apenas nesta cópia, mantendo dados visuais necessários.
for s in list(bpy.data.scenes):
 if s not in scenes:bpy.data.scenes.remove(s)
bpy.context.window.scene=scenes[0]
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL'
gpu=True
if '--render' in sys.argv:
 prefs=bpy.context.preferences.addons['cycles'].preferences
 try:
  prefs.compute_device_type='CUDA';prefs.get_devices();gpu=any(d.type=='CUDA' for d in prefs.devices)
  for d in prefs.devices:d.use=d.type=='CUDA'
 except Exception:gpu=False
for s in scenes:s.cycles.device='GPU' if gpu else 'CPU'
bpy.ops.wm.save_as_mainfile(filepath=str(DEST),compress=True)
if '--render' in sys.argv:
 for s in scenes:
  bpy.context.window.scene=s;bpy.ops.render.render(write_still=True,scene=s.name)
assert hashlib.sha256(src.read_bytes()).hexdigest()==sha
(ROOT/'relatorios'/key/'verificacao-pavimentos.json').write_text(json.dumps({'variant':key,'source':str(src.relative_to(ROOT)),'source_sha256':sha,'source_preserved':True,'blend':str(DEST.relative_to(ROOT)),'same_camera':True,'roof_removed':True,'side_walls_full_height':True,'jobs':receipts},ensure_ascii=False,indent=2),encoding='utf-8')
print('VISUALIZACOES_OK',key,flush=True)
