"""Refinamento de mobiliário, PBR e luz; arquitetura da variante v01 preservada."""
import argparse
import datetime as dt
import json
import math
from pathlib import Path
import random
import sys

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
import blender_primitives as g
import style_industrial as v1
import audit_envelope

ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config/estilo-industrial-v02.json').read_text())
REPORTS=ROOT/CFG['report_directory']
COL='HQ_Detalhes'
RECORDS=[]
for name in CFG['asset_manifests']:
    RECORDS+=json.loads((ROOT/name).read_text())['records']


def image(asset,channel,color=False):
    record=next(r for r in RECORDS if r['asset']==asset and r['channel']==channel)
    path=ROOT/record['path'];assert v1.sha(path)==record['sha256']
    im=bpy.data.images.load(str(path),check_existing=True)
    if not color:im.colorspace_settings.name='Non-Color'
    im.pack()
    return im


def pbr(name,asset,period,tint=(1,1,1),saturation=1,normal=.25):
    mat=g.basic(name,(.2,.2,.2),.5);mat['texture_period_m']=period
    nodes=mat.node_tree.nodes;links=mat.node_tree.links;bsdf=nodes.get('Principled BSDF')
    coord=nodes.new('ShaderNodeTexCoord');coord.location=(-850,0)
    textures={}
    for i,channel in enumerate(['Diffuse','Rough','nor_gl']):
        tex=nodes.new('ShaderNodeTexImage');tex.image=image(asset,channel,channel=='Diffuse')
        tex.location=(-620,300-i*260);tex.label=channel+' · CC0 Poly Haven'
        links.new(coord.outputs['UV'],tex.inputs['Vector']);textures[channel]=tex
    hue=nodes.new('ShaderNodeHueSaturation');hue.inputs['Saturation'].default_value=saturation
    links.new(textures['Diffuse'].outputs['Color'],hue.inputs['Color'])
    mul=nodes.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1
    mul.inputs[2].default_value=(*tint,1);links.new(hue.outputs['Color'],mul.inputs[1]);links.new(mul.outputs[0],bsdf.inputs['Base Color'])
    links.new(textures['Rough'].outputs['Color'],bsdf.inputs['Roughness'])
    n=nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=normal
    links.new(textures['nor_gl'].outputs['Color'],n.inputs['Color']);links.new(n.outputs['Normal'],bsdf.inputs['Normal'])
    return mat


def uv(obj,period):
    """Projeção por face em escala métrica, sem esticar as texturas."""
    if obj.type!='MESH':return
    mesh=obj.data;layer=mesh.uv_layers.get('HQ_Metrique') or mesh.uv_layers.new(name='HQ_Metrique')
    mesh.uv_layers.active=layer;layer.active_render=True
    offset=(sum(ord(c) for c in obj.name)%73)/11
    for poly in mesh.polygons:
        axis=max(range(3),key=lambda i:abs(poly.normal[i]))
        axes=(1,2) if axis==0 else (0,2) if axis==1 else (0,1)
        if any(m and m.name=='HQ Madeira' for m in mesh.materials):
            long_axis=max(axes,key=lambda i:obj.dimensions[i])
            axes=(next(i for i in axes if i!=long_axis),long_axis)
        for index in poly.loop_indices:
            co=mesh.vertices[mesh.loops[index].vertex_index].co
            layer.data[index].uv=(co[axes[0]]*obj.scale[axes[0]]/period+offset,co[axes[1]]*obj.scale[axes[1]]/period+offset*.37)


def assign(obj,mat):
    v1.assign(obj,mat)
    if 'texture_period_m' in g.M[mat]:uv(obj,g.M[mat]['texture_period_m'])


def box(name,loc,size,mat,bevel=.006,par=None):
    obj=g.box('HQ '+name,loc,size,mat,COL,bevel,par)
    if 'texture_period_m' in g.M[mat]:uv(obj,g.M[mat]['texture_period_m'])
    return obj


def hide_tree(obj):
    for child in [obj,*obj.children_recursive]:child.hide_render=True


