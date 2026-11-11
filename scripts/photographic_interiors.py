"""Cena fotográfica inteiramente 3D: ativos, materiais, luz e câmeras editáveis.

Executar com run_blender.py --wsl-gpu. Imagens finais são saídas do Cycles;
nenhum retoque generativo ou imagem de conceito substitui a geometria.
"""
import argparse
import datetime as dt
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
import blender_primitives as g
import style_industrial as v1
import audit_envelope

ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config/estilo-industrial-v03.json').read_text())
REPORTS=ROOT/CFG['report_directory']
ASSETS=json.loads((ROOT/CFG['asset_manifest']).read_text())['records']
COL='PHOTO_Mobiliario'
ROOT_COL=COL
CACHE={}
PLACEMENTS=[]
USED=set()


def collection():
    c=bpy.data.collections.new(COL);g.C[COL]=c
    for scene in bpy.data.scenes:
        if scene.name!='ESTUDOS_Superior':scene.collection.children.link(c)
    for room in ['Sala','Cozinha','Lazer','Quarto']:
        child=bpy.data.collections.new('PHOTO_'+room+'_Objetos');c.children.link(child);g.C[child.name]=child


def hide(obj):
    for child in [obj,*obj.children_recursive]:child.hide_render=True


def hide_prefix(*prefixes):
    for obj in list(bpy.data.objects):
        if obj.name.startswith(prefixes):hide(obj)


def box(name,loc,size,mat,bevel=.006):
    return g.box('PHOTO '+name,loc,size,mat,COL,bevel)


def template(asset,res='2k'):
    key=(asset,res)
    if key in CACHE:return CACHE[key]
    record=next(r for r in ASSETS if r['asset']==asset and r['path'].endswith(f'{asset}_{res}.blend'))
    file=ROOT/record['path'];assert v1.sha(file)==record['sha256'];USED.add(record['path'])
    with bpy.data.libraries.load(str(file),link=False) as (src,dst):
        assert asset in src.collections,(asset,src.collections)
        dst.collections=[asset]
    source=dst.collections[0];source.name='PHOTO_Ativo_'+asset+'_'+res
    objects=list(source.all_objects)
    for obj in objects:obj.name='SRC '+asset+' '+obj.name
    allowed=set()
    def renderable(c,visible=True):
        visible=visible and not c.hide_render
        if visible:allowed.update(o for o in c.objects if not o.hide_render)
        for child in c.children:renderable(child,visible)
    renderable(source)
    # Avaliar hierarquias, rigs e Geometry Nodes antes de dimensionar o ativo.
    # Coordenadas locais ou bounding boxes sem avaliação dão escalas incorretas.
    evaluation=bpy.data.scenes.new('PHOTO_AVALIACAO_TEMP');evaluation.collection.children.link(source)
    points=[]
    with bpy.context.temp_override(scene=evaluation,view_layer=evaluation.view_layers[0]):
        evaluation.view_layers[0].update();deps=bpy.context.evaluated_depsgraph_get()
        for instance in deps.object_instances:
            obj=instance.object
            if obj.type!='MESH' or not len(obj.data.vertices):continue
            if not instance.is_instance and obj.original not in allowed:continue
            if instance.is_instance and instance.parent and instance.parent.original not in allowed:continue
            points.extend(instance.matrix_world@Vector(v) for v in obj.bound_box)
    bpy.data.scenes.remove(evaluation)
    assert points,asset
    low=Vector(tuple(min(v[i] for v in points) for i in range(3)));high=Vector(tuple(max(v[i] for v in points) for i in range(3)))
    data={'collection':source,'low':low,'high':high,'objects':objects,'size':high-low}
    CACHE[key]=data;print('PHOTO_ASSET',asset,list(data['size']),flush=True)
    return data


def place(asset,name,loc,*,res='2k',width=None,height=None,fit=None,angle=0):
    data=template(asset,res);size=data['size'];lo=data['low'];hi=data['high'];center=(lo+hi)/2
    if fit:scale=Vector(tuple(fit[i]/size[i] for i in range(3)))
    else:
        factor=width/size.x if width else height/size.z if height else 1
        scale=Vector((factor,)*3)
    root=g.parent('PHOTO '+name,COL,loc,asset_cc0=asset)
    root.rotation_euler.z=angle
    inst=bpy.data.objects.new('Instância editável '+name,None);g.C[COL].objects.link(inst)
    inst.instance_type='COLLECTION';inst.instance_collection=data['collection'];inst.parent=root
    offset=data['collection'].instance_offset
    inst.scale=scale;inst.location=((offset.x-center.x)*scale.x,(offset.y-center.y)*scale.y,(offset.z-lo.z)*scale.z)
    PLACEMENTS.append({'name':root.name,'asset':asset,'location':list(loc),'rotation_z':angle,'asset_size':list(size),'scale':list(scale),'size_before_rotation':list(Vector((size[i]*scale[i] for i in range(3))))})
    return root


