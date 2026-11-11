"""Reconstrução revisada por relações fotográficas; executar com o Python do Blender."""
import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
import house_geometry as h
import build_scene as g
import facade_details

ROOT=None
CFG=None


def box(*a,**kw):return h.box(*a,**kw)


def wall(*a,**kw):return h.wall(*a,**kw)


def architecture():
    d=CFG['estimated_dimensions_m'];layout=CFG['layout'];s=layout['spine_x'];w=d['width'];up=d['upper_front_y'];ub=d['upper_back_y']
    rear=layout['bar']['back_y'];garage=layout['garage_extension_bounds'];entry=layout['entry_diagonal']
    h.floor_rect('Laje sala — dimensões estimadas',(0,s,0,7.6),0,'Piso creme','Terreo')
    h.floor_rect('Laje faixa lateral',(s,w,garage[3],7.6),0,'Piso creme','Terreo')
    h.floor_rect('Piso churrasqueira',(0,s,7.6,rear),0,'Piso creme','Terreo',.12)
    h.floor_rect('Acesso externo condomínio',(0,w,-4.4,up),0,'Rejunte','Terreo',.12)
    h.floor_rect('Garagem sob volume superior',(0,w,up,0),0,'Piso creme','Terreo',.12)
    h.floor_rect('Garagem continuação direita',garage,0,'Piso creme','Terreo',.12)
    h.floor_rect('Piso lavanderia conforme croqui',layout['laundry_bounds'],0,'Piso creme','Terreo',.12)
    hole=layout['stair_hole']
    x0,x1,y0,y1=hole
    h.floor_rect('Laje superior oeste do vão',(0,x0,up,ub),1,'Piso laminado','Superior',.20)
    h.floor_rect('Laje superior à frente do vão',(x0,w,up,y0),1,'Piso laminado','Superior',.20)
    h.floor_rect('Laje superior atrás do vão',(x0,w,y1,ub),1,'Piso laminado','Superior',.20)
    wall('T0 limite oeste',(0,0),(0,rear),0,'Corte_Terreo')
    wall('T0 limite leste',(w,0),(w,rear),0,'Corte_Terreo')
    wall('T0 fachada sala',(0,0),tuple(entry['start']),0,'Corte_Terreo',[
        h.opening(.40,1.98,'Janela sala','window',.82,2.18,['exterior2.webp','sala3.webp'])])
    diagonal_entry()
    # Uma mesma face x=s contém TV, porta, escada e entrada da cozinha.
    # Não há vão lateral expondo a escada ao longo da sala.
    openings=[h.opening(*layout['portals']['lavabo'],'Porta lavabo'),
              h.opening(*layout['portals']['stair'],'Portal escada','passage',top=2.7),
              h.opening(*layout['portals']['kitchen'],'Entrada cozinha','passage',top=2.7)]
    offset=entry['end'][1]
    for op in openings:op['start']-=offset;op['end']-=offset
    wall('ESPINHA_Lateral TV lavabo escada cozinha',(s,offset),(s,7.25),0,'Terreo',openings)
    for o in g.C['Terreo'].objects:
        if o.name.startswith('Porta lavabo —'):
            o.rotation_euler.z=0
            o['evidencia']='sala2.webp; sala4.webp — porta fechada entre TV e escada'
    # O lavabo ocupa a projeção do segundo lance; paredes acompanham o forro.
    lavabo_walls()
    # Janela e bancada da cozinha voltadas para o mesmo pátio visto pela porta do bar.
    kitchen=layout['kitchen'];wx0,wx1=kitchen['window_x']
    wall('Parede janela cozinha',(s,7.6),(w,7.6),0,'Terreo',[
        h.opening(wx0-s,wx1-s,'Janela cozinha','window',1.05,2.30,['cozinha1.webp','cozinha2.webp','sala7.webp'])])
    wall('Separação escada cozinha',(s,4.9),(w,4.9),0,'Terreo')
    wall('Fundo bar',(0,rear),(s,rear),0,'Terreo')
    ay0,ay1=layout['laundry_access_y']
    wall('Separação churrasqueira lavanderia',(s,7.25),(s,rear),0,'Terreo',[
        h.opening(ay0-7.25,ay1-7.25,'Acesso lavanderia','passage',refs=['referencias-ajustes/planta-terreo-anotada.png'])])
    # Ripas sobre a face lateral, atrás da entrada da cozinha.
    ya,yb=layout['slat_y']
    box('Base painel ripado',(s-.033,(ya+yb)/2,1.35),(.045,yb-ya,2.7),'Armario cozinha cinza','Terreo',.002,h.FLOORS[0])
    for i in range(23):box('Ripa vertical cozinha',(s-.072,ya+(i+.5)*(yb-ya)/23,1.35),(.045,.023,2.7),'Metal preto','Terreo',.002,h.FLOORS[0])
    box('Interfone pilar entre escada e cozinha',(s-.091,4.775,1.49),(.027,.075,.20),'Armario branco','Terreo',.009,h.FLOORS[0])
    wall('Lavanderia fundo conforme croqui',(s,rear),(w,rear),0,'Terreo',[
        h.opening(.35,2.10,'Janela lavanderia','window',1.05,2.30,['lavanderia1.webp'])])
    # Superior: apenas envoltória e aberturas externas vistas na fachada.
    # Não repetir a distribuição refutada dos quartos dentro desta envoltória.
    wall('S1 lateral oeste',(0,up),(0,ub),1,'Superior',mat='Fachada areia')
    wall('S1 lateral leste',(w,up),(w,ub),1,'Corte_Superior',mat='Fachada areia')
    wall('S1 limite posterior não levantado',(0,ub),(w,ub),1,'Superior')
    facade_details.build(CFG)
    box('Cobertura cozinha atrás da laje superior',((s+w)/2,(ub+7.6)/2,2.77),(w-s,7.6-ub,.12),'Parede branca','Cobertura',.003)
    roof=g.parent('COBERTURA_BAR_vidro observada','Cobertura')
    for i in range(5):
        x=.075+i*(s-.15)/4
        g.rod('Viga cobertura bar',(x,6.95,2.75),(x,rear,3.05),.046,'Madeira bar','Cobertura',roof)
    for i in range(4):
        pane=box('Vidro cobertura bar',((i+.5)*s/4,(6.95+rear)/2,2.90),(s/4-.08,rear-6.95,.014),'Vidro transparente','Cobertura',.001,roof)
        pane.rotation_euler.x=math.atan2(.30,rear-6.95)
    for y in [i*.60 for i in range(15)]:g.rod('Junta piso transversal',(0,y,.003),(s,y,.003),.0012,'Rejunte','Terreo',h.FLOORS[0])
    for x in [i*.6 for i in range(6)]:g.rod('Junta piso longitudinal',(x,0,.003),(x,rear,.003),.0012,'Rejunte','Terreo',h.FLOORS[0])