def soft(name,loc,size,mat,par=None,rotation=None):
    """Estofado com volume arredondado, afundamento e pregas suaves reais."""
    o=box(name,loc,size,mat,min(size)*.40,par)
    if rotation:o.rotation_euler=rotation
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    bevel=o.modifiers[0];bevel.segments=5;bpy.ops.object.modifier_apply(modifier=bevel.name)
    for modifier in list(o.modifiers):o.modifiers.remove(modifier)
    sub=o.modifiers.new('Malha para pregas','SUBSURF');sub.subdivision_type='SIMPLE';sub.levels=3
    bpy.ops.object.modifier_apply(modifier=sub.name)
    sx,sy,sz=size
    for v in o.data.vertices:
        x,y,z=v.co;u=x/(sx/2);t=y/(sy/2);top=max(0,z/(sz/2))
        crease=.0055*math.sin(26*t+3*math.sin(u*4))*(abs(u)**6)+.003*math.sin(31*u+3*t)*(abs(t)**6)
        depression=.012*math.exp(-((u*.9)**2+(t*1.0)**2)*3)
        v.co.z+=top*(crease-depression)
    for poly in o.data.polygons:poly.use_smooth=True
    uv(o,g.M[mat].get('texture_period_m',.4))
    o.select_set(False)
    return o


def seam(name,points,par=None):
    return g.curve('HQ costura '+name,points,.0016,'HQ Linha costura',COL,par)


def sofa():
    root=bpy.data.objects['SOFA_original cinza — mover conjunto'];hide_tree(root)
    for obj in bpy.data.objects:
        if obj.name.startswith('IND almofada linho'):obj.hide_render=True
    p=g.parent('HQ SOFÁ couro — conjunto',COL,root.matrix_world.translation)
    box('estrutura sofá',(0,0,.23),(1.0,2.70,.24),'HQ Couro',.08,p)
    soft('encosto sofá',(-.38,0,.66),(.21,2.68,.76),'HQ Couro',p)
    for y in [-.86,0,.86]:
        soft('assento sofá',(.08,y,.43),(.86,.835,.19),'HQ Couro',p)
        soft('encosto solto',(-.23,y,.76),(.25,.81,.56),'HQ Couro',p,rotation=(0,-.08,0))
        pts=[(-.29,y-.39,.515),(.45,y-.39,.515),(.49,y-.34,.515),(.49,y+.34,.515),(.45,y+.39,.515),(-.29,y+.39,.515),(-.29,y-.39,.515)]
        seam('assento',pts,p)
    for y in [-1.30,1.30]:soft('braço couro',(.04,y,.57),(1.02,.15,.30),'HQ Couro',p)
    # A chaise conserva a projeção da versão anterior.
    soft('chaise',(.48,-.90,.36),(.85,.91,.24),'HQ Couro',p)
    for y in [-1.12,1.12]:
        for x in [-.35,.35]:g.rod('HQ pé sofá',(x,y,.025),(x,y,.18),.021,'IND Aço preto',COL,p)
    for i,y in enumerate([-.87,.88]):
        pillow=soft('almofada tecido',(.09,y,.75),(.18,.43,.42),'HQ Tecido',p,rotation=(.1,-.25,.07 if i else -.04))
    # Manta com caída irregular, apoiada no encosto e assento.
    verts=[];faces=[];nx=22;ny=32
    for i in range(nx+1):
        u=i/nx;x=-.28+u*.98
        for j in range(ny+1):
            t=j/ny;y=-.1+t*.59
            z=.51+.38*math.exp(-u*9) if u<.72 else .51-(u-.72)*1.15
            z+=.012*math.sin(t*math.tau*7+u*3)
            verts.append((x,y,z))
    for i in range(nx):
        for j in range(ny):a=i*(ny+1)+j;faces.append((a,a+1,a+ny+2,a+ny+1))
    me=bpy.data.meshes.new('Manta com pregas');me.from_pydata(verts,[],faces);me.update()
    o=bpy.data.objects.new('HQ manta sofá',me);g.C[COL].objects.link(o);o.parent=p;assign(o,'HQ Tecido')
    for poly in me.polygons:poly.use_smooth=True
    o.modifiers.new('Espessura tecido','SOLIDIFY').thickness=.002


