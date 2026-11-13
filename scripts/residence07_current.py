"""Estado atual por fotos na base métrica 07; móveis sem deformação de escala."""
import argparse
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix,Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
import blender_primitives as g
import residence07_build as base
import residence07_geometry as geo
import residence07_studies_data as data
import residence07_studies_scene as s

ROOMS={}
FURNITURE=[]


def world_matrix(obj):
    return world_matrix(obj.parent)@obj.matrix_parent_inverse@obj.matrix_basis if obj.parent else obj.matrix_basis.copy()


def ancestry(obj):
    names=[]
    while obj is not None:names.append(obj.name);obj=obj.parent
    return names


def furniture():
    source=geo.ROOT/data.CFG['current']['furniture_source']
    wanted=['AMB_sala','AMB_jantar','AMB_bar','AMB_cozinha','AMB_lavabo','AMB_lavanderia','AMB_quarto_azul','AMB_quarto_branco']
    with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.collections=[n for n in wanted if n in src.collections]
    g.M.update({m.name:m for m in bpy.data.materials})
    for oldcol in dst.collections:
        room=oldcol.name.split('.')[0];target=s.collection('ATUAL_'+room);ROOMS[room]=target
        originals=list(oldcol.objects);worlds={o:world_matrix(o) for o in originals};clones={};desired={}
        for obj in originals:
            family=ancestry(obj);name=obj.name
            if room=='AMB_sala' and (any(n.startswith('TV_E_RACK') for n in family) or name.startswith('Fundo cinza painel')):continue
            if room=='AMB_cozinha' and name.startswith('Bancada pia cozinha'):continue
            if room=='AMB_quarto_branco' and name.startswith('Armário quarto frente'):continue
            if room=='AMB_lavabo' and ('Piso' in name or 'parede' in name.lower()):continue
            mat=worlds[obj].copy();x,y,z=mat.translation
            if room=='AMB_sala':delta=(.04,-.05,0)
            elif room=='AMB_jantar':delta=(.08,-1.30,0)
            elif room=='AMB_bar':delta=(0,-.10,0)
            elif room=='AMB_cozinha':
                fridge=any('Geladeira cozinha' in n for n in family)
                delta=(.65 if x>=4.95 else .30,-.12 if fridge else -.54,0)
                if 'Cuba cozinha' in name or 'Torneira cozinha' in name:delta=(.62,-.54,0)
            elif room=='AMB_lavanderia':delta=(.65 if x>=4.95 else .30,-.10,0)
            elif room=='AMB_lavabo':delta=(.40,.10,0)
            elif room=='AMB_quarto_azul':delta=(.75,-.65,-.20)
            else:delta=(.85,.30,-.20)
            mat.translation+=Vector(delta)
            if room=='AMB_quarto_azul' and name.startswith(('Parede azul','TV quarto')):mat.translation.x=3.46 if name.startswith('Parede') else 3.49
            new=obj.copy();new.name='ATUAL '+name;new.parent=None;new.matrix_world=mat;new.hide_render=False;new.hide_viewport=False
            new['photo_room']=room;new['source_furniture']=str(source.relative_to(geo.ROOT));new['furniture_scale_preserved']=True
            target.objects.link(new);clones[obj]=new;desired[obj]=mat
        for old,new in clones.items():
            if old.parent in clones:
                new.parent=clones[old.parent];new.matrix_parent_inverse=Matrix.Identity(4);new.matrix_basis=desired[old.parent].inverted_safe()@desired[old]
            else:new.matrix_world=desired[old]
        FURNITURE.extend(clones.values())
    return source


def architecture():
    groups={key:s.collection('ATUAL_'+key) for key in ['Arquitetura','Terreo','Superior','Corte_Terreo','Corte_Superior']}
    for level,suffix in [(0,'Terreo'),(1,'Superior')]:
        for kind in ['Paredes_','Piso_','Esquadrias_']:
            for old in bpy.data.collections['R07_'+kind+suffix].objects:
                if old.get('wall_id')=='T-fundos-sala' or any('PJ1-jardim' in n for n in ancestry(old)):continue
                obj=old.copy();obj.name='ATUAL BASE '+old.name
                if kind in ['Paredes_','Piso_']:
                    obj.data=old.data.copy();obj.data.materials.clear();obj.data.materials.append(s.M['ATUAL Parede' if kind=='Paredes_' else 'ATUAL Piso'])
                    if kind=='Piso_':
                        obj.data.materials.append(s.M['ATUAL Branco'])
                        for face in obj.data.polygons:
                            if face.normal.z<-.5:face.material_index=1
                groups[suffix].objects.link(obj);groups['Arquitetura'].objects.link(obj)
        for old in bpy.data.collections['R07_Corte_'+suffix].objects:
            if old.get('wall_id')=='T-fundos-sala':continue
            obj=old.copy();obj.name='ATUAL CORTE '+old.name;obj.data=old.data.copy();obj.data.materials.clear();obj.data.materials.append(s.M['ATUAL Parede'])
            groups['Corte_'+suffix].objects.link(obj)
    stairs=s.collection('ATUAL_Escada');s.copy_objects(bpy.data.collections['R07_Escada'],stairs,g.M.get('Granito escada',s.M['ATUAL Pedra']),prefix='ATUAL ')
    for obj in stairs.objects:groups['Arquitetura'].objects.link(obj);groups['Terreo'].objects.link(obj)
    return groups