def diagonal_entry():
    """Porta em plano diagonal, com pivô próprio; garagem aberta à direita."""
    spec=CFG['layout']['entry_diagonal'];a=Vector((*spec['start'],0));b=Vector((*spec['end'],0));v=b-a;length=v.length;angle=math.atan2(v.y,v.x);height=spec['opening_height']
    frame=g.parent('ENTRADA_DIAGONAL conforme croqui','Entrada_Diagonal',a,origem='croqui do usuário; medidas estimadas');frame.parent=h.FLOORS[0];frame.rotation_euler.z=angle
    for x in [.025,length-.025]:box('Batente entrada diagonal',(x,0,height/2),(.05,.15,height),'Parede branca','Entrada_Diagonal',.003,frame)
    box('Verga entrada diagonal',(length/2,0,(height+2.7)/2),(length,.15,2.7-height),'Parede branca','Vergas_Terreo',.003,frame)
    pivot=g.parent('Porta entrada diagonal — abrir/girar','Entrada_Diagonal',(.05,0,0));pivot.parent=frame;pivot.rotation_euler.z=math.radians(spec['door_open_angle_deg'])
    leaf=box('Porta entrada diagonal folha',((length-.10)/2,0,height/2),(length-.10,.04,height-.03),'Armario branco','Entrada_Diagonal',.005,pivot);leaf['tipo_elemento']='porta';leaf['origem']='croqui do usuário'
    box('Puxador vertical entrada diagonal',(length-.19,-.045,1.12),(.025,.045,.45),'Inox','Entrada_Diagonal',.006,pivot)
    mesh=bpy.data.meshes.new('Recuo triangular entrada');mesh.from_pydata([(a.x,a.y,.005),(b.x,a.y,.005),(b.x,b.y,.005)],[],[(0,1,2)])
    triangle=bpy.data.objects.new('Piso garagem recuo diagonal',mesh);g.C['Terreo'].objects.link(triangle);triangle.parent=h.FLOORS[0];mesh.materials.append(g.M['Piso creme'])


def stairs():
    cfg=CFG['layout']['stairs'];s=cfg['x_min'];run=cfg['run'];w=cfg['flight_width'];z=CFG['estimated_dimensions_m']['floor_height'];n=cfg['risers']//2;rise=z/(2*n);tread=run/n
    p=g.parent('ESCADA_TRANSVERSAL — retorno ainda inferido','Escada',direcao_primeiro_lance='entra na faixa lateral +X',forma_retorno='hipótese U, não confirmada',risers=2*n)
    for flight,y in [(0,cfg['first_y']),(1,cfg['return_y'])]:
        for i in range(n):
            xx=s+(i+.5)*tread if flight==0 else s+run-(i+.5)*tread
            height=(i+1)*rise if flight==0 else z/2+(i+1)*rise
            o=box(f'Degrau {flight*n+i+1:02} granito',(xx,y,height-.019),(tread+.015,w,.038),'Granito escada','Escada',.0025,p)
            o['lance']=flight+1;o['origem']='observação parcial' if flight==0 else 'retorno inferido'
            edge=s+i*tread if flight==0 else s+run-i*tread
            box('Espelho fechado degrau',(edge,y,height-rise/2),(.022,w,rise),'Parede branca','Escada',.002,p)
    ymin=cfg['return_y']-w/2;ymax=cfg['first_y']+w/2
    box('Patamar transversal inferido',(s+run+cfg['landing_depth']/2,(ymin+ymax)/2,z/2-.04),(cfg['landing_depth'],ymax-ymin,.08),'Granito escada','Escada',.004,p)
    # Fechamento sob o retorno, sobre o lavabo; não expor estrutura vazada no estar.
    verts=[(s,cfg['return_y']-w/2,z-.18),(s+run,cfg['return_y']-w/2,z/2-.18),(s+run,cfg['return_y']+w/2,z/2-.18),(s,cfg['return_y']+w/2,z-.18)]
    me=bpy.data.meshes.new('Face inferior escada');me.from_pydata(verts,[],[(0,1,2,3)]);o=bpy.data.objects.new('Forro inclinado sob retorno — inferido',me);g.C['Escada'].objects.link(o);o.parent=p;me.materials.append(g.M['Parede branca']);o.modifiers.new('Espessura forro','SOLIDIFY').thickness=.07
    for i in range(1,n):
        xx=s+i*tread
        box('Ressalto sob segundo lance',(xx,cfg['return_y'],return_ceiling_height(xx)-.025),(.035,w,.12),'Parede branca','Escada',.002,p)
    # Guarda-corpo na borda horizontal da abertura superior, como em escada1.
    y=ymax+.01
    box('Guarda-corpo vidro patamar superior',((s+s+run)/2,y,z+.49),(run,.012,.96),'Vidro transparente','Escada',.001,p)
    for x in [s+.10,s+run*.52,s+run-.10]:g.rod('Suporte inox vidro',(x,y,z),(x,y,z+.97),.013,'Inox','Escada',p)
    box('Mureta superior observada',((s+s+run)/2,ymin-.03,z+.37),(run,.10,.74),'Parede branca','Escada',.005,p)
    box('Capa granito mureta',((s+s+run)/2,ymin-.03,z+.755),(run+.04,.16,.035),'Granito escada','Escada',.004,p)


