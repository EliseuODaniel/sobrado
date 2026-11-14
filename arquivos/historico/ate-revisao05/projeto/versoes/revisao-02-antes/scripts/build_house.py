"""Planta 3D editável das fotos originais. Não é levantamento métrico do imóvel."""
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
import build_scene as g

ROOT=None
CFG=None
ROOMS={}
PARENTS={}
FLOORS={}


def collection(name,parent=None):
    c=bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(c)
    g.C[name]=c
    return c


def box(name,loc,size,mat,col,bevel=.006,par=None):
    return g.box(name,loc,size,mat,col,bevel,par)


def room_parent(key):
    r=ROOMS[key]
    if key not in PARENTS:
        c=collection('AMB_'+key,g.C['Terreo' if r['level']==0 else 'Superior'])
        p=g.parent('AMBIENTE_'+key,c.name)
        p.parent=FLOORS[r['level']]
        p['fontes']=json.dumps(r['references'],ensure_ascii=False)
        p['confianca_implantacao']=r['position_confidence']
        p['medidas']='ESTIMADAS — sem levantamento'
        PARENTS[key]=p
    return PARENTS[key],'AMB_'+key


def materials():
    simple={
        'Parede branca':((.73,.71,.65),.85,0),
        'Fachada areia':((.52,.43,.30),.85,0),
        'Piso creme':((.57,.53,.44),.22,0),
        'Azulejo branco':((.77,.78,.73),.28,0),
        'Armario branco':((.64,.62,.54),.4,0),
        'Armario cozinha cinza':((.10,.12,.14),.38,0),
        'Sofa cinza':((.055,.061,.063),.87,0),
        'Estofado cadeira cinza':((.22,.21,.18),.89,0),
        'Lencol':((.76,.74,.67),.93,0),
        'Piso laminado':((.44,.40,.33),.55,0),
        'Parede azul':((.035,.095,.17),.85,0),
        'Madeira bar':((.21,.085,.025),.43,0),
        'Rack amarelo':((.58,.28,.009),.35,0),
        'Metal preto':((.015,.017,.016),.36,.7),
        'Inox':((.40,.44,.46),.25,.9),
        'Cromado':((.55,.59,.61),.1,.98),
        'Vidro mesa':((.03,.055,.05),.08,.25),
        'TV desligada':((.009,.012,.017),.16,.22),
        'Espelho fisico':((.97,.97,.97),.003,1),
        'Louca branca':((.8,.79,.73),.2,0),
        'Cotas tinta':((.035,.10,.14),.7,0),
        'Hipotese tinta':((.5,.20,.025),.7,0),
        'Area desconhecida':((.33,.30,.22),.8,0),
        'Luz quente':((1,.62,.24),.3,0),
        'Rejunte':((.26,.25,.22),.9,0),
        'Ceramica preta':((.014,.018,.015),.28,0),
        'Ceramica creme':((.76,.7,.57),.25,0),
        'Terra':((.018,.012,.007),.95,0)
    }
    for name,(color,rough,metal) in simple.items():g.basic(name,color,rough,metal)
    g.basic('Vidro transparente',(.95,.98,1),.05,transmission=1)
    g.basic('Lampada quente',(1,.62,.25),.3,emission=4)
    for i,c in enumerate([(.04,.13,.018),(.11,.22,.035),(.20,.30,.04),(.025,.09,.01)]):g.basic('Folha '+str(i),c,.5)
    g.textured('Granito escada',[(.025,.03,.03),(.12,.13,.13),(.23,.23,.21)],'stone',.3,.002)
    g.textured('Granito preto',[(.003,.004,.003),(.022,.025,.02),(.075,.07,.05)],'stone',.15,.002)
    for i in range(5):g.textured(f'Pedra bar {i}',[(.025,.03,.025),(.09+i*.006,.075,.045),(.16,.10,.045)],'stone',.7,.012)


def mark(obj,refs=(),certainty='estimated',kind=None):
    obj['fontes']=json.dumps(list(refs),ensure_ascii=False)
    obj['confianca']=certainty
    if kind:obj['tipo_elemento']=kind
    return obj


