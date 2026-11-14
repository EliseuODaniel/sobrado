"""Adiciona comparação lado a lado no mesmo Blender, sem renderizar."""
from pathlib import Path
import bpy,json,sys
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1]
receipts=[]
for key in ['original','atual','industrial']:
 path=ROOT/('.tools/floor-repair' if '--repair' in sys.argv else 'projeto')/key/'visualizacao-pavimentos.blend'
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.preferences.filepaths.save_version=0
 name='VISUALIZACAO_'+key+'_COMPARACAO'
 assert name not in bpy.data.scenes,'A comparação já existe neste arquivo'
 source=bpy.data.scenes['VISUALIZACAO_'+key+'_terreo']
 bpy.context.window.scene=bpy.data.scenes['VISUALIZACAO_'+key+'_dois-pavimentos']
 bpy.context.scene.frame_set(bpy.context.scene.frame_current);bpy.context.view_layer.update()
 scene=bpy.data.scenes.new(name);scene.use_fake_user=True;scene.world=source.world
 counts=[]
 for mode,dx,label in [('terreo',-5.2,'SOMENTE TÉRREO'),('dois-pavimentos',5.2,'TÉRREO + SEGUNDO PAVIMENTO')]:
  bpy.context.window.scene=bpy.data.scenes['VISUALIZACAO_'+key+'_'+mode]
  bpy.context.scene.frame_set(bpy.context.scene.frame_current);bpy.context.view_layer.update()
  depsgraph=bpy.context.evaluated_depsgraph_get();depsgraph.update()
  group=bpy.data.collections.new('COMPARACAO_'+mode);scene.collection.children.link(group)
  count=0
  for old in bpy.data.collections['APRESENTACAO_'+mode].objects:
   # Grandes pisos do entorno são omitidos apenas do painel para não sobrepor as casas.
   matrix=old.evaluated_get(depsgraph).matrix_world.copy()
   pts=[matrix@Vector(p) for p in old.bound_box]
   if pts and max(p.z for p in pts)<.12 and max(p.x for p in pts)-min(p.x for p in pts)>8:continue
   obj=old.copy();obj.name='COMPARACAO '+mode+' '+old.name;obj.parent=None;obj.matrix_world=Matrix.Translation((dx,0,0))@matrix;group.objects.link(obj);count+=1
  font=bpy.data.curves.new(label,'FONT');font.body=label;font.size=.32;font.align_x='CENTER'
  material=bpy.data.materials.get('COMPARACAO Texto') or bpy.data.materials.new('COMPARACAO Texto');material.diffuse_color=(.025,.055,.05,1);font.materials.append(material)
  text=bpy.data.objects.new(label,font);group.objects.link(text);text.location=(3.175+dx,-2.2,.05)
  counts.append(count)
 scene.collection.children.link(bpy.data.collections['APRESENTACAO_Luzes'])
 data=bpy.data.cameras.new(name);camera=bpy.data.objects.new(name,data);scene.collection.objects.link(camera);scene.camera=camera
 camera.location=(3.175,-25,33);camera.rotation_euler=(Vector((3.175,4.1,1.5))-camera.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=22.5;data.clip_end=200
 scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True;scene.cycles.device=source.cycles.device;scene.cycles.transparent_max_bounces=24
 scene.render.resolution_x=2400;scene.render.resolution_y=1500;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 scene.render.filepath=str(ROOT/'renders'/key/'vistas-pavimentos/comparacao-lado-a-lado.png')
 scene.view_settings.view_transform=source.view_settings.view_transform;scene.view_settings.look=source.view_settings.look;scene.view_settings.exposure=source.view_settings.exposure
 scene['scope']='Esquerda: térreo isolado. Direita: térreo com segundo pavimento, sem telhado. Paredes laterais completas nas duas casas.'
 bpy.context.window.scene=scene
 for screen in bpy.data.screens:
  for area in screen.areas:
   if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL'
 assert len([s for s in bpy.data.scenes if s.name.startswith('VISUALIZACAO_')])==3
 bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
 receipts.append({'variant':key,'default_scene':name,'left':'terreo','right':'dois-pavimentos','copied_objects':counts,'rendered':False,'blend':path.relative_to(ROOT).as_posix()})
(ROOT/'relatorios/comparacao-lado-a-lado.json').write_text(json.dumps(receipts,ensure_ascii=False,indent=2),encoding='utf-8')
print('COMPARACAO_LADO_A_LADO_OK',receipts,flush=True)