def rear():
    col=s.collection('ATUAL_Fundos');roof=s.collection('ATUAL_Cobertura_Fundos')
    for i,(x0,x1,y0,y1) in enumerate([[0,3.30,5.70,10.40],[3.30,6.35,7.20,10.40]]):
        base.prism('ATUAL Piso fundos '+str(i),[[x0,y0],[x1,y0],[x1,y1],[x0,y1]],-.15,0,'ATUAL Piso',col.name)
    pieces=[('Muro oeste',(.075,8.05,1.40),(.15,4.70,2.80)),('Muro leste',(6.30,8.80,1.40),(.10,3.20,2.80)),
        ('Fundo lazer',(1.65,10.325,1.40),(3.30,.15,2.80)),('Fundo lavanderia peitoril',(4.80,10.325,.525),(2.90,.15,1.05)),
        ('Fundo lavanderia verga',(4.80,10.325,2.525),(2.90,.15,.55)),('Janela lateral esquerda',(3.60,10.325,1.65),(.45,.15,1.20)),
        ('Janela lateral direita',(6.10,10.325,1.65),(.30,.15,1.20)),('Divisao frente',(3.375,7.425,1.35),(.15,.45,2.70)),
        ('Divisao fundo',(3.375,9.425,1.35),(.15,1.95,2.70)),('Divisao verga',(3.375,8.05,2.40),(.15,.80,.60))]
    for name,loc,size in pieces:s.box('ATUAL '+name,loc,size,s.M['ATUAL Parede'],col)
    for y in [7.65,8.45]:s.box('ATUAL Caixilho divisao',(3.375,y,1.05),(.06,.035,2.10),s.M['ATUAL Branco'],col)
    s.box('ATUAL Vidro divisao',(3.375,8.05,1.05),(.012,.76,2.05),g.M['Vidro transparente'],col,.001)
    for z in [1.075,2.225]:s.box('ATUAL Caixilho janela lavanderia',(4.90,10.25,z),(2.10,.05,.035),s.M['ATUAL Branco'],col)
    s.box('ATUAL Vidro janela lavanderia',(4.90,10.25,1.65),(2.05,.012,1.10),g.M['Vidro transparente'],col,.001)
    for i,(xa,xb,ya,yb) in enumerate([[.15,3.30,6.50,10.40],[3.45,6.25,7.20,10.40]]):
        for j in range(6):
            x=xa+j*(xb-xa)/5;s.polyline('ATUAL Viga madeira cobertura',[(x,ya,2.75),(x,yb,3.0)],.075,g.M['Madeira bar'],roof)
        mesh=bpy.data.meshes.new('ATUAL Cobertura');mesh.from_pydata([(xa,ya,2.79),(xb,ya,2.79),(xb,yb,3.04),(xa,yb,3.04)],[],[(0,1,2,3)])
        mesh.materials.append(g.M['Vidro transparente']);mesh.update();obj=bpy.data.objects.new('ATUAL Cobertura vidro '+str(i),mesh);roof.objects.link(obj)
        for y in [ya,yb]:s.box('ATUAL Travessa',((xa+xb)/2,y,2.75 if y==ya else 3.0),(xb-xa,.08,.09),g.M['Madeira bar'],roof)
    return col,roof