def wall(name,a,b,level,col,openings=(),mat='Parede branca',height=None):
    """Paredes segmentadas: vãos são geometria aberta, com peitoril e verga."""
    h=height or CFG['estimated_dimensions_m']['clear_height'];t=CFG['estimated_dimensions_m']['wall_thickness']
    dx,dy=b[0]-a[0],b[1]-a[1]
    assert (abs(dx)<1e-8) != (abs(dy)<1e-8),'Parede precisa ser ortogonal e ter comprimento'
    length=abs(dx+dy);ux,uy=dx/length,dy/length
    openings=sorted(openings,key=lambda q:q['start'])
    cursor=0
    def piece(s,e,z0,z1,suffix):
        if e-s<.005 or z1-z0<.005:return
        loc=(a[0]+ux*(s+e)/2,a[1]+uy*(s+e)/2,(z0+z1)/2)
        size=(e-s,t,z1-z0) if dx else (t,e-s,z1-z0)
        o=box(name+' '+suffix,loc,size,mat,col,.003,FLOORS[level]);o['parede']=True;o['pavimento']=level
    for i,op in enumerate(openings):
        s,e=op['start'],op['end'];z0,z1=op.get('sill',0),op.get('top',2.1)
        assert 0<=cursor<=s<e<=length+.001,(name,op,length)
        piece(cursor,s,0,h,'trecho')
        piece(s,e,0,z0,'peitoril');piece(s,e,z1,h,'verga')
        cx,cy=a[0]+ux*(s+e)/2,a[1]+uy*(s+e)/2
        width=e-s
        if op.get('kind')=='window':
            obj=box(op['id']+' vidro',(cx,cy,(z0+z1)/2),(width-.05,.018,z1-z0-.05) if dx else (.018,width-.05,z1-z0-.05),'Vidro transparente',col,.001,FLOORS[level])
            mark(obj,op.get('refs',()),'orientation_estimated' if level else 'observed_relative','janela')
            for pos in [s,(s+e)/2,e]:
                xx,yy=a[0]+ux*pos,a[1]+uy*pos
                box(op['id']+' caixilho',(xx,yy,(z0+z1)/2),(.03,.045,z1-z0) if dx else (.045,.03,z1-z0),'Armario branco',col,.002,FLOORS[level])
            for z in [z0,z1]:box(op['id']+' travessa',(cx,cy,z),(width,.045,.03) if dx else (.045,width,.03),'Armario branco',col,.002,FLOORS[level])
        elif op.get('kind')=='door':
            obj=box(op['id']+' folha',(cx,cy,z1/2),(width-.04,.035,z1-.035) if dx else (.035,width-.04,z1-.035),'Armario branco',col,.005,FLOORS[level])
            obj['tipo_elemento']='porta';obj['largura_estimada_m']=width;obj['pavimento']=level
            # Folhas de porta ficam abertas nas plantas; pivot no batente.
            pivot=g.parent(op['id']+' — abrir/girar',col,(a[0]+ux*s,a[1]+uy*s,0))
            pivot.parent=FLOORS[level]
            obj.parent=pivot;obj.location=(ux*width/2,uy*width/2,z1/2)
            pivot.rotation_euler[2]=0 if op['id']=='Porta entrada' else math.radians(75 if dx else -75)
        cursor=e
    piece(cursor,length,0,h,'trecho final')


def opening(start,end,id,kind='door',sill=0,top=2.1,refs=()):return dict(start=start,end=end,id=id,kind=kind,sill=sill,top=top,refs=refs)


def floor_rect(name,rect,level,mat,col,thickness=.18):
    x0,x1,y0,y1=rect
    return box(name,((x0+x1)/2,(y0+y1)/2,-thickness/2),(x1-x0,y1-y0,thickness),mat,col,.002,FLOORS[level])


