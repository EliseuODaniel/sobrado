"""Direção de arte v04: formas contemporâneas, vegetação e luz comum às vistas."""
import argparse
import datetime as dt
import json
import math
from pathlib import Path
import random
import sys
import time

import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import blender_primitives as g
import style_industrial as prior
import photographic_interiors as photo
import audit_envelope

CFG=json.loads((ROOT/'config/estilo-industrial-v04.json').read_text())
REPORT=ROOT/CFG['report_directory']
NEW_ASSETS=json.loads((ROOT/CFG['asset_manifest']).read_text())['records']
photo.ASSETS+=NEW_ASSETS
RNG=random.Random(404)
COL='DESIGN_Sala_Objetos'
LEAF=None


def stamp():return dt.datetime.now(dt.timezone.utc).isoformat()


def set_room(room):
    global COL
    COL='DESIGN_'+room+'_Objetos';photo.COL=COL


def box(name,loc,size,mat,bevel=.006,parent=None):
    return g.box('DESIGN '+name,loc,size,mat,COL,bevel,parent)


def assign(obj,mat):
    obj.data.materials.clear();obj.data.materials.append(mat)


def copy_material(name,source):
    mat=bpy.data.materials[source].copy();mat.name='DESIGN '+name;g.M[mat.name]=mat
    return mat


def image(asset,needle,color=True):
    records=[*photo.ASSETS,*json.loads((ROOT/'assets/industrial-v02/manifesto.json').read_text())['records']]
    item=next(r for r in records if r['asset']==asset and needle in Path(r['path']).name)
    p=ROOT/item['path'];assert prior.sha(p)==item['sha256']
    im=bpy.data.images.load(str(p),check_existing=True)
    if not color:im.colorspace_settings.name='Non-Color'
    im.pack();return im


def materials():
    wood=copy_material('Carvalho mel','HQ Madeira');n=wood.node_tree.nodes;l=wood.node_tree.links;bs=n.get('Principled BSDF')
    source=bs.inputs['Base Color'].links[0].from_socket
    hue=n.new('ShaderNodeHueSaturation');hue.inputs['Value'].default_value=2.4;hue.inputs['Saturation'].default_value=.95;l.new(source,hue.inputs['Color']);tint=n.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=(1.25,1.02,.70,1);l.new(hue.outputs[0],tint.inputs[1]);l.new(tint.outputs[0],bs.inputs['Base Color'])
    bs.inputs['Roughness'].default_value=.43
    for link in list(bs.inputs['Roughness'].links):l.remove(link)
    for node in n:
        if node.type=='NORMAL_MAP':node.inputs['Strength'].default_value=.13
    wood['acabamento']='Carvalho quente; escala e veios herdados da marcenaria'
    for obj in list(bpy.data.objects):
        if obj.type not in {'MESH','CURVE'}:continue
        for slot in obj.material_slots:
            if slot.material and slot.material.name=='HQ Madeira':slot.material=wood
    # Porcelanato limpo: juntas métricas e discreta variação fotográfica.
    floor=g.basic('DESIGN Porcelanato acetinado',(.4,.37,.32),.18);n=floor.node_tree.nodes;l=floor.node_tree.links;bs=n.get('Principled BSDF')
    geom=n.new('ShaderNodeNewGeometry');brick=n.new('ShaderNodeTexBrick');brick.offset=0;brick.inputs['Scale'].default_value=1;brick.inputs['Brick Width'].default_value=.60;brick.inputs['Row Height'].default_value=.60;brick.inputs['Mortar Size'].default_value=.0015
    brick.inputs['Color1'].default_value=(.39,.36,.31,1);brick.inputs['Color2'].default_value=(.37,.34,.295,1);brick.inputs['Mortar'].default_value=(.19,.18,.16,1);l.new(geom.outputs['Position'],brick.inputs['Vector']);l.new(brick.outputs['Color'],bs.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.001;l.new(brick.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
    bs.inputs['Coat Weight'].default_value=.12;bs.inputs['Coat Roughness'].default_value=.20
    for name in ['Laje sala — dimensões estimadas','Laje faixa lateral','Piso churrasqueira']:assign(bpy.data.objects[name],floor)
    g.basic('DESIGN Aço fosco',(.009,.011,.012),.38,.75)
    g.basic('DESIGN Costura couro',(.14,.055,.018),.54)
    g.basic('DESIGN Cerâmica preta',(.017,.021,.018),.32)
    g.basic('DESIGN Vidro',(.91,.97,.94),.07,transmission=1)
    g.basic('DESIGN Papel',(.55,.51,.42),.85)
    g.basic('DESIGN Terra',(.032,.021,.012),.93)
    g.textured('DESIGN Juta',[(.27,.22,.155),(.38,.33,.24)],'leather',.94,.0012)
    g.basic('DESIGN Haste vegetal',(.045,.075,.012),.62)
    for i,col in enumerate([(.10,.19,.026),(.065,.14,.016),(.16,.25,.035)]):
        mat=g.basic('DESIGN Folha '+str(i),col,.43);n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n.get('Principled BSDF');bs.inputs['Subsurface Weight'].default_value=.08
        tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=24;tex.inputs['Detail'].default_value=3
        bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.0003;l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])


