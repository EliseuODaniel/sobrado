"""Ático v05: dois U exatamente sobrepostos, caixa lateral e forro preservado."""
import argparse
import datetime as dt
import json
from pathlib import Path
import sys
import time

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
import blender_primitives as g
import residence07_geometry as geo
import residence07_attic_v05_data as data
from residence07_attic_primitives import collection,prism,ghost
from residence07_industrial import geometry_fingerprint,world

ROOT=data.ROOT;CFG=data.CFG;REPORT=ROOT/CFG['report_directory']
PRESERVE=['ATC3_Cobertura','ATC3_Fachadas_Mansardas','ATC3_Janelas','ATC3_Detalhes','ATC_Oitoes','ATC4_Forro','ATC4_Forro_Fixacao','ATUAL_Fundos','ATUAL_Cobertura_Fundos','R07_Contexto']


def stamp():return dt.datetime.now(dt.timezone.utc).isoformat()


def dump(name,value):
    REPORT.mkdir(parents=True,exist_ok=True);(REPORT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def states(cols):return {o.name:geometry_fingerprint(o) for c in cols for o in bpy.data.collections[c].all_objects}


def box(name,loc,size,mat,col):return g.box('ATC5 '+name,loc,size,mat,col.name,0)


def rail(name,points,col):
    for a,b in zip(points,points[1:]):g.rod('ATC5 '+name,a,b,.018,'ATC4 Metal',col.name)


def load_current_body():
    old=bpy.data.collections['ATUAL_Arquitetura']
    for o in list(old.objects):bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.collections.remove(old)
    with bpy.data.libraries.load(str(ROOT/CFG['current_blend']),link=False) as (src,dst):dst.collections=['ATUAL_Arquitetura']
    body=dst.collections[0];assert body.name=='ATUAL_Arquitetura'
    removed={}
    for o in list(body.objects):
        if 'R07 Montante guarda-corpo' in o.name or 'R07 Corrimao hall' in o.name:
            removed[o.name]=geometry_fingerprint(o);bpy.data.objects.remove(o,do_unlink=True)
    assert len(removed)==4
    return body,removed


def new_stair():
    tread=collection('ATC5_Escada');core=collection('ATC5_Espelhos');guard=collection('ATC5_Guardas')
    points=[]
    for step in data.steps():
        z=step['top'];p=step['polygon'];i=step['index']
        obj=prism(f'V05 Piso {i:02}',[(x,y,z-.025) for x,y in p],(0,0,.025),'ATC4 Granito',tread)
        obj['stair_index']=i;obj['top_z']=z;obj['exact_xy_source_index']=i
        obj=prism(f'V05 Corpo {i:02}',[(x,y,z-.29875) for x,y in p],(0,0,.27375),'ATC4 Branco',core)
        obj['stair_index']=i;obj['illustrative_stair_structure']=True
        if i<=5:x=sum(x for x,y in p)/len(p);y=4.11
        elif i<=11:x,y=max(p,key=lambda v:v[0]);x=min(6.21,x);y=max(2.19,min(4.11,y))
        else:x=sum(x for x,y in p)/len(p);y=2.19
        points.append((x,y,z+.93));rail('Montante escada',[(x,y,z),(x,y,z+.93)],guard)
    rail('Corrimao externo',points,guard)
    for y,z0,z1 in [(3.21,2.86875,3.54375),(3.09,5.4,4.725)]:
        rail('Corrimao interno',[(4.12,y,z0+.92),(5.32,y,z1+.92)],guard)
        for t in [0,.5,1]:
            x=4.12+1.2*t;z=z0*(1-t)+z1*t;rail('Montante interno',[(x,y,z),(x,y,z+.92)],guard)
    # Perímetro do vão em L; saída oeste no trecho de retorno Y=2,15..3,05.
    loop=[(4.1,2.15),(6.25,2.15),(6.25,4.15),(4.6,4.15),(4.6,3.25),(4.1,3.25),(4.1,3.05)]
    for p,q in zip(loop,loop[1:]):
        for t in [0,.5,1]:
            x=p[0]*(1-t)+q[0]*t;y=p[1]*(1-t)+q[1]*t;rail('Guarda vao',[(x,y,5.4),(x,y,6.4)],guard)
        for z in [5.85,6.4]:rail('Guarda travessa',[(p[0],p[1],z),(q[0],q[1],z)],guard)
    return tread,core,guard


def floor():
    col=collection('ATC5_Laje')
    for i,(a,b,c,d) in enumerate(data.floor_cells()):
        o=box('Laje '+str(i),((a+b)/2,(c+d)/2,5.325),(b-a,d-c,.15),'ATC Madeira',col);o['attic_floor']=True
    return col


def technical():
    col=collection('ATC5_Tecnica')
    for name,loc,size in [
        ('frente',(1.725,2.15,6.45),(3.15,.1,2.1)),('fundo',(1.725,4.3,6.45),(3.15,.1,2.1)),
        ('porta sul',(3.25,2.39,6.45),(.1,.48,2.1)),('porta norte',(3.25,3.91,6.45),(.1,.78,2.1)),
        ('verga',(3.25,3.07,7.46),(.1,.9,.08))]:box('Tecnica '+name,loc,size,'ATC Parede',col)
    return col


def relocate_tank():
    tank=bpy.data.collections['ATC_Reservatorio'];before={o.name:geometry_fingerprint(o) for o in tank.objects};delta=Vector((-3.55,0,0))
    for o in tank.objects:
        assert o.parent is None;o.location+=delta
        o['proposed_relocation_v05']=True
        if o.get('capacity_liters'):
            o['former_position_source']=o.get('position_source','');o['position_source']='Proposta v05 autorizada pelo usuário: X=1,80 / Y=3,175 / base Z=5,45 m.'
    return tank,before


def resize(o,size):
    o.data=o.data.copy()
    ext=[max(v.co[i] for v in o.data.vertices)-min(v.co[i] for v in o.data.vertices) for i in range(3)]
    for v in o.data.vertices:
        for i in range(3):v.co[i]*=size[i]/ext[i]


def furniture():
    col=bpy.data.collections['ATC_Mobiliario'];changes=[]
    for o in col.objects:
        old=list(o.location)
        if any(k in o.name for k in ['Mesa escritorio','Pe mesa','Monitor','Cadeira','Encosto']):o.location.y+=1.35
        if 'Sofa' in o.name:o.location.y-=1.0
        if 'Mesa lateral' in o.name:o.location.y=1.1
        if 'Tapete' in o.name:o.location.y=1.1;resize(o,(2.6,1.6,.025))
        if 'Armario baixo' in o.name:
            if o.location.y>3:o.location=(5.85,5.5,5.78);resize(o,(.6,1.2,.76))
            else:o.location.z=5.6;resize(o,(3.1,.65,.4))
        if list(o.location)!=old:changes.append({'object':o.name,'before':old,'after':list(o.location)})
    return col,changes


def heights():
    col=collection('ATC5_Alturas')
    for ix in range(61):
        xa=.15+ix*.1;xb=min(6.25,xa+.1);x=(xa+xb)/2;states=[]
        for iy in range(84):
            y=-1.15+iy*.1;states.append(None if not data.on_floor(x,y) else data.ceiling_z(x,y)-5.4>=2.1)
        start=0
        for iy in range(1,len(states)+1):
            if iy<len(states) and states[iy]==states[start]:continue
            if states[start] is not None:
                ya=-1.2+start*.1;yb=-1.2+iy*.1
                box('Faixa altura',((xa+xb)/2,(ya+yb)/2,5.412),(xb-xa,yb-ya,.015),'ATC4 Faixa alta' if states[start] else 'ATC4 Faixa baixa',col)
            start=iy
    return col


def isolated_context(originalstairs,tank,stair,core,guards):
    slabs=collection('ATC5_Recortes_Detalhe');route=collection('ATC5_Percurso_Detalhe')
    for z,rects in [(0,[[3.45,4.1,3.25,4.15]]),(2.7,[[3.45,4.1,2.15,4.15],[4.1,4.6,3.25,4.15]]),(5.4,[[3.3,4.1,2.15,4.15],[4.1,4.6,3.25,4.15],[.15,3.3,2.1,4.35]])]:
        for i,(a,b,c,d) in enumerate(rects):box(f'Recorte {z} {i}',((a+b)/2,(c+d)/2,z-.075),(b-a,d-c,.15),'ATC Madeira',slabs)
    old=geo.stair_polygons(geo.load());path=[(3.8,3.7,.045)]
    for i,p in enumerate(old):path.append((sum(x for x,y in p)/len(p),sum(y for x,y in p)/len(p),(i+1)*.16875+.045))
    path.extend([(3.8,2.6,2.745),(3.8,3.7,2.745),(4.1,3.7,2.745)])
    for step in data.steps():
        p=step['polygon'];path.append((sum(x for x,y in p)/len(p),sum(y for x,y in p)/len(p),step['top']+.045))
    path.extend([(3.65,2.6,5.445),(3.4,2.6,5.445)])
    for a,b in zip(path,path[1:]):g.rod('ATC5 Percurso completo',a,b,.014,'ATC4 Percurso',route.name)
    return [originalstairs,tank,stair,core,guards,slabs,route]


def build():
    data.validate();assert Path(bpy.data.filepath).resolve()==ROOT/CFG['base_blend'];dest=ROOT/CFG['output_blend'];assert not dest.exists(),dest
    source_hash=geo.sha(ROOT/CFG['base_blend']);current_hash=geo.sha(ROOT/CFG['current_blend']);before=states(PRESERVE)
    body,removed=load_current_body()
    g.C.update({c.name:c for c in bpy.data.collections});g.M.update({m.name:m for m in bpy.data.materials})
    expected_body={o.name:geometry_fingerprint(o) for o in body.objects}
    stair,core,guards=new_stair();slab=floor();tech=technical();tank,former_tank=relocate_tank();f,changes=furniture();heightmap=heights()
    techg=ghost(tech,'ATC5_Tecnica_Transparente');slabg=ghost(slab,'ATC5_Laje_Transparente');bodyg=ghost(body,'ATC5_Casa_Transparente')
    originalstairs=collection('ATC5_Escada_Existente')
    for o in body.objects:
        if 'ATUAL R07 Degrau' in o.name or 'ATUAL R07 Longarina' in o.name:originalstairs.objects.link(o)
    route=collection('ATC5_Percurso_Hall')
    for a,b in zip(CFG['stair']['arrival_path'],CFG['stair']['arrival_path'][1:]):g.rod('ATC5 Percurso hall',Vector(a)+Vector((0,0,.025)),Vector(b)+Vector((0,0,.025)),.014,'ATC4 Percurso',route.name)
    isolated=isolated_context(originalstairs,tank,stair,core,guards)
    roof=bpy.data.collections['ATC3_Cobertura'];lining=bpy.data.collections['ATC4_Forro'];roofg=bpy.data.collections['ATC3_Cobertura_Transparente'];liningg=bpy.data.collections['ATC4_Forro_Transparente']
    gab=bpy.data.collections['ATC_Oitoes'];gabg=bpy.data.collections['ATC_Oitoes_Transparentes'];walls=bpy.data.collections['ATC3_Fachadas_Mansardas'];wallg=bpy.data.collections['ATC3_Fachadas_Transparentes'];windows=bpy.data.collections['ATC3_Janelas'];details=bpy.data.collections['ATC3_Detalhes'];fix=bpy.data.collections['ATC4_Forro_Fixacao']
    actualbody=[body,*[bpy.data.collections[k] for k in ['ATUAL_Fundos','ATUAL_Cobertura_Fundos','R07_Contexto']]]
    cameras=collection('ATC5_Cameras');lighting=bpy.data.collections['R07_Iluminacao'];detail_lights=collection('ATC5_Luzes_Detalhe')
    detail_world=bpy.data.worlds.new('ATC5 Fundo claro');detail_world.use_nodes=True;detail_world.node_tree.nodes['Background'].inputs['Color'].default_value=(.82,.86,.9,1);detail_world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
    for name,loc,energy,size in [('principal',(-3,-3,11),1400,6),('preenchimento',(9,6,10),1100,5)]:
        ld=bpy.data.lights.new('ATC5 '+name,'AREA');ld.energy=energy;ld.size=size;o=bpy.data.objects.new(ld.name,ld);detail_lights.objects.link(o);o.location=loc;o.rotation_euler=(Vector((3.2,3.175,3.3))-o.location).to_track_quat('-Z','Y').to_euler()
    jobs=[]
    for j in data.jobs():
        mode=j['mode'];isolated_mode=mode=='isolated'
        if isolated_mode:cols=isolated
        elif mode in ['exterior','roof-detail','interior']:cols=[*actualbody,slab,stair,core,guards,f,tank,tech,gab,roof,walls,windows,details,lining]
        elif mode=='tank':cols=[slab,tank,techg,gabg,liningg,fix]
        elif mode in ['access','entry']:cols=[bodyg,originalstairs,slabg,stair,core,guards,tank,techg,route]
        elif mode=='stair':cols=isolated
        elif mode=='lower-plan':cols=[*actualbody,stair,core,guards,route]
        elif mode=='ceiling-cut':cols=[slab,stair,core,guards,tank,techg,f,bpy.data.collections['ATC4_Cobertura_Corte'],bpy.data.collections['ATC4_Forro_Corte'],fix,wallg,windows]
        elif mode=='heights':cols=[slab,heightmap,stair,core,guards,tank,techg,wallg,windows]
        elif mode=='ghost':cols=[slab,stair,core,guards,tank,techg,gabg,f,roofg,liningg,windows,wallg,details]
        else:cols=[slab,stair,core,guards,tank,techg,gabg,f,wallg,windows]
        scene=bpy.data.scenes.new('ATC5_'+j['id']);scene.use_fake_user=True;scene.world=detail_world if isolated_mode else bpy.data.worlds.get('R07 Ceu diurno')
        for col in [*cols,cameras,detail_lights if isolated_mode else lighting]:
            if col.name not in scene.collection.children:scene.collection.children.link(col)
        cd=bpy.data.cameras.new(scene.name);cam=bpy.data.objects.new(scene.name+'_Camera',cd);cameras.objects.link(cam);scene.camera=cam
        cam.location=j['pos'];cam.rotation_euler=(Vector(j['target'])-cam.location).to_track_quat('-Z','Y').to_euler()
        if j.get('top'):cam.rotation_euler=(0,0,0)
        if 'ortho' in j:cd.type='ORTHO';cd.ortho_scale=j['ortho']
        else:cd.lens=j['lens']
        cd.clip_start=.03;scene.render.engine='CYCLES';scene.cycles.samples=32 if j['group']=='orbit' else CFG['samples'];scene.cycles.use_denoising=True;scene.cycles.adaptive_threshold=.03;scene.cycles.transparent_max_bounces=40
        resolution=[900,1000] if j['group']=='orbit' else [1800,2000] if j['group']=='detail' else CFG['resolution']
        scene.render.resolution_x,scene.render.resolution_y=resolution;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA' if isolated_mode else 'RGB';scene.render.film_transparent=isolated_mode
        scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=.15 if isolated_mode else -.1 if mode=='interior' else -.5
        folder='07-escadas/02-giro/quadros' if j['group']=='orbit' else '07-escadas/01-vistas' if j['group']=='detail' else '01-exteriores' if mode in ['exterior','roof-detail'] else '02-interiores' if mode=='interior' else '04-plantas' if mode in ['plan','lower-plan','heights'] else '03-tecnica'
        path=Path(CFG['render_directory'])/folder/(j['id']+'.png');scene.render.filepath=str(ROOT/path);scene.unit_settings.system='METRIC';scene['attic_version']=CFG['version'];scene['config_sha256']=geo.sha(data.CONFIG)
        jobs.append({**j,'scene':scene.name,'file':str(path),'resolution':resolution})
    for s in list(bpy.data.scenes):
        if s.name not in {j['scene'] for j in jobs}:bpy.data.scenes.remove(s)
    bpy.context.window.scene=bpy.data.scenes['ATC5_01-referencia'];bpy.context.view_layer.update()
    assert states(PRESERVE)==before;assert {o.name:geometry_fingerprint(o) for o in body.objects}==expected_body
    bpy.ops.file.pack_all();bpy.ops.outliner.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
    dest.parent.mkdir(parents=True,exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
    assert geo.sha(ROOT/CFG['base_blend'])==source_hash and geo.sha(ROOT/CFG['current_blend'])==current_hash
    dump('modelo.json',{'timestamp_utc':stamp(),'version':CFG['version'],'blend':CFG['output_blend'],'blend_sha256':geo.sha(dest),'base_blend':CFG['base_blend'],'base_sha256':source_hash,'current_blend':CFG['current_blend'],'current_sha256':current_hash,'config_sha256':geo.sha(data.CONFIG),
        'preserved_geometry':before,'body_geometry':expected_body,'removed_guard':removed,'tank_before':former_tank,'tank_after':states(['ATC_Reservatorio']),'furniture_changes':changes,'jobs':jobs,'geometry':data.validate(),
        'generators':{str(p.relative_to(ROOT)):geo.sha(p) for p in [Path(__file__),data.CONFIG,ROOT/'scripts/residence07_attic_v05_data.py',ROOT/'scripts/residence07_attic_primitives.py',ROOT/'scripts/residence07_attic_roof.py',ROOT/'config/residencia-07-cobertura.json',ROOT/'scripts/residence07_geometry.py',ROOT/'scripts/residence07_industrial.py',ROOT/'scripts/blender_primitives.py']},'notes':CFG['notes']})
    print('ATC5_BUILD_OK',len(jobs),'vistas',data.validate(),flush=True)


def render(group='main',preview=False,only=None):
    model=json.loads((REPORT/'modelo.json').read_text());assert geo.sha(bpy.data.filepath)==model['blend_sha256']
    for p,h in model['generators'].items():assert geo.sha(ROOT/p)==h,p
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices();assert any(d.type=='CUDA' for d in prefs.devices)
    for d in prefs.devices:d.use=d.type=='CUDA'
    for j in model['jobs']:
        if only and j['id'] not in only.split(','):continue
        if not only and group!='all' and j['group']!=group:continue
        scene=bpy.data.scenes[j['scene']];bpy.context.window.scene=scene;scene.cycles.device='GPU'
        dest=REPORT/'previas'/(j['id']+'.png') if preview else ROOT/j['file'];dest.parent.mkdir(parents=True,exist_ok=True);scene.render.filepath=str(dest)
        scene.render.resolution_percentage=40 if preview else 100;scene.cycles.samples=16 if preview else 32 if j['group']=='orbit' else CFG['samples']
        start=time.monotonic();bpy.ops.render.render(write_still=True,scene=scene.name)
        path=REPORT/('previas.json' if preview else 'renders.json');rows=json.loads(path.read_text()) if path.exists() else []
        merged={r['id']:r for r in rows if r['blend_sha256']==model['blend_sha256']};merged[j['id']]={'id':j['id'],'file':str(dest.relative_to(ROOT)),'sha256':geo.sha(dest),'blend_sha256':model['blend_sha256'],'group':j['group'],'preview':preview,'seconds':round(time.monotonic()-start,2)};dump(path.name,list(merged.values()))
        print('ATC5_RENDER_OK',j['id'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--render',action='store_true');p.add_argument('--preview',action='store_true');p.add_argument('--group',default='main');p.add_argument('--only');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if a.render:render(a.group,a.preview,a.only)
    else:build()