def architecture():
    d=CFG['estimated_dimensions_m'];w=d['width'];back=d['main_depth'];split=d['living_dining_width'];upfront=d['upper_front_y'];upback=d['upper_back_y']
    floor_rect('Laje térrea — retângulo base hipotético 42,50 m²',(0,w,0,back),0,'Piso creme','Terreo')
    floor_rect('Piso garagem — projeção estimada',(0,w,-4.4,0),0,'Rejunte','Terreo',.10)
    floor_rect('Piso anexo bar — perímetro estimado',(0,split,back,10.3),0,'Piso creme','Terreo',.10)
    floor_rect('Pátio e lavanderia — perímetro incerto',(2.6,w,8.5,12.4),0,'Piso creme','Terreo',.10)
    # Laje superior recortada na abertura da escada. Não duplicar o térreo.
    floor_rect('Laje superior faixa esquerda',(0,split,upfront,upback),1,'Piso laminado','Superior',.20)
    floor_rect('Laje superior faixa frontal',(split,w,upfront,d['stair_front_y']),1,'Piso laminado','Superior',.20)
    floor_rect('Laje superior faixa fundos',(split,w,d['stair_back_y'],upback),1,'Piso laminado','Superior',.20)
    wall('T0 lateral esquerda',(0,0),(0,10.3),0,'Terreo')
    wall('T0 lateral direita',(w,0),(w,8.5),0,'Corte_Terreo')
    wall('T0 fachada entrada',(0,0),(w,0),0,'Corte_Terreo',[
        opening(.40,2.20,'Janela sala','window',.85,2.20,['sala3.webp','exterior2.webp']),opening(2.65,3.48,'Porta entrada')])
    wall('T0 fundo bar',(0,10.3),(split,10.3),0,'Terreo')
    wall('T0 lateral bar porta pátio',(split,8.5),(split,10.3),0,'Terreo',[opening(.55,1.45,'Porta lateral bar',refs=['area2.webp','area3.webp'])])
    wall('T0 fundo cozinha janela',(split,8.5),(w,8.5),0,'Terreo',[opening(.20,1.63,'Janela cozinha','window',1.05,2.25,['cozinha1.webp','cozinha2.webp'])])
    # Escada observada ao lado da sala; lavabo acessível sob o lance alto.
    wall('T0 parede acesso escada',(split,3.3),(w,3.3),0,'Terreo',[
        opening(.08,.87,'Vão escada','passage',top=2.7),opening(1.04,1.77,'Porta lavabo')])
    wall('T0 parede lateral escada',(split,3.3),(split,6.1),0,'Terreo',[opening(0,2.0,'Abertura lateral escada','passage',top=2.7)])
    wall('T0 parede fundo escada',(split,6.1),(w,6.1),0,'Terreo',[opening(.13,1.18,'Passagem cozinha','passage',top=2.5)])
    wall('T0 parede lavabo',(4.13,3.3),(4.13,4.9),0,'Terreo',height=2.35)
    wall('T0 fundo lavabo',(4.13,4.9),(w,4.9),0,'Terreo',height=1.75)
    # Divisória ao lado da cozinha com passagem real até as bancadas.
    part=box('Divisória ripada — observada em sala1/sala7',(split-.16,6.65,1.36),(.28,.95,2.72),'Armario cozinha cinza','Terreo',.005,FLOORS[0])
    for j in range(18):box('Ripa cozinha',(split-.325,6.20+j*.052,1.36),(.045,.022,2.72),'Metal preto','Terreo',.002,FLOORS[0])
    # Lavanderia: ambiente visto, mas conexão e posição não documentadas.
    wall('HIPÓTESE lavanderia frente',(2.6,10.6),(w,10.6),0,'Terreo',[opening(1.38,2.18,'Porta lavanderia')])
    wall('HIPÓTESE lavanderia fundo',(2.6,12.4),(w,12.4),0,'Terreo',[opening(.35,1.88,'Janela lavanderia','window',1.05,2.25,['lavanderia1.webp'])])
    wall('HIPÓTESE lavanderia esquerda',(2.6,10.6),(2.6,12.4),0,'Terreo')
    wall('HIPÓTESE lavanderia direita',(w,10.6),(w,12.4),0,'Terreo')
    # Paredes do superior: distribuição explicitamente hipotética.
    wall('S1 lateral esquerda',(0,upfront),(0,upback),1,'Superior',[
        opening(4.30,5.0,'Janela banheiro social — orientação incerta','window',1.65,2.30,['banheiro2.webp'])])
    wall('S1 lateral direita',(w,upfront),(w,upback),1,'Corte_Superior')
    wall('S1 fachada direita',(2.5,upfront),(w,upfront),1,'Corte_Superior',[
        opening(.48,1.92,'Janela quarto branco','window',.85,2.15,['quartobranco1.webp','exterior2.webp'])])
    wall('S1 fundo varanda',(0,-.9),(2.5,-.9),1,'Corte_Superior',[
        opening(.38,2.10,'Janela quarto azul / varanda — ligação incerta','window',.70,2.20,['quartoazul2.webp','exterior2.webp'])])
    wall('S1 divisão quartos frente',(2.5,upfront),(2.5,1.3),1,'Superior')
    wall('S1 fundos quartos frente',(0,1.3),(w,1.3),1,'Superior',[
        opening(1.56,2.32,'Porta quarto azul'),opening(2.80,3.56,'Porta quarto branco')])
    wall('S1 banho social esquerda',(0,2.4),(1.65,2.4),1,'Superior')
    wall('S1 banho social direita',(1.65,2.4),(1.65,4.65),1,'Superior',[opening(.35,1.08,'Porta banho social')])
    wall('S1 banho social fundo',(0,4.65),(1.65,4.65),1,'Superior')
    wall('S1 suíte frente',(0,5.0),(split,5.0),1,'Superior',[opening(2.20,2.96,'Porta suíte')])
    wall('S1 suíte lateral',(split,5.0),(split,upback),1,'Superior',[opening(1.60,2.34,'Porta banho suíte')])
    wall('S1 fundo dormitórios',(0,upback),(w,upback),1,'Superior',[
        opening(.60,2.55,'Janela suíte','window',.85,2.30,['quartosuite1.webp']),
        opening(3.60,4.32,'Janela banho suíte','window',1.60,2.25,['suite1.webp'])])
    wall('S1 frente banho suíte',(split,6.35),(w,6.35),1,'Superior')
    # Varanda observada na fachada. Profundidade ainda estimada.
    box('Varanda mureta frontal',(1.25,upfront,.49),(2.5,.12,.98),'Fachada areia','Superior',.007,FLOORS[1])
    for x in [.03,2.47]:box('Varanda retorno',(x,-1.3,.49),(.12,.8,.98),'Fachada areia','Superior',.006,FLOORS[1])
    for x in [.08,4.92]:box('Pilar fachada garagem',(x,-4.3,1.35),(.16,.20,2.70),'Fachada areia','Corte_Terreo',.005,FLOORS[0])
    # Cobertura de vidro confirmada pelas fotos originais, separada do volume superior.
    roof=g.parent('COBERTURA_Vidro observada — inclinação estimada','Cobertura')
    for i in range(5):
        x=.08+i*.76
        g.rod('Viga madeira cobertura',(x,8.5,2.76),(x,10.30,2.98),.048,'Madeira bar','Cobertura',roof)
    for i in range(4):
        pane=box('Vidro cobertura bar',(.46+i*.76,9.4,2.87),(.66,1.81,.015),'Vidro transparente','Cobertura',.002,roof)
        pane.rotation_euler.x=math.atan2(.22,1.8)
    box('Cobertura principal — forma não documentada',(w/2,(upfront+upback)/2,2.9+2.8),(w+.15,upback-upfront+.15,.15),'Fachada areia','Cobertura',.01)
    box('Cobertura garagem — projeção estimada',(w/2,(-4.4+upfront)/2,2.78),(w,abs(-4.4-upfront),.12),'Fachada areia','Cobertura',.008)
    # Rodapés e juntas de piso leves, separados para edição.
    for y in [i*.6 for i in range(15)]:
        g.rod('Junta piso transversal',(0,y,.004),(w,y,.004),.0013,'Rejunte','Terreo',FLOORS[0])
    for x in [i*.6 for i in range(9)]:
        if x<w:g.rod('Junta piso longitudinal',(x,0,.004),(x,back,.004),.0013,'Rejunte','Terreo',FLOORS[0])