def recolor(asset,res,*,tint=(1,1,1),saturation=1,plain=None):
    materials={m for o in template(asset,res)['objects'] if o.type=='MESH' for m in o.data.materials if m}
    for mat in materials:
        if not mat.use_nodes:continue
        n=mat.node_tree.nodes;l=mat.node_tree.links;bs=next((x for x in n if x.type=='BSDF_PRINCIPLED'),None)
        if bs is None or not bs.inputs['Base Color'].links:continue
        original=bs.inputs['Base Color'].links[0].from_socket
        hue=n.new('ShaderNodeHueSaturation');hue.label='Ajuste de cor editável';hue.inputs['Saturation'].default_value=saturation;l.new(original,hue.inputs['Color'])
        mul=n.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;mul.inputs[2].default_value=(*tint,1);l.new(hue.outputs[0],mul.inputs[1]);out=mul.outputs[0]
        if plain:
            mix=n.new('ShaderNodeMixRGB');mix.inputs[0].default_value=.28;mix.inputs[1].default_value=(*plain,1);l.new(out,mix.inputs[2]);out=mix.outputs[0]
        l.new(out,bs.inputs['Base Color'])


def asset_image(asset,needle,color=True):
    record=next(r for r in ASSETS if r['asset']==asset and needle in Path(r['path']).name)
    file=ROOT/record['path'];assert v1.sha(file)==record['sha256'];USED.add(record['path'])
    im=bpy.data.images.load(str(file),check_existing=True)
    if not color:im.colorspace_settings.name='Non-Color'
    im.pack();return im


def surfaces():
    mat=g.basic('PHOTO Porcelanato bege',(.4,.38,.33),.22)
    n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n.get('Principled BSDF');uv=n.new('ShaderNodeTexCoord')
    for channel,needle,socket in [('cor','_diff_','Base Color'),('rugosidade','_rough_','Roughness'),('normal','_nor_gl_','Normal')]:
        tex=n.new('ShaderNodeTexImage');tex.image=asset_image('floor_tiles_02',needle,channel=='cor');tex.label=channel+' · Poly Haven CC0';l.new(uv.outputs['UV'],tex.inputs['Vector'])
        if channel=='normal':
            normal=n.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.18;l.new(tex.outputs[0],normal.inputs['Color']);l.new(normal.outputs[0],bs.inputs[socket])
        elif channel=='rugosidade':
            remap=n.new('ShaderNodeMath');remap.operation='MULTIPLY_ADD';remap.inputs[1].default_value=.25;remap.inputs[2].default_value=.10;l.new(tex.outputs[0],remap.inputs[0]);l.new(remap.outputs[0],bs.inputs[socket])
        else:l.new(tex.outputs[0],bs.inputs[socket])
    bs.inputs['Coat Weight'].default_value=.12;bs.inputs['Coat Roughness'].default_value=.18
    for name in ['Laje sala — dimensões estimadas','Laje faixa lateral','Piso churrasqueira']:
        obj=bpy.data.objects[name];obj.data.materials.clear();obj.data.materials.append(mat)
        layer=obj.data.uv_layers.new(name='PHOTO_PisoMetrico');layer.active_render=True
        for index,loop in enumerate(obj.data.loops):
            point=obj.matrix_world@obj.data.vertices[loop.vertex_index].co
            layer.data[index].uv=(point.x/3,point.y/3)
    hide_prefix('Junta piso transversal','Junta piso longitudinal')


