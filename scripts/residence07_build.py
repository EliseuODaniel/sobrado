"""Reconstrói a unidade 07 em Blender, com cenas nativas e render reprodutível.

Geração: run_blender.py --wsl-gpu --background arquivos/versoes-anteriores-2026-11-14/projeto/fontes/mobiliario-industrial.blend --python este.py
Render: run_blender.py --wsl-gpu --background projeto/original/casa-07.blend
        --python este.py -- --render-only [--preview] [--only <id>]
"""
import argparse
import datetime as dt
import json
import math
from pathlib import Path
import sys
import time

import bpy
import bmesh
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
import blender_primitives as g
import residence07_geometry as geo

ROOT=geo.ROOT
CFG=geo.load()
OUT=ROOT/CFG['delivery']['renders']
REPORT=ROOT/CFG['delivery']['reports']
BLEND=ROOT/CFG['delivery']['blend']
COL='R07_Mobiliario_Terreo'


def box(name,loc,size,mat='Branco',bevel=.006,col=None,par=None):
    return g.box('R07 '+name,loc,size,mat,col or COL,bevel,par)


def prism(name,poly,z0,z1,mat,col,**props):
    if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))<0:poly=list(reversed(poly))
    n=len(poly);verts=[(x,y,z) for z in [z0,z1] for x,y in poly]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);g.C[col].objects.link(obj);mesh.materials.append(g.M[mat])
    for k,v in props.items():obj[k]=v
    return obj


def prepare():
    """Reaproveita apenas móveis da biblioteca independente; a arquitetura é criada do zero."""
    keep=set();roots=[]
    for obj in bpy.data.objects:
        if obj.name in ['DESIGN Sofá contemporâneo','DESIGN Mesa de centro'] or (obj.type=='EMPTY' and obj.name.startswith('DESIGN Cadeira jantar ')):
            roots.append(obj);keep.add(obj);keep.update(obj.children_recursive)
    assert len(roots)==6,'Abrir a biblioteca de mobiliário para reaproveitar os seis móveis.'
    for scene in list(bpy.data.scenes)[1:]:bpy.data.scenes.remove(scene)
    scene=bpy.context.scene;scene.name='R07_BASE'
    for obj in list(bpy.data.objects):
        if obj not in keep:bpy.data.objects.remove(obj,do_unlink=True)
    temp=bpy.data.collections.new('R07_REUSO');scene.collection.children.link(temp)
    for obj in keep:temp.objects.link(obj)
    for collection in list(bpy.data.collections):
        if collection!=temp:bpy.data.collections.remove(collection)
    g.C.clear();g.M.clear();g.LEAF_MESHES.clear();g.RNG.seed(707)
    names=['Paredes_Terreo','Paredes_Superior','Corte_Terreo','Corte_Superior','Piso_Terreo','Piso_Superior',
           'Teto_Terreo','Teto_Superior','Escada','Mobiliario_Terreo','Mobiliario_Superior','Esquadrias_Terreo',
           'Esquadrias_Superior','Cobertura','Contexto','Proposta_Fundos','Iluminacao','Cameras','Diagnostico','Superior_Explodido']
    for name in names:
        col=bpy.data.collections.new('R07_'+name);scene.collection.children.link(col);g.C[col.name]=col
    # Helpers compartilhados usam estes nomes de coleção.
    g.C['Iluminacao']=g.C['R07_Iluminacao']
    chairs=[]
    for obj in keep:
        temp.objects.unlink(obj);g.C['R07_Mobiliario_Terreo'].objects.link(obj)
        obj.hide_render=False;obj.hide_viewport=False;obj.hide_set(False)
        obj['R07_reused_furniture']=True
    for obj in roots:
        old=obj.name;obj.name='R07 Reuso '+old
        if 'Sofá' in old:obj.location=(.64,1.65,0)
        elif 'Mesa de centro' in old:obj.location=(1.85,1.7,0);obj.scale*=.84
        else:chairs.append(obj)
    for obj,loc in zip(sorted(chairs,key=lambda o:o.name),[(.88,3.85,0),(.88,4.65,0),(2.35,3.85,0),(2.35,4.65,0)]):obj.location=loc
    bpy.data.collections.remove(temp)
    return len(keep)


def materials():
    for name,color,rough,metal,trans in [
        ('Branco',(.73,.72,.67),.68,0,0),('Areia',(.53,.48,.38),.75,0,0),
        ('Preto',(.012,.018,.018),.32,.7,0),('Pedra',(.075,.088,.08),.24,0,0),
        ('Louca',(.86,.88,.82),.20,0,0),('Vidro',(.90,.96,.94),.07,0,1),
        ('Espelho',(.92,.95,.92),.015,1,0),('Azulejo',(.35,.43,.37),.24,0,0),
        ('Argila',(.23,.115,.063),.88,0,0),('Terra',(.04,.025,.012),.94,0,0),
        ('Ceramica preta',(.018,.025,.02),.40,0,0),('Tecido',(.52,.50,.42),.89,0,0),
        ('Tecido verde',(.12,.19,.14),.90,0,0),('Papel',(.8,.72,.56),.85,0,0),
        ('Asfalto',(.11,.13,.12),.90,0,0),('Tela',(.009,.014,.02),.18,0,0)]:g.basic(name,color,rough,metal,trans)
    g.textured('Madeira',[(.16,.065,.021),(.38,.19,.065),(.23,.10,.028)],'wood',.42,.001)
    original=bpy.data.materials.get('DESIGN Carvalho mel')
    if original:
        wood=original.copy();wood.name='R07 Carvalho mel';g.M['Madeira']=wood
        nodes=wood.node_tree.nodes;links=wood.node_tree.links;bs=nodes.get('Principled BSDF')
        coord=nodes.new('ShaderNodeTexCoord');mapping=nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(3,3,1.5)
        links.new(coord.outputs['Generated'],mapping.inputs[0])
        for node in nodes:
            if node.type=='TEX_IMAGE':
                node.projection='BOX';node.projection_blend=.20;links.new(mapping.outputs[0],node.inputs['Vector'])
        if bs.inputs['Base Color'].links:
            source=bs.inputs['Base Color'].links[0].from_socket;mix=nodes.new('ShaderNodeMixRGB');mix.inputs[0].default_value=.48;mix.inputs[2].default_value=(.27,.14,.055,1)
            links.new(source,mix.inputs[1]);links.new(mix.outputs[0],bs.inputs['Base Color'])
    g.textured('Concreto',[(.31,.33,.30),(.43,.44,.39)],'plaster',.78,.0008)
    g.textured('Piso',[(.48,.45,.38),(.53,.49,.43)],'plaster',.34,.0004)
    g.textured('Grama',[(.10,.16,.04),(.20,.28,.075)],'plaster',.92,.004)
    for i,color in enumerate([(.045,.12,.025),(.10,.18,.035),(.15,.23,.06),(.05,.10,.018)]):g.basic(f'Folha {i}',color,.53)
    g.basic('Luz quente',(1,.60,.28),emission=4)
    g.basic('Estrutura neutra',(.56,.59,.55),.76)