def dining_and_stools(house):
    path=ROOT/'assets/industrial-v02/dining_chair_02/dining_chair_02_2k.blend'
    with bpy.data.libraries.load(str(path),link=False) as (src,dst):dst.objects=src.objects
    loaded=[o for o in dst.objects if o is not None and o.type=='MESH']
    assert loaded
    asset=bpy.data.collections.new('HQ_Fonte_Cadeira_CC0')
    for o in loaded:
        asset.objects.link(o)
        o.name='HQ fonte '+o.name
    points=[o.matrix_world@Vector(v) for o in loaded for v in o.bound_box]
    lo=Vector(tuple(min(v[i] for v in points) for i in range(3)));hi=Vector(tuple(max(v[i] for v in points) for i in range(3)))
    scale=.46/(hi.x-lo.x);center=(lo+hi)/2
    for chair in [o for o in list(bpy.data.objects) if o.name.startswith('CADEIRA_')]:
        hide_tree(chair)
        holder=g.parent('HQ cadeira jantar',COL,chair.matrix_world.translation);holder.rotation_euler=chair.matrix_world.to_euler()
        inst=bpy.data.objects.new('HQ cadeira CC0 — malha instanciada',None);g.C[COL].objects.link(inst)
        inst.instance_type='COLLECTION';inst.instance_collection=asset;inst.parent=holder;inst.scale=(scale,)*3
        inst.location=(-center.x*scale,-center.y*scale,-lo.z*scale)
    for chair in [o for o in list(bpy.data.objects) if o.name.startswith('BANQUETA_BAR_')]:hide_tree(chair)
    bar=house['layout']['bar']
    for x in bar['stool_x']:
        y=bar['stool_y'];g.cylinder('HQ banqueta assento',(x,y,.76),.22,.055,'HQ Madeira',COL)
        # Pernas de aço abertas e anel de apoio, como na inspiração.
        for a in range(4):
            angle=(a+.5)*math.tau/4
            g.rod('HQ banqueta aço',(x+math.cos(angle)*.23,y+math.sin(angle)*.23,.03),(x+math.cos(angle)*.15,y+math.sin(angle)*.15,.73),.014,'IND Aço preto',COL)
        bpy.ops.mesh.primitive_torus_add(major_radius=.20,minor_radius=.010,major_segments=48,minor_segments=8,location=(x,y,.28));g.finish(bpy.context.object,'HQ apoio pés banqueta',COL,'IND Aço preto')