def curtains():
    hide_prefix('Cortina frontal fotografada')
    mat=g.basic('PHOTO Linho translúcido',(.66,.63,.56),.85)
    n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n.get('Principled BSDF');out=n.get('Material Output')
    trans=n.new('ShaderNodeBsdfTranslucent');trans.inputs['Color'].default_value=(.74,.71,.65,1)
    mix=n.new('ShaderNodeMixShader');mix.inputs[0].default_value=.58;l.new(bs.outputs[0],mix.inputs[1]);l.new(trans.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs[0]);bs.inputs['Sheen Weight'].default_value=.5
    for left,right in [(.25,1.12),(1.27,2.15)]:
        verts=[];faces=[];nx=72;nz=32
        for i in range(nx+1):
            u=i/nx
            for j in range(nz+1):
                t=j/nz;x=left+(right-left)*u+.009*math.sin(t*4+u*6)*(1-t)
                y=.155+.034*math.sin(u*math.tau*6)+.008*math.sin(u*math.tau*2)*(1-t)
                z=.045+2.575*t+.012*math.sin(u*math.tau*4)*(1-t)
                verts.append((x,y,z))
        for i in range(nx):
            for j in range(nz):a=i*(nz+1)+j;faces.append((a,a+1,a+nz+2,a+nz+1))
        mesh=bpy.data.meshes.new('Linho com queda e pregas');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('PHOTO Cortina de linho',mesh);g.C[COL].objects.link(o);mesh.materials.append(mat)
        for p in mesh.polygons:p.use_smooth=True
        o.modifiers.new('Espessura tecido','SOLIDIFY').thickness=.0008
        sub=o.modifiers.new('Suavizar pregas','SUBSURF');sub.levels=1


def living():
    hide_prefix('HQ SOFÁ couro','IND mesa centro','IND livro mesa centro','IND almofada linho')
    hide_prefix('Arranjo jantar original','IND planta prateleira','IND vaso bar','IND planta escritório','Planta janela cozinha')
    place('sofa_02','Sofá Chesterfield',(.60,1.65,0),res='4k',width=1.90,angle=math.pi/2)
    recolor('sofa_02','4k',tint=(2.8,1.45,.70),saturation=.75)
    place('throw_pillows_01','Almofadas',(.47,1.65,.36),width=.92,angle=math.pi/2)
    recolor('throw_pillows_01','2k',saturation=.1,plain=(.42,.39,.34))
    place('industrial_coffee_table','Mesa industrial',(1.75,1.62,0),fit=(.56,.98,.38))
    place('potted_plant_04','Planta mesa',(1.75,1.65,.39),height=.20)
    place('potted_plant_01','Planta piso',(.37,2.96,0),res='1k',height=.78,angle=.3)
    place('potted_plant_04','Planta prateleira',(.23,3.30,2.18),height=.24,angle=1.0)
    hide_prefix('IND livros sala')
    place('book_encyclopedia_set_01','Livros sala',(.23,2.90,1.62),width=.48,angle=math.pi/2)
    place('industrial_wall_lamp','Arandela sala',(.15,2.90,1.55),res='1k',width=.25,angle=math.pi/2)
    # Impressão da referência fornecida, selecionada por UV dentro do próprio 3D.
    art=g.basic('PHOTO Arte floresta',(.5,.5,.5),.94)
    n=art.node_tree.nodes;l=art.node_tree.links;tex=n.new('ShaderNodeTexImage');tex.image=asset_image('garden_nook','_2k.hdr')
    mono=n.new('ShaderNodeHueSaturation');mono.inputs['Saturation'].default_value=0;mono.inputs['Value'].default_value=.25;l.new(tex.outputs[0],mono.inputs['Color']);l.new(mono.outputs[0],n.get('Principled BSDF').inputs['Base Color'])
    panel=box('Arte sobre sofá',(.098,1.65,1.65),(.008,1.0,.68),'PHOTO Arte floresta',.001)
    layer=panel.data.uv_layers.active
    for index,loop in enumerate(panel.data.loops):
        co=panel.data.vertices[loop.vertex_index].co;u=co.y+.5;v=(co.z+.34)/.68
        layer.data[index].uv=(.15+u*.45,.30+v*.50)
    for yy in [1.14,2.16]:box('Moldura arte',(.11,yy,1.65),(.035,.025,.73),'IND Aço preto',.003)
    for zz in [1.29,2.01]:box('Moldura arte',(.11,1.65,zz),(.035,1.04,.025),'IND Aço preto',.003)
    place('potted_plant_04','Arranjo jantar',(1.52,5.80,.81),height=.25,angle=.9)


