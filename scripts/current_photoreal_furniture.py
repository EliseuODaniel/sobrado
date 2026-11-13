"""Móveis observados: sofá cinza, cadeiras altas, rack mel e luminária em laços."""
import math
import bpy
from mathutils import Matrix,Vector
from current_photoreal_geometry import *
from current_photoreal_materials import M,assign,metric_uv


def living(c,protected):
    remove_objects(bpy.data.collections['ATUAL_AMB_sala'].objects,protected)
    for o in list(bpy.data.collections['ATUAL_Detalhes'].objects):
        if any(k in o.name for k in ['Painel TV','Rack','ATUAL TV']):remove_objects([o],protected)
    # Chaise contínua no lado da janela, encosto solto com costuras e pés cromados.
    for y in [.48,2.77]:
        for x in [.33,1.04]:cyl('Sofa pe cromado',(x,y,.045),.025,.09,'Cromado',c)
    box('Sofa base',(.69,1.65,.235),(1.02,2.68,.29),'Sofa camurca cinza',c,.09)
    box('Sofa encosto estrutural',(.29,1.65,.66),(.24,2.66,.69),'Sofa camurca cinza',c,.09)
    for y in [.35,2.94]:box('Sofa braco',(.75,y,.55),(1.20,.19,.53),'Sofa camurca cinza',c,.075)
    for i,y in enumerate([.80,1.65,2.50]):
        length=1.44 if i==0 else .87;xx=.52+length/2
        box('Sofa base chaise' if i==0 else 'Sofa caixa retratil',(xx,y,.25),(length,.82,.28),'Sofa camurca cinza',c,.055)
        pillow('Sofa assento macio',(xx,y,.47),(length+.025,.825,.22),'Sofa camurca cinza',c,power=.22)
        line('Sofa vivo assento',rounded_loop((xx,y,.445),(length,.81),.085,samples=16),.002,'Sofa camurca cinza',c,True)
        # Pillow local thickness along X by rotation Y.
        p=pillow('Sofa almofada encosto',(.46,y,.80),(.59,.83,.23),'Sofa camurca cinza',c,power=.35,wrinkle=.003,rotation=(0,math.radians(76),0))
        p['reference_photo']='sala1.webp'
    # Fundo cinza, painel de três módulos laqueados e iluminação vertical.
    box('Parede acabamento TV',(3.294,1.50,1.27),(.008,2.70,2.53),'Parede TV cinza',c,.001)
    for y in [.61,1.51,2.41]:box('Painel TV branco arredondado',(3.22,y,1.45),(.07,.884,2.07),'Branco laqueado',c,.055)
    for y in [.17,2.85]:box('Friso LED TV',(3.172,y,1.45),(.012,.011,2.06),'LED quente',c,.003)
    box('TV moldura',(3.133,1.51,1.53),(.043,1.11,.655),'Borracha',c,.012)
    box('TV tela',(3.108,1.51,1.53),(.004,1.083,.622),'Tela',c,.008)
    sphere('TV LED standby',(3.103,1.49,1.208),(.002,.002,.002),'LED quente',c)
    # Rack baixo de madeira com bordas curvadas, gavetas claras e nicho central.
    for y in [.55,2.48]:
        for x in [2.84,3.15]:rod('Rack pe inclinado',(x,y,.03),(x+.035,y,.21),.024,'Madeira mel',c)
    box('Rack carvalho corpo',(3.005,1.51,.36),(.47,2.18,.33),'Madeira mel',c,.055)
    box('Rack tampo arredondado',(2.995,1.51,.555),(.50,2.23,.065),'Madeira mel',c,.035)
    for y in [.83,2.19]:
        box('Rack gaveta branca',(2.758,y,.36),(.027,.76,.235),'Branco laqueado',c,.038)
        line('Rack puxador',( (2.738,y-.18,.445),(2.738,y+.18,.445)),.003,'Madeira mel',c)
    box('Rack nicho escuro',(2.765,1.51,.39),(.015,.45,.16),'Madeira mel',c,.005)
    box('Rack prateleira nicho',(2.77,1.51,.315),(.08,.44,.018),'Madeira mel',c,.004)
    box('Rack aparelho preto',(2.72,1.51,.35),(.10,.28,.035),'Tela',c,.004)
    curtain('Cortina sala voil',.18,2.63,.225,.025,2.49,c)
    box('Cortineiro sala',(1.42,.155,2.51),(2.52,.19,.095),'Parede branco quente',c,.012)


