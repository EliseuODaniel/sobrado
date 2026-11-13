"""Utilitários Blender para versões de estudo independentes da residência 07."""
import datetime as dt
import json
import math
from pathlib import Path
import sys
import time

import bpy
from mathutils import Vector

import blender_primitives as g
import residence07_geometry as geo
import residence07_studies_data as data

ROOT=geo.ROOT
REPORT=ROOT/data.CFG['report_directory']
M={};C={};JOBS=[]
COLORS={'cold':(.015,.22,.95),'hot':(.90,.045,.025),'sewer':(.32,.095,.018),
        'vent':(.05,.52,.13),'electric':(1.0,.42,.015),'telecom':(.02,.62,.72)}
LABELS={'cold':'Água fria','hot':'Água quente','sewer':'Esgoto','vent':'Ventilação','electric':'Elétrica','telecom':'TV / telefone'}


def stamp():return dt.datetime.now(dt.timezone.utc).isoformat()


def collection(name):
    col=bpy.data.collections.new(name);C[name]=col;g.C[name]=col
    return col


def material(name,color,opacity=1,emission=0):
    mat=g.basic(name,color,.72);M[name]=mat
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if emission:
        bs.inputs['Emission Color'].default_value=(*color,1);bs.inputs['Emission Strength'].default_value=emission
    if opacity<1:
        nodes,links=mat.node_tree.nodes,mat.node_tree.links
        transparent=nodes.new('ShaderNodeBsdfTransparent');mix=nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=opacity
        links.new(transparent.outputs[0],mix.inputs[1]);links.new(bs.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],nodes.get('Material Output').inputs['Surface'])
    mat.diffuse_color=(*color,opacity);mat['study_opacity']=opacity
    return mat


def initialize():
    g.C.update({c.name:c for c in bpy.data.collections});g.M.update({m.name:m for m in bpy.data.materials})
    g.C['Iluminacao']=bpy.data.collections['R07_Iluminacao']
    palette=data.CFG['palette']
    material('EST Parede sálvia suave',palette['wall']);material('EST Laje creme',palette['slab']);material('EST Escada areia',palette['stair'])
    material('EST Parede transparente',palette['wall'],palette['wall_opacity'])
    material('EST Laje transparente',palette['slab'],palette['slab_opacity'])
    material('EST Contorno',(.28,.37,.32));material('EST Caixa dagua',(.035,.12,.27));material('EST Branco',(.76,.74,.68))
    for key,color in COLORS.items():material('EST Rede '+key,color,emission=.17)
    REPORT.mkdir(parents=True,exist_ok=True)


def copy_objects(source,dest,mat=None,offset=(0,0,0),prefix='EST '):
    result=[]
    for original in list(source.objects):
        obj=original.copy();obj.name=prefix+original.name;obj.location+=Vector(offset)
        if mat and obj.type in ['MESH','CURVE']:
            obj.data=original.data.copy();obj.data.materials.clear();obj.data.materials.append(mat)
        obj['study_source_object']=original.name;obj['study_geometry_unchanged']=True
        dest.objects.link(obj);result.append(obj)
    return result


def architectural_variant(kind):
    """Matériaux propres au scénario; aucun matériau du modèle source n'est modifié."""
    col=collection('EST_Architecture_'+kind)
    transparent=kind=='ghost'
    keys=['R07_Paredes_Terreo','R07_Paredes_Superior','R07_Piso_Terreo','R07_Piso_Superior','R07_Escada']
    for key in keys:
        wall='Paredes' in key;floor='Piso_' in key
        mat=M['EST Parede transparente' if wall and transparent else 'EST Laje transparente' if transparent and floor else 'EST Parede sálvia suave' if wall else 'EST Laje creme' if floor else 'EST Escada areia']
        copy_objects(bpy.data.collections[key],col,mat,prefix='EST '+kind+' ')
    return col


def polyline(name,points,diameter,mat,col,**props):
    # Spline poligonal: os tubos não ganham curvas ou interpolações inventadas.
    curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.resolution_u=1;curve.bevel_depth=diameter/2;curve.bevel_resolution=3
    spline=curve.splines.new('POLY');spline.points.add(len(points)-1)
    for p,xyz in zip(spline.points,points):p.co=(*xyz,1)
    obj=bpy.data.objects.new(name,curve);col.objects.link(obj);curve.materials.append(mat)
    for k,v in props.items():obj[k]=v
    return obj


def box(name,loc,size,mat,col,bevel=.006):
    return g.box(name,loc,size,mat,col.name,bevel)


def tank(col,position=None):
    cfg=data.CFG['tank'];x,y=position or cfg['center_xy'];z=cfg['base_z'];r=cfg['display_diameter']/2;h=cfg['display_height']
    obj=g.lathe('EST Caixa dagua 1000 L',[(0,0),(.80*r,0),(.88*r,.08),(.97*r,h-.13),(r,h-.08),(r,h),(.90*r,h+.035),(0,h+.035)],(x,y,z),'EST Caixa dagua',col.name,segments=64)
    obj['capacity_liters']=1000;obj['position_source']=cfg['position_source'];obj['envelope_status']=cfg['envelope_status']
    for zz in [.25,.55,.85]:
        rr=r*(.88+.09*zz/h)
        polyline('EST Friso reservatorio',[(x+rr*math.cos(i*math.tau/64),y+rr*math.sin(i*math.tau/64),z+zz) for i in range(65)],.018,M['EST Caixa dagua'],col)
    # Folga de acesso superior ilustrativa, sem representar suporte calculado.
    return obj