def kitchen():
    hide_prefix('FOGAO_cozinha','MICROONDAS_nicho_cozinha','IND pote cozinha')
    place('electric_stove','Fogão detalhado',(5.215,6.52,0),fit=(.55,.60,.88),angle=-math.pi/2)
    place('vintage_microwave','Micro-ondas',(5.31,7.14,1.43),fit=(.49,.41,.30),angle=-math.pi/2)
    place('vintage_electric_kettle','Chaleira',(5.19,5.68,.94),height=.27,angle=-.3)
    for i,x in enumerate([3.85,5.05]):place('potted_plant_04','Ervas janela '+str(i),(x,7.76,1.08),height=.23,angle=i*1.7)


def leisure(house):
    hide_prefix('HQ banqueta','HQ apoio pés banqueta')
    for i,x in enumerate(house['layout']['bar']['stool_x']):
        place('metal_stool_01','Banqueta '+str(i),(x,house['layout']['bar']['stool_y'],0),height=.77)
    place('potted_plant_04','Planta bar',(.25,9.55,1.03),height=.29)
    place('wine_bottles_01','Garrafas bar',(2.02,10.21,1.88),res='1k',width=.50)


def office(house):
    z=house['estimated_dimensions_m']['floor_height']
    hide_prefix('IND livros escritório')
    place('book_encyclopedia_set_01','Livros escritório',(3.11,6.05,z+1.80),width=.54,angle=math.pi/2)
    place('potted_plant_04','Planta escritório',(3.11,6.88,z+2.30),height=.25,angle=.4)
    g.basic('PHOTO Aço luminária',(.018,.021,.024),.32,.8)
    g.cylinder('PHOTO Base luminária',(3.14,5.75,z+.785),.075,.028,'PHOTO Aço luminária',COL)
    joints=[(3.14,5.75,z+.80),(3.10,5.75,z+1.03),(3.29,5.75,z+1.19)]
    for a,b in zip(joints,joints[1:]):g.rod('PHOTO Braço luminária',a,b,.009,'PHOTO Aço luminária',COL)
    for a in joints:g.sphere('PHOTO Articulação luminária',a,(.017,)*3,'PHOTO Aço luminária',COL)
    g.lathe('PHOTO Cúpula luminária',[(.065,0),(.065,.008),(.025,.09),(.022,.105)],(3.29,5.75,z+1.10),'PHOTO Aço luminária',COL)
    g.basic('PHOTO Difusor luminária',(.8,.65,.4),.5,emission=2)
    g.cylinder('PHOTO Difusor luminária',(3.29,5.75,z+1.103),.059,.003,'PHOTO Difusor luminária',COL)
    place('potted_plant_04','Planta bancada',(3.16,6.95,z+.77),height=.17)
    hide_prefix('IND base cadeira','IND pé estrela','IND assento escritório','IND encosto escritório','IND braço cadeira')
    black=g.basic('PHOTO Nylon cadeira',(.012,.014,.015),.58)
    g.basic('PHOTO Metal cadeira',(.035,.041,.045),.30,.85)
    g.basic('PHOTO Borracha',(.009,.010,.011),.82)
    meshmat=g.basic('PHOTO Tela ergonômica',(.012,.015,.017),.85)
    n=meshmat.node_tree.nodes;l=meshmat.node_tree.links;out=n.get('Material Output');bs=n.get('Principled BSDF');bs.inputs['Sheen Weight'].default_value=.3
    coord=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');comb=n.new('ShaderNodeCombineXYZ');l.new(coord.outputs['Generated'],sep.inputs[0]);l.new(sep.outputs['Y'],comb.inputs['X']);l.new(sep.outputs['Z'],comb.inputs['Y'])
    grid=n.new('ShaderNodeTexBrick');grid.inputs['Scale'].default_value=100;grid.inputs['Mortar Size'].default_value=.08;grid.inputs['Brick Width'].default_value=.5;grid.inputs['Row Height'].default_value=.5;l.new(comb.outputs[0],grid.inputs['Vector'])
    transparent=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');l.new(grid.outputs['Fac'],mix.inputs[0]);l.new(transparent.outputs[0],mix.inputs[1]);l.new(bs.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs[0])
    cx,cy=3.80,6.21
    box('Assento ergonômico',(cx,cy,z+.49),(.45,.46,.09),'PHOTO Nylon cadeira',.04)
    verts=[];faces=[];ny=28;nz=32
    for i in range(ny+1):
        u=-1+2*i/ny
        for j in range(nz+1):
            t=j/nz;w=.205+.025*math.sin(t*math.pi)
            verts.append((cx+.20-.055*math.sin(t*math.pi),cy+u*w,z+.59+t*.62))
    for i in range(ny):
        for j in range(nz):a=i*(nz+1)+j;faces.append((a,a+1,a+nz+2,a+nz+1))
    me=bpy.data.meshes.new('Encosto curvo em tela');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('PHOTO Encosto ergonômico',me);g.C[COL].objects.link(o);me.materials.append(meshmat)
    for p in me.polygons:p.use_smooth=True
    for side in [-1,1]:
        points=[]
        for j in range(13):
            t=j/12;points.append((cx+.205-.055*math.sin(t*math.pi),cy+side*(.22+.025*math.sin(t*math.pi)),z+.58+t*.64))
        g.curve('PHOTO Moldura encosto',points,.017,'PHOTO Nylon cadeira',COL)
        g.rod('PHOTO Apoio braço',(cx+.08,cy+side*.24,z+.47),(cx+.08,cy+side*.24,z+.70),.014,'PHOTO Metal cadeira',COL)
        box('Braço ergonômico',(cx-.01,cy+side*.24,z+.71),(.31,.045,.04),'PHOTO Nylon cadeira',.018)
    box('Apoio lombar',(cx+.18,cy,z+.68),(.035,.38,.11),'PHOTO Nylon cadeira',.015)
    box('Apoio de cabeça',(cx+.20,cy,z+1.30),(.075,.35,.15),'PHOTO Nylon cadeira',.035)
    g.cylinder('PHOTO Pistão cadeira',(cx,cy,z+.28),.028,.40,'PHOTO Metal cadeira',COL)
    for i in range(5):
        angle=(i+.15)*math.tau/5;x=cx+.26*math.cos(angle);y=cy+.26*math.sin(angle)
        g.rod('PHOTO Base estrela',(cx,cy,z+.16),(x,y,z+.075),.018,'PHOTO Metal cadeira',COL)
        for side in [-1,1]:g.cylinder('PHOTO Rodízio',(x-side*.014*math.sin(angle),y+side*.014*math.cos(angle),z+.038),.036,.022,'PHOTO Borracha',COL,rotation=(math.pi/2,0,angle))
    hide_prefix('HQ colchão beliche','HQ travesseiro beliche','HQ colcha dobrada')
    bed=bpy.data.objects['Beliche quarto fundos'];origin=bed.matrix_world.translation
    cloth=g.textured('PHOTO Algodão',[(.45,.43,.39),(.55,.52,.46)],'leather',.94,.0002);cloth.node_tree.nodes.get('Principled BSDF').inputs['Sheen Weight'].default_value=.4
    for height in [.46,1.48]:
        mattress=box('Colchão',tuple(origin+Vector((0,0,height))),(.845,1.875,.17),'PHOTO Algodão',.05)
        mattress.parent=bed;mattress.matrix_parent_inverse=bed.matrix_world.inverted()
        vertices=[];polys=[];nx=48;ny=80
        for i in range(nx+1):
            u=-1+2*i/nx;x=u*.47
            for j in range(ny+1):
                v=j/ny;y=-.94+v*1.72
                drape=.15*max(0,(abs(u)-.85)/.15)**1.1
                zz=height+.11-drape+.009*math.sin(u*15+v*9)+.006*math.sin(u*29-v*17)
                vertices.append((x,y,zz))
        for i in range(nx):
            for j in range(ny):a=i*(ny+1)+j;polys.append((a,a+1,a+ny+2,a+ny+1))
        me=bpy.data.meshes.new('Roupa de cama com caída');me.from_pydata(vertices,[],polys);me.update();o=bpy.data.objects.new('PHOTO Edredom com pregas',me);g.C[COL].objects.link(o);o.parent=bed;me.materials.append(cloth)
        for p in me.polygons:p.use_smooth=True
        o.modifiers.new('Espessura algodão','SOLIDIFY').thickness=.003
        pillows=place('throw_pillows_01','Almofadas beliche '+str(height),tuple(origin+Vector((0,.61,height+.09))),width=.72)
        pillows.parent=bed;pillows.matrix_parent_inverse=bed.matrix_world.inverted()
    # Estrutura completa do beliche, com travessas e abertura junto à escada.
    for y in [-.95,.95]:
        for height in [.30,.74,1.32,1.79]:g.rod('PHOTO Travessa beliche',(-.44,y,height),(.44,y,height),.014,'PHOTO Metal cadeira',COL,bed)
    for x in [-.44,.44]:
        for height in [1.65,1.79]:
            spans=[(-.92,-.60),(-.05,.92)] if x<0 else [(-.92,.92)]
            for a,b in spans:g.rod('PHOTO Proteção lateral beliche',(x,a,height),(x,b,height),.014,'PHOTO Metal cadeira',COL,bed)
    for y in [-.55,-.08]:g.rod('PHOTO Montante escada beliche',(-.49,y,.04),(-.49,y,1.67),.017,'PHOTO Metal cadeira',COL,bed)