def architecture():
    height=CFG['dimensions']['clear_height']
    for wall in CFG['walls']:
        level=wall['level'];base=CFG['levels'][level]['z'];suffix='Terreo' if level==0 else 'Superior'
        col='R07_Paredes_'+suffix;cutcol='R07_Corte_'+suffix
        for i,(a,b,z0,z1) in enumerate(geo.wall_cells(wall,height)):
            poly=geo.wall_polygon(wall,a,b)
            prism('R07 Parede '+wall['id']+f' {i:02}',poly,base+z0,base+z1,'Branco',col,
                  wall_id=wall['id'],level=level,local_z0=z0,local_z1=z1,start=a,end=b)
            if z0<1.15:
                prism('R07 Corte '+wall['id']+f' {i:02}',poly,base+z0,base+min(z1,1.15),'Branco',cutcol,wall_id=wall['id'])
        for op in wall.get('openings',[]):opening(wall,op,base,'R07_Esquadrias_'+suffix)
    for level in CFG['levels']:
        suffix='Terreo' if level['z']==0 else 'Superior';base=level['z']
        for i,poly in enumerate(level['slabs']):
            prism('R07 Laje '+suffix+f' {i:02}',poly,base-.15,base,'Piso' if suffix=='Terreo' else 'Madeira','R07_Piso_'+suffix,level=0 if suffix=='Terreo' else 1,slab=True)
        # O teto do térreo segue as células da laje do superior: mantém o vão real da escada.
        ceiling=CFG['levels'][1]['slabs'] if suffix=='Terreo' else [level['outline']]
        for i,poly in enumerate(ceiling):
            prism('R07 Teto '+suffix+f' {i:02}',poly,base+2.55,base+2.70,'Branco','R07_Teto_'+suffix)
    # Revestimentos no piso com junta real, sem alterar o contorno das lajes.
    for room in CFG['rooms']:
        if room['id'] in ['cozinha','lavabo','banheiro-suite','banheiro-social','sacada']:
            lv=room['level'];col='R07_Mobiliario_'+('Terreo' if lv==0 else 'Superior')
            prism('R07 Piso ambiente '+room['id'],room['polygon'],CFG['levels'][lv]['z']+.001,CFG['levels'][lv]['z']+.009,'Concreto',col)
    # Somente o térreo possui pilares sob a projeção frontal do piso superior.
    for x in [.075,6.30]:box('Pilar fachada',(x,-1.125,1.275),(.15,.15,2.55),'Areia',col='R07_Paredes_Terreo')
    # Viga frontal documentada na elevação.
    box('Viga sobre garagem',(3.20,-1.125,2.47),(6.25,.15,.16),'Branco',col='R07_Paredes_Terreo')


def opening(wall,op,base,col):
    start=op['start'];width=op['width'];sill=op.get('sill',0);height=op['height']
    center=geo.point(wall,start+width/2);theta=math.atan2(wall['b'][1]-wall['a'][1],wall['b'][0]-wall['a'][0])
    root=g.parent('R07 Vao '+op['id'],col,(center[0],center[1],base+sill),opening_id=op['id'],width_m=width,height_m=height,sill_m=sill)
    root.rotation_euler.z=theta
    def part(name,loc,size,mat):return box(op['id']+' '+name,loc,size,mat,.004,col,root)
    frame='Madeira' if op['kind']=='door' else 'Preto'
    for x in [-width/2,width/2]:part('montante',(x,0,height/2),(.035,.06,height+.03),frame)
    part('verga',(0,0,height),(width,.06,.035),frame)
    if op['kind']=='door':
        # Folha entreaberta: pivô editável, sem bloquear a leitura dos interiores.
        hinge=g.parent('R07 Folha '+op['id'],col,(-width/2,wall['t']/2+.025,0));hinge.parent=root
        hinge.rotation_euler.z=math.radians(170)
        box('Porta '+op['id'],(width/2,0,height/2),(width-.03,.035,height-.025),'Madeira',.012,col,hinge)
        g.rod('R07 Maçaneta '+op['id'],(width-.12,-.055,1.03),(width-.035,-.055,1.03),.008,'Preto',col,hinge)
    else:
        part('peitoril',(0,0,0),(width,.09,.035),'Pedra')
        part('travessa',(0,0,height),(width,.06,.035),'Preto')
        for x in [-width/4,width/4]:part('vidro',(x,.012 if x>0 else -.012,height/2),(width/2-.035,.012,height-.05),'Vidro')
        part('central',(0,0,height/2),(.025,.065,height),'Preto')
    return root