def stairs():
    d=CFG['estimated_dimensions_m'];z=d['floor_height'];start=d['stair_front_y'];back=d['stair_back_y'];run=2.0;rise=z/18;step=run/9
    p=g.parent('ESCADA_U — geometria completa estimada','Escada',forma='hipótese U; fotos mostram apenas trechos',risers=18,riser_m=rise)
    for flight,x in [(0,3.60),(1,4.57)]:
        for i in range(9):
            y=start+(i+.5)*step if flight==0 else start+run-(i+.5)*step
            h=(i+1)*rise if flight==0 else z/2+(i+1)*rise
            box(f'Degrau {flight*9+i+1:02} granito',(x,y,h-.02),(.78,step+.018,.04),'Granito escada','Escada',.003,p)
            yy=y+step/2 if flight==0 else y-step/2
            box('Espelho do degrau',(x,yy,h-rise/2),(.78,.025,rise),'Parede branca','Escada',.002,p)
    box('Patamar intermediário',(4.085,(start+run+back)/2,z/2-.045),(1.75,back-(start+run),.09),'Granito escada','Escada',.004,p)
    # Guarda-corpo transparente no lance e na borda da abertura superior.
    for y in [3.45,4.3,5.2]:
        zz=z-(y-start)/run*z/2
        g.rod('Montante inox guarda-corpo',(4.12,y,zz),(4.12,y,zz+.95),.015,'Inox','Escada',p)
    verts=[(4.12,start,z+.10),(4.12,start+run,z/2+.10),(4.12,start+run,z/2+.95),(4.12,start,z+.95)]
    me=bpy.data.meshes.new('Vidro guarda corpo');me.from_pydata(verts,[],[(0,1,2,3)]);o=bpy.data.objects.new('Guarda-corpo de vidro — observado escada1',me);g.C['Escada'].objects.link(o);o.parent=p;me.materials.append(g.M['Vidro transparente']);o.modifiers.new('Espessura vidro','SOLIDIFY').thickness=.012
    box('Mureta superior escada',(3.12,4.72,z+.36),(.10,2.65,.72),'Parede branca','Escada',.005,p)
    box('Tampo granito mureta',(3.12,4.72,z+.74),(.16,2.68,.035),'Granito escada','Escada',.005,p)


def chair(name,loc,col,par,rotation=0,stool=False):
    p=g.parent(name,col,loc,categoria='banqueta_original' if stool else 'cadeira_original')
    p.parent=par;p.rotation_euler[2]=rotation
    h=.73 if stool else .46
    box('Assento estofado',(0,0,h),(.42,.43,.08),'Estofado cadeira cinza',col,.03,p)
    box('Encosto estofado',(0,.19,h+.23),(.42,.07,.43),'Estofado cadeira cinza',col,.024,p)
    for x in [-.17,.17]:
        for y in [-.16,.16]:box('Pé cadeira',(x,y,h/2),(.035,.035,h),'Madeira bar',col,.003,p)
    return p


def furniture():
    p,c=room_parent('sala')
    sofa=g.parent('SOFA_original cinza — mover conjunto',c,(.62,1.7,0));sofa.parent=p
    box('Base sofá',(0,0,.27),(1.02,2.70,.40),'Sofa cinza',c,.10,sofa)
    box('Encosto sofá',(-.38,0,.67),(.22,2.68,.70),'Sofa cinza',c,.09,sofa)
    for i in [-.86,0,.86]:
        box('Almofada assento',(.08,i,.48),(.86,.84,.17),'Sofa cinza',c,.07,sofa)
        box('Almofada encosto',(-.23,i,.77),(.20,.84,.50),'Sofa cinza',c,.07,sofa)
    box('Chaise do sofá',(.48,-.90,.29),(.85,.91,.45),'Sofa cinza',c,.09,sofa)
    for y in [-1.30,1.30]:box('Braço sofá',(.04,y,.57),(1.02,.14,.30),'Sofa cinza',c,.05,sofa)
    for x in [-.35,.35]:
        for y in [-1.10,1.10]:box('Pé sofá',(x,y,.035),(.05,.05,.07),'Metal preto',c,.003,sofa)
    for y in [-1.25,-.55]:box('Pé chaise',(.75,y,.033),(.05,.05,.066),'Metal preto',c,.003,sofa)
    # Painel, TV, rack amarelo e espelho como vistos nas fotos, sem restyling industrial.
    tv=g.parent('TV_E_RACK_original',c,(4.84,1.67,0));tv.parent=p
    box('Painel TV branco',(0,0,1.55),(.07,2.6,1.60),'Armario branco',c,.06,tv)
    box('TV preta independente',(-.065,0,1.65),(.06,1.65,.94),'TV desligada',c,.015,tv)
    box('Rack amarelo tampo',(-.26,0,.55),(.46,2.62,.06),'Rack amarelo',c,.015,tv)
    box('Rack frentes brancas',(-.20,0,.31),(.34,2.48,.34),'Armario branco',c,.03,tv)
    for yy in [-1.16,1.16]:box('Rack pés',(-.18,yy,.19),(.30,.055,.38),'Rack amarelo',c,.01,tv)
    for yy in [-1.14,1.14]:box('Barra luminosa painel',(-.05,yy,1.58),(.014,.016,1.31),'Lampada quente',c,.003,tv)
    mark(box('Espelho original sala',(.021,4.50,1.43),(.015,1.05,2.30),'Espelho fisico',c,.001,p),['sala7.webp'],'observed_relative','espelho')
    p,c=room_parent('jantar');table=g.parent('MESA_JANTAR_original seis lugares',c,(1.58,6.0,0));table.parent=p
    box('Tampo vidro escuro',(0,0,.77),(1.0,1.72,.045),'Vidro mesa',c,.012,table)
    box('Base central mesa',(0,0,.36),(.50,.64,.72),'Armario branco',c,.012,table)
    box('Sapata mesa',(0,0,.045),(.68,.85,.09),'Granito preto',c,.01,table)
    for side in [-1,1]:
        for j,y in enumerate([-.47,.47]):chair(f'CADEIRA_{side}_{j}',(side*.77,y,0),c,table,-side*math.pi/2)
    chair('CADEIRA_cabeceira_frente',(0,-1.16,0),c,table,math.pi)
    chair('CADEIRA_cabeceira_fundos',(0,1.16,0),c,table,0)
    g.plant('Arranjo jantar original',(1.58,6.0,.80),.48,c,'Ceramica creme')
    # Pendente em dois anéis, observado em sala1/sala7.
    for radius,zz in [(.25,2.25),(.19,2.33)]:
        bpy.ops.mesh.primitive_torus_add(major_radius=radius,minor_radius=.012,major_segments=48,minor_segments=8,location=(1.58,6,zz))
        g.finish(bpy.context.object,'Anel pendente original',c,'Lampada quente',p)
    g.rod('Cabo pendente jantar',(1.58,6,2.3),(1.58,6,2.69),.004,'Metal preto',c,p)
    p,c=room_parent('bar')
    box('Bar frente madeira',(1.44,9.25,.48),(2.84,.12,.96),'Madeira bar',c,.007,p)
    box('Bar tampo granito',(1.45,9.45,1.0),(2.95,.65,.045),'Granito preto',c,.008,p)
    box('Bar painel vertical madeira',(.51,10.21,1.88),(.94,.08,1.75),'Madeira bar',c,.004,p)
    for i in range(10):
        for j in range(7):box('Pedra bar original',(1.04+i*.20,10.19,1.12+j*.13),(.196,.025,.126),f'Pedra bar {(i+j)%5}',c,.003,p)
    for k in range(3):
        x=1.25+k*.63
        box('Armário superior bar fundo',(x,10.10,2.17),(.61,.06,.62),'Armario cozinha cinza',c,.004,p)
        for z in [1.85,2.48]:box('Armário superior bar prateleira',(x,9.94,z),(.64,.35,.025),'Armario branco',c,.003,p)
        box('Porta vidro armário bar',(x,9.75,2.17),(.59,.014,.58),'Vidro transparente',c,.001,p)
        for xx in [x-.31,x+.31]:box('Perfil armário bar',(xx,9.74,2.17),(.025,.03,.65),'Armario branco',c,.002,p)
    for i in range(4):chair(f'BANQUETA_BAR_{i+1}',(.39+i*.71,8.88,0),c,p,0,True)
    box('Cuba bar',(1.75,9.46,1.024),(.41,.30,.012),'Inox',c,.015,p)
    g.curve('Torneira bar',[(1.75,9.66,1),(1.75,9.66,1.28),(1.75,9.45,1.32),(1.75,9.42,1.19)],.01,'Cromado',c,p)
    fridge('Geladeira bar observada',(2.78,9.92,0),c,p)
    for x in [.6,1.9]:
        g.lathe('Pendente bar original',[(.13,0),(.12,.05),(.06,.16),(.03,.23)],(x,9.6,2.20),'Metal preto',c,p)
        g.rod('Cabo pendente bar',(x,9.6,2.4),(x,9.6,2.85),.005,'Metal preto',c,p)
    kitchen();bathroom('lavabo',small=True);bathroom('banho_social');bathroom('banho_suite');laundry();bedrooms()