def sinks(house):
    for key in ['cozinha','bar']:
        is_kitchen=key=='cozinha'
        x,y,_=house['layout']['kitchen']['sink'] if is_kitchen else (1.75,house['layout']['bar']['counter_y']+.25,1.0)
        z=.932 if is_kitchen else 1.024
        bpy.data.objects['Cuba cozinha' if is_kitchen else 'Cuba bar'].hide_render=True
        cutter=box('cortador cuba '+key,(x,y,z-.10),(.45,.32,.34),'IND Aço preto',.035)
        cutter.hide_render=True;cutter.hide_viewport=True;cutter.display_type='WIRE'
        countertop=bpy.data.objects['Bancada pia cozinha' if is_kitchen else 'Bar tampo granito']
        mod=countertop.modifiers.new('HQ abertura real cuba','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
        verts=[];faces=[];segments=32
        for width,depth,height in [(.47,.34,z+.002),(.43,.30,z-.02),(.37,.24,z-.18)]:
            for i in range(segments):
                a=i*math.tau/segments
                verts.append((x+math.copysign(abs(math.cos(a))**.32,a and math.cos(a) or 1)*width/2,y+math.copysign(abs(math.sin(a))**.32,math.sin(a))*depth/2,height))
        for ring in range(2):
            for i in range(segments):a=ring*segments+i;b=ring*segments+(i+1)%segments;faces.append((a,b,b+segments,a+segments))
        faces.append(tuple(range(2*segments,3*segments)))
        mesh=bpy.data.meshes.new('Cuba profunda');mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new('HQ cuba inox '+key,mesh);g.C[COL].objects.link(obj);assign(obj,'HQ Inox escovado')
        for p in mesh.polygons:p.use_smooth=True
        g.cylinder('HQ ralo cuba',(x,y,z-.176),.027,.003,'IND Aço preto',COL)


def details(house):
    # Tela com conteúdo abstrato próprio e moldura discreta, sem foto de terceiros.
    m=g.basic('HQ Tela paisagem',(.035,.065,.09),.34,emission=.3)
    n=m.node_tree.nodes;l=m.node_tree.links;tex=n.new('ShaderNodeTexImage')
    tex.image=bpy.data.images.load(str(ROOT/'referencias-estilo-industrial/01-cena-final-menos-warn.png'),check_existing=True);tex.image.pack()
    bs=n.get('Principled BSDF');l.new(tex.outputs['Color'],bs.inputs['Base Color']);l.new(tex.outputs['Color'],bs.inputs['Emission Color'])
    screen=box('TV paisagem da referência',(2.977,2.0,1.60),(.003,1.50,.84),'HQ Tela paisagem',.001)
    layer=screen.data.uv_layers.active
    # A imagem fornecida permanece intacta; apenas o mapeamento UV seleciona a TV.
    for poly in screen.data.polygons:
        for index in poly.loop_indices:
            co=screen.data.vertices[screen.data.loops[index].vertex_index].co
            u=(co.y+.75)/1.50;v=(co.z+.42)/.84
            top=318-58*u;bottom=507+43*u
            layer.data[index].uv=((1230+u*300)/1671,1-((1-v)*bottom+v*top)/941)
    editor=g.basic('HQ Tela editor',(.02,.03,.04),.48,emission=.22)
    n=editor.node_tree.nodes;l=editor.node_tree.links;im=n.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(ROOT/'assets/industrial-v02/editor-demonstrativo.png'));im.image.pack()
    coords=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');combine=n.new('ShaderNodeCombineXYZ')
    l.new(coords.outputs['Generated'],sep.inputs[0]);l.new(sep.outputs['Y'],combine.inputs['X']);l.new(sep.outputs['Z'],combine.inputs['Y']);l.new(combine.outputs[0],im.inputs[0])
    bs=n.get('Principled BSDF');l.new(im.outputs['Color'],bs.inputs['Base Color']);l.new(im.outputs['Color'],bs.inputs['Emission Color'])
    for obj in bpy.data.objects:
        if obj.name.startswith('IND monitor tela'):assign(obj,'HQ Tela editor')
    # Rodapés finos criam o contato entre acabamento e piso.
    box('rodapé sala',(.084,3.6,.055),(.018,7.10,.11),'IND Grafite',.002)
    box('rodapé quarto fundos',(4.20,7.514,2.955),(2.54,.018,.11),'IND Grafite',.002)
    for obj in list(bpy.data.objects):
        if obj.name.startswith('IND tela linhas'):obj.hide_render=True
    # Teclas individuais substituem o bloco liso do teclado.
    for i in range(5):
        for j in range(13):box('tecla',(3.20+i*.021,6.16+j*.026,3.698),(.018,.022,.006),'IND Grafite',.001)
    # Colchas e travesseiros com volume suavizado mantêm a posição do beliche.
    root=bpy.data.objects['Beliche quarto fundos'];origin=root.matrix_world.translation
    for o in root.children_recursive:
        if o.name.startswith(('Colchão cama','Travesseiro')):o.hide_render=True
    for z in [.46,1.48]:
        soft('colchão beliche',tuple(origin+Vector((0,0,z))),(.845,1.875,.17),'HQ Tecido')
        soft('travesseiro beliche',tuple(origin+Vector((0,.60,z+.14))),(.66,.43,.13),'HQ Tecido')
        box('colcha dobrada',tuple(origin+Vector((0,-.48,z+.12))),(.84,.65,.055),'HQ Azul tecido',.025)