def leather_material(source):
    mat=source.copy();mat.name='DESIGN Couro conhaque';g.M[mat.name]=mat;n=mat.node_tree.nodes;l=mat.node_tree.links;bs=next(x for x in n if x.type=='BSDF_PRINCIPLED')
    tex=n.new('ShaderNodeTexImage');tex.image=image('brown_leather','albedo');tex.projection='BOX';tex.projection_blend=.3
    coord=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeMapping');mapping.inputs['Scale'].default_value=(2,2,2);l.new(coord.outputs['Generated'],mapping.inputs['Vector']);l.new(mapping.outputs[0],tex.inputs['Vector'])
    hue=n.new('ShaderNodeHueSaturation');hue.inputs['Value'].default_value=1.7;hue.inputs['Saturation'].default_value=.80;l.new(tex.outputs[0],hue.inputs['Color'])
    tint=n.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=(1.65,.92,.50,1);l.new(hue.outputs[0],tint.inputs[1]);l.new(tint.outputs[0],bs.inputs['Base Color'])
    for link in list(bs.inputs['Roughness'].links):l.remove(link)
    bs.inputs['Roughness'].default_value=.44;bs.inputs['Metallic'].default_value=0;bs.inputs['Coat Weight'].default_value=.08;bs.inputs['Coat Roughness'].default_value=.35;bs.inputs['Sheen Weight'].default_value=.10
    for node in n:
        if node.type=='NORMAL_MAP':node.inputs['Strength'].default_value=.42
    return mat


def cushion_components(obj):
    mesh=obj.data;faces=[p for p in mesh.polygons if 'pillow' in mesh.materials[p.material_index].name];adj={}
    for face in faces:
        for vertex in face.vertices:adj.setdefault(vertex,set()).update(face.vertices)
    remaining=set(adj);components=[]
    while remaining:
        pending=[remaining.pop()];component=set(pending)
        while pending:
            current=pending.pop();new=adj[current]&remaining;remaining.difference_update(new);pending.extend(new);component.update(new)
        if len(component)>200:components.append(component)
    assert len(components)==2,len(components)
    return sorted(components,key=lambda comp:min((obj.matrix_world@mesh.vertices[v].co).z for v in comp))