def fridge(name,loc,col,par):
    p=g.parent(name,col,loc);p.parent=par
    box('Corpo geladeira',(0,0,.86),(.59,.61,1.72),'Inox',col,.025,p)
    for z,height in [(1.38,.56),(.54,1.05)]:box('Porta geladeira',(0,-.32,z),(.57,.035,height),'Inox',col,.018,p)
    for z in [.72,1.4]:g.rod('Puxador geladeira',(-.18,-.35,z-.16),(-.18,-.35,z+.16),.012,'Cromado',col,p)


def kitchen():
    p,c=room_parent('cozinha')
    for j in range(3):
        x=3.45+j*.59
        box('Armário inferior pia',(x,8.15,.44),(.57,.59,.88),'Armario cozinha cinza',c,.008,p)
        box('Porta cozinha',(x,7.84,.46),(.55,.025,.79),'Armario cozinha cinza',c,.005,p)
    box('Bancada pia cozinha',(4.08,8.15,.91),(1.83,.65,.04),'Granito preto',c,.005,p)
    for y in [6.68,7.28]:box('Armário bancada lateral',(4.67,y,.44),(.60,.57,.88),'Armario cozinha cinza',c,.007,p)
    box('Bancada lateral cozinha',(4.67,7.0,.91),(.64,1.35,.04),'Granito preto',c,.005,p)
    box('Cuba cozinha',(4.06,8.13,.934),(.46,.33,.01),'Inox',c,.02,p)
    g.curve('Torneira cozinha',[(4.06,8.38,.93),(4.06,8.38,1.25),(4.06,8.10,1.28),(4.06,8.06,1.12)],.012,'Cromado',c,p)
    box('Fogão forno',(4.67,6.63,.44),(.57,.57,.87),'Inox',c,.012,p)
    box('Vidro forno',(4.35,6.63,.46),(.015,.43,.40),'TV desligada',c,.01,p)
    for x in [4.52,4.80]:
        for y in [6.48,6.78]:g.cylinder('Boca fogão',(x,y,.89),.066,.014,'Metal preto',c,p)
    for y in [7.10,7.72]:box('Armário aéreo cozinha',(4.78,y,2.10),(.36,.60,.70),'Armario cozinha cinza',c,.007,p)
    for i in range(14):box('Persiana cozinha',(4.08,8.42,2.20-i*.035),(1.35,.055,.018),'Armario branco',c,.001,p)
    fridge('Geladeira cozinha — posição aproximada',(3.48,6.58,0),c,p)