def chair(name,pos,angle,c,bar=False):
    # Local X transversal, assento voltado para -Y. Transformar família ao final.
    start=set(bpy.data.objects);h=.75 if bar else .47;bh=.64;w=.44
    for x in [-.185,.185]:
        for y in [-.19,.19]:
            rod(name+' perna',(x*1.07,y*1.08,.025),(x,y,h-.04),.022,'Madeira cadeiras',c)
        if bar:rod(name+' apoio lateral',(x,-.20,.29),(x,.20,.29),.015,'Madeira cadeiras',c)
    if bar:rod(name+' apoio pes',( -.19,-.2,.27),(.19,-.2,.27),.018,'Madeira cadeiras',c)
    box(name+' chassi',(0,0,h-.06),(.43,.44,.07),'Madeira cadeiras',c,.012)
    pillow(name+' assento',(0,0,h),(.465,.46,.105),'Cadeiras tecido cinza',c,power=.23,wrinkle=.0008)
    # Encosto alto contínuo e leve curvatura, topo com detalhe de madeira escura.
    p=pillow(name+' encosto',(0,.225,h+.29),(.45,.075,bh),'Cadeiras tecido cinza',c,power=.16,wrinkle=.0008)
    p.rotation_euler.x=math.radians(-5)
    box(name+' travessa topo',(0,.255,h+.605),(.46,.035,.032),'Madeira cadeiras',c,.009)
    for x in [-.208,.208]:rod(name+' espaldar',(x,.19,h-.06),(x,.265,h+.60),.012,'Madeira cadeiras',c)
    # Costuras diagonais reais nas duas faces do encosto.
    for direction in [-1,1]:
        for offset in [-.36,-.12,.12,.36]:
            pts=[]
            for i in range(80):
                z=h+.02+.55*i/79;x=offset+direction*.52*(z-h-.28)
                if abs(x)<.207:pts.append((x,.177+(z-h-.29)*.085,z))
            if len(pts)>2:line(name+' costura losango',pts,.00065,'Cadeiras tecido cinza',c)
    transform=Matrix.Translation(Vector(pos))@Matrix.Rotation(angle,4,'Z')
    for o in set(bpy.data.objects)-start:o.matrix_world=transform@o.matrix_basis