def stairs():
    col='R07_Escada';s=CFG['stair']
    for i,poly in enumerate(geo.stair_polygons(CFG)):
        z=(i+1)*s['rise']
        # Degraus estruturais em placas, deixando o lavabo livre sob o lance alto.
        prism(f'R07 Degrau {i+1:02}',poly,z-.13,z,'Madeira',col,stair_index=i+1,tread_top=z)
    # Nervuras de apoio sob os lances retos; ficam fora do vão útil do lavabo.
    for y in [s['top_y']-.045,s['bottom_y']+.045]:
        ascending=y>3
        a=(s['start_x'],y,.03 if ascending else 2.54);b=(s['turn_x'],y,.74 if ascending else 1.86)
        g.rod('R07 Longarina',a,b,.045,'Preto',col)
    # Guarda-corpo superior do lado do hall, sem laje atravessando o vão.
    for y in [3.27,3.66,4.10]:
        g.rod('R07 Montante guarda-corpo',(4.60,y,2.7),(4.60,y,3.60),.012,'Preto',col)
    g.rod('R07 Corrimao hall',(4.60,3.25,3.60),(4.60,4.15,3.60),.019,'Preto',col)


def counter(name,x,y,width,depth,base=0,doors=3,col=None):
    col=col or COL
    box(name+' corpo',(x,y,base+.43),(width,depth,.80),'Madeira',col=col)
    box(name+' rodape',(x,y,base+.065),(width-.07,depth-.07,.13),'Preto',col=col)
    box(name+' pedra',(x,y,base+.86),(width+.025,depth+.035,.045),'Pedra',.012,col)
    for i in range(doors):
        xx=x-width/2+(i+.5)*width/doors
        box(name+' porta',(xx,y-depth/2-.008,base+.46),(width/doors-.015,.025,.70),'Madeira',.004,col)
        box(name+' puxador',(xx,y-depth/2-.03,base+.74),(.15,.018,.014),'Preto',.003,col)


def living():
    global COL
    COL='R07_Mobiliario_Terreo'
    box('Parede cimento estar',(0.157,2.85,1.275),(.012,5.40,2.55),'Concreto',.001)
    box('Tapete sala',(1.60,1.70,.016),(2.10,2.65,.025),'Tecido',.025)
    # Painel acompanha o retorno da garagem, preservando a entrada diagonal.
    box('Painel TV',(3.225,1.37,1.30),(.045,1.10,2.42),'Madeira',.012)
    box('Televisao',(3.18,1.37,1.45),(.035,.98,.59),'Tela',.01)
    box('Rack TV',(3.03,1.38,.40),(.34,1.12,.25),'Madeira',.025)
    for y in [1.0,1.73]:box('Rack friso',(2.85,y,.4),(.015,.012,.20),'Preto',.002)
    # Mesa e aparador deixam o corredor de acesso à cozinha livre.
    box('Mesa jantar tampo',(1.62,4.25,.76),(.82,1.48,.055),'Madeira',.035)
    for y in [3.68,4.82]:
        box('Mesa jantar pe',(1.62,y,.39),(.065,.065,.74),'Preto',.01)
        box('Mesa jantar base',(1.62,y,.055),(.68,.055,.035),'Preto')
    box('Aparador',(0.40,4.17,.85),(.45,1.45,.045),'Madeira',.01)
    for y in [3.57,4.77]:box('Aparador perna',(0.40,y,.425),(.03,.03,.85),'Preto')
    # Quadro, espelho e trilhos seguem a linguagem industrial já aprovada no projeto.
    box('Quadro estar',(0.165,1.72,1.62),(.025,1.35,.63),'Preto')
    box('Arte abstrata',(0.184,1.72,1.62),(.012,1.26,.55),'Areia')
    for i in range(7):box('Arte linha',(0.193,1.20+i*.16,1.63),(.008,.04,.35 if i%2 else .2),'Argila',.002)
    box('Espelho jantar',(0.168,4.16,1.58),(.025,1.20,.92),'Espelho',.02)
    g.plant('R07 Vegetacao estar',(0.57,3.12,0),1.3,COL)
    g.plant('R07 Arranjo jantar',(1.62,4.25,.79),.45,COL)
    for x in [1.2,1.7,2.05]:
        g.cylinder('R07 Ceramica mesa',(x,4.45,.82),.07,.045,'Louca',COL)
    # Juntas do piso na sala e cozinha são físicas e ficam alinhadas aos eixos.
    for y in [i*.6 for i in range(10)]:g.rod('R07 Junta piso',(0.15,y,.001),(3.25,y,.001),.0008,'Areia',COL)


def kitchen():
    global COL
    COL='R07_Mobiliario_Terreo'
    counter('Bancada janela',4.84,6.73,2.76,.60,doors=5)
    # Braço direito do L, com frentes voltadas para o centro da cozinha.
    root=g.parent('R07 Bancada L girar',COL,(5.94,5.75,0));root.rotation_euler.z=-math.pi/2
    # Criar elementos em coordenadas locais para as portas não ficarem na parede.
    before=set(bpy.data.objects);counter('Bancada lateral',0,0,1.30,.60,doors=2)
    for obj in set(bpy.data.objects)-before:obj.parent=root
    # Cuba sobreposta, torneira e metais.
    box('Cuba cozinha borda',(4.90,6.73,.902),(.67,.43,.025),'Preto',.06)
    box('Cuba cozinha interior',(4.90,6.73,.910),(.55,.32,.016),'Pedra',.065)
    g.curve('R07 Torneira cozinha',[(5.1,6.97,.90),(5.1,6.97,1.27),(5.1,6.80,1.32),(5.1,6.72,1.19)],.012,'Preto',COL)
    box('Cooktop',(5.94,5.65,.902),(.49,.60,.02),'Preto',.015)
    for x in [5.80,6.08]:
        for y in [5.48,5.81]:g.cylinder('R07 Boca cooktop',(x,y,.920),.065,.015,'Pedra',COL)
    box('Forno',(5.60,5.64,.48),(.03,.56,.44),'Preto',.015)
    box('Forno vidro',(5.58,5.64,.48),(.012,.45,.28),'Tela',.008)
    g.rod('R07 Forno puxador',(5.55,5.40,.65),(5.55,5.88,.65),.012,'Preto',COL)
    box('Geladeira',(5.91,4.73,.98),(.65,.72,1.96),'Concreto',.045)
    box('Geladeira divisao',(5.57,4.73,.65),(.018,.70,.02),'Preto')
    for z in [.95,1.45]:g.rod('R07 Geladeira puxador',(5.55,4.46,z-.13),(5.55,4.46,z+.13),.012,'Preto',COL)
    # Frontão e prateleiras com juntas de azulejo.
    box('Frontao janela',(4.85,7.035,1.0),(2.76,.02,.20),'Azulejo')
    box('Prateleira cozinha',(3.75,6.73,1.92),(.59,.45,.045),'Madeira')
    for x in [3.57,3.77,3.98]:
        g.cylinder('R07 Pote mantimentos',(x,6.75,2.03),.065,.19,'Vidro',COL)
        g.cylinder('R07 Tampa pote',(x,6.75,2.13),.067,.025,'Madeira',COL)
    g.plant('R07 Tempero cozinha',(3.72,6.62,.89),.5,COL)