def bathroom(key,small=False):
    p,c=room_parent(key);r=ROOMS[key];x0,x1,y0,y1=r['bounds'];w=x1-x0;depth=y1-y0
    cy=y0+.45;cx=x0+.30
    # Cuba e bancada independentes; banheiro pequeno e original sob escada.
    box('Bancada banheiro',(cx,cy,.85),(.47,.70,.05),'Granito preto' if small else 'Granito escada',c,.007,p)
    if not small:box('Gabinete banheiro',(cx,cy,.43),(.43,.65,.78),'Armario branco',c,.007,p)
    g.lathe('Cuba louça',[(0,0),(.10,0),(.16,.06),(.19,.14),(.19,.16),(.175,.145),(.13,.08),(0,.06)],(cx,cy,.88 if small else .84),'Louca branca',c,p)
    box('Espelho banheiro',(x0+.018,cy,1.55),(.012,.68,.68),'Espelho fisico',c,.001,p)
    toilet=g.parent('VASO_SANITARIO_'+key,c,(x1-.31,y0+1.05,0));toilet.parent=p
    g.sphere('Base vaso sanitário',(0,0,.20),(.15,.23,.20),'Louca branca',c,toilet)
    g.sphere('Bacia vaso sanitário',(0,-.06,.39),(.18,.26,.095),'Louca branca',c,toilet)
    box('Caixa acoplada',(0,.20,.59),(.32,.14,.40),'Louca branca',c,.035,toilet)
    if not small:
        yy=y1-.76
        box('Box vidro',(x0+w/2,yy,1.02),(w-.08,.012,2.04),'Vidro transparente',c,.001,p)
        box('Piso box',(x0+w/2,y1-.39,.012),(w-.08,.72,.025),'Azulejo branco',c,.002,p)
        g.rod('Chuveiro haste',(x1-.05,y1-.40,2.1),(x1-.34,y1-.40,2.1),.012,'Cromado',c,p)
        g.cylinder('Chuveiro',(x1-.34,y1-.40,2.08),.09,.025,'Louca branca',c,p)


def laundry():
    p,c=room_parent('lavanderia')
    box('Lavanderia bancada fundo',(3.77,12.10,.90),(2.18,.59,.045),'Granito preto',c,.006,p)
    box('Lavanderia bancada L',(2.91,11.47,.90),(.57,1.24,.045),'Granito preto',c,.006,p)
    for x in [2.96,3.54]:box('Gabinete lavanderia',(x,12.10,.44),(.55,.56,.86),'Armario branco',c,.007,p)
    for x in [4.08,4.68]:
        box('Máquina lavar',(x,12.08,.44),(.56,.57,.88),'Louca branca',c,.025,p)
    g.cylinder('Porta lavadora frontal',(4.08,11.78,.43),.205,.035,'Inox',c,p,rotation=(math.pi/2,0,0))
    g.cylinder('Vidro lavadora frontal',(4.08,11.75,.43),.165,.018,'Vidro mesa',c,p,rotation=(math.pi/2,0,0))
    box('Tampa lavadora superior',(4.68,12.08,.90),(.48,.48,.035),'Vidro mesa',c,.025,p)
    box('Cuba lavanderia',(3.45,12.1,.927),(.45,.37,.012),'Inox',c,.015,p)
    for x in [2.94,4.63]:box('Armário superior lavanderia',(x,12.18,2.1),(.58,.35,.72),'Armario branco',c,.007,p)


def bed(name,loc,width,length,col,par,bunk=False):
    p=g.parent(name,col,loc,categoria='cama');p.parent=par
    levels=[.46,1.48] if bunk else [.46]
    for h in levels:
        box('Estrado cama',(0,0,h-.13),(width,length,.18),'Armario branco',col,.018,p)
        box('Colchão cama',(0,0,h),(width-.035,length-.025,.17),'Lencol',col,.06,p)
        box('Travesseiro',(0,length/2-.35,h+.14),(width*.76,.43,.13),'Lencol',col,.05,p)
    for x in [-width/2+.06,width/2-.06]:
        for y in [-length/2+.10,length/2-.10]:box('Pé cama',(x,y,.13),(.07,.07,.26),'Armario branco',col,.004,p)
    if bunk:
        for x in [-width/2,width/2]:
            for y in [-length/2,length/2]:box('Pilar beliche',(x,y,.92),(.055,.055,1.84),'Armario branco',col,.005,p)
        for j in range(5):g.rod('Degrau escada beliche',(-width/2-.04,-.52,.20+j*.28),(-width/2-.04,-.10,.20+j*.28),.016,'Armario branco',col,p)
    return p


def bedrooms():
    p,c=room_parent('quarto_azul')
    box('Parede azul referência',(2.39,.15,1.3),(.025,2.0,2.6),'Parede azul',c,.002,p)
    bed('BELICHE_quarto azul',(.69,.12,0),.86,1.90,c,p,True)
    box('Bancada escritório quarto azul',(2.16,.03,.74),(.40,1.65,.04),'Armario branco',c,.007,p)
    box('TV quarto azul',(2.34,.05,1.25),(.05,.58,.36),'TV desligada',c,.007,p)
    p,c=room_parent('quarto_branco')
    bed('CAMA_quarto branco',(3.19,-.05,0),.86,1.90,c,p)
    box('Armário quarto branco',(4.67,.20,1.3),(.48,1.7,2.6),'Armario branco',c,.01,p)
    box('Armário aéreo quarto branco',(3.14,.95,2.12),(1.20,.44,.60),'Armario branco',c,.008,p)
    p,c=room_parent('suite')
    bed('CAMA_suite',(1.48,6.62,0),1.50,1.95,c,p)
    box('Cabeceira suíte',(1.48,7.68,.68),(1.72,.09,1.1),'Lencol',c,.04,p)
    box('Armário suíte',(.31,6.78,1.3),(.53,2.2,2.6),'Madeira bar',c,.008,p)
    for y in [5.8,6.5,7.2]:box('Perfil porta armário suíte',(.59,y,1.3),(.015,.02,2.5),'Inox',c,.001,p)
    box('Painel TV suíte',(1.25,5.08,1.28),(.86,.05,1.7),'Madeira bar',c,.006,p)
    box('TV suíte',(1.25,5.02,1.52),(.80,.04,.47),'TV desligada',c,.008,p)