def return_ceiling_height(x):
    spec=CFG['layout']['stairs'];height=CFG['estimated_dimensions_m']['floor_height']
    t=max(0,min(1,(x-spec['x_min'])/spec['run']))
    return height-.18-t*height/2-.07


def lavabo_walls():
    x0,x1,y0,y1=CFG['layout']['lavabo_bounds'];t=CFG['estimated_dimensions_m']['wall_thickness']
    def sloped(name,y,col,xa=x0,xb=x1,zbase=0,zcap=None):
        # Colunas em cada extremidade e na mudança de inclinação do forro.
        xs=sorted(set([xa,xb]+[x for x in [CFG['layout']['stairs']['x_min']] if xa<x<xb]));verts=[]
        for x in xs:
            z=return_ceiling_height(x)-.005
            if zcap is not None:z=min(z,zcap)
            verts.extend([(x,y-t/2,zbase),(x,y+t/2,zbase),(x,y-t/2,z),(x,y+t/2,z)])
        faces=[(0,2,3,1)]
        for i in range(len(xs)-1):
            a=i*4;b=a+4
            faces.extend([(a,b,b+1,a+1),(a+2,a+3,b+3,b+2),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)])
        a=(len(xs)-1)*4;faces.append((a,a+1,a+3,a+2))
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
        obj=bpy.data.objects.new(name,mesh);g.C[col].objects.link(obj);obj.parent=h.FLOORS[0];mesh.materials.append(g.M['Parede branca']);obj['parede']=True;obj['sob_lance']=2
    wx0,wx1=CFG['facade']['small_window_x'];wz0,wz1=CFG['facade']['small_window_z']
    sloped('Lavabo divisão com garagem esquerda',y0,'Corte_Lavabo',xb=wx0)
    sloped('Lavabo divisão com garagem direita',y0,'Corte_Lavabo',xa=wx1)
    sloped('Lavabo divisão com garagem peitoril',y0,'Corte_Lavabo',xa=wx0,xb=wx1,zcap=wz0)
    sloped('Lavabo divisão com garagem verga',y0,'Corte_Lavabo',xa=wx0,xb=wx1,zbase=wz1)
    box('Janela pequena garagem vidro',((wx0+wx1)/2,y0,(wz0+wz1)/2),(wx1-wx0,.015,wz1-wz0),'Vidro transparente','Corte_Lavabo',.001,h.FLOORS[0])
    # O acabamento branco é acrescentado após a criação dos materiais da fachada.
    sloped('Lavabo parede posterior sob segundo lance',y1,'Lavabo_Estrutura')
    height=return_ceiling_height(x1)-.005
    box('Lavabo fechamento lateral baixo',(x1,(y0+y1)/2,height/2),(t,y1-y0,height),'Parede branca','Corte_Lavabo',.003,h.FLOORS[0])
    piso=h.floor_rect('Piso detalhe lavabo',(x0,x1,y0,y1),0,'Piso creme','Lavabo_Estrutura',.10);piso.location.z-=.005


def living_and_dining():
    p,c=h.room_parent('sala');pos=CFG['layout']['furniture']
    sofa=g.parent('SOFA_original cinza — mover conjunto',c,pos['sofa']);sofa.parent=p
    box('Base sofá',(0,0,.27),(1.02,2.7,.40),'Sofa cinza',c,.10,sofa)
    box('Encosto sofá',(-.38,0,.67),(.22,2.68,.70),'Sofa cinza',c,.09,sofa)
    for y in [-.86,0,.86]:
        box('Assento sofá',(.08,y,.48),(.86,.84,.17),'Sofa cinza',c,.07,sofa)
        box('Almofada encosto',(-.23,y,.77),(.20,.84,.50),'Sofa cinza',c,.07,sofa)
    box('Chaise lado janela',(.48,-.9,.29),(.85,.91,.45),'Sofa cinza',c,.09,sofa)
    for y in [-1.3,1.3]:box('Braço sofá',(.04,y,.57),(1.02,.14,.30),'Sofa cinza',c,.05,sofa)
    for x in [-.35,.35]:
        for y in [-1.1,1.1]:box('Pé sofá',(x,y,.035),(.05,.05,.07),'Metal preto',c,.003,sofa)
    tv=g.parent('TV_E_RACK_original',c,pos['tv']);tv.parent=p
    box('Fundo cinza painel TV',(CFG['layout']['spine_x']-.079,1.735,1.35),(.009,2.17,2.70),'Cinza parede TV',c,.001,p)
    box('Painel TV branco',(0,0,1.53),(.07,2.10,1.65),'Armario branco',c,.06,tv)
    box('TV preta independente',(-.065,.20,1.60),(.06,1.60,.94),'TV desligada',c,.012,tv)
    box('Rack amarelo tampo',(-.26,0,.55),(.46,2.10,.06),'Rack amarelo',c,.012,tv)
    box('Rack frentes brancas',(-.20,0,.31),(.34,1.95,.34),'Armario branco',c,.025,tv)
    for y in [-.91,.91]:
        box('Rack pés',(-.18,y,.19),(.30,.055,.38),'Rack amarelo',c,.009,tv)
        box('Barra luminosa painel',(-.05,y,1.58),(.014,.016,1.31),'Lampada quente',c,.003,tv)
    h.mark(box('Espelho original sala',pos['mirror'],(.015,1.15,1.70),'Espelho fisico',c,.001,p),['sala7.webp','sala5.webp'],'observed_relative','espelho')
    mx,my,mz=pos['mirror']
    for yy in [my-.575,my+.575]:box('Moldura vertical espelho',(mx+.012,yy,mz),(.018,.012,1.72),'Metal preto',c,.002,p)
    for zz in [mz-.85,mz+.85]:box('Moldura horizontal espelho',(mx+.012,my,zz),(.018,1.15,.012),'Metal preto',c,.002,p)
    # Cortina fotografada, independente e editável.
    for a,b in [(.25,1.12),(1.27,2.15)]:
        verts=[];faces=[]
        for i in range(49):
            x=a+(b-a)*i/48;y=.13+.022*math.sin(i*math.pi/3)
            verts.extend([(x,y,.045),(x,y,2.62)])
        for i in range(48):faces.append((i*2,i*2+2,i*2+3,i*2+1))
        mesh=bpy.data.meshes.new('Tecido cortina');mesh.from_pydata(verts,[],faces);o=bpy.data.objects.new('Cortina frontal fotografada',mesh);g.C[c].objects.link(o);o.parent=p;mesh.materials.append(g.M['Lencol']);o.modifiers.new('Espessura tecido','SOLIDIFY').thickness=.001
    g.rod('Trilho cortina',(.22,.13,2.63),(2.18,.13,2.63),.015,'Armario branco',c,p)
    p,c=h.room_parent('jantar');xyz=pos['dining_table'];table=g.parent('MESA_JANTAR_original seis lugares',c,xyz);table.parent=p
    box('Tampo vidro escuro',(0,0,.77),(1.02,1.72,.045),'Vidro mesa',c,.009,table)
    box('Base central mesa',(0,0,.36),(.50,.64,.72),'Armario branco',c,.012,table)
    box('Sapata mesa',(0,0,.045),(.68,.85,.09),'Granito preto',c,.008,table)
    for side in [-1,1]:
        for j,y in enumerate([-.47,.47]):h.chair(f'CADEIRA_{side}_{j}',(side*.76,y,0),c,table,-side*math.pi/2)
    h.chair('CADEIRA_cabeceira_frente',(0,-1.15,0),c,table,math.pi);h.chair('CADEIRA_cabeceira_fundos',(0,1.15,0),c,table)
    g.plant('Arranjo jantar original',(xyz[0],xyz[1],.80),.48,c,'Ceramica creme')
    for radius,z,tilt in [(.25,2.25,.35),(.19,2.33,-.48)]:
        bpy.ops.mesh.primitive_torus_add(major_radius=radius,minor_radius=.012,major_segments=48,minor_segments=8,location=(xyz[0],xyz[1],z));ring=g.finish(bpy.context.object,'Anel pendente original',c,'Lampada quente',p);ring.rotation_euler.x=tilt
    g.rod('Cabo pendente jantar',(xyz[0],xyz[1],2.33),(xyz[0],xyz[1],2.69),.004,'Metal preto',c,p)