def camera_scene(job,collections,path,prefix='EST_',exposure=-.65):
    scene=bpy.data.scenes.new(prefix+job['id']);scene.world=bpy.data.worlds.get('R07 Ceu diurno') or bpy.context.scene.world
    for col in collections:scene.collection.children.link(col)
    if 'R07_Iluminacao' not in scene.collection.children:scene.collection.children.link(bpy.data.collections['R07_Iluminacao'])
    cameras=C.get('EST_Cameras') or collection('EST_Cameras')
    scene.collection.children.link(cameras)
    cd=bpy.data.cameras.new(prefix+job['id']);cam=bpy.data.objects.new(cd.name,cd);cameras.objects.link(cam)
    cam.location=job['pos'];cam.rotation_euler=(Vector(job['target'])-cam.location).to_track_quat('-Z','Y').to_euler()
    if job.get('top'):cam.rotation_euler=(0,0,0)
    if 'ortho' in job:cd.type='ORTHO';cd.ortho_scale=job['ortho']
    else:cd.lens=job.get('lens',24)
    cd.clip_start=.04;scene.camera=cam
    scene.unit_settings.system='METRIC';scene.unit_settings.length_unit='METERS'
    scene.render.engine='CYCLES';scene.cycles.samples=data.CFG['samples'];scene.cycles.use_denoising=True;scene.cycles.adaptive_threshold=.03
    scene.cycles.transparent_max_bounces=32;scene.cycles.max_bounces=12
    scene.render.resolution_x,scene.render.resolution_y=data.CFG['resolution'];scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.filepath=str(path)
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=exposure
    scene['study_view']=job['id'];scene['study_title']=job['title'];scene['study_config_sha256']=geo.sha(data.CONFIG)
    scene['geometry_source_sha256']=geo.sha(geo.CONFIG)
    JOBS.append({**job,'scene':scene.name,'file':str(path.relative_to(ROOT))})
    return scene


def finish_build(kind,destination,metadata):
    if destination.exists():raise FileExistsError('Destino já existe: '+str(destination))
    new_scenes={j['scene'] for j in JOBS}
    for scene in list(bpy.data.scenes):
        if scene.name not in new_scenes:bpy.data.scenes.remove(scene)
    bpy.context.window.scene=bpy.data.scenes[JOBS[0]['scene']]
    bpy.ops.file.pack_all();bpy.ops.outliner.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
    destination.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(destination),compress=True)
    receipt={'timestamp_utc':stamp(),'kind':kind,'blend':str(destination.relative_to(ROOT)),'blend_sha256':geo.sha(destination),
             'source_blend':data.CFG['base_blend'],'source_blend_sha256':geo.sha(ROOT/data.CFG['base_blend']),
             'config_sha256':geo.sha(data.CONFIG),'jobs':JOBS,'objects':len(bpy.data.objects),**metadata}
    receipt['generators']={str(p.relative_to(ROOT)):geo.sha(p) for p in (ROOT/'scripts').glob('residence07_*.py') if p.name in ['residence07_studies_scene.py','residence07_studies_data.py','residence07_'+{'atual':'current','atico':'attic','instalacoes':'services'}[kind]+'.py']}
    (REPORT/(kind+'-modelo.json')).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print('STUDY_BUILD_OK',kind,len(JOBS),'views',flush=True)


def render(kind,preview=False,only=None):
    path=REPORT/(kind+'-modelo.json');model=json.loads(path.read_text())
    assert geo.sha(bpy.data.filepath)==model['blend_sha256'],'Modelo alterado após a geração.'
    assert geo.sha(data.CONFIG)==model['config_sha256'],'Configuração alterada após a geração.'
    for path,digest in model.get('generators',{}).items():assert geo.sha(ROOT/path)==digest,'Gerador alterado após salvar o modelo: '+path
    if only:assert set(only.split(','))<={j['id'] for j in model['jobs']},'Câmera solicitada inexistente.'
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices()
    assert any(d.type=='CUDA' for d in prefs.devices)
    for d in prefs.devices:d.use=d.type=='CUDA'
    records=[]
    for job in model['jobs']:
        if only and job['id'] not in only.split(','):continue
        scene=bpy.data.scenes[job['scene']];bpy.context.window.scene=scene;scene.cycles.device='GPU'
        dest=ROOT/job['file']
        if preview:dest=REPORT/'previas'/kind/dest.name
        dest.parent.mkdir(parents=True,exist_ok=True);scene.render.filepath=str(dest)
        scene.render.resolution_percentage=45 if preview else 100;scene.cycles.samples=24 if preview else data.CFG['samples']
        start=time.monotonic();bpy.ops.render.render(write_still=True,scene=scene.name)
        records.append({'id':job['id'],'scene':job['scene'],'file':str(dest.relative_to(ROOT)),
                        'sha256':geo.sha(dest),'source_blend':model['blend'],'blend_sha256':model['blend_sha256'],
                        'seconds':round(time.monotonic()-start,2),'preview':preview})
        (REPORT/(kind+('-previas' if preview else '-renders-parcial')+'.json')).write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
        print('STUDY_RENDER_OK',kind,job['id'],records[-1]['seconds'],flush=True)
    if not preview:
        final=REPORT/(kind+'-renders.json');old=json.loads(final.read_text()) if final.exists() else []
        merged={r['id']:r for r in old if r['blend_sha256']==model['blend_sha256']};merged.update({r['id']:r for r in records})
        final.write_text(json.dumps(list(merged.values()),ensure_ascii=False,indent=2)+'\n')
    return records
