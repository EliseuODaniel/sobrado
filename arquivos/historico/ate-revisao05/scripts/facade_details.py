"""Fachada observada em exterior1/2; dimensões e telhado completo são aproximados."""
import math
import bpy
import house_geometry as h
import build_scene as g


def lines(name,segments,material,col,radius=.003):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.bevel_depth=radius;data.bevel_resolution=0;data.resolution_u=1
    for a,b in segments:
        spline=data.splines.new('POLY');spline.points.add(1)
        spline.points[0].co=(*a,1);spline.points[1].co=(*b,1)
    obj=bpy.data.objects.new(name,data);g.C[col].objects.link(obj);data.materials.append(g.M[material]);return obj


def window_trim(name,x0,x1,y,z0,z1,col,grille=False):
    for x in [x0-.035,x1+.035]:h.box(name+' acabamento vertical',(x,y,(z0+z1)/2),(.07,.075,z1-z0+.14),'Esquadria branca',col,.003)
    for z in [z0-.035,z1+.035]:h.box(name+' acabamento horizontal',((x0+x1)/2,y,z),(x1-x0+.14,.075,.07),'Esquadria branca',col,.003)
    if grille:
        segments=[]
        for i in range(11):
            x=x0+i*(x1-x0)/10;segments.append(((x,y-.045,z0),(x,y-.045,z1)))
        for i in range(8):
            z=z0+i*(z1-z0)/7;segments.append(((x0,y-.045,z),(x1,y-.045,z)))
        lines(name+' grade quadriculada',segments,'Esquadria branca',col,.006)


def materials():
    g.basic('Esquadria branca',(.86,.86,.81),.38)
    material=g.textured('Fachada areia',[(.64,.54,.40),(.66,.56,.42),(.68,.58,.44)],'stone',.88,.0006)
    for node in material.node_tree.nodes:
        if node.type=='TEX_NOISE':node.inputs['Scale'].default_value=90
    g.textured('Telha cinza',[(.04,.045,.045),(.10,.11,.11),(.17,.18,.17)],'stone',.8,.002)
    g.basic('Paver cinza',(.30,.29,.26),.95)