def bar():
    p,c=h.room_parent('bar');cfg=CFG['layout']['bar'];y=cfg['counter_y'];back=cfg['back_y'];a,b=cfg['counter_x']
    box('Bar frente madeira',((a+b)/2,y+.09,.48),(b-a,.14,.96),'Madeira bar',c,.006,p)
    box('Bar tampo granito',((a+b)/2,y+.25,1.0),(b-a+.10,.63,.045),'Granito preto',c,.007,p)
    # Churrasqueira no canto posterior esquerdo, conforme croqui aproximado.
    grill=g.parent('CHURRASQUEIRA conforme croqui',c,(.50,back-.38,0));grill.parent=p
    box('Churrasqueira revestimento madeira frontal',(0,-.30,1.35),(.94,.07,2.70),'Madeira bar',c,.003,grill)
    box('Churrasqueira lateral madeira',(-.43,0,1.35),(.08,.65,2.70),'Madeira bar',c,.003,grill)
    for z,height in [(.40,.80),(2.15,1.10)]:box('Churrasqueira fechamento lateral',(.43,0,z),(.08,.65,height),'Madeira bar',c,.003,grill)
    for yy in [-.29,.29]:box('Churrasqueira boca lateral perfil',(.47,yy,1.20),(.05,.055,.80),'Metal preto',c,.003,grill)
    box('Churrasqueira boca lateral escura',(.40,0,1.20),(.04,.55,.75),'Metal preto',c,.003,grill)
    for x in [-.25,-.15,-.05,.05,.15,.25]:g.rod('Grelha churrasqueira',(x,-.26,.89),(x,.23,.89),.006,'Inox',c,grill)
    for i in range(10):
        for j in range(7):box('Pedra bar original',(1.04+i*.20,back-.095,1.12+j*.13),(.196,.025,.126),f'Pedra bar {(i+j)%5}',c,.003,p)
    for k in range(3):
        x=1.25+k*.63
        box('Armário bar fundo',(x,back-.10,2.17),(.61,.06,.62),'Armario cozinha cinza',c,.003,p)
        for z in [1.85,2.48]:box('Armário bar prateleira',(x,back-.25,z),(.64,.35,.025),'Armario branco',c,.003,p)
        box('Armário bar vidro',(x,back-.44,2.17),(.59,.014,.58),'Vidro transparente',c,.001,p)
        for xx in [x-.31,x+.31]:box('Armário bar perfil',(xx,back-.45,2.17),(.025,.03,.65),'Armario branco',c,.002,p)
    for i,x in enumerate(cfg['stool_x']):h.chair(f'BANQUETA_BAR_{i+1}',(x,cfg['stool_y'],0),c,p,0,True)
    box('Cuba bar',(1.75,y+.25,1.024),(.41,.30,.012),'Inox',c,.015,p)
    g.curve('Torneira bar',[(1.75,y+.45,1),(1.75,y+.45,1.28),(1.75,y+.24,1.32),(1.75,y+.21,1.19)],.01,'Cromado',c,p)
    h.fridge('Geladeira bar observada',(2.78,back-.38,0),c,p)
    for x in [.60,1.90]:
        g.lathe('Pendente bar original',[(.13,0),(.12,.05),(.06,.16),(.03,.23)],(x,y+.15,2.20),'Metal preto',c,p)
        g.rod('Cabo pendente bar',(x,y+.15,2.40),(x,y+.15,2.95),.005,'Metal preto',c,p)