def sofa():
    photo.hide_prefix('PHOTO Sofá Chesterfield');photo.hide(bpy.data.objects['PHOTO Almofadas'])
    source=photo.template('modern_arm_chair_01');obj=next(o for o in source['objects'] if o.type=='MESH')
    parts=cushion_components(obj);leather=leather_material(next(m for m in obj.data.materials if 'pillow' in m.name))
    # Estrutura própria, com três assentos e encostos derivados de almofadas 3D.
    root=g.parent('DESIGN Sofá contemporâneo',COL,(.56,1.65,0));root.rotation_euler.z=math.pi/2
    for x in [-1.08,1.08]:
        for y in [-.31,.31]:g.cylinder('DESIGN Pé sofá',(x,y,.105),.028,.19,'DESIGN Aço fosco',COL,root)
    box('Base sofá',(0,0,.285),(2.38,.83,.24),leather,.065,root)
    for x in [-1.14,1.14]:box('Braço estofado',(x,-.015,.56),(.18,.87,.54),leather,.075,root)
    box('Costas sofá',(0,.34,.69),(2.16,.15,.56),leather,.055,root)
    for kind,component in enumerate(parts):
        original=sorted(component);index={v:i for i,v in enumerate(original)};points=[obj.matrix_world@obj.data.vertices[v].co for v in original]
        low=Vector(tuple(min(p[i] for p in points) for i in range(3)));high=Vector(tuple(max(p[i] for p in points) for i in range(3)));center=(low+high)/2;size=high-low
        target=Vector((.70,.69,.19) if kind==0 else (.70,.26,.55));location=Vector((0,-.025,.465) if kind==0 else (0,.245,.79))
        vertices=[tuple(Vector(tuple((p[i]-center[i])*target[i]/size[i] for i in range(3)))+location) for p in points]
        selected=[p for p in obj.data.polygons if all(v in component for v in p.vertices)];faces=[tuple(index[v] for v in p.vertices) for p in selected]
        mesh=bpy.data.meshes.new('DESIGN Almofada couro com pregas');mesh.from_pydata(vertices,[],faces);mesh.update();mesh.materials.append(leather)
        for polygon in mesh.polygons:polygon.use_smooth=True
        for layer in obj.data.uv_layers:
            new=mesh.uv_layers.new(name=layer.name)
            for a,b in zip(mesh.polygons,selected):
                for dest,old in zip(a.loop_indices,b.loop_indices):new.data[dest].uv=layer.data[old].uv
        for x in [-.72,0,.72]:
            new=bpy.data.objects.new('DESIGN '+('Assento couro' if kind==0 else 'Encosto couro'),mesh);g.C[COL].objects.link(new);new.parent=root;new.location.x=x
    # Pespontos do assento, discretos e com curvas editáveis.
    for x in [-.72,0,.72]:
        pts=[(x+math.cos(a)*.329,-.02+math.sin(a)*.319,.537) for a in [i*math.tau/96 for i in range(97)]]
        g.curve('DESIGN Costura assento',pts,.0015,'DESIGN Costura couro',COL,root)
    # Almofadas soltas de linho em escala compatível com o sofá.
    photo.place('throw_pillows_01','V04 Almofadas linho',(.39,2.28,.55),width=.75,angle=math.pi/2)
    cloth=copy_material('Manta linho','HQ Tecido');cloth.node_tree.nodes.get('Principled BSDF').inputs['Sheen Weight'].default_value=.55
    verts=[];faces=[];nx=48;ny=64
    for i in range(nx+1):
        u=i/nx
        for j in range(ny+1):
            v=j/ny;x=-1.02+u*.65;y=-.62+v*.98;drop=.49*max(0,(-y-.34)/.28)**.8
            z=.57-drop+.018*math.sin(u*38+v*8)+.008*math.sin(u*76-v*15)
            verts.append((x,y,z))
    for i in range(nx):
        for j in range(ny):a=i*(ny+1)+j;faces.append((a,a+1,a+ny+2,a+ny+1))
    me=bpy.data.meshes.new('Manta com pregas');me.from_pydata(verts,[],faces);me.update();me.materials.append(cloth);o=bpy.data.objects.new('DESIGN Manta com caída',me);g.C[COL].objects.link(o);o.parent=root
    for p in me.polygons:p.use_smooth=True
    uv=me.uv_layers.new(name='DESIGN_Tecido')
    for i,loop in enumerate(me.loops):
        v=me.vertices[loop.vertex_index].co;uv.data[i].uv=((v.x+1.02)*2,(v.y+.62)*2)
    o.modifiers.new('Espessura tecido','SOLIDIFY').thickness=.002
    for i in range(43):
        u=i/42;x=-1.02+u*.65;z=.08+.018*math.sin(u*38)
        g.curve('DESIGN Franja manta',[(x,-.62,z),(x+.003,-.64,z-.025),(x+.006,-.65,z-.045)],.0008,cloth.name,COL,root)