def lighting():
    for obj in bpy.data.objects:
        if obj.type=='LIGHT':obj.hide_render=True
    world=bpy.data.worlds.new('PHOTO Jardim e luz natural CC0');world.use_nodes=True;n=world.node_tree.nodes;l=world.node_tree.links
    env=n.new('ShaderNodeTexEnvironment');env.image=asset_image('garden_nook','_2k.hdr')
    tex=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeMapping');mapping.inputs['Rotation'].default_value[2]=1.1
    l.new(tex.outputs['Generated'],mapping.inputs['Vector']);l.new(mapping.outputs[0],env.inputs['Vector']);l.new(env.outputs[0],n.get('Background').inputs['Color']);n.get('Background').inputs['Strength'].default_value=.65
    for scene in bpy.data.scenes:scene.world=world
    data=bpy.data.lights.new('PHOTO Sol difuso','SUN');data.energy=1.4;data.color=(1,.87,.68);data.angle=math.radians(5)
    sun=bpy.data.objects.new('PHOTO Sol difuso',data);g.C['Iluminacao'].objects.link(sun);sun.location=(1,-7,3)
    sun.rotation_euler=(Vector((1.5,2,.8))-sun.location).to_track_quat('-Z','Y').to_euler()
    for name,loc,power in [('arandela sala',(.24,2.90,1.75),5),('pendente jantar',(1.52,5.27,2.17),15),('pendente jantar',(1.52,6.33,2.17),15),('pendente bar',(.60,9.50,2.17),15),('pendente bar',(1.90,9.50,2.17),15),('luminária escritório',(3.34,5.88,4.00),6)]:
        g.light('PHOTO '+name,loc,power,color=(1,.62,.30),kind='POINT',size=.018)
    for y in [5.70,6.48,7.13]:
        g.light('PHOTO LED cozinha',(5.15,y,1.71),4,color=(1,.72,.43),kind='POINT',size=.018)
    g.light('PHOTO LED escritório',(3.22,6.35,4.64),6,color=(1,.62,.30),kind='POINT',size=.015)
    g.light('PHOTO LED bar',(1.85,10.10,1.80),10,color=(1,.55,.23),kind='POINT',size=.018)


