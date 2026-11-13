"""Proposta industrial sobre o arquivo atual, preservando a arquitetura métrica."""
import argparse
from array import array
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import sys
import time

import bpy
from mathutils import Matrix,Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
import blender_primitives as g
import residence07_geometry as geo
import residence07_industrial_data as data
import industrial_bar_policy

ROOT=data.ROOT;CFG=data.CFG;REPORT=ROOT/CFG['report_directory']
PLACEMENTS=[]


def stamp():return dt.datetime.now(dt.timezone.utc).isoformat()


def world(obj):return world(obj.parent)@obj.matrix_parent_inverse@obj.matrix_basis if obj.parent else obj.matrix_basis.copy()


def family(obj):
    names=[]
    while obj:names.append(obj.name);obj=obj.parent
    return names


def geometry_fingerprint(obj):
    h=hashlib.sha256()
    if obj.type=='MESH':
        coords=array('f',[0])*len(obj.data.vertices)*3;obj.data.vertices.foreach_get('co',coords);h.update(coords.tobytes())
        h.update(json.dumps([list(p.vertices) for p in obj.data.polygons]).encode())
    elif obj.type=='CURVE':
        h.update(json.dumps([[list(p.co) for p in sp.points] for sp in obj.data.splines]).encode())
    state={'type':obj.type,'world':[[round(x,7) for x in row] for row in world(obj)],
        'modifiers':[(m.name,m.type) for m in obj.modifiers],'hidden':obj.hide_render}
    h.update(json.dumps(state,sort_keys=True).encode());return h.hexdigest()


def protected():
    objects={o for key in CFG['protected_collections'] for o in bpy.data.collections[key].all_objects}
    return {o.name:geometry_fingerprint(o) for o in sorted(objects,key=lambda o:o.name)}


def collection(name):
    col=bpy.data.collections.new(name);g.C[name]=col;return col


def box(name,loc,size,mat,col,bevel=.008,par=None):return g.box('IND07 '+name,loc,size,mat,col.name,bevel,par)


def assign(obj,mat):
    if obj.type not in ['MESH','CURVE']:return
    obj.data=obj.data.copy();obj.data.materials.clear();obj.data.materials.append(g.M[mat] if isinstance(mat,str) else mat)


def remove_family(root):
    for obj in [*root.children_recursive,root]:
        if bpy.data.objects.get(obj.name):bpy.data.objects.remove(obj,do_unlink=True)


def materials():
    p=CFG['palette']
    g.textured('IND07 Cimento',p['cement'],'stone',.78,.00065)
    g.textured('IND07 Piso cimento',p['floor'],'stone',.30,.00018)
    g.textured('IND07 Madeira quente',p['wood'],'wood',.40,.0006)
    g.textured('IND07 Linho',p['linen'],'leather',.92,.00025)
    g.textured('IND07 Couro',p['leather'],'leather',.47,.00025)
    g.basic('IND07 Aco',p['metal'],.36,.7);g.basic('IND07 Grafite',p['graphite'],.50)
    g.basic('IND07 Petroleo',p['petrol'],.76);g.basic('IND07 Teto',(.72,.69,.62),.82)
    g.basic('IND07 LED',(1,.56,.22),.40,emission=3)
    g.basic('IND07 Pedra',(.025,.030,.027),.23)
    g.textured('IND07 Juta',[[.22,.18,.12],[.42,.35,.25]],'leather',.96,.0008)
    # Reutilizar superfícies PBR da biblioteca de móveis, sem aproveitar sua arquitetura.
    for old,new in [('DESIGN Couro conhaque','IND07 Couro PBR'),('DESIGN Carvalho mel','IND07 Carvalho PBR'),('HQ Cimento','IND07 Cimento PBR')]:
        mat=bpy.data.materials.get(old)
        if mat:copy=mat.copy();copy.name=new;g.M[new]=copy
    leather=g.M['IND07 Couro PBR'];nodes,links=leather.node_tree.nodes,leather.node_tree.links;bs=nodes.get('Principled BSDF')
    source=bs.inputs['Base Color'].links[0].from_socket;hue=nodes.new('ShaderNodeHueSaturation');hue.inputs['Value'].default_value=.68;hue.inputs['Saturation'].default_value=.88
    links.new(source,hue.inputs['Color']);links.new(hue.outputs[0],bs.inputs['Base Color'])