def leaf_mesh():
    global LEAF
    if LEAF:return LEAF
    data=photo.template('potted_plant_02')
    for ob in data['objects']:
        if ob.type=='MESH' and 'leaves' in ob.name:
            for mat in ob.data.materials:
                if not mat or mat.get('DESIGN_ajuste_vegetal'):continue
                n=mat.node_tree.nodes;l=mat.node_tree.links;bs=next((x for x in n if x.type=='BSDF_PRINCIPLED'),None)
                if bs and bs.inputs['Base Color'].links:
                    source=bs.inputs['Base Color'].links[0].from_socket;hue=n.new('ShaderNodeHueSaturation');hue.inputs['Value'].default_value=.68;hue.inputs['Saturation'].default_value=1.05;l.new(source,hue.inputs['Color']);l.new(hue.outputs[0],bs.inputs['Base Color']);mat['DESIGN_ajuste_vegetal']=True
    obj=next(o for o in data['objects'] if o.type=='MESH' and 'leaves' in o.name)
    mesh=obj.data;adj={}
    for f in mesh.polygons:
        for v in f.vertices:adj.setdefault(v,set()).update(f.vertices)
    remaining=set(adj);components=[]
    while remaining:
        stack=[remaining.pop()];component=set(stack)
        while stack:
            v=stack.pop();new=adj[v]&remaining;remaining.difference_update(new);stack.extend(new);component.update(new)
        if 80<len(component)<3000:components.append(component)
    assert components,'Folhas sem componente separado'
    component=max(components,key=len);indices=sorted(component);lookup={v:i for i,v in enumerate(indices)}
    points=[obj.matrix_world@mesh.vertices[v].co for v in indices]
    low=Vector(tuple(min(p[i] for p in points) for i in range(3)));high=Vector(tuple(max(p[i] for p in points) for i in range(3)));size=high-low;axis=max(range(3),key=lambda i:size[i]);vector=Vector((0,0,0));vector[axis]=1
    rotation=vector.rotation_difference(Vector((0,1,0)));center=(low+high)/2;rotated=[rotation@(p-center) for p in points];minimum=min(p.y for p in rotated);length=max(p.y for p in rotated)-minimum
    vertices=[(p.x/length,(p.y-minimum)/length,p.z/length) for p in rotated];polygons=[p for p in mesh.polygons if all(v in component for v in p.vertices)]
    LEAF=bpy.data.meshes.new('DESIGN Folha botânica com UV');LEAF.from_pydata(vertices,[],[tuple(lookup[v] for v in p.vertices) for p in polygons]);LEAF.update();LEAF.materials.append(mesh.materials[0])
    for p in LEAF.polygons:p.use_smooth=True
    for layer in mesh.uv_layers:
        uv=LEAF.uv_layers.new(name=layer.name)
        for new,old in zip(LEAF.polygons,polygons):
            for a,b in zip(new.loop_indices,old.loop_indices):uv.data[a].uv=layer.data[b].uv
    print('BOTANICAL_LEAF',len(indices),'vertices; source components',len(components),flush=True)
    return LEAF


def leaf(name,loc,direction,length,angle):
    obj=bpy.data.objects.new('DESIGN '+name,leaf_mesh());g.C[COL].objects.link(obj);obj.location=loc;obj.scale=(length,)*3
    obj.rotation_euler=Vector(direction).to_track_quat('Y','Z').to_euler();obj.rotation_euler.rotate_axis('Y',angle)
    return obj


def trailing_plant(loc,drop=.85):
    x,y,z=loc
    g.lathe('DESIGN Vaso suspenso',[(.075,0),(.09,.15),(.095,.16)],loc,'DESIGN Cerâmica preta',COL)
    g.cylinder('DESIGN Terra vaso',(x,y,z+.15),.087,.008,'DESIGN Terra',COL)
    for branch in range(8):
        phi=branch*math.tau/8;points=[]
        for step in range(15):
            t=step/14;points.append((x+.05+(.12+.08*math.sin(t*3))*math.cos(phi)+.025*math.sin(t*9+branch),y+.12*math.sin(phi)+.10*math.sin(t*2+branch),z+.17-drop*t+.08*math.sin(t*4)))
        g.curve('DESIGN Jiboia haste',points,.0015,'DESIGN Haste vegetal',COL)
        for step in range(1,15):

            if RNG.random()<.22:continue
            p=Vector(points[step]);side=(-1)**step;direction=Vector((.5,side*.7,-.15+RNG.random()*.4))
            leaf('Jiboia folha',p,direction,RNG.uniform(.075,.13),RNG.uniform(.7,2.3))


def arrangement(loc,height=.45):
    photo.place('potted_plant_02','V04 Arranjo botânico '+str(loc),loc,height=height)
    for obj in photo.template('potted_plant_02')['objects']:
        if obj.type=='MESH' and 'potted_plant_02_pot' in obj.name:assign(obj,g.M['DESIGN Cerâmica preta'])


def dining():
    photo.hide_prefix('HQ cadeira jantar')
    source_parts=[next(o for o in bpy.data.objects if o.name.startswith('DESIGN '+prefix)) for prefix in ['Assento couro','Encosto couro']]
    meshes=[]
    for k,source in enumerate(source_parts):
        mesh=source.data.copy();points=[v.co.copy() for v in mesh.vertices];lo=Vector(tuple(min(v[i] for v in points) for i in range(3)));hi=Vector(tuple(max(v[i] for v in points) for i in range(3)));size=hi-lo;center=(hi+lo)/2;target=Vector((.43,.43,.075) if k==0 else (.43,.10,.48));loc=Vector((0,0,.48) if k==0 else (0,.19,.76))
        for v in mesh.vertices:v.co=Vector(tuple((v.co[i]-center[i])*target[i]/size[i] for i in range(3)))+loc
        meshes.append(mesh)
    for i,(x,y,angle) in enumerate([(.82,5.30,math.pi/2),(.82,6.30,math.pi/2),(2.22,5.30,-math.pi/2),(2.22,6.30,-math.pi/2)]):
        root=g.parent('DESIGN Cadeira jantar '+str(i+1),COL,(x,y,0));root.rotation_euler.z=angle
        for k,mesh in enumerate(meshes):
            obj=bpy.data.objects.new('DESIGN '+('Assento' if k==0 else 'Encosto')+' cadeira',mesh);g.C[COL].objects.link(obj);obj.parent=root
        for side in [-1,1]:
            for yloc in [-.17,.17]:g.rod('DESIGN Pé aço cadeira',(side*.19,yloc,.445),(side*.215,yloc*1.18,.025),.012,'DESIGN Aço fosco',COL,root)
            g.rod('DESIGN Travessa aço cadeira',(side*.19,-.17,.43),(side*.19,.20,.43),.012,'DESIGN Aço fosco',COL,root)