def toilet(x,y,z,col,angle=0):
    root=g.parent('R07 Vaso sanitario',col,(x,y,z));root.rotation_euler.z=angle
    g.sphere('R07 Louca base',(0,0,.20),(.19,.26,.20),'Louca',col,root)
    g.sphere('R07 Louca assento',(0,-.04,.40),(.20,.285,.055),'Louca',col,root)
    g.sphere('R07 Louca abertura',(0,-.06,.445),(.125,.19,.006),'Pedra',col,root)
    box('Caixa acoplada',(0,.20,.60),(.36,.15,.40),'Louca',.04,col,root)
    return root


def vanity(x,y,z,width,col,angle=0):
    root=g.parent('R07 Lavatorio',col,(x,y,z));root.rotation_euler.z=angle
    box('Gabinete banho',(0,0,.53),(width,.43,.43),'Madeira',.01,col,root)
    box('Bancada banho',(0,0,.77),(width+.025,.45,.035),'Pedra',.012,col,root)
    g.sphere('R07 Cuba banho',(0,0,.81),(.22,.15,.06),'Louca',col,root)
    g.curve('R07 Torneira banho',[(.20,.12,.79),(.20,.12,1.02),(.12,.12,1.05),(.10,.06,1.02)],.009,'Preto',col,root)
    box('Espelho banho',(0,.235,1.45),(width,.015,.80),'Espelho',.025,col,root)


def bathrooms():
    col='R07_Mobiliario_Terreo'
    toilet(5.00,2.74,0,col)
    vanity(4.35,2.88,0,.65,col)
    # Painel sob o retorno alto da escada, sem atravessar degraus nem caixa da janela.
    box('Revestimento lavabo',(4.80,3.095,.90),(2.80,.012,1.70),'Concreto',col=col)
    col='R07_Mobiliario_Superior'
    for x in [.90,2.55]:
        toilet(x-.38,4.82,2.7,col,math.pi/2)
        vanity(x-.39,3.95,2.7,.67,col,math.pi/2)
        # Área de banho na extremidade posterior, conforme os complementares HID04.
        box('Base box',(x,5.92,2.72),(1.40,.80,.035),'Concreto',col=col)
        box('Vidro box',(x,5.49,3.73),(1.42,.012,2.02),'Vidro',.001,col)
        g.rod('R07 Trilho box',(x-.71,5.49,4.75),(x+.71,5.49,4.75),.012,'Preto',col)
        g.curve('R07 Chuveiro',[(x-.65,6.1,4.5),(x-.50,6.1,4.65),(x-.31,6.1,4.65)],.012,'Preto',col)
        g.cylinder('R07 Ducha',(x-.28,6.1,4.63),.095,.025,'Preto',col)
        # Não cobrir a janela: faixa superior termina no peitoril e laterais livres.
        box('Faixa azulejo inferior',(x,6.325,3.45),(1.42,.012,1.45),'Azulejo',.001,col)
        for z in [2.95,3.25,3.55,3.85,4.15]:g.rod('R07 Junta azulejo',(x-.69,6.31,z),(x+.69,6.31,z),.0008,'Areia',col)


def bed(name,x,y,z,width,length,col,angle=0):
    root=g.parent('R07 '+name,col,(x,y,z));root.rotation_euler.z=angle
    box(name+' estrado',(0,0,.24),(width,length,.28),'Madeira',.04,col,root)
    box(name+' colchao',(0,0,.46),(width-.025,length-.02,.24),'Tecido',.09,col,root)
    box(name+' cabeceira',(0,length/2+.02,.72),(width+.12,.09,1.25),'Tecido verde',.06,col,root)
    # Colcha com pregas em malha, nativa e com UV.
    verts=[];faces=[];nx=32;ny=42
    for i in range(nx+1):
        u=i/nx;along=(u-.5)*(width+.45);xx=max(-width/2-.015,min(width/2+.015,along))
        for j in range(ny+1):
            v=j/ny;yy=-length/2-.05+v*length*.77
            drop=max(0,abs(along)-width/2)*1.1+max(0,-yy-length/2)*2.5
            zz=.615-drop+.002*math.sin(u*56+v*9)+.001*math.sin(v*64)
            verts.append((xx,yy,zz))
    for i in range(nx):
        for j in range(ny):a=i*(ny+1)+j;faces.append((a,a+ny+1,a+ny+2,a+1))
    mesh=bpy.data.meshes.new(name+' colcha');mesh.from_pydata(verts,[],faces);mesh.materials.append(g.M['Tecido verde']);mesh.update()
    ob=bpy.data.objects.new('R07 '+name+' colcha',mesh);g.C[col].objects.link(ob);ob.parent=root
    for poly in mesh.polygons:poly.use_smooth=True
    for xx in ([-width*.24,width*.24] if width>1.2 else [0]):box(name+' travesseiro',(xx,length*.32,.65),(width*.43,.42,.14),'Tecido',.065,col,root)
    return root