def orchid(c):
    # Orquídea branca observada, com hastes arqueadas e pétalas assimétricas.
    base=(1.60,4.50,.805)
    o=g.lathe('FIEL2 Vaso orquideas',[(0,0),(.13,0),(.19,.06),(.205,.12),(.18,.17),(.17,.16)],base,M['Cromado'].name,c.name,segments=80);mark(o)
    for k in range(7):
        a=math.tau*k/7;end=(base[0]+.32*math.cos(a),base[1]+.27*math.sin(a),1.24+.09*math.sin(k*3))
        pts=[]
        for i in range(41):
            t=i/40;pts.append((base[0]+.32*math.cos(a)*t,base[1]+.27*math.sin(a)*t,base[2]+.14+.57*math.sin(t*1.8)))
        line('Orquidea haste',pts,.003,'Grafite ripado',c)
        for j in range(5):
            t=.42+j*.13;x,y,z=pts[int(t*40)];theta=a+math.pi/2
            for m in range(5):
                b=m*math.tau/5;vertices=[];faces=[]
                # Pétala fina e curva, não um volume esférico.
                horizontal=Vector((math.cos(theta),math.sin(theta),0));vertical=Vector((0,0,1));normal=horizontal.cross(vertical)
                radial=horizontal*math.cos(b)+vertical*math.sin(b);cross=-horizontal*math.sin(b)+vertical*math.cos(b)
                for iv in range(13):
                    v=iv/12;length=.010+.057*v;width=.033*math.sin(math.pi*v)**.62
                    for iu in range(9):
                        u=-1+iu/4;point=Vector((x,y,z))+radial*length+cross*(width*u)+normal*(.010*v*v+.003*u*u)
                        vertices.append(tuple(point))
                for iv in range(12):
                    for iu in range(8):
                        q=iv*9+iu;faces.append((q,q+1,q+10,q+9))
                pet=mesh('Orquidea petala fina',vertices,faces,'Petala branca',c,True);sol=pet.modifiers.new('Membrana petala','SOLIDIFY');sol.thickness=.00025
            sphere('Orquidea miolo',(x,y-.008,z-.010),(.006,.004,.008),'Miolo orquidea',c)
    leaf=M.get('Folha orquidea') or g.basic('FIEL2 Folha orquidea',(.025,.082,.018),.35);M['Folha orquidea']=leaf
    for k in range(6):
        t=k*math.tau/6;o=sphere('Orquidea folha',(1.6+.11*math.cos(t),4.5+.11*math.sin(t),.99),(.17,.042,.012),'Folha orquidea',c);o.rotation_euler=(0,.18,t)


def dining(c,protected):
    remove_objects(bpy.data.collections['ATUAL_AMB_jantar'].objects,protected)
    box('Mesa sapata',(1.60,4.50,.045),(.66,.87,.075),'Granito preto',c,.025)
    box('Mesa base madeira',(1.60,4.50,.39),(.47,.65,.66),'Madeira cadeiras',c,.022)
    box('Mesa aro inox',(1.60,4.50,.751),(1.052,1.815,.038),'Inox',c,.012)
    box('Mesa vidro preto',(1.60,4.50,.780),(1.04,1.80,.022),'Vidro fumê mesa',c,.011)
    for x,angle in [(.80,math.pi/2),(2.40,-math.pi/2)]:
        for y in [4.04,4.96]:chair('Cadeira jantar',(x,y,0),angle,c)
    for y,angle in [(3.33,math.pi),(5.67,0)]:chair('Cadeira cabeceira',(1.6,y,0),angle,c)
    orchid(c)
    cyl('Canopla pendente',(1.60,4.50,2.50),.085,.035,'Ouro pendente',c)
    # Laço duplo espacial contínuo, mais fiel que os aros circulares do modelo anterior.
    for i in range(3):
        a=i*math.tau/3;rod('Pendente cabo fino',(1.60+.05*math.cos(a),4.50+.05*math.sin(a),2.48),(1.60+.38*math.cos(a),4.50+.29*math.sin(a),2.10+.07*math.sin(a)),.0009,'Inox',c)
    for k in [-1,1]:
        pts=[(1.60+k*.105+.225*math.cos(t),4.50+k*.025+.13*math.sin(t),2.095+k*.13*math.sin(t)) for t in [math.tau*i/180 for i in range(181)]]
        line('Pendente laco ouro',pts,.008,'Ouro pendente',c,True)
        line('Pendente difusor LED',[(x,y,z-.006) for x,y,z in pts],.004,'LED quente',c,True)



def bar_chairs(c,protected):
    old=bpy.data.collections['ATUAL_AMB_bar']
    def ischair(o):
        while o:
            if 'BANQUETA_BAR' in o.name:return True
            o=o.parent
        return False
    remove_objects([o for o in old.objects if ischair(o)],protected)
    for x in [.43,1.08,1.73,2.38]:chair('Banqueta bar',(x,8.48,0),math.pi,c,True)