def kitchen():
    p,c=h.room_parent('cozinha');cfg=CFG['layout']['kitchen'];s,x1,y0,y1=cfg['bounds'];rear=y1-.33;east=x1-.32
    for i in range(4):
        x=s+.31+i*(x1-s-.62)/3
        box('Armário pia cozinha',(x,rear,.44),(.59,.60,.88),'Armario cozinha cinza',c,.006,p)
        box('Porta pia cozinha',(x,rear-.315,.46),(.57,.025,.79),'Armario cozinha cinza',c,.004,p)
    box('Bancada pia cozinha',((s+x1)/2,rear,.91),(x1-s-.02,.65,.04),'Granito preto',c,.004,p)
    for y in [5.88,7.13]:box('Armário lado fogão',(east,y,.44),(.60,.59,.88),'Armario cozinha cinza',c,.006,p)
    for ya,yb in [(5.525,6.20),(6.84,7.475)]:box('Bancada lado fogão segmentada',(east,(ya+yb)/2,.91),(.65,yb-ya,.04),'Granito preto',c,.004,p)
    sx,sy,_=cfg['sink'];box('Cuba cozinha',(sx,sy,.934),(.46,.33,.01),'Inox',c,.016,p)
    g.curve('Torneira cozinha',[(sx,y1-.12,.93),(sx,y1-.12,1.25),(sx,y1-.40,1.28),(sx,y1-.44,1.12)],.012,'Cromado',c,p)
    stove=g.parent('FOGAO_cozinha',c,cfg['stove']);stove.parent=p
    box('Fogão forno',(0,0,.44),(.57,.59,.87),'Inox',c,.012,stove)
    box('Vidro forno',(-.303,0,.46),(.014,.43,.40),'TV desligada',c,.009,stove)
    for x in [-.14,.14]:
        for y in [-.15,.15]:g.cylinder('Boca fogão',(x,y,.90),.066,.014,'Metal preto',c,stove)
    box('Mesa fogão',(0,0,.88),(.57,.59,.02),'TV desligada',c,.004,stove)
    for y in [5.95,7.03]:box('Armário aéreo cozinha',(x1-.19,y,2.10),(.36,.75,.70),'Armario cozinha cinza',c,.006,p)
    box('Coifa corpo',(x1-.17,6.52,1.84),(.36,.65,.065),'Inox',c,.015,p)
    box('Coifa duto',(x1-.15,6.52,2.15),(.22,.26,.55),'Inox',c,.005,p)
    box('Armário aéreo junto ao ripado',(s+.20,6.80,2.12),(.37,.81,.74),'Armario cozinha cinza',c,.006,p)
    for yy in [6.60,7.00]:box('Puxador aéreo junto ripado',(s+.402,yy,1.79),(.018,.29,.018),'Inox',c,.003,p)
    for yy in [5.95,7.03]:box('Puxador aéreo lado fogão',(x1-.385,yy,1.78),(.018,.60,.018),'Inox',c,.003,p)
    for i in range(4):
        x=s+.31+i*(x1-s-.62)/3;box('Puxador armário pia',(x,rear-.34,.76),(.42,.025,.018),'Inox',c,.003,p)
    for yy in [5.88,7.13]:box('Puxador armário lado fogão',(x1-.63,yy,.76),(.025,.41,.018),'Inox',c,.003,p)
    micro=g.parent('MICROONDAS_nicho_cozinha',c,(x1-.29,7.14,1.58));micro.parent=p
    box('Micro-ondas corpo',(0,0,0),(.41,.49,.30),'Inox',c,.008,micro)
    box('Micro-ondas vidro',(-.213,0,0),(.012,.39,.21),'TV desligada',c,.005,micro)
    for z in [1.39,1.77]:box('Prateleira nicho micro-ondas',(x1-.27,7.14,z),(.48,.57,.025),'Armario branco',c,.003,p)
    for i in range(7):
        for j in range(6):
            yy=5.30+i*.32+(j%2)*.16
            if yy>7.48:continue
            box('Azulejo metro parede fogão',(x1-.082,yy,1.04+j*.125),(.014,.31,.115),'Azulejo branco',c,.003,p)
    for i in range(8):box('Azulejo metro sob janela',(s+.17+i*.30,y1-.082,1.01),(.29,.014,.115),'Azulejo branco',c,.003,p)
    wx0,wx1=cfg['window_x']
    for i in range(15):box('Persiana cozinha',((wx0+wx1)/2,y1-.07,2.25-i*.036),(wx1-wx0-.04,.055,.018),'Armario branco',c,.001,p)
    fr=h.fridge('Geladeira cozinha',cfg['fridge'],c,p)
    fr.rotation_euler.z=math.radians(cfg['fridge_rotation_deg'])
    # Lava-louças junto à entrada, observado em cozinha2, com retorno curto em L.
    box('Bancada lava-louças junto ao ripado',(s+.31,6.74,.91),(.60,.82,.04),'Granito preto',c,.004,p)
    box('Lava-louças',(s+.31,6.74,.43),(.55,.75,.86),'Inox',c,.012,p)
    box('Lava-louças painel frontal',(s+.595,6.74,.43),(.018,.67,.71),'Armario branco',c,.005,p)
    box('Lava-louças comando',(s+.61,6.74,.77),(.018,.65,.085),'Metal preto',c,.005,p)