def lighting():
    # Substitui a iluminação de preenchimento uniforme por fontes localizadas.
    for obj in bpy.data.objects:
        if obj.type=='LIGHT':obj.data.energy*=.30
    world=bpy.data.worlds.new('HQ Jardim HDRI CC0');world.use_nodes=True
    n=world.node_tree.nodes;l=world.node_tree.links;env=n.new('ShaderNodeTexEnvironment');env.image=image('residential_garden','hdri',True)
    tex=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeMapping');mapping.inputs['Rotation'].default_value[2]=.7
    l.new(tex.outputs['Generated'],mapping.inputs['Vector']);l.new(mapping.outputs['Vector'],env.inputs['Vector']);l.new(env.outputs['Color'],n.get('Background').inputs['Color']);n.get('Background').inputs['Strength'].default_value=.35
    for scene in bpy.data.scenes:scene.world=world
    for loc,target,power,size,color in [((1.4,.42,2.15),(1.5,4,1),170,1.7,(.88,.94,1)),((1.5,8.0,3.35),(1.6,9.9,.8),100,1.4,(.90,.95,1)),((4.2,7.25,5),(3.8,6,3.6),75,1.3,(.92,.96,1))]:
        light=g.light('HQ janela difusa',loc,power,color=color,size=size,target=target)
        if loc[0]>3 or loc[1]>7.5:
            light.data.type='SPOT';data=light.data;data.energy=power*2.3
            data.spot_size=math.radians(120);data.spot_blend=.8;data.shadow_soft_size=.035
    g.light('HQ preenchimento cozinha',(4.15,5.55,2.5),65,color=(.96,.94,.88),size=.9,target=(4.60,7,.8))
    fill=g.light('HQ preenchimento quarto',(3.55,4.70,5.3),45,color=(1,.87,.69),kind='SPOT',target=(3.7,6.5,3.6))
    fill.data.spot_size=math.radians(115);fill.data.spot_blend=.8;fill.data.shadow_soft_size=.02
    for y in [1.4,3.1,4.8]:
        light=g.light('HQ spot parede sala',(.28,y,2.58),24,color=(1,.70,.41),kind='SPOT',target=(.08,y,1.15))
        light.data.spot_size=math.radians(62);light.data.spot_blend=.5
    for loc,target,power,size in [((2.90,.90,1.6),(3.02,.90,1.6),9,.18),((2.90,2.71,1.6),(3.02,2.71,1.6),9,.18),((1.6,10.07,1.82),(1.6,10.40,1.35),35,1.1),((3.22,6.35,4.62),(2.96,6.35,4.15),19,.6)]:
        g.light('HQ luz quente indireta',loc,power,color=(1,.55,.23),target=target,size=size)
    # Pendentes acesos e reflexos presentes nos materiais.
    for x,y,z in [(1.52,5.27,2.17),(1.52,6.33,2.17),(.60,9.5,2.17),(1.90,9.5,2.17)]:
        g.light('HQ pendente luz',(x,y,z),24,color=(1,.69,.36),kind='POINT',size=.06)
    for obj in bpy.data.objects:
        if obj.type=='LIGHT' and obj.data.type=='AREA':
            obj.visible_glossy=False;obj.data.specular_factor=0;obj.data.transmission_factor=0


