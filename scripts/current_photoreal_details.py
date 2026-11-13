"""Acabamentos, eletrodomésticos e dormitórios reconstruídos pelas referências."""
import json
import math
import bpy
from mathutils import Matrix,Vector
from current_photoreal_data import ROOT,REPORT
from current_photoreal_geometry import *
from current_photoreal_materials import M,assign,metric_uv,scanned_surface


def opening_repairs():
    official=json.loads((REPORT/'esquadrias-originais.json').read_text());repaired={}
    for row in official:
        o=bpy.data.objects.get('ATUAL BASE '+row['name'])
        if not o:continue
        o.parent=None;o.matrix_world=Matrix(row['matrix_world']);o['restored_from_official_07']=True
        repaired[o.name]=row['matrix_world']
        if o.type in {'MESH','CURVE'}:
            if 'vidro' in o.name.lower():assign(o,'Vidro')
            elif any(t in o.name for t in ['montante','travessa','central','verga','Porta','batente']):assign(o,'Branco laqueado')
            metric_uv(o)
    for suffix in ['.001','.002']:
        for root,children in [('Vaso sanitario',['Louca base','Louca assento','Louca abertura']),('Lavatorio',['Gabinete banho','Bancada banho','Cuba banho','Espelho banho'])]:
            parent=bpy.data.objects['ATUAL R07 '+root+suffix]
            for child in children:
                o=bpy.data.objects['ATUAL R07 '+child+suffix];local=o.matrix_basis.copy();o.parent=parent;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=local
                o['restored_parent']=parent.name
    return repaired