def lavabo_and_service():
    p,c=h.room_parent('lavabo')
    spec=CFG['layout']['lavabo_fixtures'];sx,sy,sz=spec['sink']
    box('Bancada lavabo',(sx,sy,sz),(.48,.30,.05),'Granito preto',c,.007,p)
    g.lathe('Cuba lavabo',[(0,0),(.10,0),(.14,.06),(.15,.12),(.15,.14),(.13,.12),(.10,.06),(0,.06)],(sx,sy,sz+.03),'Louca branca',c,p)
    box('Espelho lavabo',spec['mirror'],(.45,.012,.65),'Espelho fisico',c,.001,p)
    box('Gabinete lavabo preto',(sx,sy,sz-.20),(.43,.26,.35),'Metal preto',c,.012,p)
    g.curve('Torneira lavabo',[(sx,sy+.10,sz+.03),(sx,sy+.10,sz+.27),(sx,sy,sz+.27),(sx,sy,sz+.20)],.009,'Cromado',c,p)
    g.rod('Porta toalhas lavabo',(sx-.20,sy-.18,sz-.08),(sx+.20,sy-.18,sz-.08),.010,'Cromado',c,p)
    box('Prateleira vidro lavabo',(sx,sy+.04,1.20),(.45,.12,.01),'Vidro transparente',c,.001,p)
    # Padrão geométrico aproximado da parede fotografada, sem textura externa.
    for i in range(8):
        for j in range(7):
            cx=3.27+i*.225;cz=.28+j*.32;points=[]
            for k in range(33):
                angle=k*math.tau/32;xx=cx+.108*math.cos(angle);zz=cz+.155*math.sin(angle)
                if zz>return_ceiling_height(xx)-.015:break
                points.append((xx,3.57,zz))
            if len(points)==33:g.curve('Padrão elíptico parede lavabo',points,.0018,'Padrao lavabo azul',c,p)
    # Nenhuma louça deve atravessar ou ser visível através da porta fechada.
    g.sphere('Bacia vaso lavabo',spec['toilet'],(.23,.15,.08),'Louca branca',c,p)
    tx,ty,_=spec['toilet']
    g.sphere('Corpo vaso lavabo',(tx,ty,.24),(.20,.14,.20),'Louca branca',c,p)
    box('Base vaso lavabo',(tx,ty,.06),(.28,.23,.12),'Louca branca',c,.035,p)
    box('Caixa vaso lavabo',spec['tank'],(.15,.32,.38),'Louca branca',c,.026,p)
    p,c=h.room_parent('lavanderia')
    rear=CFG['layout']['laundry_bounds'][3];y=rear-.34
    box('Bancada lavanderia fundo',(4.07,y,.90),(1.72,.59,.04),'Granito preto',c,.005,p)
    box('Bancada lavanderia lateral esquerda',(3.47,rear-.39,.90),(.57,.63,.04),'Granito preto',c,.005,p)
    for x in [3.45,4.03]:box('Gabinete lavanderia',(x,y,.44),(.55,.56,.88),'Armario branco',c,.006,p)
    for x in [4.62,5.21]:box('Máquina lavar',(x,y,.44),(.56,.57,.88),'Louca branca',c,.02,p)
    g.cylinder('Porta lavadora frontal',(4.62,y-.30,.43),.205,.035,'Inox',c,p,rotation=(math.pi/2,0,0))
    g.cylinder('Vidro lavadora',(4.62,y-.33,.43),.165,.018,'Vidro mesa',c,p,rotation=(math.pi/2,0,0))
    box('Tampa lavadora superior',(5.21,y,.90),(.48,.48,.035),'Vidro mesa',c,.02,p)
    box('Tanque lavanderia',(4.05,y,.925),(.49,.39,.012),'Inox',c,.016,p)
    g.curve('Torneira lavanderia',[(4.05,y+.20,.93),(4.05,y+.20,1.18),(4.05,y,1.18)],.009,'Cromado',c,p)
    for x in [3.45,5.20]:box('Armário aéreo lavanderia',(x,rear-.20,2.05),(.55,.33,.72),'Armario branco',c,.006,p)
    for x in [3.45,4.03]:box('Puxador gabinete lavanderia',(x,y-.30,.75),(.38,.02,.018),'Inox',c,.003,p)
    for x in [3.65,4.25,4.85,5.35]:g.plant('Planta janela cozinha',(x,7.76,1.08),.26,c,'Ceramica creme')


def upper_studies():
    """Modelos locais de cômodos, fora da envoltória; nenhuma adjacência inventada."""
    specs=[(key,spec['position'],spec['size']) for key,spec in CFG['room_studies'].items()]
    for key,loc,(w,depth) in specs:
        p=g.parent('ESTUDO_'+key,'Estudos_Superior',loc,implantacao='NÃO ESTABELECIDA; módulo fora da casa',fontes=json.dumps(h.ROOMS[key]['references']))
        p['not_house_coordinates']=True
        box('Estudo piso '+key,(w/2,depth/2,-.06),(w,depth,.12),'Piso laminado','Estudos_Superior',.002,p)
        for x in [0,w]:box('Estudo parede '+key,(x,depth/2,1.35),(.10,depth,2.7),'Parede azul' if key=='quarto_azul' and x==0 else 'Parede branca','Estudos_Superior',.003,p)
        # Parede de fundo modelada apenas até o peitoril para não ocultar o módulo.
        box('Estudo peitoril '+key,(w/2,depth,.40),(w,.10,.80),'Parede branca','Estudos_Superior',.003,p)
        if key=='quarto_azul':
            h.bed('BELICHE estudo',(w-.58,depth/2,0),.87,1.9,'Estudos_Superior',p,True)
            box('Escrivaninha azul',(.30,depth/2,.74),(.48,1.65,.04),'Armario branco','Estudos_Superior',.006,p)
            box('TV azul',(.08,depth/2,1.25),(.04,.58,.36),'TV desligada','Estudos_Superior',.007,p)
        elif key=='quarto_branco':
            h.bed('Cama branca estudo',(w-.55,depth/2,0),.86,1.9,'Estudos_Superior',p)
            box('Armário branco estudo',(.52,.35,1.3),(.90,.55,2.6),'Armario branco','Estudos_Superior',.008,p)
        elif key=='suite':
            h.bed('Cama suíte estudo',(1.65,1.65,0),1.50,1.95,'Estudos_Superior',p)
            box('Armário suíte estudo',(.29,1.55,1.3),(.50,2.4,2.6),'Madeira bar','Estudos_Superior',.008,p)
        else:
            box('Gabinete banheiro estudo',(.31,.55,.43),(.47,.80,.86),'Armario branco','Estudos_Superior',.006,p)
            box('Bancada banheiro estudo',(.32,.55,.87),(.52,.85,.045),'Granito escada','Estudos_Superior',.006,p)
            g.sphere('Vaso banheiro estudo',(w-.32,1.15,.38),(.17,.25,.12),'Louca branca','Estudos_Superior',p)
            box('Box banheiro estudo',(w/2,depth-.72,1.02),(w-.10,.012,2.04),'Vidro transparente','Estudos_Superior',.001,p)
        text=h.text('Legenda estudo '+key,key.replace('_',' ').upper()+'\nSEM POSIÇÃO CONFIRMADA',(loc[0]+w/2,loc[1]-.45,.02),.16,'Estudos_Cotas','Hipotese tinta')