def build():
    base=ROOT/CFG['base_blend'];assert Path(bpy.data.filepath).resolve()==base
    before=v1.geometry();base_hash=v1.sha(base)
    g.C.update({c.name:c for c in bpy.data.collections});g.M.update({m.name:m for m in bpy.data.materials});g.RNG.seed(112026)
    v1.collection(COL)
    wood=pbr('HQ Madeira','wood_table_001',.65,(.90,1.0,1.07),.58,.10)
    bs=wood.node_tree.nodes.get('Principled BSDF');rough=bs.inputs['Roughness'].links[0].from_socket
    remap=wood.node_tree.nodes.new('ShaderNodeMath');remap.operation='MULTIPLY_ADD';remap.inputs[1].default_value=.30;remap.inputs[2].default_value=.45
    wood.node_tree.links.new(rough,remap.inputs[0]);wood.node_tree.links.new(remap.outputs[0],bs.inputs['Roughness'])
    pbr('HQ Couro','brown_leather',.45,(1.05,.84,.65),.8,.12)
    cement=pbr('HQ Cimento','grey_plaster',.55,(.65,.63,.59),0,.045)
    bs=cement.node_tree.nodes.get('Principled BSDF');existing=bs.inputs['Base Color'].links[0].from_socket
    blend=cement.node_tree.nodes.new('ShaderNodeMixRGB');blend.inputs[0].default_value=.20;blend.inputs[1].default_value=(.15,.145,.13,1)
    cement.node_tree.links.new(existing,blend.inputs[2]);cement.node_tree.links.new(blend.outputs[0],bs.inputs['Base Color'])
    pbr('HQ Tecido','denim_fabric',.32,(2.0,1.86,1.58),0,.35)
    g.M['HQ Tecido'].node_tree.nodes.get('Principled BSDF').inputs['Sheen Weight'].default_value=.35
    g.textured('HQ Azul tecido',[(.018,.035,.045),(.055,.085,.095)],'leather',.94,.0004)
    g.basic('HQ Linha costura',(.11,.055,.026),.8)
    g.basic('HQ Inox escovado',(.38,.42,.45),.24,.96)
    g.textured('HQ Pedra grafite',[(.003,.004,.005),(.012,.011,.009),(.035,.022,.010)],'stone',.72,.002)
    g.M['HQ Inox escovado'].node_tree.nodes.get('Principled BSDF').inputs['Anisotropic'].default_value=.35
    for obj in list(bpy.data.objects):
        if obj.type!='MESH':continue
        mats={m.name.split('.')[0] for m in obj.data.materials if m}
        target={'IND Nogueira':'HQ Madeira','Madeira bar':'HQ Madeira','IND Couro caramelo':'HQ Couro','IND Cimento':'HQ Cimento','IND Linho':'HQ Tecido','IND Tapete':'HQ Tecido'}
        for old,new in target.items():
            if old in mats:assign(obj,new);break
        if obj.name.startswith('Pedra bar original'):
            assign(obj,'HQ Pedra grafite')
        if obj.name.startswith('IND travessa cobertura'):obj.hide_render=True
    house=json.loads((ROOT/'config/planta-casa.json').read_text());bpy.context.view_layer.update()
    sofa();dining_and_stools(house);sinks(house);details(house);lighting()
    for im in bpy.data.images:
        if im.source=='FILE' and not im.packed_file:
            path=Path(bpy.path.abspath(im.filepath))
            if path.is_file():im.pack()
    for job in CFG['jobs']:
        scene=bpy.data.scenes[job['source_scene']].copy();scene.name=job['scene'];scene.use_fake_user=True
        scene.render.resolution_x,scene.render.resolution_y=CFG['resolution'];scene.render.resolution_percentage=100
        scene.cycles.samples=CFG['samples'];scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=CFG['adaptive_threshold'];scene.cycles.adaptive_min_samples=32
        scene.cycles.use_denoising=True;scene.cycles.max_bounces=12;scene.cycles.diffuse_bounces=5;scene.cycles.glossy_bounces=6;scene.cycles.transmission_bounces=10
        scene.cycles.sample_clamp_indirect=5;scene.view_settings.exposure=.15
        looks=[x.identifier for x in scene.view_settings.bl_rna.properties['look'].enum_items]
        for value in ['AgX - Medium High Contrast','Medium High Contrast']:
            if value in looks:scene.view_settings.look=value;break
        scene['style_version']=CFG['version'];scene['base_sha256']=base_hash
    after=v1.geometry();diff=[n for n,h in before.items() if after.get(n)!=h]
    assert set(diff)<={'Bancada pia cozinha','Bar tampo granito'},diff
    envelope=audit_envelope.audit(house);assert envelope['all_passed']
    output=ROOT/CFG['output_blend'];assert not output.exists(),output;output.parent.mkdir(parents=True,exist_ok=True)
    bpy.context.window.scene=bpy.data.scenes['HQ_Sala'];bpy.ops.wm.save_as_mainfile(filepath=str(output),compress=True)
    assert v1.sha(base)==base_hash
    report={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'base_sha256':base_hash,'blend_sha256':v1.sha(output),'geometry_before':before,'expected_furniture_modifier_changes':diff,'envelope':envelope,'assets':RECORDS,'packed_images':len([i for i in bpy.data.images if i.packed_file]),'source_dining_asset':'https://polyhaven.com/a/dining_chair_02'}
    (REPORTS/'modelo.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('HQ_MODEL_BUILT',len(before),'source geometries;',diff,flush=True)


def validate():
    report=json.loads((REPORTS/'modelo.json').read_text());file=Path(bpy.data.filepath)
    assert v1.sha(file)==report['blend_sha256'] and v1.sha(ROOT/CFG['base_blend'])==report['base_sha256']
    geometry=v1.geometry();diff=[n for n,h in report['geometry_before'].items() if geometry.get(n)!=h]
    assert diff==report['expected_furniture_modifier_changes']
    envelope=audit_envelope.audit(json.loads((ROOT/'config/planta-casa.json').read_text()));assert envelope['all_passed']
    missing=[i.name for i in bpy.data.images if i.source=='FILE' and not i.packed_file];assert not missing,missing
    metric_uv={}
    for name in ['Bar frente madeira','Churrasqueira revestimento madeira frontal','Escrivaninha quarto fundos','HQ assento sofá']:
        obj=bpy.data.objects[name];layer=obj.data.uv_layers.get('HQ_Metrique')
        metric_uv[name]=bool(layer and layer.active_render)
    assert all(metric_uv.values()),metric_uv
    old_cfg=json.loads((ROOT/'config/estilo-industrial-v01.json').read_text())
    house_cfg=json.loads((ROOT/'config/planta-casa.json').read_text());cameras={}
    for job in CFG['jobs']:
        source=next(j for j in old_cfg['jobs'] if j['scene']==job['source_scene'])
        spec=source if 'position' in source else house_cfg['cameras'][source['source_scene'].replace('FOTO_','CAM_Foto_',1)]
        scene=bpy.data.scenes[job['scene']];scene.view_layers[0].update();cam=scene.camera
        eye=cam.matrix_world.translation;direction=cam.matrix_world.to_quaternion()@Vector((0,0,-1))
        wanted=(Vector(spec['target'])-Vector(spec['position'])).normalized()
        assert (eye-Vector(spec['position'])).length<1e-4 and abs(cam.data.lens-spec['lens'])<1e-4 and direction.dot(wanted)>.99999
        cameras[job['scene']]={'position':list(eye),'lens':cam.data.lens,'same_as_v01':True}
    receipt={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'blend_sha256':report['blend_sha256'],
             'source_geometries_checked':len(report['geometry_before']),'expected_furniture_changes':diff,
             'envelope':envelope,'missing_images':missing,'active_metric_uv':metric_uv,'cameras':cameras,'base_preserved':True,'all_passed':True}
    (REPORTS/'validacao.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    return report,envelope


def render(preview,only):
    model,envelope=validate();g.configure_device('cpu');outputs={}
    for job in CFG['jobs']:
        if only and job['file'].split('.')[0] not in only:continue
        scene=bpy.data.scenes[job['scene']];scene.cycles.device='CPU'
        scene.cycles.samples=24 if preview else CFG['samples'];scene.render.resolution_percentage=40 if preview else 100
        scene.cycles.adaptive_min_samples=12 if preview else 32
        scene.render.filepath=str(ROOT/CFG['render_directory']/('previas' if preview else '')/job['file']);Path(scene.render.filepath).parent.mkdir(parents=True,exist_ok=True)
        bpy.ops.render.render(write_still=True,scene=scene.name)
        p=Path(scene.render.filepath);outputs[str(p.relative_to(ROOT))]={'sha256':v1.sha(p),'bytes':p.stat().st_size,'scene':scene.name}
        print('HQ_RENDER',scene.name,flush=True)
    validate()
    receipt={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'blend_sha256':model['blend_sha256'],'preview':preview,'device':'CPU','envelope':envelope,'outputs':outputs}
    (REPORTS/('previas.json' if preview else 'renders.json')).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser();p.add_argument('--render-only',action='store_true');p.add_argument('--build-only',action='store_true');p.add_argument('--validate-only',action='store_true');p.add_argument('--preview',action='store_true');p.add_argument('--only',nargs='*')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);REPORTS.mkdir(parents=True,exist_ok=True)
    if args.validate_only:validate();print('HQ_NATIVE_VALIDATED',flush=True);return
    if not args.render_only:build()
    if not args.build_only:render(args.preview,args.only)


if __name__=='__main__':main()