def append_furniture(target):
    """Importar apenas coleções de móveis e instanciar componentes selecionados."""
    with bpy.data.libraries.load(str(ROOT/CFG['furniture_library']),link=False) as (src,dst):
        dst.collections=['DESIGN_Sala_Objetos'];dst.materials=['DESIGN Pedra natural oxidada']
    col=dst.collections[0];g.M.update({m.name:m for m in bpy.data.materials})
    definitions=[('DESIGN Sofá contemporâneo',(.65,1.70,0)),('DESIGN Mesa de centro',(1.72,1.72,0))]
    definitions += [('DESIGN Cadeira jantar '+str(i+1),(*xy,0)) for i,xy in enumerate(CFG['dining']['chairs'])]
    definitions += [('PHOTO V04 Almofadas linho',(.48,2.33,.55)),('PHOTO V04 Planta canto',(.44,3.12,.24)),
        ('PHOTO V04 Arranjo botânico (1.72, 2.0, 0.418)',(1.72,1.97,.418)),
        ('PHOTO V04 Arranjo botânico (1.52, 5.8, 0.815)',(1.60,4.5,.80))]
    for name,position in definitions:
        original=next(o for o in col.objects if o.name==name);members=[original,*original.children_recursive]
        offset=Vector(position)-world(original).translation;copies={};desired={}
        for old in members:
            clone=old.copy();clone.name='IND07 '+old.name;clone.hide_render=False;clone.hide_viewport=False
            mat=world(old);mat.translation+=offset;clone.parent=None;clone.matrix_world=mat;target.objects.link(clone)
            copies[old]=clone;desired[old]=mat;clone['industrial_asset_source']=name
        for old,clone in copies.items():
            if old.parent in copies:
                clone.parent=copies[old.parent];clone.matrix_parent_inverse=Matrix.Identity(4);clone.matrix_basis=desired[old.parent].inverted_safe()@desired[old]
            else:clone.matrix_world=desired[old]
        PLACEMENTS.append({'source':name,'location':list(position),'objects':len(copies),'scale_policy':'Escala original preservada; somente translação do conjunto'})


def restyle():
    mappings={'ATUAL Parede':'IND07 Cimento','ATUAL Piso':'IND07 Piso cimento','Areia':'IND07 Piso cimento',
        'Piso':'IND07 Piso cimento','Armario cozinha cinza':'IND07 Grafite','ATUAL Cinza':'IND07 Grafite',
        'Parede azul':'IND07 Petroleo','Armario branco':'IND07 Grafite','Lencol':'IND07 Linho',
        'ATUAL Tecido':'IND07 Linho','Madeira bar.001':'IND07 Madeira quente','R07 Carvalho mel':'IND07 Madeira quente',
        'Metal preto':'IND07 Aco','Preto':'IND07 Aco','Estofado cadeira cinza':'IND07 Couro','ATUAL Pedra':'IND07 Pedra',
        'DESIGN Couro conhaque':'IND07 Couro PBR'}
    for obj in list(bpy.data.objects):
        if obj.type not in ['MESH','CURVE']:continue
        for slot in obj.material_slots:
            if slot.material and slot.material.name in mappings:slot.material=g.M[mappings[slot.material.name]]
        n=obj.name
        if n.startswith('R07 Teto'):assign(obj,'IND07 Teto')
        elif n.startswith(('ATUAL Painel TV','ATUAL Cabeceira suite')):assign(obj,'IND07 Cimento')
        elif n.startswith(('ATUAL Rack branco','ATUAL Roupeiro quarto','ATUAL Armario suspenso')):assign(obj,'IND07 Grafite')
        elif n.startswith(('ATUAL Rack tampo','ATUAL Bancada pia adaptada','ATUAL Escrivaninha')):assign(obj,'IND07 Madeira quente' if 'pia' not in n else 'IND07 Pedra')
        elif n.startswith(('ATUAL Caixilho','ATUAL Ripado','ATUAL Trilho','ATUAL Puxador')):assign(obj,'IND07 Aco')
    # Evitar linguagem antiga na sala/jantar e retirar apenas banquetas, não o balcão.
    for key in ['ATUAL_AMB_sala','ATUAL_AMB_jantar']:
        col=bpy.data.collections[key]
        for obj in list(col.objects):
            if bpy.data.objects.get(obj.name):bpy.data.objects.remove(obj,do_unlink=True)
    stools=[o for o in bpy.data.collections['ATUAL_AMB_bar'].objects if o.type=='EMPTY' and 'BANQUETA_BAR_' in o.name]
    for obj in stools:remove_family(obj)
    for obj in list(bpy.data.collections['ATUAL_AMB_bar'].objects):
        if obj.name.startswith(('ATUAL Pendente bar original','ATUAL Cabo pendente bar')):bpy.data.objects.remove(obj,do_unlink=True)