def sink_hole(counter,center,w,d,c):
    cutter=box('Gabarito recorte cuba',(center[0],center[1],center[2]),(w-.018,d-.018,.5),'Inox',c,.052)
    mod=counter.modifiers.new('Recorte real da cuba','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.context.view_layer.objects.active=counter;bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)


def kitchen(c,protected):
    old=bpy.data.collections['ATUAL_AMB_cozinha']
    # Portas e caixas existentes aproveitadas; os eletrodomésticos ganham peças próprias.
    replace=['Cuba cozinha','Torneira cozinha','Coifa corpo','Coifa duto','Boca fogão','Fogão forno','Mesa fogão','Vidro forno','Micro-ondas','Lava-louças painel','Lava-louças comando']
    remove_objects([o for o in old.objects if any(k in o.name for k in replace)],protected)
    top=bpy.data.objects['ATUAL Bancada pia adaptada'];sink_hole(top,(4.90,6.73,.934),.56,.40,c)
    bowl('Cuba cozinha profunda',(4.90,6.73,.934),.56,.40,.19,c)
    # As caixas de gabinete da base eram sólidas: retirar a face superior sob a cuba.
    open_cabinet_top(bpy.data.objects['ATUAL Armário pia cozinha.002'])
    # Torneira preta/inox com curva alta e mola.
    pts=[(4.90,6.96,.94),(4.90,6.96,1.28),(4.90,6.90,1.40),(4.90,6.76,1.43),(4.90,6.64,1.34),(4.90,6.64,1.24)]
    line('Torneira cozinha tubo',pts,.012,'Cromado',c)
    line('Torneira mangueira preta',[(4.90,6.96,1.18),(4.90,6.94,1.34),(4.90,6.88,1.42),(4.90,6.75,1.43),(4.90,6.65,1.36)],.009,'Borracha',c)
    for i in range(16):
        z=1.08+i*.012;line('Torneira mola inox',[(4.90+.018*math.cos(t),6.96+.018*math.sin(t),z+.012*t/math.tau) for t in [math.tau*j/20 for j in range(21)]],.0017,'Inox',c)
    cyl('Torneira misturador',(4.97,6.96,1.04),.02,.17,'Cromado',c)
    # Fogão orientado para oeste, ao longo da parede leste.
    box('Fogao corpo',(5.94,5.98,.445),(.56,.61,.85),'Inox',c,.034)
    box('Fogao junta porta',(5.642,5.98,.45),(.020,.545,.55),'Borracha',c,.028)
    box('Fogao vidro duplo',(5.626,5.98,.43),(.018,.50,.46),'Tela',c,.035)
    box('Fogao janela interna',(5.614,5.98,.43),(.004,.41,.33),'Vidro fumê mesa',c,.022)
    rod('Fogao puxador inox',(5.574,5.74,.72),(5.574,6.22,.72),.014,'Inox',c)
    box('Fogao faixa comandos',(5.625,5.98,.81),(.035,.565,.105),'Inox',c,.009)
    for y in [5.77,5.88,5.99,6.10,6.21]:cyl('Fogao botao',(5.60,y,.81),.023,.027,'Borracha',c,(0,math.pi/2,0))
    box('Fogao mesa esmaltada',(5.94,5.98,.884),(.57,.61,.026),'Tela',c,.02)
    for x in [5.80,6.08]:
        for y in [5.82,6.13]:
            cyl('Fogao espalhador',(x,y,.91),.05,.018,'Borracha',c)
            cyl('Fogao queimador inox',(x,y,.899),.062,.014,'Inox',c)
            for angle in [0,math.pi/2]:
                dx=.11*math.cos(angle);dy=.11*math.sin(angle)
                rod('Fogao trempe',(x-dx,y-dy,.932),(x+dx,y+dy,.932),.006,'Borracha',c)
    # Coifa com vidro curvo, corpo fino e chaminé.
    box('Coifa chamine',(6.07,5.98,2.13),(.28,.23,.62),'Inox',c,.009)
    box('Coifa motor',(5.99,5.98,1.81),(.40,.34,.10),'Inox',c,.026)
    verts=[]
    for x in [5.70,6.24]:
        for j in range(41):
            u=-1+2*j/40;verts.append((x,5.98+u*.36,1.69+.045*u*u))
    faces=[(j,j+1,j+42,j+41) for j in range(40)];o=mesh('Coifa vidro curvo',verts,faces,'Vidro',c,True);sol=o.modifiers.new('Vidro temperado 6 mm','SOLIDIFY');sol.thickness=.006
    for y in [5.87,6.09]:cyl('Coifa spot',(5.77,y,1.685),.025,.008,'LED quente',c)
    # Micro-ondas com janela, teclado, puxador e frestas de ventilação.
    box('Microondas inox',(5.99,6.61,1.57),(.43,.57,.32),'Inox',c,.025)
    box('Microondas vidro',(5.765,6.56,1.57),(.018,.415,.26),'Tela',c,.016)
    rod('Microondas puxador',(5.724,6.76,1.46),(5.724,6.76,1.68),.009,'Inox',c)
    box('Microondas painel',(5.756,6.85,1.57),(.015,.10,.26),'Borracha',c,.008)
    box('Microondas display',(5.744,6.85,1.645),(.005,.075,.038),'Tela',c,.004)
    for yy in [6.824,6.852,6.88]:
        for zz in [1.50,1.535,1.57]:cyl('Microondas tecla',(5.741,yy,zz),.007,.005,'Inox',c,(0,math.pi/2,0))
    # Lava-louças frontal orientada à circulação.
    box('Lavaloucas frente inox',(4.067,6.20,.445),(.025,.54,.74),'Inox',c,.014)
    box('Lavaloucas comando',(4.087,6.20,.78),(.012,.54,.065),'Tela',c,.005)
    rod('Lavaloucas puxador',(4.12,5.99,.715),(4.12,6.41,.715),.009,'Inox',c)
    for y in [6.03,6.11,6.19]:cyl('Lavaloucas botao',(4.098,y,.78),.009,.005,'Cromado',c,(0,math.pi/2,0))
    # Peças finas com rejunte claro e escala próxima às fotografias.
    remove_objects([o for o in old.objects if 'Azulejo metro parede' in o.name],protected)
    box('Base rejunte cozinha',(6.242,5.66,1.35),(.010,2.72,.90),'Branco fosco',c,.001)
    for row in range(10):
        for j in range(14):
            y=4.34+j*.20+(row%2)*.10
            if y<7.01:box('Azulejo metro fino',(6.232,y,.97+row*.075),(.006,.197,.072),'Ceramica',c,.0007)
    # Ajustar somente a marcenaria junto à coifa; o vão construtivo permanece intacto.
    for name,center,width in [('ATUAL Armário aéreo cozinha.001',5.355,.64),('ATUAL Armário aéreo cozinha.002',6.5725,.585)]:
        o=bpy.data.objects[name];o.location.y+=center-o.matrix_world.translation.y;o.scale.y*=width/o.dimensions.y
    bpy.context.view_layer.update()
    # Frentes dos aéreos separadas por vãos de 2 mm.
    for o in list(old.objects):
        if o.name.startswith('ATUAL Armário aéreo cozinha'):
            mat=o.matrix_world;center=mat.translation
            # Referências originais têm frente à esquerda/oeste.
            x=5.871;y=center.y;w=o.dimensions.y
            for sign in [-1,1]:box('Porta aerea cozinha',(x,y+sign*w/4,2.10),(.022,w/2-.003,.694),'Cozinha cinza azulado',c,.003)
    # Cordões, lâminas e caixa superior da persiana existente.
    for x in [4.02,5.34]:rod('Persiana cordao',(x,6.951,1.73),(x,6.951,2.27),.0012,'Branco fosco',c)
    box('Persiana caixa',(4.695,6.96,2.29),(1.91,.07,.07),'Branco laqueado',c,.008)
    # Reposicionar plantas da cozinha: vieram na coleção de lavanderia com deslocamento incorreto.
    roots=[o for o in bpy.data.collections['ATUAL_AMB_lavanderia'].objects if o.type=='EMPTY' and 'Planta janela cozinha' in o.name]
    for root in roots:root.location.y-=.46;root.location.z+=.03
    for root in roots:
        for o in [root,*root.children_recursive]:
            for oc in list(o.users_collection):oc.objects.unlink(o)
            c.objects.link(o)


def rear(c,protected,roof):
    old=bpy.data.collections['ATUAL_AMB_bar']
    # Louceiro branco e perfis em alumínio, prateleiras e copos atrás do vidro.
    for o in old.objects:
        if any(k in o.name for k in ['Armário bar perfil','Armário bar prateleira','Armário bar fundo']):assign(o,'Branco laqueado')
    for z in [1.99,2.20,2.41]:box('Louceiro prateleira vidro',(1.87,10.15,z),(1.84,.34,.008),'Vidro',c,.003)
    for j in range(9):
        for k in range(2):
            x=1.02+j*.195;y=10.04+k*.15;z=2.02 if j%2 else 2.23
            o=g.lathe('FIEL2 Copo louceiro',[(.022,0),(.026,.005),(.032,.10),(.028,.103),(.025,.009),(.020,.006)],(x,y,z),M['Vidro'].name,c.name,segments=32);mark(o)
    # Mosaico oxidado de placas pequenas com variação de cor/relevo.
    remove_objects([o for o in old.objects if 'Pedra bar original' in o.name],protected)
    tones=[(.20,.10,.045),(.28,.17,.085),(.12,.10,.075),(.35,.20,.105),(.17,.15,.115),(.39,.25,.13)]
    for i,color in enumerate(tones):M['Pedra mosaico '+str(i)]=g.basic('FIEL2 Pedra mosaico '+str(i),color,.63)
    for i,color in enumerate(tones):scanned_surface(M['Pedra mosaico '+str(i)],'slate_floor_03',tuple(v*.5 for v in color),color,2.5,.40)
    for row in range(12):
        z=1.065+row*.061
        for j in range(12):
            x=.965+j*.15+(row%2)*.075
            if x<2.72:box('Mosaico bar',(x,10.236,z),(.146,.024,.057),'Pedra mosaico '+str(RNG.randrange(len(tones))),c,.004)
    # Cuba realmente rebaixada na pedra.
    top=bpy.data.objects['ATUAL Bar tampo granito'];sink_hole(top,(1.75,9.25,1.024),.37,.30,c)
    remove_objects([o for o in old.objects if o.name=='ATUAL Cuba bar'],protected)
    bowl('Cuba bar profunda',(1.75,9.25,1.024),.37,.30,.14,c)
    # Guarnições, puxador e trilho da passagem para lavanderia.
    for z in [.025,2.09]:box('Porta divisao travessa',(3.335,8.05,z),(.07,.78,.045),'Branco laqueado',c,.004)
    rod('Porta divisao puxador',(3.29,7.75,.91),(3.29,7.75,1.11),.008,'Inox',c)
    box('Porta divisao trilho',(3.335,8.05,.012),(.075,.81,.025),'Inox',c,.003)
    # Fechar os encontros superiores que antes deixavam céu visível entre muro e vidro.
    box('Fechamento superior posterior',(3.20,10.325,2.90),(6.10,.145,.20),'Parede branco quente',roof,.002)
    for x,width,y0,y1,z0,z1 in [(.075,.15,7.28,10.40,2.80,3.0),(6.30,.10,7.84,10.40,2.80,3.0),(3.375,.15,7.20,10.40,2.75,3.0)]:
        bottom=2.70 if x==3.375 else 2.80
        verts=[(xx,y,z) for xx in [x-width/2,x+width/2] for y,z in [(y0,bottom),(y1,bottom),(y1,z1),(y0,z0)]]
        mesh('Fechamento lateral cobertura',verts,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'Parede branco quente',roof)
    # Ripas transversais da cobertura e elementos de vedação, respeitando o envelope aprovado.
    for x0,x1,y0,y1 in [(.15,3.30,6.50,10.40),(3.45,6.25,7.20,10.40)]:
        for j in range(1,6):
            y=y0+j*(y1-y0)/6;z=2.75+.25*(y-y0)/(y1-y0)
            box('Cobertura caibro transversal',((x0+x1)/2,y,z),(x1-x0,.055,.075),'Madeira mel',roof,.005)
            box('Cobertura vedacao EPDM',((x0+x1)/2,y,z+.050),(x1-x0,.016,.012),'Borracha',roof,.003)


def laundry(c,protected):
    old=bpy.data.collections['ATUAL_AMB_lavanderia']
    remove_objects([o for o in old.objects if any(k in o.name for k in ['Máquina lavar','Porta lavadora','Vidro lavadora','Tampa lavadora','Tanque lavanderia','Torneira lavanderia'])],protected)
    counter=bpy.data.objects['ATUAL Bancada lavanderia fundo'];sink_hole(counter,(4.35,10.06,.925),.49,.41,c);bowl('Tanque profundo',(4.35,10.06,.925),.49,.41,.26,c)
    open_cabinet_top(bpy.data.objects['ATUAL Gabinete lavanderia.001'])
    # Máquina frontal com aro concêntrico, vidro convexo e tambor visível.
    box('Lavadora frontal corpo',(4.98,10.025,.44),(.60,.58,.86),'Branco laqueado',c,.035)
    box('Lavadora frontal face',(4.98,9.724,.45),(.565,.025,.79),'Branco laqueado',c,.026)
    cyl('Lavadora aro externo',(4.98,9.690,.415),.218,.035,'Inox',c,(math.pi/2,0,0))
    cyl('Lavadora borracha',(4.98,9.668,.415),.193,.025,'Borracha',c,(math.pi/2,0,0))
    cyl('Lavadora tambor',(4.98,9.706,.415),.171,.065,'Inox',c,(math.pi/2,0,0))
    cyl('Lavadora vidro',(4.98,9.647,.415),.174,.017,'Vidro fumê mesa',c,(math.pi/2,0,0))
    box('Lavadora puxador',(5.165,9.636,.445),(.045,.028,.105),'Inox',c,.014)
    cyl('Lavadora seletor',(4.94,9.689,.772),.036,.023,'Inox',c,(math.pi/2,0,0))
    box('Lavadora gaveta sabao',(4.78,9.699,.773),(.18,.013,.064),'Branco fosco',c,.005)
    box('Lavadora display',(5.14,9.695,.773),(.12,.012,.046),'Tela',c,.005)
    for x in [5.08,5.14,5.20]:cyl('Lavadora teclas',(x,9.680,.724),.007,.006,'Inox',c,(math.pi/2,0,0))
    # Máquina de tampa superior, painel traseiro elevado azul/cinza.
    box('Lavadora superior corpo',(5.91,10.025,.46),(.61,.60,.90),'Branco laqueado',c,.075)
    box('Lavadora superior aro',(5.91,10.025,.92),(.62,.61,.08),'Branco laqueado',c,.06)
    box('Lavadora superior tampa',(5.91,9.99,.967),(.48,.43,.025),'Vidro fumê mesa',c,.065)
    box('Lavadora superior painel',(5.91,10.265,1.00),(.57,.12,.15),'Branco laqueado',c,.026)
    box('Lavadora superior comandos',(5.91,10.201,1.015),(.45,.012,.065),'Cozinha cinza azulado',c,.014)
    cyl('Lavadora superior seletor',(5.91,10.188,1.018),.029,.022,'Inox',c,(math.pi/2,0,0))
    # Travertino em filetes e torneira de parede.
    tones=[(.54,.47,.35),(.68,.61,.49),(.42,.37,.28),(.75,.69,.58)]
    for i,color in enumerate(tones):M['Travertino '+str(i)]=g.basic('FIEL2 Travertino '+str(i),color,.65)
    for r in range(5):
        for j in range(17):
            x=3.52+j*.16+(r%2)*.08
            if x<6.25:box('Filete travertino',(x,10.237,.953+r*.038),(.157,.014,.034),'Travertino '+str(RNG.randrange(4)),c,.002)
    rod('Tanque torneira parede',(4.35,10.22,1.14),(4.35,10.08,1.14),.011,'Cromado',c)
    rod('Tanque bica',(4.35,10.08,1.14),(4.35,10.08,1.08),.011,'Cromado',c)
    # Plantas menores no peitoril posterior, sem objetos atravessando a bancada.
    for x in [3.94,4.60,5.32]:
        g.lathe('FIEL2 Vaso lavanderia',[(0,0),(.05,0),(.065,.10),(.06,.11),(.055,.105)],(x,10.19,1.10),M['Ceramica'].name,c.name)
        for k in range(7):
            a=k*math.tau/7;rod('Planta lavanderia haste',(x,10.19,1.18),(x+.05*math.cos(a),10.19+.05*math.sin(a),1.38+.02*math.sin(k)),.0014,'Folha orquidea',c)
            p=sphere('Planta lavanderia folha',(x+.06*math.cos(a),10.19+.06*math.sin(a),1.32),(.045,.020,.006),'Folha orquidea',c);p.rotation_euler=(0,.55,a)


def bedding(name,center,size,z,c,drop=.20):
    # Colcha com dobra caída nas bordas; deformação em milímetros no topo.
    w,l=size;nu,nv=74,100;verts=[];faces=[]
    for j in range(nv+1):
        v=-1+2*j/nv
        for i in range(nu+1):
            u=-1+2*i/nu;x=center[0]+u*(w/2+.10);y=center[1]+v*(l/2+.10)
            outside=max(abs(u)*(w/2+.10)-w/2,abs(v)*(l/2+.10)-l/2,0)
            zz=z-drop*min(outside/.1,1)**.65+.0035*math.sin(39*u+5*v)*math.sin(19*v)*(.20+abs(u)**8)
            verts.append((x,y,zz))
    for j in range(nv):
        for i in range(nu):
            k=j*(nu+1)+i;faces.append((k,k+1,k+nu+2,k+nu+1))
    o=mesh(name,verts,faces,'Colcha branca',c,True);sol=o.modifiers.new('Colcha espessura 2 mm','SOLIDIFY');sol.thickness=.002;return o


def bedrooms(c,protected):
    # Suíte: preservar layout atual, corrigir tecidos, ripado e portas do roupeiro.
    old=bpy.data.collections['ATUAL_Suite']
    remove_objects([o for o in old.objects if any(k in o.name for k in ['Travesseiro','Cabeceira','Cama suite.001'])],protected)
    box('Suite fundo cabeceira',(.163,1.36,4.10),(.018,3.50,2.28),'Taupe suite',c,.002)
    for j in range(27):
        y=-.32+j*.134
        box('Suite friso vertical',(.177,y,4.10),(.003,.009,2.28),'Parede TV cinza',c,.001)
    for i,y in enumerate([.55,1.35]):
        for zz in [3.48,3.86]:box('Suite cabeceira modulo',(.24,y,zz),(.12,.785,.365),'Cabeceira bege',c,.038)
    for o in old.objects:
        if 'Roupeiro suite' in o.name:assign(o,'Madeira suite')
        if 'Apoio lateral' in o.name or 'Painel TV' in o.name:assign(o,'Madeira suite')
    for x in [.195,.905,1.615,2.325,3.035]:box('Roupeiro trilho vertical',(x,2.601,3.88),(.020,.023,2.35),'Inox',c,.003)
    for z in [2.728,5.035]:box('Roupeiro trilho horizontal',(1.615,2.60,z),(2.88,.030,.027),'Inox',c,.003)
    bedding('Suite colcha drapeada',(1.30,.95),(1.95,1.43),3.345,c,.21)
    for y in [.59,1.31]:pillow('Suite travesseiro',(.62,y,3.45),(.45,.65,.16),'Colcha branca',c,power=.5,wrinkle=.004)
    curtain('Suite cortina voil',.24,3.20,-.342,2.735,5.16,c)
    curtain('Suite cortina lateral A',.22,.63,-.275,2.735,5.16,c,'Cortina suite padrao',.065)
    curtain('Suite cortina lateral B',2.76,3.22,-.275,2.735,5.16,c,'Cortina suite padrao',.065)
    rod('Suite varao cortina',(.20,-.27,5.18),(3.23,-.27,5.18),.012,'Inox',c)
    # Split observado acima da cabeceira.
    box('Suite ar condicionado',(.29,2.35,4.92),(.25,.78,.27),'Branco laqueado',c,.055)
    for z in [4.82,4.835,4.85]:box('Suite aletas split',(.151,2.35,z),(.015,.64,.008),'Branco fosco',c,.002)
    # Quarto branco: cama com grades, armários com portas e papel delicado.
    oldwhite=bpy.data.collections['ATUAL_AMB_quarto_branco']
    remove_objects([o for o in oldwhite.objects if 'Travesseiro' in o.name],protected)
    for o in oldwhite.objects:
        if 'Colchão' in o.name:assign(o,'Colcha branca')
    box('Quarto branco papel coracoes',(6.237,.45,3.86),(.008,2.05,1.02),'Papel coracoes',c,.001)
    for y in [-.51,1.41]:
        box('Cama branca travessa',(5.60,y,3.53),(.93,.045,.055),'Branco laqueado',c,.01)
        for x in [5.18,5.39,5.60,5.81,6.02]:box('Cama branca grade',(x,y,3.36),(.035,.035,.32),'Branco laqueado',c,.009)
    box('Cama branca grade lateral',(6.04,.45,3.53),(.038,1.94,.045),'Branco laqueado',c,.008)
    for y in [-.35,-.10,.15,.40,.65,.90,1.15]:box('Cama branca ripas',(6.04,y,3.36),(.03,.035,.30),'Branco laqueado',c,.006)
    bedding('Quarto branco colcha',(5.60,.45),(.845,1.875),3.255,c,.19)
    pillow('Quarto branco travesseiro',(5.6,1.07,3.35),(.63,.43,.15),'Colcha branca',c,power=.5)
    for j in range(3):
        y=-.245+j*.53;box('Roupeiro branco porta',(4.103,y,3.9),(.018,.524,2.35),'Branco laqueado',c,.003)
        rod('Roupeiro branco puxador',(4.126,y+.16,3.62),(4.126,y+.16,3.94),.005,'Inox',c)
    for j in range(4):
        y=-.46+j*.47;box('Aereo branco porta',(5.652,y,4.77),(.022,.463,.775),'Branco laqueado',c,.003)
        rod('Aereo branco puxador',(5.628,y+.12,4.56),(5.628,y+.12,4.82),.005,'Inox',c)
    # Estante observada junto à porta.
    for z in [2.74,3.1,3.46,3.82,4.18]:box('Quarto branco estante prateleira',(4.45,1.86,z),(.53,.26,.025),'Branco laqueado',c,.005)
    for x in [4.19,4.71]:box('Quarto branco estante lateral',(x,1.86,3.46),(.025,.26,1.47),'Branco laqueado',c,.005)
    box('Quarto branco TV',(4.50,1.97,4.63),(.71,.035,.42),'Tela',c,.014)
    # Rolo acima da janela frontal.
    cyl('Quarto branco persiana',(4.75,-.991,4.89),.036,1.61,'Cabeceira bege',c,(0,math.pi/2,0))
    box('Quarto branco faixa persiana',(4.75,-.989,4.78),(1.56,.012,.23),'Cabeceira bege',c,.002)
    # Quarto azul: papel geométrico na parede de acesso e bancada de trabalho real.
    blue=bpy.data.collections['ATUAL_AMB_quarto_azul']
    remove_objects([o for o in blue.objects if 'Travesseiro' in o.name],protected)
    for xmin,xmax in [(3.45,3.50),(4.20,6.24)]:box('Papel azul junto porta',((xmin+xmax)/2,4.308,3.97),(xmax-xmin,.008,2.54),'Papel geometrico azul',c,.001)
    box('Papel azul acima porta',(3.85,4.308,5.03),(.70,.008,.43),'Papel geometrico azul',c,.001)
    # Painel azul escuro existente encontra a parede de acesso, sem volume atravessando vão.
    for o in blue.objects:
        if 'Parede azul' in o.name:assign(o,'Azul parede')
    for z in [4.60,4.95]:box('Quarto azul prateleira',(3.70,5.70,z),(.45,1.66,.038),'Branco laqueado',c,.006)
    for y in [4.93,6.47]:box('Quarto azul tampo apoio',(3.92,y,3.06),(.49,.025,.69),'Branco laqueado',c,.006)
    box('Quarto azul teclado',(3.88,5.66,3.48),(.17,.46,.025),'Borracha',c,.006)
    for row in range(4):
        for j in range(13):box('Tecla teclado',(3.825+row*.035,5.45+j*.035,3.496),(.026,.027,.006),'Grafite ripado',c,.002)
    sphere('Quarto azul mouse',(3.91,6.08,3.49),(.055,.035,.018),'Borracha',c)
    box('Quarto azul gabinete PC',(3.82,6.23,3.04),(.24,.45,.56),'Borracha',c,.015)
    line('Quarto azul cabo TV',[(3.51,5.90,3.82),(3.54,5.98,3.65),(3.60,5.98,3.47)],.003,'Borracha',c)
    for z in [3.255,4.275]:
        bedding('Beliche colcha',(5.60,5.70),(.845,1.875),z,c,.14)
        pillow('Beliche travesseiro',(5.60,6.30,z+.09),(.63,.43,.14),'Colcha branca',c,power=.5)
    # Grade de proteção e fundo do beliche, existentes na foto.
    box('Beliche grade superior',(5.12,5.70,4.48),(.035,1.88,.25),'Branco laqueado',c,.018)
    box('Beliche cabeceira',(5.60,6.65,3.86),(.91,.035,1.12),'Branco laqueado',c,.009)
    cyl('Quarto azul persiana',(4.75,6.98,4.89),.034,1.61,'Branco laqueado',c,(0,math.pi/2,0))
    # UV de papéis projetada na parede em metros.
    for o in c.objects:
        if any(t in o.name for t in ['Papel azul','papel coracoes']):metric_uv(o)


def bathrooms(c,protected):
    # O lavabo tem papel elíptico, não parede lisa.
    box('Lavabo papel elipses',(4.54,3.091,.845),(1.61,.008,1.69),'Papel lavabo',c,.001)
    # Molduras e louças dos banheiros superiores são recuperadas pelos pais em opening_repairs.
    for o in bpy.data.collections['ATUAL_Banheiros'].objects:
        if any(k in o.name for k in ['Bancada banho']):assign(o,'Granito cinza')
        if any(k in o.name for k in ['Trilho box','Ducha','Chuveiro']):assign(o,'Inox')
        if 'Gabinete banho' in o.name:assign(o,'Madeira suite')
        if 'Faixa azulejo inferior' in o.name:assign(o,'Ceramica')
    # Azulejo cerâmico branco em placas grandes nas paredes laterais dos dois banheiros.
    for x0,x1 in [(.15,1.65),(1.80,3.30)]:
        for x in [x0+.005,x1-.005]:
            for iy in range(6):
                for iz in range(5):
                    box('Banheiro placa branca',(x,3.62+iy*.50,2.97+iz*.50),(.010,.497,.497),'Ceramica',c,.0015)
        # Espelho maior e perfil metálico dos vidros.
        for z in [2.75,4.75]:box('Banheiro perfil box',((x0+x1)/2,5.48,z),(x1-x0-.04,.028,.027),'Branco laqueado',c,.004)
        rod('Banheiro puxador vidro',(x0+.82,5.451,3.68),(x0+.82,5.451,3.88),.007,'Cromado',c)
    for o in c.objects:
        if 'papel elipses' in o.name:metric_uv(o)


def sanitary_refinement(c,protected):
    """Louça com cavidade real e caixa acoplada ausente na cópia anterior."""
    for suffix in ['.001','.002']:
        root=bpy.data.objects['ATUAL R07 Vaso sanitario'+suffix];transform=root.matrix_basis.copy()
        start=set(bpy.data.objects)
        # Assento anular elíptico, sem disco preto atravessando a superfície branca.
        verts=[];faces=[];nu,nv=96,16
        for j in range(nv):
            v=math.tau*j/nv
            for i in range(nu):
                u=math.tau*i/nu;verts.append(((.156+.029*math.cos(v))*math.cos(u),-.05+(.225+.029*math.cos(v))*math.sin(u),.434+.014*math.sin(v)))
        for j in range(nv):
            for i in range(nu):faces.append((j*nu+i,j*nu+(i+1)%nu,((j+1)%nv)*nu+(i+1)%nu,((j+1)%nv)*nu+i))
        temp=mesh('Gabarito assento louca',verts,faces,'Ceramica',c,True);old=bpy.data.objects['ATUAL R07 Louca assento'+suffix];old.data=temp.data;old.location=(0,0,0);old.scale=(1,1,1);bpy.data.objects.remove(temp,do_unlink=True)
        # Corpo e interior da bacia, com fundo rebaixado.
        profile=[(.115,.16,.035),(.12,.17,.10),(.16,.22,.26),(.185,.26,.40),(.17,.245,.425),(.14,.215,.398),(.10,.16,.32),(.055,.08,.27)]
        verts=[];faces=[]
        for a,b,z in profile:
            for i in range(96):
                u=math.tau*i/96;verts.append((a*math.cos(u),-.045+b*math.sin(u),z))
        for j in range(len(profile)-1):
            for i in range(96):faces.append((j*96+i,j*96+(i+1)%96,(j+1)*96+(i+1)%96,(j+1)*96+i))
        faces.append(tuple(range(7*96,8*96)));temp=mesh('Gabarito bacia louca',verts,faces,'Ceramica',c,True);old=bpy.data.objects['ATUAL R07 Louca base'+suffix];old.data=temp.data;old.location=(0,0,0);old.scale=(1,1,1);bpy.data.objects.remove(temp,do_unlink=True)
        bpy.data.objects['ATUAL R07 Louca abertura'+suffix].hide_render=True
        box('Vaso caixa acoplada',(0,.23,.63),(.365,.155,.39),'Ceramica',c,.033)
        box('Vaso tampa caixa',(0,.23,.836),(.38,.169,.035),'Ceramica',c,.016)
        cyl('Vaso botao duplo',(0,.23,.858),.029,.005,'Cromado',c)
        sphere('Vaso agua rebaixada',(0,-.05,.273),(.054,.076,.003),'Vidro',c)
        for o in set(bpy.data.objects)-start:o.matrix_world=transform@o.matrix_basis
        # Cuba oval rebaixada no tampo, preservando a posição do gabinete.
        parent=bpy.data.objects['ATUAL R07 Lavatorio'+suffix];mat=parent.matrix_basis.copy();counter=bpy.data.objects['ATUAL R07 Bancada banho'+suffix]
        cutter=sphere('Gabarito recorte oval',(0,0,.77),(.225,.155,.25),'Ceramica',c);cutter.matrix_world=mat@cutter.matrix_basis
        bpy.context.view_layer.update();mod=counter.modifiers.new('Recorte oval real','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter;mod.solver='EXACT';bpy.context.view_layer.objects.active=counter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
        verts=[];faces=[];rings=[(.224,.154,.79),(.212,.142,.784),(.19,.12,.75),(.15,.09,.68),(.075,.045,.65)]
        for a,b,z in rings:
            for i in range(96):
                t=math.tau*i/96;verts.append((a*math.cos(t),b*math.sin(t),z))
        for j in range(4):
            for i in range(96):faces.append((j*96+i,j*96+(i+1)%96,(j+1)*96+(i+1)%96,(j+1)*96+i))
        faces.append(tuple(reversed(range(384,480))))
        temp=mesh('Gabarito cuba oval',verts,faces,'Ceramica',c,True);old=bpy.data.objects['ATUAL R07 Cuba banho'+suffix];old.data=temp.data;old.location=(0,0,0);old.scale=(1,1,1);bpy.data.objects.remove(temp,do_unlink=True)
        open_cabinet_top(bpy.data.objects['ATUAL R07 Gabinete banho'+suffix])
        start=set(bpy.data.objects)
        cyl('Banheiro ralo cuba',(0,0,.653),.023,.004,'Cromado',c)
        line('Banheiro torneira bancada',[(.22,.12,.79),(.22,.12,.97),(.14,.12,1.01),(.11,.04,1.01)],.009,'Cromado',c)
        for o in set(bpy.data.objects)-start:o.matrix_world=mat@o.matrix_basis


def open_cabinet_top(o):
    import bmesh
    o.data=o.data.copy();bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.normal.z>.9],context='FACES')
    bm.to_mesh(o.data);bm.free();o.data.update();o['sink_cabinet_open_top']=True


def glass_stair_guard(c):
    box('Guarda corpo vidro atual',(4.60,3.70,3.20),(.012,.90,.94),'Vidro',c,.009)
    for y in [3.36,4.04]:
        box('Guarda vidro fixacao inox',(4.60,y,2.79),(.065,.048,.16),'Inox',c,.007)
        cyl('Guarda vidro parafuso',(4.639,y,2.81),.009,.008,'Cromado',c,(0,math.pi/2,0))


def stair_risers(ground,upper):
    import residence07_geometry as official
    cfg=official.load();rise=cfg['stair']['rise']
    for i,poly in enumerate(official.stair_polygons(cfg)):
        z0=i*rise;z1=(i+1)*rise-.13;n=len(poly)
        verts=[(x,y,z) for z in [z0,z1] for x,y in poly]
        faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
        o=mesh('Espelho granito degrau '+str(i+1),verts,faces,'Granito cinza',ground)
        upper.objects.link(o)