def details():
    col=s.collection('ATUAL_Detalhes')
    pieces=[('Painel TV',(3.235,1.40,1.42),(.065,1.15,1.65),'ATUAL Branco'),('TV',(3.18,1.40,1.48),(.045,1.05,.61),'ATUAL Tela'),
        ('Rack tampo',(3.01,1.40,.54),(.44,1.17,.045),'Madeira bar'),('Rack branco',(3.03,1.40,.33),(.38,1.12,.34),'ATUAL Branco'),
        ('Bancada pia adaptada',(4.84,6.73,.91),(2.76,.65,.045),'ATUAL Pedra'),('Modulo cozinha',(5.47,6.72,.44),(.35,.60,.88),'ATUAL Cinza')]
    for name,loc,size,mat in pieces:s.box('ATUAL '+name,loc,size,g.M[mat],col,.012)
    for i in range(17):s.box('ATUAL Ripado cozinha',(3.29,4.40+i*.065,1.28),(.055,.028,2.55),s.M['ATUAL Cinza'],col,.002)
    bar=ROOMS['AMB_bar'];stools=sorted([o for o in bar.objects if o.type=='EMPTY' and 'BANQUETA_BAR_' in o.name],key=lambda o:o.name)
    for i,obj in enumerate(stools):obj.location.x=.45+i*.65
    if stools:
        src=stools[0];copies={}
        for old in [src,*src.children_recursive]:
            new=old.copy();new.name='ATUAL Quarta banqueta '+old.name;bar.objects.link(new);copies[old]=new
        for old,new in copies.items():new.parent=copies.get(old.parent,old.parent)
        copies[src].location.x=2.40
    return col


def suite():
    col=s.collection('ATUAL_Suite')
    for zz,h,w,l,mat in [(3.00,.40,1.45,1.96,s.M['ATUAL Tecido']),(3.25,.17,1.42,1.93,s.M['ATUAL Branco'])]:s.box('ATUAL Cama suite',(1.30,.95,zz),(l,w,h),mat,col,.065)
    for y in [.59,1.31]:s.box('ATUAL Travesseiro suite',(.58,y,3.40),(.42,.63,.12),s.M['ATUAL Branco'],col,.06)
    s.box('ATUAL Cabeceira suite',(.24,.95,3.56),(.10,1.65,.98),s.M['ATUAL Tecido'],col,.05)
    for i in range(4):s.box('ATUAL Roupeiro suite',(.55+i*.71,2.89,3.88),(.70,.55,2.35),g.M['Madeira bar'],col,.01)
    for y in [.0,1.95]:
        s.box('ATUAL Apoio lateral cabeceira',(.22,y,3.47),(.10,.30,1.10),g.M['Madeira bar'],col,.012)
        s.box('ATUAL Mesa cabeceira',(.47,y,3.11),(.42,.30,.12),s.M['ATUAL Branco'],col,.01)
    for name,loc,size,mat in [('Painel TV suite',(3.265,.65,4.10),(.045,.90,1.0),g.M['Madeira bar']),('TV suite',(3.23,.65,4.18),(.035,.76,.44),s.M['ATUAL Tela']),
        ('Movel lareira suite',(3.02,.65,3.18),(.43,.78,.72),s.M['ATUAL Branco']),('Nicho lareira',(2.79,.65,3.18),(.02,.60,.45),s.M['ATUAL Tela'])]:s.box('ATUAL '+name,loc,size,mat,col,.012)
    front=s.collection('ATUAL_Detalhes_Quarto_Frente')
    s.box('ATUAL Roupeiro quarto branco',(3.79,.55,3.90),(.61,1.60,2.36),s.M['ATUAL Branco'],front,.012)
    s.box('ATUAL Armario suspenso',(5.94,.25,4.77),(.55,1.9,.78),s.M['ATUAL Branco'],front,.01)
    return col,front