def softbox(scene,job):
    """Preenchimento fotográfico editável, fora da imagem e dos reflexos."""
    rigs={
        'PHOTO_Sala':((2.65,3.65,2.15),(.6,1.65,.70),2.0,18),
        'PHOTO_Sala_Integrada':((1.7,.20,2.10),(1.6,5,1.0),1.8,22),
        'PHOTO_Cozinha':((3.7,4.70,2.2),(4.6,7,1.1),1.4,22),
        'PHOTO_Lazer':((2.4,7.70,2.4),(1.6,10,1.2),1.5,22),
        'PHOTO_Quarto':((3.85,4.35,5.1),(4.1,6.45,3.7),1.2,22)
    }
    loc,target,size,power=rigs[job['scene']]
    c=bpy.data.collections.new('RIG_'+scene.name);scene.collection.children.link(c)
    mesh=bpy.data.meshes.new('Painel fotográfico');mesh.from_pydata([(-size/2,-size/2,0),(size/2,-size/2,0),(size/2,size/2,0),(-size/2,size/2,0)],[],[(0,1,2,3)])
    obj=bpy.data.objects.new('Softbox '+scene.name,mesh);c.objects.link(obj);obj.location=loc;obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('Z','Y').to_euler()
    obj.visible_camera=False;obj.visible_glossy=False;obj.visible_transmission=False;obj.visible_shadow=False
    mat=bpy.data.materials.new('Emissor '+scene.name);mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();em=n.new('ShaderNodeEmission');em.inputs['Color'].default_value=(1,.93,.83,1);em.inputs['Strength'].default_value=power;out=n.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(em.outputs[0],out.inputs['Surface']);mesh.materials.append(mat)