def build(cfg):
    d=cfg['estimated_dimensions_m'];spec=cfg['facade'];w=d['width'];front=spec['front_y'];split=spec['balcony_width'];recess=spec['balcony_recess'];level=d['floor_height']
    window_trim('Janela pequena garagem',*spec['small_window_x'],cfg['layout']['lavabo_bounds'][2]-.082,*spec['small_window_z'],'Corte_Lavabo')
    # Garagem recuada sob a própria laje, com paredes laterais contínuas.
    for x in [0,w]:
        h.wall('Parede lateral contínua garagem',(x,front),(x,0),0,'Corte_Terreo',mat='Fachada areia')
        h.box('Coluna frontal integrada',(x,front+.06,2.85),(.22,.26,5.70),'Fachada areia','Fachada',.004)
    # Parede externa vertical antes do volume sob a escada; fecha a garagem.
    s=cfg['layout']['spine_x'];rear=cfg['layout']['lavabo_bounds'][2]-.075
    wx0,wx1=spec['small_window_x'];z0,z1=spec['small_window_z']
    h.wall('Garagem parede posterior',(s,rear),(w,rear),0,'Corte_Terreo',[
        h.opening(wx0-s,wx1-s,'Janela posterior garagem','window',z0,z1,['exterior2.webp'])],mat='Fachada areia')
    h.box('Testeira laje sobre garagem',(w/2,front,level-.10),(w,.18,.20),'Fachada areia','Fachada',.003)
    # Varanda à esquerda e janela no volume frontal da direita.
    h.wall('Fachada superior direita',(split,front),(w,front),1,'Fachada',[
        h.opening(.54,1.79,'Janela frontal superior','window',1.03,2.28,['exterior2.webp'])],mat='Fachada areia')
    h.wall('Fundo recuado varanda',(0,front+recess),(split,front+recess),1,'Fachada',[
        h.opening(.77,2.27,'Janela varanda','window',.85,2.10,['exterior2.webp'])],mat='Fachada areia')
    h.box('Mureta varanda fotografada',(split/2,front,level+spec['balcony_parapet_height']/2),(split,.16,spec['balcony_parapet_height']),'Fachada areia','Fachada',.004)
    h.box('Divisória vertical varanda',(split,front+recess/2,level+1.35),(.17,recess,2.7),'Fachada areia','Fachada',.003)
    h.box('Viga superior fachada',(w/2,front,5.57),(w,.22,.27),'Fachada areia','Fachada',.004)
    for x in [.77,2.27]:h.box('Cortina varanda',(x+.06,front+recess+.055,level+1.46),(.15,.025,1.20),'Lencol','Fachada',.003)
    window_trim('Janela frontal superior',split+.54,split+1.79,front-.028,level+1.03,level+2.28,'Fachada')
    window_trim('Janela varanda',.77,2.27,front+recess-.028,level+.85,level+2.10,'Fachada')
    window_trim('Janela sala',.40,1.98,-.045,.82,2.18,'Corte_Terreo',True)
    # Rede diagonal, representada por fios editáveis em vez de uma superfície opaca.
    xmin,xmax=.13,split-.10;zmin,zmax=level+spec['balcony_parapet_height'],5.43;segments=[]
    for slope in [-1,1]:
        low=zmin-max(slope*xmin,slope*xmax);high=zmax-min(slope*xmin,slope*xmax)
        for i in range(math.ceil((high-low)/.105)+1):
            c=low+i*.105;points=[]
            for x in [xmin,xmax]:
                z=slope*x+c
                if zmin-1e-6<=z<=zmax+1e-6:points.append((x,front-.025,z))
            for z in [zmin,zmax]:
                x=(z-c)/slope
                if xmin-1e-6<=x<=xmax+1e-6:points.append((x,front-.025,z))
            if len(points)>=2:segments.append((points[0],points[-1]))
    lines('Rede de proteção varanda',segments,'Esquadria branca','Fachada',.0025)
    g.rod('Condutor pluvial frontal',(.045,front-.145,.12),(.045,front-.145,5.62),.026,'Esquadria branca','Fachada')
    h.box('Calha frontal branca',(w/2,front-.12,5.72),(w+.16,.16,.12),'Esquadria branca','Fachada',.006)
    # Piso externo intertravado na faixa à frente da garagem.
    verts=[];faces=[];xstep=.24;ystep=.12;y=-4.4
    row=0
    while y<front:
        x=-.12 if row%2 else 0
        while x<w:
            xa=max(0,x+.006);xb=min(w,x+xstep-.006);yb=min(front,y+ystep-.006)
            if xb>xa and yb>y+.006:
                i=len(verts);verts.extend([(xa,y+.006,.006),(xb,y+.006,.006),(xb,yb,.006),(xa,yb,.006)]);faces.append((i,i+1,i+2,i+3))
            x+=xstep
        y+=ystep;row+=1
    mesh=bpy.data.meshes.new('Pavimento intertravado');mesh.from_pydata(verts,[],faces);obj=bpy.data.objects.new('Pavers acesso condomínio',mesh);g.C['Terreo'].objects.link(obj);mesh.materials.append(g.M['Paver cinza'])
    for x in [1.18,1.62,4.40,4.75]:
        h.box('Protetor parede garagem',(x,.09 if x<2 else 2.70,.62),(.075,.05,.38),'Metal preto','Fachada_Detalhes_Terreo',.01)
        for z in [.52,.64,.76]:h.box('Refletor amarelo protetor',(x,.055 if x<2 else 2.665,z),(.043,.008,.055),'Rack amarelo','Fachada_Detalhes_Terreo',.005)
    for x,y in [(.42,-.50),(5.0,2.15)]:
        g.plant('Vegetação fachada',(x,y,0),1.3,'Fachada_Detalhes_Terreo','Esquadria branca')
    for x in [.42,.75,1.08]:
        h.box('Régua jardim vertical',(x,-.11,1.57),(.055,.05,1.0),'Esquadria branca','Fachada_Detalhes_Terreo',.002)
    for x,z in [(.45,1.35),(.77,1.65),(.48,1.95)]:g.plant('Vaso jardim vertical',(x,-.22,z),.24,'Fachada_Detalhes_Terreo','Ceramica creme')
    # Cobertura em duas águas é hipótese baseada nas unidades vizinhas, não medida.
    roof_vertices=[];roof_faces=[];eave=spec['roof_eave_z'];ridge=spec['roof_ridge_z'];yb=d['upper_back_y']+.15
    def roof_z(x):return eave+(ridge-eave)*(1-abs(x-w/2)/(w/2+.14))
    for side in [0,1]:
        xa,xb=(-.14,w/2) if side==0 else (w/2,w+.14)
        i=len(roof_vertices);roof_vertices.extend([(xa,front-.18,roof_z(xa)),(xb,front-.18,roof_z(xb)),(xb,yb,roof_z(xb)),(xa,yb,roof_z(xa))]);roof_faces.append((i,i+1,i+2,i+3))
    mesh=bpy.data.meshes.new('Cobertura inclinada aproximada');mesh.from_pydata(roof_vertices,[],roof_faces);obj=bpy.data.objects.new('Telhado duas águas — hipótese do conjunto',mesh);g.C['Cobertura'].objects.link(obj);mesh.materials.append(g.M['Telha cinza']);obj['status']=spec['roof_shape_status']
    segments=[]
    for i in range(32):
        x=-.12+i*(w+.24)/31;segments.append(((x,front-.18,roof_z(x)+.012),(x,yb,roof_z(x)+.012)))
    for i in range(29):
        y=front-.18+i*(yb-front+.18)/28
        for xa,xb in [(-.14,w/2),(w/2,w+.14)]:segments.append(((xa,y,roof_z(xa)+.012),(xb,y,roof_z(xb)+.012)))
    lines('Juntas telhas aproximadas',segments,'Metal preto','Cobertura',.006)
    # Contexto de fachada repetida, apenas nas câmeras externas; sem interiores.
    col='Contexto_Condominio'
    floor=h.floor_rect('Contexto piso circulação',(-w,2*w,-10,front),0,'Rejunte',col,.08);floor.location.z-=.02
    for offset in [-w,w]:
        root=g.parent('Contexto unidade vizinha aproximada',col,(offset,0,0),status='contexto inferido pela repetição da fachada; sem planta interna')
        h.box('Contexto parede fundo garagem',(w/2,2.79,1.35),(w,.12,2.7),'Fachada areia',col,.003,root)
        h.box('Contexto piso garagem',(w/2,(front+2.79)/2,-.07),(w,2.79-front,.12),'Piso creme',col,.003,root)
        h.box('Contexto parede sala',(1.1,0,1.35),(2.2,.12,2.7),'Fachada areia',col,.003,root)
        h.box('Contexto janela térrea',(1.1,-.07,1.5),(1.30,.018,1.25),'Vidro transparente',col,.001,root)
        for x in [0,w]:h.box('Contexto pilar vizinho',(x,front,2.85),(.22,.24,5.7),'Fachada areia',col,.003,root)
        for z,height in [(3.40,1.00),(5.55,.30)]:h.box('Contexto faixa fachada',(w/2,front,z),(w,.18,height),'Fachada areia',col,.003,root)
        h.box('Contexto volume direito',(4.38,front,4.65),(2.42,.16,1.50),'Fachada areia',col,.003,root)
        for x,y,z in [(4.25,front-.09,4.60),(1.50,front+.90,4.55)]:
            h.box('Contexto janela vizinha',(x,y,z),(1.25,.02,1.20),'Vidro transparente',col,.001,root)
            for xx in [x-.67,x+.67]:h.box('Contexto moldura vizinha',(xx,y-.025,z),(.07,.06,1.32),'Esquadria branca',col,.002,root)