def panel_tv():
    old=bpy.data.objects['Painel TV branco'];old.hide_render=True;center=old.matrix_world.translation;outline=[];hy=1.05;hz=.825;r=.10
    for cy,cz,start in [(hy-r,hz-r,0),(-hy+r,hz-r,90),(-hy+r,-hz+r,180),(hy-r,-hz+r,270)]:
        for j in range(9):
            a=math.radians(start+j*90/8);outline.append((cy+r*math.cos(a),cz+r*math.sin(a)))
    verts=[(center.x+x,center.y+y,center.z+z) for x in [-.035,.035] for y,z in outline];n=len(outline);faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    for i in range(n):faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
    mesh=bpy.data.meshes.new('DESIGN Painel arredondado');mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(g.M['HQ Cimento']);uv=mesh.uv_layers.new(name='DESIGN_PainelMetrique')
    for i,loop in enumerate(mesh.loops):
        v=mesh.vertices[loop.vertex_index].co;uv.data[i].uv=(v.y/.65,v.z/.65)
    obj=bpy.data.objects.new('DESIGN Painel TV arredondado',mesh);g.C[COL].objects.link(obj)


def living():
    photo.hide_prefix('PHOTO Mesa industrial','PHOTO Planta mesa','PHOTO Planta piso','PHOTO Arranjo jantar','IND tapete sala')
    panel_tv();sofa();dining();photo.recolor('throw_pillows_01','2k',saturation=.04,plain=(.43,.39,.33));wood=g.M['DESIGN Carvalho mel']
    box('Tapete juta',(1.75,1.80,.019),(1.40,2.60,.022),'DESIGN Juta',.014)
    for side in [-1,1]:
        for i in range(95):
            x=1.06+i*.0145;y=1.80+side*1.30
            g.curve('DESIGN Franja tapete',[(x,y,.022),(x+.002,y+side*.035,.017),(x-.001,y+side*.055,.012)],.001,'DESIGN Juta',COL)
    root=g.parent('DESIGN Mesa de centro',COL,(1.75,1.75,0))
    for i in range(3):box('Tábua mesa centro',((i-1)*.19,0,.39),(.186,1.08,.045),wood,.005,root)
    for x in [-.255,.255]:
        for y in [-.49,.49]:box('Pé mesa centro',(x,y,.18),(.025,.025,.36),'DESIGN Aço fosco',.003,root)
        for z in [.045,.35]:box('Longarina mesa centro',(x,0,z),(.025,1.02,.025),'DESIGN Aço fosco',.003,root)
    for y in [-.49,.49]:box('Travessa mesa centro',(0,y,.045),(.52,.025,.025),'DESIGN Aço fosco',.003,root)
    arrangement((1.72,2.0,.418),.48)
    for i in range(3):box('Livro mesa centro',(1.75,1.43,.435+i*.026),(.24,.28,.023),['DESIGN Papel','IND Grafite','DESIGN Papel'][i],.002)
    g.lathe('DESIGN Tigela mesa',[(.035,0),(.065,.025),(.07,.035)],(1.75,1.43,.51),'DESIGN Cerâmica preta',COL)
    data=photo.template('calathea_orbifolia_01')
    selected=max([o for o in data['objects'] if o.type=='MESH'],key=lambda o:o.dimensions.z)
    solo=bpy.data.collections.new('DESIGN_Ativo_Calathea_solitario');solo.objects.link(selected)
    points=[selected.matrix_world@Vector(v) for v in selected.bound_box]
    low=Vector(tuple(min(p[i] for p in points) for i in range(3)));high=Vector(tuple(max(p[i] for p in points) for i in range(3)))
    data.update(collection=solo,low=low,high=high,size=high-low)
    photo.place('calathea_orbifolia_01','V04 Planta canto',(.43,3.35,.24),height=.56)
    g.lathe('DESIGN Cachepô canto',[(.12,0),(.17,.23),(.18,.25)],(.43,3.35,0),'DESIGN Cerâmica preta',COL)
    trailing_plant((.23,3.30,2.18),.88)
    arrangement((1.52,5.80,.815),.43)
    arrangement((2.87,2.45,.60),.48)