def light(name,loc,target,power=15,size=.4,color=(1,.72,.43),kind='AREA'):
    obj=g.light('IND07 '+name,loc,power,color,kind,target,size)
    if kind=='AREA':obj.visible_glossy=False;obj.visible_transmission=False
    return obj


def strip(name,a,b,col,power=8):
    g.rod('IND07 '+name,a,b,.007,'IND07 LED',col.name)
    center=(Vector(a)+Vector(b))/2;light(name,center,center+Vector((0,-.35,-.35)),power,size=.30)


def pendant(name,x,y,z,col):
    g.rod('IND07 Cabo '+name,(x,y,z+.21),(x,y,2.54),.003,'IND07 Aco',col.name)
    g.lathe('IND07 Cupula '+name,[(.18,0),(.17,.04),(.10,.16),(.03,.21)],(x,y,z),'IND07 Aco',col.name,segments=48)
    g.sphere('IND07 Lampada '+name,(x,y,z+.01),(.045,.045,.028),'IND07 LED',col.name)
    light('Pendente '+name,(x,y,z-.02),(x,y,0),24,size=.28)


def table_and_stools(col):
    x,y=CFG['dining']['center'];w,l,h=CFG['dining']['table_size'];wood='IND07 Carvalho PBR' if 'IND07 Carvalho PBR' in g.M else 'IND07 Madeira quente'
    for i in range(4):box('Tabua mesa jantar',(x-w/2+(i+.5)*w/4,y,h),(w/4-.004,l,.045),wood,col,.006)
    for xx in [x-w/2+.06,x+w/2-.06]:
        box('Saia mesa jantar',(xx,y,h-.10),(.045,l-.12,.15),wood,col)
        for yy in [y-l/2+.10,y+l/2-.10]:
            g.lathe('IND07 Pe torneado mesa',[(.042,0),(.037,.07),(.032,.27),(.047,.43),(.045,.50),(.052,.56),(.052,h-.03)],(xx,yy,0),wood,col.name,segments=32)
            box('Bloco encaixe mesa',(xx,yy,h-.12),(.108,.108,.20),wood,col,.004)
    for yy in [y-l/2+.06,y+l/2-.06]:box('Saia ponta mesa',(x,yy,h-.10),(w-.12,.045,.15),wood,col)
    for i,x in enumerate([.45,1.1,1.75,2.4]):
        root=g.parent('IND07 Banqueta '+str(i+1),col.name,(x,8.45,0));root['seat_height_m']=.74
        g.cylinder('IND07 Assento banqueta',(0,0,.75),.215,.055,wood,col.name,root)
        for a in [math.pi/4+k*math.pi/2 for k in range(4)]:
            g.rod('IND07 Pe banqueta',(.13*math.cos(a),.13*math.sin(a),.72),(.22*math.cos(a),.22*math.sin(a),.025),.014,'IND07 Aco',col.name,root)
        g.curve('IND07 Aro apoio pes',[(.18*math.cos(k*math.tau/48),.18*math.sin(k*math.tau/48),.27) for k in range(49)],.012,'IND07 Aco',col.name,root)