def annotations():
    for room in CFG['rooms']:
        if room['level']!=0:continue
        x0,x1,y0,y1=room['bounds'];z=2.78
        label=room['name'].split(' · ')[0]
        if room['position_confidence']=='hypothesis':label+='\nPOSIÇÃO NÃO CONFIRMADA'
        if room['id']=='lavabo':label='Lavabo sob\n2º lance';z=4.0
        y=8.10 if room['id']=='bar' else (y0+y1)/2
        h.text('Rótulo '+room['id'],label,((x0+x1)/2,y,z),.15,'Cotas_Terreo')
    h.text('Rótulo churrasqueira','Churrasqueira',(.63,10.25,2.80),.11,'Cotas_Terreo')
    h.text('Rótulo bancada bar','Bancada',(1.50,9.35,2.78),.15,'Cotas_Terreo')
    h.text('Superior sem planta comprovada','DISTRIBUIÇÃO INTERNA NÃO ESTABELECIDA\nQuartos e banheiros em ESTUDOS_Superior\nNão interpretar como pavimento vazio real',(2.8,1.0,5.70),.20,'Cotas_Superior','Hipotese tinta')
    garage=CFG['layout']['garage_extension_bounds']
    h.text('Garagem continuação direita','GARAGEM\nAMPLIADA',((garage[0]+garage[1])/2,(garage[2]+garage[3])/2,2.78),.19,'Cotas_Terreo')
    h.text('Legenda entrada diagonal','ENTRADA\nDIAGONAL',(2.5,-.65,.03),.15,'Cotas_Terreo')
    h.text('Aviso estimativas','TÉRREO CONFORME CROQUI DO USUÁRIO • MEDIDAS APROXIMADAS',(2.8,11.2,.03),.16,'Cotas_Terreo','Hipotese tinta')


