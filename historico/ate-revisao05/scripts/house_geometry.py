"""Primitivas de modelagem compartilhadas; implantação definida pelo gerador e pela configuração."""
import json
import math
import bpy
from mathutils import Vector
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
        'Rack amarelo':((.85,.40,.012),.35,0),
        'Cinza parede TV':((.23,.24,.23),.85,0),
        'Metal preto':((.015,.017,.016),.36,.7),
        'Inox':((.40,.44,.46),.25,.9),
        'Cromado':((.55,.59,.61),.1,.98),
        'Vidro mesa':((.006,.010,.009),.08,.25),
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
        'Padrao lavabo azul':((.12,.16,.22),.8,0),
        'Terra':((.018,.012,.007),.95,0)
    }
    for name,(color,rough,metal) in simple.items():g.basic(name,color,rough,metal)
    g.basic('Vidro transparente',(.95,.98,1),.05,transmission=1)
    g.basic('Lampada quente',(1,.62,.25),.3,emission=4)
    for i,c in enumerate([(.04,.13,.018),(.11,.22,.035),(.20,.30,.04),(.025,.09,.01)]):g.basic('Folha '+str(i),c,.5)
    g.textured('Granito escada',[(.035,.04,.035),(.20,.21,.19),(.45,.46,.40)],'stone',.3,.002)
    g.textured('Granito preto',[(.003,.004,.003),(.022,.025,.02),(.075,.07,.05)],'stone',.15,.002)
    wood=g.textured('Madeira bar',[(.10,.035,.012),(.22,.09,.032),(.30,.15,.07)],'wood',.45,.0015)
    next(node for node in wood.node_tree.nodes if node.type=='VECT_MATH').inputs[1].default_value=(1.5,.6,25)
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
        header_col='Vergas_Terreo' if level==0 else 'Vergas_Superior'
        target=header_col if suffix=='verga' and header_col in g.C else col
        o=box(name+' '+suffix,loc,size,mat,target,.003,FLOORS[level]);o['parede']=True;o['pavimento']=level
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


def chair(name,loc,col,par,rotation=0,stool=False):
    p=g.parent(name,col,loc,categoria='banqueta_original' if stool else 'cadeira_original')
    p.parent=par;p.rotation_euler[2]=rotation
    h=.73 if stool else .46
    box('Assento estofado',(0,0,h),(.42,.43,.08),'Estofado cadeira cinza',col,.03,p)
    box('Encosto estofado',(0,.19,h+.23),(.42,.07,.43),'Estofado cadeira cinza',col,.024,p)
    box('Acabamento madeira encosto',(0,.19,h+.465),(.44,.075,.025),'Madeira bar',col,.004,p)
    for x in [-.17,.17]:
        for y in [-.16,.16]:box('Pé cadeira',(x,y,h/2),(.035,.035,h),'Madeira bar',col,.003,p)
    return p


def fridge(name,loc,col,par):
    p=g.parent(name,col,loc);p.parent=par
    box('Corpo geladeira',(0,0,.86),(.59,.61,1.72),'Inox',col,.025,p)
    for z,height in [(1.38,.56),(.54,1.05)]:box('Porta geladeira',(0,-.32,z),(.57,.035,height),'Inox',col,.018,p)
    for z in [.72,1.4]:g.rod('Puxador geladeira',(-.18,-.35,z-.16),(-.18,-.35,z+.16),.012,'Cromado',col,p)
    return p


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


def text(name,body,loc,size,col,mat='Cotas tinta',rotation=(0,0,0)):
    data=bpy.data.curves.new(name,'FONT');data.body=body;data.size=size;data.align_x='CENTER';data.space_line=1.15
    o=bpy.data.objects.new(name,data);g.C[col].objects.link(o);o.location=loc;o.rotation_euler=rotation;data.materials.append(g.M[mat]);return o


def camera(name,loc,target,ortho=None,lens=25):
    data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);g.C['Cameras'].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    data.clip_start=.05;data.clip_end=100;data.lens=lens
    if ortho:data.type='ORTHO';data.ortho_scale=ortho
    return o


def exclude(scene,names):
    def walk(layer):
        if layer.name in names:layer.exclude=True
        for child in layer.children:walk(child)
    walk(scene.view_layers[0].layer_collection)