def stone():
    photo.hide_prefix('Pedra bar original')
    mat=g.basic('DESIGN Pedra natural oxidada',(.10,.07,.04),.66);n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n.get('Principled BSDF');uv=n.new('ShaderNodeTexCoord')
    for needle,socket in [('_diff_','Base Color'),('_rough_','Roughness'),('_nor_gl_','Normal')]:
        tex=n.new('ShaderNodeTexImage');tex.image=image('slate_floor_03',needle,socket=='Base Color');l.new(uv.outputs['UV'],tex.inputs['Vector'])
        if socket=='Normal':
            normal=n.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.35;l.new(tex.outputs[0],normal.inputs['Color']);l.new(normal.outputs[0],bs.inputs[socket])
        elif socket=='Base Color':
            hue=n.new('ShaderNodeHueSaturation');hue.inputs['Saturation'].default_value=.7;hue.inputs['Value'].default_value=.30;l.new(tex.outputs[0],hue.inputs['Color']);l.new(hue.outputs[0],bs.inputs[socket])
        else:l.new(tex.outputs[0],bs.inputs[socket])
    for i in range(10):
        for j in range(5):
            height=.176 if j==4 else .196;z=1.055+j*.2+height/2
            obj=box('Pedra quadrada bar',(.94+i*.2+.10,10.405,z),(.196,.028,height),mat,.002)
            layer=obj.data.uv_layers.active;offset=(RNG.random()*.65,RNG.random()*.65)
            for idx,loop in enumerate(obj.data.loops):
                v=obj.data.vertices[loop.vertex_index].co;layer.data[idx].uv=(offset[0]+(v.x+.1)*.8,offset[1]+(v.z+.1)*.8)


def details():
    set_room('Lazer');stone();trailing_plant((.23,10.18,2.43),.58)
    set_room('Quarto');trailing_plant((3.12,6.88,5.20),.50)


def lamp(name,loc,target,power,color=(1,.78,.56),size=.5,kind='AREA'):
    data=bpy.data.lights.new('DESIGN '+name,kind);data.energy=power;data.color=color
    if kind=='AREA':data.shape='DISK';data.size=size
    if kind=='SPOT':data.spot_size=math.radians(65);data.spot_blend=.65;data.shadow_soft_size=.065
    if kind=='POINT':data.shadow_soft_size=size
    obj=bpy.data.objects.new('DESIGN '+name,data);g.C['DESIGN_Iluminacao'].objects.link(obj);obj.location=loc
    if target:obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    if kind=='AREA':
        # Painel emissivo nativo: ilumina sem discos flutuantes no espelho/vidro.
        obj.hide_render=True
        width,height=(.50,.014) if 'LED' in name else (size,size)
        mesh=bpy.data.meshes.new('DESIGN Emissor '+name);mesh.from_pydata([(-width/2,-height/2,0),(width/2,-height/2,0),(width/2,height/2,0),(-width/2,height/2,0)],[],[(0,1,2,3)]);mesh.update()
        emitter=bpy.data.objects.new('DESIGN Painel '+name,mesh);g.C['DESIGN_Iluminacao'].objects.link(emitter);emitter.location=loc;emitter.rotation_euler=(Vector(target)-emitter.location).to_track_quat('Z','Y').to_euler()
        emitter.visible_camera=False;emitter.visible_glossy=False;emitter.visible_transmission=False;emitter.visible_shadow=False
        mat=bpy.data.materials.new('DESIGN Emissão '+name);mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();em=n.new('ShaderNodeEmission');em.inputs['Color'].default_value=(*color,1);em.inputs['Strength'].default_value=power/(math.pi*width*height);out=n.new('ShaderNodeOutputMaterial');geo=n.new('ShaderNodeNewGeometry');transparent=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');mat.node_tree.links.new(geo.outputs['Backfacing'],mix.inputs[0]);mat.node_tree.links.new(em.outputs[0],mix.inputs[1]);mat.node_tree.links.new(transparent.outputs[0],mix.inputs[2]);mat.node_tree.links.new(mix.outputs[0],out.inputs['Surface']);mesh.materials.append(mat)
    return obj