def setup():
    g.light('Luz geral',(3,4,14),1600,color=(1,.91,.78),size=10,target=(2.5,4,0))
    for z in [2.55]:
        for y in [1.3,4.6,6.3]:g.light('Luz ambiente',(1.7,y,z),95,color=(1,.85,.66),size=1.8,target=(1.7,y,z-2))
    g.light('Luz cozinha',(4.4,6.3,2.5),100,color=(1,.92,.80),size=1.6,target=(4.3,6.4,.7))
    g.light('Luz lavabo',(3.60,3.22,2.25),45,color=(1,.93,.82),kind='POINT',size=.15)
    g.light('Luz cobertura bar',(1.6,8,3.6),230,color=(.88,.94,1),size=2.4,target=(1.6,7.5,0))
    g.light('Luz estudos superiores',(14,3,10),2000,color=(1,.94,.84),size=9,target=(14,3,0))
    g.light('Luz céu frontal difusa',(2.8,-7,7),2100,color=(1,.94,.84),size=8,target=(2.8,0,2.3))
    for obj in g.C['Iluminacao'].objects:
        if obj.type=='LIGHT' and obj.data.type=='AREA':
            obj.visible_glossy=False;obj.data.specular_factor=0;obj.data.transmission_factor=0
    world=bpy.data.worlds.new('Ambiente');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.52,.59,.66,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.40;bpy.context.scene.world=world
    h.camera('CAM_Terreo_3D',(-11,-13,17),(2.8,3.7,.5),ortho=20)
    h.camera('CAM_Superior_3D',(13,-10,17),(2.8,2.7,3.1),ortho=16.5)
    h.camera('CAM_Terreo_Cotas',(2.8,3.4,25),(2.8,3.4,0),ortho=18)
    h.camera('CAM_Superior_Cotas',(2.8,2.65,25),(2.8,2.65,0),ortho=12)
    h.camera('CAM_Estudos_Superior',(23,-10,17),(14,2.7,.9),ortho=16)
    h.camera('CAM_Exterior',(12,-15,10),(2.8,2.4,2.5),ortho=18)
    h.camera('CAM_Corte_Lavabo',(8,-4,4.2),(4.1,3.4,1.6),ortho=5.2)
    for name,cfg in CFG['cameras'].items():h.camera(name,cfg['position'],cfg['target'],lens=cfg['lens'])
    inv=json.loads((ROOT/'relatorios/referencias-originais/inventario.json').read_text());seen=set()
    for i,(name,meta) in enumerate(inv['inputs'].items()):
        if meta['sha256'] in seen:continue
        seen.add(meta['sha256']);im=bpy.data.images.load(str(ROOT/'referencias-originais'/name));im.pack();o=bpy.data.objects.new('REF_'+name,None);o.empty_display_type='IMAGE';o.data=im;o.empty_display_size=2;o.location=(25+(i%4)*2.2,(i//4)*1.5,0);o.hide_render=True;g.C['Referencias'].objects.link(o)
    g.C['Referencias'].hide_render=True


def scenes(device):
    base=bpy.context.scene;base.name='PLANTA_Terreo';base.camera=bpy.data.objects['CAM_Terreo_3D']
    studies={'Estudos_Superior','Estudos_Cotas'};labels={'Cotas_Terreo','Cotas_Superior'}
    presets=[('CASA_Completa','CAM_Exterior',labels|studies),
             ('PLANTA_Superior','CAM_Superior_3D',{'Terreo','Cobertura','Corte_Superior','Cotas_Terreo'}|studies),
             ('PLANTA_Terreo_Cotas','CAM_Terreo_Cotas',{'Superior','Cobertura','Vergas_Terreo','Cotas_Superior'}|studies),
             ('PLANTA_Superior_Cotas','CAM_Superior_Cotas',{'Terreo','Cobertura','Vergas_Superior','Cotas_Terreo'}|studies),
             ('ESTUDOS_Superior','CAM_Estudos_Superior',{'Terreo','Superior','Cobertura','Escada','Cotas_Terreo','Cotas_Superior'})]
    for key in CFG['cameras']:
        hidden=labels|studies
        if 'Fachada' not in key:hidden=hidden|{'Fachada_Detalhes_Terreo'}
        presets.append((key.replace('CAM_Foto_','FOTO_'),key,hidden))
    for name,cam,hidden in presets:
        if not name.startswith('FOTO_Fachada'):hidden=hidden|{'Contexto_Condominio'}
        scene=base.copy();scene.name=name;scene.camera=bpy.data.objects[cam];h.exclude(scene,hidden)
    detail=bpy.data.scenes.new('CORTE_Lavabo_Escada');detail.camera=bpy.data.objects['CAM_Corte_Lavabo'];detail.world=base.world
    for name in ['Escada','AMB_lavabo','Lavabo_Estrutura','Iluminacao','Cameras']:detail.collection.children.link(g.C[name])
    detail['nota']='Paredes frontal e lateral removidas apenas nesta cena para visualizar o lavabo sob o segundo lance.'
    h.exclude(base,{'Superior','Cobertura','Corte_Terreo','Vergas_Terreo','Fixos_Paredes_Cortadas','Fachada_Detalhes_Terreo','Contexto_Condominio'}|labels|studies)
    for scene in bpy.data.scenes:
        scene.use_fake_user=True;scene.render.engine='CYCLES';scene.cycles.device='GPU' if device['backend']=='OPTIX' else 'CPU';scene.cycles.samples=CFG['render']['samples'];scene.cycles.seed=42;scene.cycles.use_denoising=True;scene.cycles.max_bounces=8;scene.cycles.transmission_bounces=6
        scene.render.resolution_x=1500;scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.view_settings.view_transform='AgX';scene.unit_settings.system='METRIC';scene.unit_settings.length_unit='METERS'
        if scene.name.endswith('_Cotas'):scene.render.resolution_x=1200;scene.render.resolution_y=1800
        if scene.name.startswith('FOTO_'):scene.render.resolution_x=1200;scene.render.resolution_y=630
        scene['config_sha256']=hashlib.sha256((ROOT/'config/planta-casa.json').read_bytes()).hexdigest();scene['revision']=CFG.get('revision_number',2);scene['upper_layout']='NOT_ESTABLISHED';scene['device_info']=json.dumps(device)


def main():
    global ROOT,CFG
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,default=Path('.'));p.add_argument('--device',choices=['auto','cpu'],default='auto');p.add_argument('--output',type=Path);p.add_argument('--preview',action='store_true');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    ROOT=args.project_root.resolve();CFG=json.loads((ROOT/'config/planta-casa.json').read_text(encoding='utf-8'));assert CFG['schema_version']==2
    h.ROOT=ROOT;h.CFG=CFG;h.ROOMS={r['id']:r for r in CFG['rooms']};h.PARENTS.clear();h.FLOORS.clear()
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections):bpy.data.collections.remove(c)
    g.C.clear();g.M.clear();g.LEAF_MESHES.clear();g.RNG.seed(1202026)
    for name in ['Terreo','Superior','Escada','Cobertura','Iluminacao','Cameras','Referencias','Cotas_Terreo','Cotas_Superior','Estudos_Superior','Estudos_Cotas']:h.collection(name)
    h.collection('Corte_Terreo',g.C['Terreo']);h.collection('Corte_Superior',g.C['Superior'])
    h.collection('Vergas_Terreo',g.C['Terreo']);h.collection('Vergas_Superior',g.C['Superior'])
    h.collection('Fixos_Paredes_Cortadas',g.C['Terreo'])
    h.collection('Entrada_Diagonal',g.C['Terreo'])
    h.collection('Lavabo_Estrutura',g.C['Terreo']);h.collection('Corte_Lavabo',g.C['Terreo'])
    h.collection('Fachada',g.C['Superior']);h.collection('Fachada_Detalhes_Terreo',g.C['Terreo'])
    h.collection('Contexto_Condominio')
    h.FLOORS[0]=g.parent('NIVEL_0 — térreo','Terreo');h.FLOORS[1]=g.parent('NIVEL_1 — superior','Superior',(0,0,CFG['estimated_dimensions_m']['floor_height']))
    h.materials()
    facade_details.materials()
    g.M['TV desligada'].node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.12
    architecture();stairs();living_and_dining();bar();kitchen();lavabo_and_service();upper_studies();annotations();setup()
    for obj in list(bpy.data.objects):
        if obj.name.startswith(('Espelho original sala','Moldura vertical espelho','Moldura horizontal espelho','Cortina frontal fotografada','Trilho cortina')):
            g.move_to(obj,'Fixos_Paredes_Cortadas')
    device=g.configure_device(args.device);scenes(device)
    output=args.output or Path(CFG['output']);output=output if output.is_absolute() else ROOT/output;assert output.suffix=='.blend';output=g.unique_path(output);output.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output))
    report={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'blend':str(output.relative_to(ROOT)),'version':bpy.app.version_string,'revision':CFG.get('revision_number',2),'device':device,'objects':len(bpy.data.objects),'scenes':[s.name for s in bpy.data.scenes],'source_status':'Térreo conforme croqui aproximado do usuário e fotos. Superior sem implantação confirmada.'}
    (ROOT/'relatorios/planta-casa/geracao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('HOUSE_BUILT',json.dumps(report,ensure_ascii=False),flush=True)
    if args.preview:
        scene=bpy.data.scenes['FOTO_Sala_Fundos'];scene.cycles.samples=16;scene.render.resolution_percentage=50;scene.render.filepath=str(ROOT/'renders/revisao-02/previa-sala.png');bpy.ops.render.render(write_still=True,scene=scene.name)


if __name__=='__main__':main()