def gpu(cpu=False):
    prefs=bpy.context.preferences.addons['cycles'].preferences
    if cpu:return {'backend':'CPU','devices':['CPU']}
    prefs.compute_device_type='CUDA';prefs.get_devices();devices=[d for d in prefs.devices if d.type=='CUDA']
    if not devices:raise RuntimeError('CUDA indisponível. Use --wsl-gpu no launcher ou --cpu explicitamente.')
    for d in prefs.devices:d.use=d.type=='CUDA'
    return {'backend':'CUDA','devices':[d.name for d in devices]}


def build(cpu):
    global COL
    base=ROOT/CFG['base_blend'];assert Path(bpy.data.filepath).resolve()==base
    before=v1.geometry();base_sha=v1.sha(base);g.C.update({c.name:c for c in bpy.data.collections});g.M.update({m.name:m for m in bpy.data.materials})
    collection();bpy.context.view_layer.update();house=json.loads((ROOT/'config/planta-casa.json').read_text())
    surfaces();curtains()
    COL='PHOTO_Sala_Objetos';living()
    COL='PHOTO_Cozinha_Objetos';kitchen()
    COL='PHOTO_Lazer_Objetos';leisure(house)
    COL='PHOTO_Quarto_Objetos';office(house)
    COL=ROOT_COL;lighting()
    device=gpu(cpu)
    for job in CFG['jobs']:
        scene=bpy.data.scenes[job['source']].copy();scene.name=job['scene'];scene.use_fake_user=True
        hidden={'PHOTO_Quarto_Objetos'} if job['scene']!='PHOTO_Quarto' else {'PHOTO_Sala_Objetos','PHOTO_Cozinha_Objetos','PHOTO_Lazer_Objetos'}
        if job['scene']=='PHOTO_Sala':hidden|={'PHOTO_Cozinha_Objetos','PHOTO_Lazer_Objetos'}
        if job['scene']=='PHOTO_Cozinha':hidden|={'PHOTO_Sala_Objetos','PHOTO_Lazer_Objetos'}
        def visibility(layer):
            if layer.name in hidden:layer.exclude=True
            for child in layer.children:visibility(child)
        visibility(scene.view_layers[0].layer_collection)
        camera=scene.camera.copy();camera.data=scene.camera.data.copy();g.C['Cameras'].objects.link(camera);camera.name=job['scene']+'_Camera';scene.camera=camera
        if 'position' in job:camera.location=job['position'];camera.rotation_euler=(Vector(job['target'])-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=job['lens']
        focus=g.parent('FOCO '+job['scene'],COL,job['focus']);camera.data.dof.use_dof=True;camera.data.dof.focus_object=focus;camera.data.dof.aperture_fstop=7.1
        scene.render.resolution_x,scene.render.resolution_y=CFG['resolution'];scene.render.resolution_percentage=100
        scene.cycles.device='CPU' if cpu else 'GPU';scene.cycles.samples=CFG['samples'];scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=CFG['adaptive_threshold'];scene.cycles.adaptive_min_samples=64;scene.cycles.use_denoising=True
        scene.cycles.max_bounces=14;scene.cycles.diffuse_bounces=6;scene.cycles.glossy_bounces=6;scene.cycles.transmission_bounces=12;scene.cycles.sample_clamp_indirect=5
        scene.view_settings.exposure=.40
        try:scene.view_settings.look='AgX - Medium High Contrast'
        except TypeError:pass
        softbox(scene,job)
    edit=bpy.data.scenes.new('EDITAR_Ativos');edit.use_fake_user=True
    for key,data in CACHE.items():edit.collection.children.link(data['collection'])
    edit.view_layers[0].update()
    for layer in edit.view_layers[0].layer_collection.children:
        layer.exclude=layer.collection!=CACHE[('sofa_02','4k')]['collection']
    missing=[]
    for im in bpy.data.images:
        if im.source!='FILE' or im.packed_file:continue
        path=Path(bpy.path.abspath(im.filepath))
        if path.is_file():im.pack()
        else:missing.append([im.name,str(path)])
    assert not missing,missing
    after=v1.geometry();differences=[n for n,h in before.items() if after.get(n)!=h];assert not differences,differences
    envelope=audit_envelope.audit(house);assert envelope['all_passed']
    output=ROOT/CFG['output_blend'];assert not output.exists(),output;output.parent.mkdir(parents=True,exist_ok=True)
    bpy.context.window.scene=bpy.data.scenes['PHOTO_Sala'];bpy.ops.wm.save_as_mainfile(filepath=str(output),compress=True);assert v1.sha(base)==base_sha
    model={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'base':CFG['base_blend'],'base_sha256':base_sha,'blend_sha256':v1.sha(output),'geometry_before':before,'geometry_differences':differences,'envelope':envelope,'placements':PLACEMENTS,'assets':ASSETS,'device':device,'packed_images':len([i for i in bpy.data.images if i.packed_file])}
    (REPORTS/'modelo.json').write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n');print('PHOTO_MODEL_BUILT',len(before),'source geometries preserved',flush=True)


def validate():
    model=json.loads((REPORTS/'modelo.json').read_text());assert v1.sha(Path(bpy.data.filepath))==model['blend_sha256']
    assert v1.sha(ROOT/CFG['base_blend'])==model['base_sha256']
    now=v1.geometry();diff=[n for n,h in model['geometry_before'].items() if now.get(n)!=h];assert not diff,diff
    envelope=audit_envelope.audit(json.loads((ROOT/'config/planta-casa.json').read_text()));assert envelope['all_passed']
    missing=[i.name for i in bpy.data.images if i.source=='FILE' and not i.packed_file];assert not missing,missing
    receipt={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'blend_sha256':model['blend_sha256'],'base_sha256':model['base_sha256'],'geometry_compared':len(model['geometry_before']),'geometry_differences':diff,'envelope':envelope,'packed_images':len([i for i in bpy.data.images if i.packed_file]),'missing_images':missing,'scenes':{},'placements_checked':len(model['placements'])}
    for job in CFG['jobs']:
        scene=bpy.data.scenes[job['scene']];assert scene.camera and scene.render.engine=='CYCLES'
        receipt['scenes'][scene.name]={'camera':scene.camera.name,'resolution':[scene.render.resolution_x,scene.render.resolution_y]}
    for placement in model['placements']:
        obj=bpy.data.objects[placement['name']];assert all(abs(obj.location[i]-placement['location'][i])<1e-5 for i in range(3))
        assert obj.children and obj.children[0].instance_collection
    receipt['all_passed']=True
    (REPORTS/'validacao.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    return model,envelope


def render(preview,only,cpu):
    model,envelope=validate();device=gpu(cpu);outputs={}
    for job in CFG['jobs']:
        if only and job['file'].split('.')[0] not in only:continue
        scene=bpy.data.scenes[job['scene']];scene.cycles.device='CPU' if cpu else 'GPU';scene.cycles.samples=64 if preview else CFG['samples'];scene.cycles.adaptive_min_samples=16 if preview else 64
        scene.render.resolution_percentage=40 if preview else 100;scene.render.filepath=str(ROOT/CFG['render_directory']/('previas' if preview else '')/job['file']);Path(scene.render.filepath).parent.mkdir(parents=True,exist_ok=True)
        bpy.ops.render.render(write_still=True,scene=scene.name);file=Path(scene.render.filepath)
        outputs[str(file.relative_to(ROOT))]={'sha256':v1.sha(file),'bytes':file.stat().st_size,'scene':scene.name};print('PHOTO_RENDER',scene.name,flush=True)
    validate();receipt={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'blend_sha256':model['blend_sha256'],'preview':preview,'device':device,'envelope':envelope,'outputs':outputs}
    (REPORTS/('previas.json' if preview else 'renders.json')).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser();p.add_argument('--render-only',action='store_true');p.add_argument('--build-only',action='store_true');p.add_argument('--validate-only',action='store_true');p.add_argument('--preview',action='store_true');p.add_argument('--only',nargs='*');p.add_argument('--cpu',action='store_true')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);REPORTS.mkdir(parents=True,exist_ok=True)
    if args.validate_only:validate();print('PHOTO_NATIVE_VALIDATED');return
    if not args.render_only:build(args.cpu)
    if not args.build_only:render(args.preview,args.only,args.cpu)


if __name__=='__main__':main()