def bedrooms():
    global COL
    COL='R07_Mobiliario_Superior'
    bed('Cama suite',1.60,1.23,2.7,1.58,1.98,COL)
    for x in [.43,2.77]:
        box('Criado suite',(x,2.05,3.0),(.45,.44,.43),'Madeira',.025)
        g.cylinder('R07 Abajur base',(x,2.05,3.25),.09,.025,'Preto',COL)
        g.cylinder('R07 Abajur haste',(x,2.05,3.37),.01,.25,'Preto',COL)
        g.cylinder('R07 Abajur cupula',(x,2.05,3.54),.13,.18,'Tecido',COL)
    # Roupeiro na parede oposta à cabeceira, sem interceptar a porta do banheiro.
    box('Roupeiro suite',(0.49,.35,3.78),(.63,1.35,2.16),'Madeira',.02)
    for y in [-.05,.40,.85]:box('Friso roupeiro suite',(.814,y,3.78),(.008,.014,2.05),'Preto',.002)
    bed('Cama quarto frente',5.63,.05,2.7,.95,1.98,COL)
    box('Roupeiro quarto frente',(3.78,-.35,3.80),(.62,1.05,2.20),'Areia',.025)
    box('Escrivaninha quarto frente',(4.20,1.25,3.45),(1.05,.52,.04),'Madeira',.015)
    for x in [3.75,4.63]:box('Pe escrivaninha',(x,1.25,3.08),(.035,.44,.72),'Preto')
    # Beliche de dimensões próprias; não esticar o móvel para preencher o novo quarto.
    for x in [5.12,6.08]:
        for y in [4.68,6.73]:box('Montante beliche',(x,y,3.74),(.055,.055,2.08),'Preto')
    for z in [3.08,4.31]:
        box('Estrado beliche',(5.60,5.70,z),(.96,2.05,.10),'Madeira',.012)
        box('Colchao beliche',(5.60,5.70,z+.13),(.90,1.98,.20),'Tecido',.07)
        box('Manta beliche',(5.60,5.30,z+.25),(.91,1.15,.02),'Tecido verde',.02)
        box('Travesseiro beliche',(5.60,6.37,z+.28),(.65,.40,.13),'Tecido',.06)
    for y in [4.72,6.68]:g.rod('R07 Guarda beliche',(5.10,y,4.75),(6.10,y,4.75),.018,'Preto',COL)
    for z in [2.90,3.18,3.46,3.74,4.02,4.30]:g.rod('R07 Escada beliche',(5.12,4.69,z),(5.50,4.69,z),.014,'Preto',COL)
    box('Bancada escritorio',(3.76,5.98,3.44),(.57,1.65,.055),'Madeira',.02)
    box('Monitor',(3.67,6.03,3.85),(.055,.59,.36),'Preto',.012)
    box('Monitor tela',(3.705,6.03,3.85),(.01,.54,.31),'Tela',.005)
    box('Teclado',(3.90,6.04,3.485),(.16,.44,.015),'Preto')
    box('Cadeira escritorio assento',(4.35,6.05,3.16),(.48,.48,.10),'Tecido verde',.06)
    box('Cadeira escritorio encosto',(4.60,6.05,3.52),(.08,.47,.56),'Tecido verde',.06)
    for y in [5.85,6.25]:
        for x in [4.18,4.52]:box('Pe cadeira escritorio',(x,y,2.92),(.022,.022,.44),'Preto')
    # Nichos e livros.
    for z in [4.12,4.50]:
        box('Prateleira escritorio',(3.61,5.93,z),(.30,1.55,.035),'Madeira')
        for i in range(9):box('Livro escritorio',(3.59,5.40+i*.09,z+.14),(.17,.045,.23 if i%2 else .26),'Papel' if i%3 else 'Tecido verde',.002)
    g.plant('R07 Planta escritorio',(3.65,6.55,3.48),.46,COL)


def roof_and_context():
    col='R07_Cobertura';x0=.02;x1=6.35;front=-1.35;back=7.35;ridge=3.0
    # Duas águas longitudinais, conforme corte FF; paredes corta-fogo nas laterais.
    for name,ya,yb,za,zb in [('frontal',front,ridge,5.4,9.4),('posterior',ridge,back,9.4,5.4)]:
        verts=[(x0,ya,za),(x1,ya,za),(x1,yb,zb),(x0,yb,zb)]
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],[(0,1,2,3)]);mesh.materials.append(g.M['Argila']);mesh.update()
        ob=bpy.data.objects.new('R07 Telhado '+name,mesh);g.C[col].objects.link(ob);ob.modifiers.new('Espessura telhado','SOLIDIFY').thickness=.08
        for i in range(41):
            x=.10+i*.153
            g.rod('R07 Capa telha',(x,ya,za+.045),(x,yb,zb+.045),.045,'Argila',col)
        for j in range(1,16):
            t=j/16;y=ya+(yb-ya)*t;z=za+(zb-za)*t
            g.rod('R07 Fiada telhado',(.02,y,z+.005),(6.35,y,z+.005),.012,'Argila',col)
    for x in [.075,6.30]:
        poly=[(front,5.38),(ridge,9.50),(back,5.38)]
        verts=[(xx,y,z) for xx in [x-.065,x+.065] for y,z in poly]
        mesh=bpy.data.meshes.new('Corta fogo');mesh.from_pydata(verts,[],[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]);mesh.materials.append(g.M['Branco']);mesh.update()
        ob=bpy.data.objects.new('R07 Parede corta-fogo',mesh);g.C[col].objects.link(ob)
    col='R07_Contexto'
    box('Terreno contexto',(3.175,3.8,-.23),(6.35,14.4,.16),'Concreto',col=col,bevel=0)
    box('Jardim frontal',(1.60,-2.14,-.06),(3.10,1.80,.05),'Grama',col=col)
    box('Acesso garagem',(4.78,-1.9,-.055),(3.05,3.80,.06),'Concreto',col=col)
    box('Quintal posterior',(3.175,8.90,-.065),(6.35,3.35,.06),'Grama',col=col)
    box('Rua interna',(3.175,-4.3,-.15),(18,2.8,.12),'Asfalto',col=col)
    box('Plano cenario',(3,3,-.42),(200,200,.10),'Areia',col=col)
    for y in [7.5,8.25,9.0]:box('Pisante quintal',(3.25,y,-.01),(.70,.50,.04),'Concreto',col=col)
    # Limites do contexto são ilustrativos; não presumir demarcação exata do lote.
    for x in [.28,6.05]:g.plant('R07 Jardim contexto',(x,8.7,0),1.4,col)