def lighting():
    for obj in list(bpy.data.objects):
        if obj.type=='LIGHT' or obj.name.startswith('Softbox PHOTO_'):obj.hide_render=True
    # Todas as vistas usam a mesma iluminação arquitetônica.
    lamp('Janela frente',(1.2,-.35,1.55),(1.6,4,.9),110,(.83,.90,1),1.8)
    lamp('Luz natural zenital',(1.5,9.1,3.0),(1.5,6.5,.7),140,(.85,.92,1),2.2)
    lamp('Preenchimento sala',(1.4,1.8,2.50),(1.4,1.7,0),45,(1,.88,.72),2.0)
    lamp('Preenchimento jantar',(1.5,5.1,2.50),(1.5,5.1,0),40,(1,.88,.72),1.8)
    g.basic('DESIGN Difusor downlight',(1,.72,.42),.5,emission=2)
    for y in [.90,1.50,2.10,2.70]:
        g.cylinder('DESIGN Aro downlight',(2.82,y,2.668),.045,.012,'DESIGN Aço fosco','DESIGN_Sala_Objetos')
        g.cylinder('DESIGN Difusor downlight',(2.82,y,2.659),.025,.004,'DESIGN Difusor downlight','DESIGN_Sala_Objetos')
        lamp('Wallwash TV',(2.82,y,2.64),(3.13,y,1.45),28,(1,.75,.48),kind='SPOT')
    for y in [.90,2.71]:lamp('LED vertical TV',(2.90,y,1.65),(3.13,y,1.65),5,(1,.60,.27),.18)
    for y in [5.27,6.33]:lamp('Pendente jantar',(1.52,y,2.16),(1.52,y,.79),36,(1,.73,.44),.24)
    for x in [.6,1.9]:lamp('Pendente bar',(x,9.50,2.15),(x,9.5,.99),32,(1,.73,.44),.22)
    for x in [1.20,1.87,2.50]:
        lamp('LED armário bar',(x,10.05,1.83),(x,10.38,1.35),14,(1,.64,.32),.42)
        lamp('Louceiro bar',(x,10.13,2.33),(x,10.13,1.94),3,(1,.69,.40),.20)
    for y in [5.70,6.48,7.13]:lamp('LED cozinha',(5.16,y,1.70),(5.16,y,.91),9,(1,.80,.58),.36)
    lamp('Cozinha ambiente',(4.3,6.4,2.55),(4.3,6.6,.7),55,(1,.87,.70),1.4)
    lamp('Arandela sala',(.24,2.90,1.75),(.10,2.9,1.2),9,(1,.68,.35),.13,kind='POINT')
    lamp('Quarto janela',(4.05,7.30,4.50),(4.1,5.8,3.6),70,(.85,.92,1),1.4)
    lamp('Quarto ambiente',(4.05,5.8,5.40),(4.1,6.2,3.5),40,(1,.85,.65),1.2)
    for y in [5.9,6.55]:lamp('LED prateleira quarto',(3.24,y,4.63),(3.0,y,4.0),8,(1,.65,.32),.35)