def text(name,body,loc,size,col,mat='Cotas tinta',rotation=(0,0,0)):
    data=bpy.data.curves.new(name,'FONT');data.body=body;data.size=size;data.align_x='CENTER';data.space_line=1.15
    o=bpy.data.objects.new(name,data);g.C[col].objects.link(o);o.location=loc;o.rotation_euler=rotation;data.materials.append(g.M[mat]);return o


def annotations():
    for r in CFG['rooms']:
        x0,x1,y0,y1=r['bounds'];level=r['level'];col='Cotas_Terreo' if level==0 else 'Cotas_Superior';z=level*CFG['estimated_dimensions_m']['floor_height']+.03
        body=r['name'].split(' · ')[0]
        if r['position_confidence']=='hypothesis':body+='\nPOSIÇÃO ESTIMADA'
        # Textos próximos ao piso não escondem a arquitetura nas vistas 3D.
        text('Rótulo '+r['id'],body,((x0+x1)/2,(y0+y1)/2,z),.16,col,'Hipotese tinta' if level else 'Cotas tinta')
    text('Aviso área não documentada','CIRCULAÇÃO / ÁREA SEM FOTO\nlayout a confirmar',(1.2,1.90,2.93),.15,'Cotas_Superior','Hipotese tinta')
    for level,col in [(0,'Cotas_Terreo'),(1,'Cotas_Superior')]:
        z=level*2.9+.04
        front=-4.85 if level==0 else CFG['estimated_dimensions_m']['upper_front_y']-.45
        rear=13.0 if level==0 else CFG['estimated_dimensions_m']['upper_back_y']+.55
        text('Cota largura estimada',r'≈ 5,00 m · ESTIMADO',(2.5,front,z),.19,col)
        text('Cota profundidade estimada',('TÉRREO BASE ≈ 8,50 m' if level==0 else 'SUPERIOR BASE ≈ 10,20 m'),(-.58,3.8,z),.18,col,rotation=(0,0,math.pi/2))
        text('Aviso sem levantamento','HIPÓTESE 3D A PARTIR DE FOTOS · NÃO É PLANTA COTADA',(2.5,rear,z),.16,col,'Hipotese tinta')
        g.rod('Linha cota largura',(0,front+.25,z),(5,front+.25,z),.005,'Cotas tinta',col)


def camera(name,loc,target,ortho=None,lens=25):
    data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);g.C['Cameras'].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    data.clip_start=.05;data.clip_end=100;data.lens=lens
    if ortho:data.type='ORTHO';data.ortho_scale=ortho
    return o