def annex():
    global COL
    COL='R07_Proposta_Fundos'
    box('Piso proposta quintal',(3.20,8.85,-.025),(6.10,3.10,.045),'Piso',bevel=0)
    box('Muro proposta fundos',(3.18,10.35,1.25),(6.35,.15,2.50),'Concreto')
    box('Divisao lazer lavanderia',(3.38,9.55,1.30),(.10,1.60,2.60),'Branco')
    counter('Bancada gourmet',1.64,10.0,2.90,.58,doors=5)
    box('Churrasqueira',(0.75,10.0,1.52),(.85,.58,.93),'Concreto',.02)
    box('Boca churrasqueira',(0.75,9.70,1.45),(.65,.025,.48),'Preto',.005)
    for x in [.50,.65,.80,.95]:g.rod('R07 Grelha',(x,9.66,1.27),(x,10.0,1.27),.006,'Preto',COL)
    box('Bar tampo',(1.78,8.85,1.04),(1.95,.52,.06),'Madeira',.025)
    for x in [1.0,1.75,2.5]:
        g.cylinder('R07 Banco bar',(x,8.31,.75),.20,.08,'Madeira',COL)
        for dx in [-.12,.12]:
            for dy in [-.12,.12]:g.rod('R07 Banco pe',(x+dx,8.31+dy,.03),(x+dx*.8,8.31+dy*.8,.72),.012,'Preto',COL)
    counter('Lavanderia bancada',4.85,10.0,2.50,.60,doors=3)
    box('Lavadora',(5.65,9.0,.45),(.65,.62,.90),'Louca',.035)
    g.cylinder('R07 Lavadora aro',(5.65,8.68,.46),.22,.028,'Preto',COL,rotation=(math.pi/2,0,0))
    g.cylinder('R07 Lavadora vidro',(5.65,8.655,.46),.17,.025,'Vidro',COL,rotation=(math.pi/2,0,0))
    g.sphere('R07 Tanque lavanderia',(4.40,10.0,.91),(.30,.22,.07),'Louca',COL)
    for x in [.25,3.25,6.15]:box('Pilar pergolado',(x,9.40,1.4),(.07,.07,2.80),'Preto')
    for x in [.25,.85,1.45,2.05,2.65,3.25,3.85,4.45,5.05,5.65,6.15]:box('Viga pergolado',(x,9.0,2.85),(.05,2.80,.08),'Madeira')
    box('Cobertura pergolado',(3.2,9.0,2.92),(6.1,2.8,.012),'Vidro',.001)
    g.plant('R07 Planta lazer',(.35,8.10,0),1.1,COL)
    g.plant('R07 Planta lavanderia',(4.0,9.95,.89),.65,COL)


def lighting():
    # Um mundo e uma iluminação compartilhados, sem mudar decoração por câmera.
    world=bpy.data.worlds.new('R07 Ceu diurno');world.use_nodes=True
    nodes=world.node_tree.nodes;links=world.node_tree.links;bg=nodes.get('Background')
    sky=nodes.new('ShaderNodeTexSky');sky.sky_type='MULTIPLE_SCATTERING';sky.sun_elevation=math.radians(40);sky.sun_rotation=math.radians(145);sky.sun_intensity=.55
    links.new(sky.outputs['Color'],bg.inputs['Color']);bg.inputs['Strength'].default_value=.22
    # Fundo claro nas vistas de planta; mantém o céu físico para a iluminação.
    camera_bg=nodes.new('ShaderNodeBackground');camera_bg.inputs['Color'].default_value=(.73,.70,.64,1);camera_bg.inputs['Strength'].default_value=.8
    path=nodes.new('ShaderNodeLightPath');mix=nodes.new('ShaderNodeMixShader')
    links.new(path.outputs['Is Camera Ray'],mix.inputs[0]);links.new(bg.outputs[0],mix.inputs[1]);links.new(camera_bg.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],nodes.get('World Output').inputs['Surface'])
    for scene in bpy.data.scenes:scene.world=world
    data=bpy.data.lights.new('R07 Sol','SUN');data.energy=1.5;data.color=(1,.88,.70);data.angle=.12
    sun=bpy.data.objects.new('R07 Sol',data);g.C['R07_Iluminacao'].objects.link(sun);sun.rotation_euler=(.50,-.45,-.6)
    for name,loc,power,size in [
        ('Estar',(1.7,1.5,2.45),90,1.5),('Jantar',(1.6,4.1,2.40),75,1.0),
        ('Cozinha',(4.8,5.75,2.45),85,1.3),('Lavabo',(4.6,2.6,1.65),18,.35),
        ('Suite',(1.7,1.3,5.15),75,1.3),('Quarto frente',(4.8,.45,5.15),65,1.1),
        ('Quarto fundos',(4.8,5.7,5.15),65,1.0),('Banho suite',(.9,4.6,5.10),40,.7),
        ('Banho social',(2.55,4.6,5.10),40,.7),('Fundos',(2,8.9,2.65),90,1.5),('Lavanderia',(4.8,9.0,2.65),75,1.0)]:
        g.light('R07 Luz '+name,loc,power,(1,.82,.60),size=size)
    for y in [1.10,2.25,3.7,4.6]:
        box('Trilho teto',(1.70,y,2.53),(.85,.045,.035),'Preto',col='R07_Mobiliario_Terreo')
        for x in [1.40,2.00]:g.cylinder('R07 Spot',(x,y,2.46),.04,.12,'Preto','R07_Mobiliario_Terreo')
    # Pendente de jantar, com cabo e lâmpada visíveis.
    g.rod('R07 Cabo pendente',(1.62,4.25,2.55),(1.62,4.25,1.98),.005,'Preto','R07_Mobiliario_Terreo')
    g.lathe('R07 Pendente jantar',[(.06,0),(.09,.03),(.19,.09),(.22,.13)],(1.62,4.25,1.84),'Preto','R07_Mobiliario_Terreo')
    g.cylinder('R07 Lampada pendente',(1.62,4.25,1.84),.07,.012,'Luz quente','R07_Mobiliario_Terreo')
    return world