def setup_scenes():
    for job in CFG['jobs']:
        scene=bpy.data.scenes[job['source']].copy();scene.name=job['scene'];scene.use_fake_user=True
        if g.C['DESIGN04'].name not in scene.collection.children:scene.collection.children.link(g.C['DESIGN04'])
        camera=scene.camera.copy();camera.data=scene.camera.data.copy();g.C['Cameras'].objects.link(camera);camera.name=scene.name+'_Camera';scene.camera=camera
        if 'position' in job:
            camera.location=job['position'];camera.rotation_euler=(Vector(job['target'])-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=job['lens']
        camera.data.dof.aperture_fstop=9
        focus=g.parent('DESIGN Foco '+scene.name,'Cameras',job['focus']);camera.data.dof.focus_object=focus
        scene.render.resolution_x,scene.render.resolution_y=CFG['resolution'];scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_depth='16'
        scene.cycles.device='GPU';scene.cycles.samples=CFG['samples'];scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=CFG['adaptive_threshold'];scene.cycles.adaptive_min_samples=64;scene.cycles.use_denoising=True;scene.cycles.use_light_tree=True
        scene.view_settings.exposure=.05
        scene.view_settings.look='AgX - Medium High Contrast'
    edit=bpy.data.scenes.new('EDITAR_Ativos_V04');edit.use_fake_user=True
    for data in photo.CACHE.values():edit.collection.children.link(data['collection'])


def build():
    base=ROOT/CFG['base_blend'];assert Path(bpy.data.filepath).resolve()==base
    base_sha=prior.sha(base);before=prior.geometry();g.C.update({c.name:c for c in bpy.data.collections});g.M.update({m.name:m for m in bpy.data.materials})
    root=bpy.data.collections.new('DESIGN04');g.C[root.name]=root
    for name in ['Sala','Lazer','Quarto','Cozinha']:
        c=bpy.data.collections.new('DESIGN_'+name+'_Objetos');root.children.link(c);g.C[c.name]=c
    light=bpy.data.collections.new('DESIGN_Iluminacao');root.children.link(light);g.C[light.name]=light
    # Conectar temporariamente para avaliar o depsgraph durante a construção.
    bpy.context.scene.collection.children.link(root);bpy.context.view_layer.update()
    materials();set_room('Sala');living();details();lighting();setup_scenes()
    for im in bpy.data.images:
        if im.source=='FILE' and not im.packed_file:im.pack()
    after=prior.geometry();diff=[name for name,digest in before.items() if after.get(name)!=digest];assert not diff,diff
    envelope=audit_envelope.audit(json.loads((ROOT/'config/planta-casa.json').read_text()));assert envelope['all_passed']
    output=ROOT/CFG['output_blend'];assert not output.exists(),output;output.parent.mkdir(parents=True,exist_ok=True)
    bpy.context.window.scene=bpy.data.scenes[CFG['jobs'][0]['scene']];bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(output),compress=True);assert prior.sha(base)==base_sha
    data={'timestamp_utc':stamp(),'base':CFG['base_blend'],'base_sha256':base_sha,'blend_sha256':prior.sha(output),'geometry_before':before,'geometry_differences':diff,'envelope':envelope,'new_assets':NEW_ASSETS,'placements':photo.PLACEMENTS,'packed_images':len([i for i in bpy.data.images if i.packed_file]),'reference_sha256':prior.sha(ROOT/'referencias-estilo-industrial/01-cena-final-menos-warn.png')}
    (REPORT/'modelo.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print('DESIGN_BUILT',len(before),'source geometries preserved',flush=True)


def validate():
    model=json.loads((REPORT/'modelo.json').read_text());assert prior.sha(Path(bpy.data.filepath))==model['blend_sha256'];assert prior.sha(ROOT/CFG['base_blend'])==model['base_sha256']
    now=prior.geometry();diff=[n for n,h in model['geometry_before'].items() if now.get(n)!=h];assert not diff,diff
    missing=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file];assert not missing,missing;assert not [item for item in bpy.data.user_map() if item.library]
    envelope=audit_envelope.audit(json.loads((ROOT/'config/planta-casa.json').read_text()));assert envelope['all_passed']
    data={'timestamp_utc':stamp(),'blend_sha256':model['blend_sha256'],'base_sha256':model['base_sha256'],'geometry_compared':len(model['geometry_before']),'geometry_differences':diff,'missing_images':missing,'packed_images':model['packed_images'],'external_libraries':[],'envelope':envelope,'all_passed':True}
    (REPORT/'validacao.json').write_text(json.dumps(data,indent=2)+'\n');return model


def render(preview,only):
    model=validate();device=photo.gpu();outputs={}
    for job in CFG['jobs']:
        if only and Path(job['file']).stem not in only:continue
        scene=bpy.data.scenes[job['scene']];scene.cycles.samples=CFG['preview_samples'] if preview else CFG['samples'];scene.cycles.adaptive_min_samples=16 if preview else 64;scene.render.resolution_percentage=40 if preview else 100
        file=ROOT/CFG['render_directory']/('previas' if preview else '')/job['file'];file.parent.mkdir(parents=True,exist_ok=True);scene.render.filepath=str(file);start=time.monotonic()
        bpy.ops.render.render(write_still=True,scene=scene.name)
        outputs[str(file.relative_to(ROOT))]={'sha256':prior.sha(file),'bytes':file.stat().st_size,'scene':scene.name,'seconds':round(time.monotonic()-start,3),'samples_max':scene.cycles.samples,'resolution_percentage':scene.render.resolution_percentage};print('DESIGN_RENDERED',scene.name,flush=True)
    validate();data={'timestamp_utc':stamp(),'blend_sha256':model['blend_sha256'],'preview':preview,'device':device,'outputs':outputs}
    (REPORT/('previas.json' if preview else 'renders.json')).write_text(json.dumps(data,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser();p.add_argument('--render-only',action='store_true');p.add_argument('--build-only',action='store_true');p.add_argument('--validate-only',action='store_true');p.add_argument('--preview',action='store_true');p.add_argument('--only',nargs='*');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    REPORT.mkdir(parents=True,exist_ok=True)
    if args.validate_only:validate();print('DESIGN_NATIVE_VALIDATED');return
    if not args.render_only:build()
    if not args.build_only:render(args.preview,args.only)


if __name__=='__main__':main()