def decorations(col):
    box('Tapete sala',(1.64,1.75,.018),(1.72,2.48,.025),'IND07 Juta',col,.015)
    for y in [.88,1.92]:strip('LED painel TV',(3.16,y,.68),(3.16,y,2.20),col,4)
    # Tela com relevo sutil, desenho original abstrato, sem modificar a janela ou a parede.
    mat=g.basic('IND07 Tela paisagem',(.07,.11,.14),.26,emission=.12)
    nodes,links=mat.node_tree.nodes,mat.node_tree.links;bs=nodes.get('Principled BSDF');tex=nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=2;tex.inputs['Detail'].default_value=1
    ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.016,.035,.055,1);ramp.color_ramp.elements[1].color=(.58,.23,.07,1);links.new(tex.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    tv=bpy.data.objects.get('ATUAL TV')
    if tv:
        assign(tv,'IND07 Aco')
        box('Tela TV paisagem',(3.153,1.40,1.48),(.004,.97,.53),mat,col,.002)
    for y in [.90,1.50,2.10]:
        g.cylinder('IND07 Aro downlight',(2.85,y,2.533),.045,.018,'IND07 Aco',col.name)
        light('Parede TV',(2.85,y,2.51),(3.22,y,1.3),12,size=.12,kind='SPOT')
    pendant('jantar A',1.60,4.05,2.12,col);pendant('jantar B',1.60,4.95,2.12,col)
    pendant('bar A',.65,9.30,2.13,col);pendant('bar B',1.95,9.30,2.13,col)
    # Pedra modular de destaque no bar, sem remover churrasqueira e louceiro existentes.
    stone=bpy.data.materials['DESIGN Pedra natural oxidada'].copy();stone.name='IND07 Pedra oxidada';g.M[stone.name]=stone
    for i in range(8):
        for j in range(4):box('Pedra bar',(1.01+i*.19,10.19,1.15+j*.19),(.184,.025,.184),stone,col,.003)
    strip('LED louceiro',(1.0,10.06,1.92),(2.5,10.06,1.92),col,15)
    for y in [5.15,5.85,6.55]:strip('LED cozinha',(6.06,y-.18,1.60),(6.06,y+.18,1.60),col,4)
    for yy in [1.18,2.12]:
        box('Prateleira sala',(.29,yy,2.12),(.25,.68,.045),'IND07 Madeira quente',col)
        for zz in [1.70,2.30]:box('Metal prateleira',(.19,yy,zz),(.04,.73,.025),'IND07 Aco',col)
    g.plant('IND07 Planta prateleira',(.29,1.18,2.14),.60,col.name,pot='IND07 Grafite',hanging=True)
    # Painel e roupeiros dos dormitórios conservam a distribuição atual.
    for pos,target in [((1.6,1.2,2.48),(1.6,1.2,0)),((4.9,5.7,2.48),(4.9,5.7,0)),((1.6,9.0,2.8),(1.6,9,0)),((1.5,1.0,5.17),(1.5,1.0,2.7))]:
        light('Preenchimento quente',pos,target,40,size=1.5,color=(1,.86,.68))


def office(col):
    cfg=CFG['office'];x,y,z=cfg['desk_center'];size=cfg['desk_size']
    box('Escritorio painel petroleo',(3.463,5.60,3.94),(.012,2.60,2.42),'IND07 Petroleo',col,.001)
    for i in range(12):box('Escritorio ripado',(3.480,4.48+i*.034,3.94),(.026,.016,2.42),'IND07 Aco',col,.002)
    for i in range(9):box('Escritorio piso madeira',(3.47+(i+.5)*2.76/9,5.64,2.707),(2.76/9-.003,2.76,.012),'IND07 Madeira quente',col,.001)
    box('Escritorio mesa',cfg['desk_center'],size,'IND07 Madeira quente',col,.014)
    for yy in [y-.84,y+.84]:
        box('Escritorio apoio mesa',(x,yy,3.08),(.045,.055,.72),'IND07 Aco',col)
        box('Escritorio travessa mesa',(x,yy,2.75),(.57,.055,.045),'IND07 Aco',col)
    screen=g.basic('IND07 Tela escritorio',(.018,.05,.09),.35,emission=.5)
    for i,yy in enumerate([5.03,5.62,6.17]):
        vertical=i==2;h=.58 if vertical else .33;w=.34 if vertical else .52
        box('Monitor moldura', (3.62,yy,3.98),(.055,w+.035,h+.035),'IND07 Aco',col,.01)
        box('Monitor tela',(3.654,yy,3.98),(.008,w,h),screen,col,.002)
        for line in range(10 if not vertical else 17):
            color=g.basic('IND07 Codigo '+str(i)+' '+str(line),[(.12,.32,.42),(.40,.20,.08),(.18,.40,.29)][line%3],.50,emission=.8)
            box('Linha de codigo',(3.660,yy-.04+(line%3)*.018,3.98+h/2-.04-line*.027),(.002,w*(.5+.1*(line%4)),.004),color,col,.001)
        box('Pe monitor',(3.69,yy,3.65),(.16,.035,.28),'IND07 Aco',col)
    for yy in [5.13,6.09]:box('Notebook fechado',(3.94,yy,3.505),(.23,.35,.018),'IND07 Grafite',col,.008)
    box('Teclado',(4.01,5.62,3.51),(.19,.43,.025),'IND07 Aco',col,.008)
    # Cadeira de trabalho modelada em escala de uso, com base giratória.
    cx,cy,cz=cfg['chair_center']
    g.cylinder('IND07 Coluna cadeira',(cx,cy,cz+.27),.035,.40,'IND07 Aco',col.name)
    for i in range(5):
        a=i*math.tau/5;p=(cx+.31*math.cos(a),cy+.31*math.sin(a),cz+.07)
        g.rod('IND07 Raio cadeira',(cx,cy,cz+.10),p,.023,'IND07 Aco',col.name)
        g.sphere('IND07 Rodizio',p,(.035,.035,.045),'IND07 Aco',col.name)
    box('Cadeira assento',(cx,cy,cz+.46),(.52,.52,.10),'IND07 Grafite',col,.07)
    box('Cadeira encosto',(cx+.23,cy,cz+.86),(.08,.49,.72),'IND07 Grafite',col,.05)
    box('Cadeira apoio cabeca',(cx+.23,cy,cz+1.24),(.10,.37,.20),'IND07 Grafite',col,.05)
    for yy in [cy-.29,cy+.29]:box('Cadeira braco',(cx,yy,cz+.69),(.34,.055,.05),'IND07 Aco',col,.018)
    for zz in [2.76,3.30,3.90,4.50,4.99]:
        box('Prateleira escritorio',(5.96,5.48,zz),(.44,1.90,.045),'IND07 Madeira quente',col)
        if zz>3.5:strip('LED estante escritorio',(5.72,4.65,zz-.035),(5.72,6.30,zz-.035),col,6)
    for yy in [4.56,6.43]:box('Estrutura estante escritorio',(5.96,yy,3.88),(.035,.035,2.38),'IND07 Aco',col)
    for i in range(10):box('Livro escritorio',(5.94,4.75+i*.055,4.10+(i%2)*.018),(.25,.045,.33+(i%3)*.018),'IND07 Linho' if i%2 else 'IND07 Grafite',col,.003)
    g.plant('IND07 Planta escritorio',(5.96,6.10,4.52),.55,col.name,pot='IND07 Grafite',hanging=True)
    box('Tapete escritorio',(4.85,5.6,2.718),(1.45,2.1,.025),'IND07 Juta',col,.015)
    light('Escritorio ambiente',(4.7,5.5,5.18),(4.4,5.6,3.2),65,size=1.2)


def setup_scenes(decor,furniture,officecol,lights,source_visibility):
    jobs=data.jobs();new=[]
    for job in jobs:
        source=bpy.data.scenes[job['source_scene']];scene=source.copy();scene.name=job['scene'];scene.use_fake_user=True
        cam=source.camera.copy();cam.data=source.camera.data.copy();cam.name=job['scene']+'_Camera';scene.collection.objects.link(cam);scene.camera=cam
        cam.location=job['pos'];cam.rotation_euler=(Vector(job['target'])-cam.location).to_track_quat('-Z','Y').to_euler()
        if job.get('top'):cam.rotation_euler=(0,0,0)
        if 'ortho' in job:cam.data.type='ORTHO';cam.data.ortho_scale=job['ortho']
        else:cam.data.type='PERSP';cam.data.lens=job['lens']
        for col in [lights]:scene.collection.children.link(col)
        if job['mode'] in ['photo','exterior','office'] or job['mode'].endswith('0'):
            scene.collection.children.link(decor);scene.collection.children.link(furniture)
        if job['mode']=='office':
            col=bpy.data.collections['ATUAL_AMB_quarto_azul']
            if col.name in scene.collection.children:scene.collection.children.unlink(col)
            scene.collection.children.link(officecol)
        scene.render.resolution_x,scene.render.resolution_y=CFG['resolution'];scene.render.resolution_percentage=100
        scene.render.filepath=str(ROOT/job['file']);scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8'
        scene.cycles.samples=CFG['samples'];scene.cycles.adaptive_threshold=CFG['adaptive_threshold'];scene.cycles.use_denoising=True
        scene.view_settings.exposure=-.45 if job['mode'].startswith(('plan','iso')) or job['mode']=='exterior' else -.12
        scene['industrial_version']=CFG['version'];scene['industrial_config_sha256']=geo.sha(data.CONFIG);scene['current_base_sha256']=geo.sha(ROOT/CFG['base_blend'])
        scene['official_config_sha256']=geo.sha(ROOT/CFG['official_config']);scene['industrial_view']=job['id']
        job['protected_visibility']=source_visibility[job['source_scene']];new.append(job)
    for scene in list(bpy.data.scenes):
        if scene.name not in {j['scene'] for j in jobs}:bpy.data.scenes.remove(scene)
    return new


def build():
    data.validate();assert Path(bpy.data.filepath).resolve()==ROOT/CFG['base_blend']
    dest=ROOT/CFG['output_blend'];assert not dest.exists(),'Preservar a revisão anterior antes de gerar outro modelo.'
    REPORT.mkdir(parents=True,exist_ok=True);before=protected();pnames=set(before)
    source_visibility={sc.name:sorted(o.name for o in sc.objects if o.name in pnames) for sc in bpy.data.scenes}
    source_hash=geo.sha(ROOT/CFG['base_blend']);g.C.update({c.name:c for c in bpy.data.collections});g.M.update({m.name:m for m in bpy.data.materials})
    furniture=collection('IND07_Mobiliario_Novo');decor=collection('IND07_Detalhes');officecol=collection('IND07_Escritorio_Alternativo');lights=collection('IND07_Iluminacao');g.C['Iluminacao']=lights
    append_furniture(furniture);materials();restyle();industrial_bar_policy.remove_bar_fridges();table_and_stools(furniture);decorations(decor);office(officecol)
    jobs=setup_scenes(decor,furniture,officecol,lights,source_visibility)
    after=protected();assert before==after,'A arquitetura foi alterada.'
    bpy.context.window.scene=bpy.data.scenes['IND07_sala-fundos'];bpy.context.view_layer.update()
    bpy.ops.file.pack_all();bpy.ops.outliner.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
    assert before==protected();dest.parent.mkdir(parents=True,exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
    assert geo.sha(ROOT/CFG['base_blend'])==source_hash
    receipt={'timestamp_utc':stamp(),'version':CFG['version'],'blend':CFG['output_blend'],'blend_sha256':geo.sha(dest),
        'source_blend':CFG['base_blend'],'source_sha256':source_hash,'config_sha256':geo.sha(data.CONFIG),
        'official_config_sha256':geo.sha(ROOT/CFG['official_config']),'current_config_sha256':geo.sha(ROOT/CFG['current_config']),
        'official_sources':[{'file':geo.load()['source'][key],'sha256':geo.sha(ROOT/geo.load()['source'][key])} for key in ['plan','section','site']],
        'furniture_library':CFG['furniture_library'],'furniture_library_sha256':geo.sha(ROOT/CFG['furniture_library']),
        'references':[{'file':str(p.relative_to(ROOT)),'sha256':geo.sha(p)} for p in data.references()],
        'generators':{str(p.relative_to(ROOT)):geo.sha(p) for p in [Path(__file__),ROOT/'scripts/residence07_industrial_data.py',ROOT/'scripts/blender_primitives.py']},
        'protected_geometry':before,'geometry_differences':[],'placements':PLACEMENTS,'jobs':jobs,
        'packed_images':len([im for im in bpy.data.images if im.source=='FILE' and im.packed_file]),'notes':CFG['notes']}
    (REPORT/'modelo.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print('IND07_BUILD_OK',len(jobs),'views;',len(before),'protected objects',flush=True)


def render(preview=False,only=None):
    model=json.loads((REPORT/'modelo.json').read_text());assert geo.sha(bpy.data.filepath)==model['blend_sha256'];assert geo.sha(data.CONFIG)==model['config_sha256']
    for p,h in model['generators'].items():assert geo.sha(ROOT/p)==h,p
    if only:assert set(only.split(','))<={j['id'] for j in model['jobs']}
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices();assert any(d.type=='CUDA' for d in prefs.devices)
    for d in prefs.devices:d.use=d.type=='CUDA'
    records=[]
    for j in model['jobs']:
        if only and j['id'] not in only.split(','):continue
        scene=bpy.data.scenes[j['scene']];bpy.context.window.scene=scene;scene.cycles.device='GPU'
        dest=REPORT/'previas'/(j['id']+'.png') if preview else ROOT/j['file'];dest.parent.mkdir(parents=True,exist_ok=True)
        scene.render.filepath=str(dest);scene.render.resolution_percentage=CFG['preview_percentage'] if preview else 100;scene.cycles.samples=CFG['preview_samples'] if preview else CFG['samples']
        start=time.monotonic();bpy.ops.render.render(write_still=True,scene=scene.name)
        row={'id':j['id'],'file':str(dest.relative_to(ROOT)),'sha256':geo.sha(dest),'blend_sha256':model['blend_sha256'],'source_blend':model['blend'],
            'preview':preview,'samples':scene.cycles.samples,'seconds':round(time.monotonic()-start,2)};records.append(row)
        (REPORT/('previas.json' if preview else 'renders-parcial.json')).write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
        print('IND07_RENDER_OK',j['id'],row['seconds'],flush=True)
    if not preview:
        path=REPORT/'renders.json';old=json.loads(path.read_text()) if path.exists() else []
        merged={r['id']:r for r in old if r['blend_sha256']==model['blend_sha256']};merged.update({r['id']:r for r in records})
        path.write_text(json.dumps(list(merged.values()),ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--render-only',action='store_true');p.add_argument('--preview',action='store_true');p.add_argument('--only')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if args.render_only:render(args.preview,args.only)
    else:build()