def scene_collections(mode):
    ground=['Paredes_Terreo','Piso_Terreo','Esquadrias_Terreo','Mobiliario_Terreo','Escada']
    upper=['Paredes_Superior','Piso_Superior','Esquadrias_Superior','Mobiliario_Superior','Escada']
    if mode=='structure0':names=['Corte_Terreo','Piso_Terreo','Escada']
    elif mode=='structure1':names=['Corte_Superior','Piso_Superior','Escada']
    elif mode=='structure-full':names=['Paredes_Terreo','Paredes_Superior','Piso_Terreo','Piso_Superior','Escada']
    elif mode=='structure-stack':names=['Corte_Terreo','Piso_Terreo','Escada','Superior_Explodido']
    elif mode=='lavabo-plan':names=['Corte_Terreo','Piso_Terreo','Mobiliario_Terreo']
    elif mode in ['plan0','iso0']:names=['Corte_Terreo','Piso_Terreo','Mobiliario_Terreo','Escada']
    elif mode in ['plan1','iso1']:names=['Corte_Superior','Piso_Superior','Mobiliario_Superior','Escada']
    elif mode in ['interior0','lavabo']:names=ground+['Teto_Terreo','Contexto']
    elif mode=='interior1':names=upper+['Teto_Superior','Contexto']
    elif mode=='annex':names=ground+upper+['Teto_Superior','Cobertura','Contexto','Proposta_Fundos']
    else:names=ground+upper+['Teto_Superior','Cobertura','Contexto']
    return ['R07_'+n for n in dict.fromkeys(names)]+['R07_Iluminacao','R07_Cameras']


def setup_scenes(world):
    bpy.context.view_layer.update()
    for view in CFG['views']:
        scene=bpy.data.scenes.new('R07_'+view['id']);scene.world=world
        scene.unit_settings.system='METRIC';scene.unit_settings.length_unit='METERS'
        for col in scene_collections(view['mode']):scene.collection.children.link(g.C[col])
        camdata=bpy.data.cameras.new('R07 Camera '+view['id']);cam=bpy.data.objects.new(camdata.name,camdata);g.C['R07_Cameras'].objects.link(cam)
        cam.location=view['pos'];cam.rotation_euler=(Vector(view['target'])-cam.location).to_track_quat('-Z','Y').to_euler()
        if view['mode'].startswith('plan') or view['id'] in ['cobertura','lavabo-planta']:cam.rotation_euler=(0,0,0)
        if 'ortho' in view:camdata.type='ORTHO';camdata.ortho_scale=view['ortho']
        else:camdata.lens=view.get('lens',22)
        camdata.clip_start=.04;camdata.clip_end=250;scene.camera=cam
        scene.render.engine='CYCLES';scene.cycles.samples=CFG['delivery']['samples'];scene.cycles.use_denoising=True
        if view['mode'].startswith('structure'):
            scene.view_layers[0].material_override=g.M['Estrutura neutra']
            scene['R07_structural_scope']='Paredes, lajes, escada e apoios representados na arquitetura; sem cálculo ou armaduras.'
            scene['R07_section_height_m']=1.15 if view['mode']!='structure-full' else 2.55
            if view['mode']=='structure-stack':scene['R07_exploded_upper_offset_m']=4.0
        scene.cycles.adaptive_threshold=.025;scene.cycles.use_light_tree=True
        scene.render.resolution_x,scene.render.resolution_y=CFG['delivery']['resolution'];scene.render.resolution_percentage=100
        scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
        scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
        scene.view_settings.exposure=-1.1 if view['mode'] in ['exterior','plan0','plan1','iso0','iso1','lavabo-plan'] or view['mode'].startswith('structure') else .1
        scene.render.film_transparent=False;scene.render.filepath=str(geo.artifact_path(view['id']))
        scene['R07_view_id']=view['id'];scene['R07_geometry_sha256']=geo.sha(geo.CONFIG);scene['R07_mode']=view['mode']
    base=bpy.data.scenes.get('R07_BASE')
    if base:bpy.data.scenes.remove(base)
    bpy.context.window.scene=bpy.data.scenes['R07_sala-integrada']


def configure_gpu(cpu=False):
    prefs=bpy.context.preferences.addons['cycles'].preferences
    if not cpu:
        prefs.compute_device_type='CUDA';prefs.get_devices()
        gpu=[d for d in prefs.devices if d.type=='CUDA']
        if not gpu:raise RuntimeError('CUDA não disponível; execute com --cpu para renderizar em CPU.')
        for device in prefs.devices:device.use=device.type=='CUDA'
    for scene in bpy.data.scenes:scene.cycles.device='CPU' if cpu else 'GPU'
    return 'CPU' if cpu else 'CUDA'