def setup():
    g.light('Luz geral exterior',(3,4,14),1800,color=(1,.91,.78),size=10,target=(2.5,4,0))
    for z in [2.6,5.4]:
        for y in [1.0,4.4,7.3]:g.light('Luz ambiente pavimento',(2.4,y,z),110,color=(1,.85,.65),size=2.0,target=(2.5,y,z-2))
    g.light('Luz fundo cobertura',(1.6,9.5,3.7),200,color=(.86,.93,1),size=2,target=(1.6,8,0))
    world=bpy.data.worlds.new('Ambiente planta 3D');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.50,.58,.66,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45;bpy.context.scene.world=world
    camera('CAM_Terreo_3D',(13,-14,17),(2.5,3.9,.5),ortho=20.5)
    camera('CAM_Superior_3D',(13,-10,17),(2.5,3.0,3.2),ortho=17.8)
    camera('CAM_Terreo_Cotas',(2.5,4.1,25),(2.5,4.1,0),ortho=19.5)
    camera('CAM_Superior_Cotas',(2.5,3.5,25),(2.5,3.5,0),ortho=12.5)
    camera('CAM_Exterior',(12,-15,10),(2.5,2.5,2.5),ortho=19)
    camera('CAM_Foto_Sala_Fundos',(3.20,.10,1.45),(2.5,7.5,1.30),lens=18)
    camera('CAM_Foto_Sala_Frente',(2.65,5.65,1.45),(2.45,.15,1.25),lens=22)
    camera('CAM_Foto_Cozinha',(4.00,6.95,1.48),(4.3,8.35,1.3),lens=16)
    # Referências são empacotadas e exibidas fora da casa, nunca como fundo de render.
    inv=json.loads((ROOT/'relatorios/referencias-originais/inventario.json').read_text())
    seen=set()
    for i,(name,meta) in enumerate(inv['inputs'].items()):
        if meta['sha256'] in seen:continue
        seen.add(meta['sha256']);im=bpy.data.images.load(str(ROOT/'referencias-originais'/name));im.pack()
        ob=bpy.data.objects.new('REF_ORIGINAL_'+name,None);ob.empty_display_type='IMAGE';ob.data=im;ob.empty_display_size=2.0;ob.location=(12+(i%4)*2.3,(i//4)*1.5,0);ob.hide_render=True;g.C['Referencias'].objects.link(ob)
    g.C['Referencias'].hide_render=True


def exclude(scene,names):
    def walk(layer):
        if layer.name in names:layer.exclude=True
        for child in layer.children:walk(child)
    walk(scene.view_layers[0].layer_collection)


def make_scenes(device):
    # Em background não há janela que mantenha cenas alternativas em uso.
    # A cena corrente é a planta inicial; fake user preserva os demais presets.
    base=bpy.context.scene;base.name='PLANTA_Terreo';base.camera=bpy.data.objects['CAM_Terreo_3D']
    configs=[('CASA_Completa','CAM_Exterior',{'Cotas_Superior','Cotas_Terreo'}),
             ('PLANTA_Superior','CAM_Superior_3D',{'Terreo','Cobertura','Corte_Superior','Cotas_Terreo','Cotas_Superior'}),
             ('PLANTA_Terreo_Cotas','CAM_Terreo_Cotas',{'Superior','Cobertura','Corte_Terreo','Cotas_Superior'}),
             ('PLANTA_Superior_Cotas','CAM_Superior_Cotas',{'Terreo','Cobertura','Corte_Superior','Cotas_Terreo'}),
             ('FOTO_Sala_Fundos','CAM_Foto_Sala_Fundos',{'Cotas_Terreo','Cotas_Superior'}),
             ('FOTO_Sala_Frente','CAM_Foto_Sala_Frente',{'Cotas_Terreo','Cotas_Superior'}),
             ('FOTO_Cozinha','CAM_Foto_Cozinha',{'Cotas_Terreo','Cotas_Superior'})]
    for name,cam,hidden in configs:
        scene=base.copy();scene.name=name;scene.camera=bpy.data.objects[cam]
        # A cópia herda exclusões; limpar antes de aplicar o preset explícito.
        def enable(l):
            l.exclude=False
            for child in l.children:enable(child)
        enable(scene.view_layers[0].layer_collection);exclude(scene,hidden)
    exclude(base,{'Superior','Cobertura','Corte_Terreo','Cotas_Superior','Cotas_Terreo'})
    for scene in bpy.data.scenes:
        scene.use_fake_user=True
        scene.render.engine='CYCLES';scene.cycles.device='GPU' if device['backend']=='OPTIX' else 'CPU';scene.cycles.samples=CFG['render']['samples'];scene.cycles.use_denoising=True;scene.cycles.seed=CFG['render']['seed'];scene.cycles.max_bounces=8;scene.cycles.transmission_bounces=6
        scene.render.resolution_x=1500;scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.view_settings.view_transform='AgX';scene.view_settings.exposure=CFG['render']['exposure']
        if scene.name.endswith('_Cotas'):scene.render.resolution_x=1200;scene.render.resolution_y=1800
        scene.unit_settings.system='METRIC';scene.unit_settings.length_unit='METERS';scene.unit_settings.scale_length=1
        scene['medidas']='Hipóteses visuais. Análise de áreas recebida é secundária e não verificada.';scene['config_sha256']=hashlib.sha256((ROOT/'config/planta-casa.json').read_bytes()).hexdigest();scene['render_device']=json.dumps(device)
    if bpy.context.window:bpy.context.window.scene=bpy.data.scenes['PLANTA_Terreo']


def main():
    global ROOT,CFG,ROOMS
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',type=Path,default=Path('.'));p.add_argument('--device',choices=['auto','cpu'],default='auto');p.add_argument('--output',type=Path);p.add_argument('--preview',action='store_true');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    ROOT=args.project_root.resolve();CFG=json.loads((ROOT/'config/planta-casa.json').read_text(encoding='utf-8'));ROOMS={r['id']:r for r in CFG['rooms']}
    assert CFG['schema_version']==1 and CFG['units']=='METERS'
    assert not CFG['confirmed_dimensions_m'],'Não promover medidas sem evidência'
    for r in CFG['rooms']:
        assert r['bounds'][0]<r['bounds'][1] and r['bounds'][2]<r['bounds'][3]
        for f in r['references']:assert (ROOT/'referencias-originais'/f).is_file()
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections):bpy.data.collections.remove(c)
    g.C.clear();g.M.clear();g.LEAF_MESHES.clear();g.RNG.seed(1202026)
    for name in ['Terreo','Superior','Escada','Cobertura','Iluminacao','Cameras','Referencias','Cotas_Terreo','Cotas_Superior']:collection(name)
    collection('Corte_Terreo',g.C['Terreo']);collection('Corte_Superior',g.C['Superior'])
    FLOORS[0]=g.parent('NIVEL_0 — térreo','Terreo');FLOORS[1]=g.parent('NIVEL_1 — superior','Superior',(0,0,CFG['estimated_dimensions_m']['floor_height']))
    materials();architecture();stairs();furniture();annotations();setup();device=g.configure_device(args.device);make_scenes(device)
    for col in ['Terreo','Superior']:
        for obj in g.C[col].objects:
            if obj.get('parede'):obj.hide_select=True
    for area in bpy.context.screen.areas if bpy.context.screen else []:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
    output=args.output or Path(CFG['output']);output=output if output.is_absolute() else ROOT/output
    assert output.suffix.lower()=='.blend';output=g.unique_path(output);output.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output))
    report={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'blend':str(output.relative_to(ROOT)) if output.is_relative_to(ROOT) else str(output),'version':bpy.app.version_string,'device':device,'objects':len(bpy.data.objects),'scenes':[s.name for s in bpy.data.scenes],'room_count':len(ROOMS),'config_sha256':hashlib.sha256((ROOT/'config/planta-casa.json').read_bytes()).hexdigest(),'source_status':'Fotos locais; áreas de análise secundária não verificadas; dimensões e implantação superior hipotéticas.'}
    (ROOT/'relatorios/planta-casa').mkdir(exist_ok=True)
    (ROOT/'relatorios/planta-casa/geracao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('HOUSE_BUILT',json.dumps(report,ensure_ascii=False),flush=True)
    if args.preview:
        scene=bpy.data.scenes['PLANTA_Terreo'];scene.render.resolution_percentage=50;scene.cycles.samples=CFG['render']['preview_samples'];scene.render.filepath=str(ROOT/'renders/planta-casa/previa-terreo.png');bpy.ops.render.render(write_still=True,scene=scene.name)


if __name__=='__main__':main()