def build():
    s.initialize()
    for name,color in [('Parede',(.75,.73,.67)),('Piso',(.58,.55,.47)),('Branco',(.75,.74,.69)),('Pedra',(.035,.04,.034)),('Cinza',(.10,.12,.14)),('Tecido',(.56,.53,.47)),('Tela',(.008,.012,.016))]:s.material('ATUAL '+name,color)
    source=furniture();g.M.update({m.name:m for m in bpy.data.materials})
    g.M['Madeira bar']=next(m for m in bpy.data.materials if m.name.startswith('Madeira bar'))
    groups=architecture();back,cover=rear();extra=details();su,front=suite()
    baths=s.collection('ATUAL_Banheiros')
    for old in bpy.data.collections['R07_Mobiliario_Superior'].objects:
        if any(token in old.name for token in ['Vaso sanitario','Louca','Cuba banho','Gabinete banho','Bancada banho','Espelho banho','Vidro box','Trilho box','Ducha','Chuveiro','Faixa azulejo','Base box','Lavatorio']):
            new=old.copy();new.name='ATUAL '+old.name;baths.objects.link(new)
    lower=[ROOMS[k] for k in ['AMB_sala','AMB_jantar','AMB_bar','AMB_cozinha','AMB_lavabo','AMB_lavanderia']]
    upper=[ROOMS[k] for k in ['AMB_quarto_azul','AMB_quarto_branco']]+[su,front,baths]
    allcols=[groups['Arquitetura'],back,cover,extra,*lower,*upper,bpy.data.collections['R07_Teto_Superior'],bpy.data.collections['R07_Cobertura'],bpy.data.collections['R07_Contexto']]
    jobs=[
        ('planta-terreo','Térreo com fundo aberto e móveis atuais',[3.2,4.1,20],[3.2,4.1,0],'plan0',17.5),
        ('planta-superior','Superior com móveis das referências',[3.2,4.1,22],[3.2,4.1,2.7],'plan1',17.5),
        ('terreo-3d','Térreo e área posterior',[15,-14,18],[3.2,4.7,.7],'iso0',16.8),
        ('superior-3d','Superior em 3D',[12,-10,17],[3.1,3,3.3],'iso1',12.5),
        ('sala-fundos','Sala integrada aos fundos',[2.85,.95,1.45],[1.6,6.5,1.2],'photo',19),
        ('sala-frente','Sofá cinza e mesa de vidro',[2.85,4.9,1.45],[1.3,1.3,1.0],'photo',20),
        ('cozinha','Cozinha com armários cinza',[3.65,4.65,1.5],[5.2,6.55,1.25],'photo',18),
        ('cozinha-reversa','Cozinha para a sala',[5.45,5.70,1.5],[3.6,4.7,1.2],'photo',19),
        ('bar','Lazer com quatro banquetas e vidro',[2.85,6.5,1.5],[1.65,9.7,1.3],'photo',23),
        ('lavanderia','Lavanderia separada do lazer',[3.8,7.6,1.5],[5.25,9.8,1.2],'photo',19),
        ('fundos-abertos','Abertura para a área posterior',[1.6,8.0,1.5],[1.6,3.5,1.2],'photo',21),
        ('divisao-lazer-lavanderia','Divisão entre lazer e lavanderia',[.85,8.8,1.5],[3.45,8.1,1.25],'photo',23),
        ('escada-acesso','Acesso à escada pela circulação',[3.80,3.95,1.48],[5.35,3.3,1.22],'photo',19),
        ('escada-superior','Escada e hall superior',[4.10,3.65,4.30],[5.50,3.10,1.7],'photo',20),
        ('lavabo','Lavabo sob a escada',[3.92,2.35,1.35],[5.70,2.90,.95],'photo',15),
        ('suite','Suíte e roupeiro fotografados',[3.0,-.08,4.2],[1.6,1.7,3.7],'photo',22),
        ('quarto-frente','Quarto branco',[4.65,-.78,4.18],[5.6,.7,3.7],'photo',20),
        ('quarto-fundos','Quarto azul, beliche e bancada',[3.8,4.65,4.18],[5.25,6.15,3.7],'photo',19),
        ('fachada-frontal','Fachada frontal na base 07',[3.1,-19,5.0],[3.1,2,4],'exterior',38),
        ('volumetria','Casa e cobertura posterior',[16,18,14],[3.1,4.8,3.8],'exterior',18)]
    for id,title,pos,target,mode,value in jobs:
        job=dict(id=id,title='Atual · '+title,pos=pos,target=target,mode=mode)
        if mode.startswith(('plan','iso')) or id=='volumetria':job['ortho']=value
        else:job['lens']=value
        if mode.startswith('plan'):job['top']=True
        if mode in ['plan0','iso0']:cols=[groups['Corte_Terreo'],bpy.data.collections['R07_Piso_Terreo'],bpy.data.collections['ATUAL_Escada'],back,extra,*lower]
        elif mode in ['plan1','iso1']:cols=[groups['Corte_Superior'],bpy.data.collections['R07_Piso_Superior'],*upper,bpy.data.collections['R07_Escada']]
        else:cols=allcols
        folder='01-plantas' if mode.startswith(('plan','iso')) else '03-exteriores' if mode=='exterior' else '02-ambientes'
        s.camera_scene(job,cols,geo.ROOT/data.CFG['current_renders']/folder/(id+'.png'),prefix='ATUAL_',exposure=-.9 if mode.startswith(('plan','iso')) or mode=='exterior' else -.1)
    s.finish_build('atual',geo.ROOT/data.CFG['current_blend'],{'photo_directory':data.CFG['current']['photo_directory'],'furniture_source':str(source.relative_to(geo.ROOT)),
        'furniture_source_sha256':geo.sha(source),'photo_rooms':list(ROOMS),'furniture_objects':len(FURNITURE),'rear_opening':data.CFG['current']['rear_opening'],'current_notes':data.CFG['current']['notes']})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--render-only',action='store_true');p.add_argument('--preview',action='store_true');p.add_argument('--only')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if args.render_only:s.render('atual',args.preview,args.only)
    else:build()