def build():
    if BLEND.exists():raise FileExistsError(f'Destino já existe: {BLEND}. Gere uma nova versão para preservar edições.')
    OUT.mkdir(parents=True,exist_ok=True);REPORT.mkdir(parents=True,exist_ok=True);BLEND.parent.mkdir(parents=True,exist_ok=True)
    reused=prepare();print('R07_REUSE_OK',reused,flush=True)
    materials();architecture();stairs();print('R07_ARCHITECTURE_OK',flush=True)
    living();kitchen();bathrooms();bedrooms();print('R07_INTERIORS_OK',flush=True)
    roof_and_context();annex();world=lighting()
    # Vista explodida explicitamente separada: os pavimentos de uso mantêm Z=2,70.
    for key in ['R07_Corte_Superior','R07_Piso_Superior']:
        for original in list(g.C[key].objects):
            obj=original.copy();obj.name='R07 Explodido '+original.name;obj.location.z+=4.0
            obj['R07_diagram_only']=True;g.C['R07_Superior_Explodido'].objects.link(obj)
    setup_scenes(world);print('R07_SCENES_OK',flush=True)
    bpy.context.view_layer.update()
    # Imagens herdadas dos móveis ficam empacotadas. A nova arquitetura não depende de referências externas.
    bpy.ops.file.pack_all()
    bpy.ops.outliner.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
    configure_gpu()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND),compress=True)
    receipt={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'blend':str(BLEND.relative_to(ROOT)),
             'blend_sha256':geo.sha(BLEND),'config_sha256':geo.sha(geo.CONFIG),'objects':len(bpy.data.objects),
             'scenes':[s.name for s in bpy.data.scenes],'reused_furniture_objects':reused,
             'source_blend':'arquivos/versoes-anteriores-2026-11-14/projeto/fontes/mobiliario-industrial.blend','geometry':geo.validate(CFG)}
    (REPORT/'modelo.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print('R07_BUILD_OK',json.dumps(receipt,ensure_ascii=False),flush=True)


def render(args):
    backend=configure_gpu(args.cpu)
    records=[];selected=[v for v in CFG['views'] if not args.only or v['id'] in args.only.split(',')]
    # A revisão de materiais tem origem própria e não deve ser sobrescrita pela base branca.
    study_path=ROOT/'config/residencia-07-estudos.json'
    if study_path.exists() and not args.preview:
        study=json.loads(study_path.read_text())
        if (ROOT/study['services_blend']).exists():
            if args.only and any(v['mode'].startswith('structure') for v in selected):
                raise ValueError('Renderize as estruturas coloridas com residence07_services.py e casa-07-instalacoes.blend.')
            selected=[v for v in selected if not v['mode'].startswith('structure')]
    assert selected,'Nenhuma câmera selecionada.'
    for view in selected:
        scene=bpy.data.scenes['R07_'+view['id']];bpy.context.window.scene=scene
        scene.render.resolution_percentage=45 if args.preview else 100;scene.cycles.samples=24 if args.preview else CFG['delivery']['samples']
        dest=geo.preview_path(view['id']) if args.preview else geo.artifact_path(view['id']);dest.parent.mkdir(parents=True,exist_ok=True)
        scene.render.filepath=str(dest)
        start=time.monotonic();bpy.ops.render.render(write_still=True,scene=scene.name)
        record={'id':view['id'],'file':str(Path(scene.render.filepath).relative_to(ROOT)),
                'seconds':round(time.monotonic()-start,2),'backend':backend,'samples':scene.cycles.samples,
                'resolution':[round(scene.render.resolution_x*scene.render.resolution_percentage/100),round(scene.render.resolution_y*scene.render.resolution_percentage/100)],
                'sha256':geo.sha(scene.render.filepath),'blend_sha256':geo.sha(BLEND)}
        records.append(record)
        (REPORT/('previas.json' if args.preview else 'renders-parcial.json')).write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
        print('R07_RENDER_OK',view['id'],record['seconds'],flush=True)
    # Quando apenas algumas vistas são reexecutadas, reconciliar pelo identificador e hash do modelo.
    if not args.preview:
        target=REPORT/'renders.json';previous=json.loads(target.read_text()) if target.exists() else []
        merged={r['id']:r for r in previous if geo.valid_render_record(r)};merged.update({r['id']:r for r in records})
        target.write_text(json.dumps(list(merged.values()),ensure_ascii=False,indent=2)+'\n')


def refresh_paths():
    assert Path(bpy.data.filepath)==BLEND
    for view in CFG['views']:bpy.data.scenes['R07_'+view['id']].render.filepath=str(geo.artifact_path(view['id']))
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND),compress=True)
    path=REPORT/'modelo.json';receipt=json.loads(path.read_text());receipt['blend_sha256']=geo.sha(BLEND)
    receipt['paths_updated_utc']=dt.datetime.now(dt.timezone.utc).isoformat();path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print('R07_PATHS_UPDATED',len(CFG['views']),flush=True)


def normalize_model():
    """Corrige a orientação das faces de prismas fechados, sem mover vértices."""
    done=set();fixed=0
    for obj in bpy.data.objects:
        if obj.type!='MESH' or obj.data in done:continue
        if not obj.name.startswith(('R07 Parede ','R07 Corte ','R07 Laje ','R07 Teto ','R07 Degrau ','R07 Piso ambiente ')):continue
        mesh=obj.data;done.add(mesh);bm=bmesh.new();bm.from_mesh(mesh)
        if bm.calc_volume(signed=True)<-1e-9:
            bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(mesh);mesh.update();fixed+=1
        bm.free()
    refresh_paths()
    (REPORT/'orientacao-faces.json').write_text(json.dumps({'fixed_closed_meshes':fixed,'checked_closed_meshes':len(done),'vertices_moved':0,'blend_sha256':geo.sha(BLEND)},indent=2)+'\n')
    print('R07_NORMALS_NORMALIZED',fixed,'closed meshes',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--render-only',action='store_true');parser.add_argument('--preview',action='store_true')
    parser.add_argument('--only');parser.add_argument('--cpu',action='store_true')
    parser.add_argument('--refresh-paths',action='store_true')
    parser.add_argument('--normalize-model',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if args.normalize_model:normalize_model()
    elif args.refresh_paths:refresh_paths()
    elif args.render_only:render(args)
    else:build()
