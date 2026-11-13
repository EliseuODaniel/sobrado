"""Acabamento externo observado e contexto ilustrativo para as vistas da casa atual."""
import math
import bpy
import blender_primitives as g
from current_photoreal_geometry import col,box,mesh,cyl,rod,mark
from current_photoreal_materials import M,basic,noise_finish,metric_uv
from current_photoreal_data import ROOT


def finishes():
    facade=basic('Fachada bege',(.60,.52,.38),.82);noise_finish(facade,170,.0007,.25)
    tiles=basic('Telha cinza envelhecida',(.065,.068,.060),.78);noise_finish(tiles,65,.001,.28)
    ids={'T-frente-sala','T-entrada-diagonal','T-retorno-garagem','T-garagem-lavabo','S-fachada-quarto','S-sacada','S-suite-sacada'}
    for o in bpy.data.collections['ATUAL_Arquitetura'].objects:
        if o.type!='MESH' or o.get('wall_id') not in ids:continue
        o.data=o.data.copy();idx=len(o.data.materials);o.data.materials.append(facade)
        # As faces externas recebem a cor da fachada; os ambientes ficam claros.
        for f in o.data.polygons:
            normal=o.matrix_world.to_3x3()@f.normal
            if normal.y<-.5 or (o.get('wall_id')=='T-retorno-garagem' and normal.x>.5):f.material_index=idx
    for o in bpy.data.collections['R07_Cobertura'].objects:
        if o.type not in {'MESH','CURVE'}:continue
        if any(t in o.name for t in ['Telhado','Capa telha','Fiada telhado']):
            o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(tiles)


def paving_material():
    m=basic('Paver espinha de peixe',(.35,.36,.32),.82);n,l=m.node_tree.nodes,m.node_tree.links;p=n.get('Principled BSDF')
    uv=n.new('ShaderNodeUVMap');uv.uv_map='FIEL2_Metros';scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=1/.84;l.new(uv.outputs[0],scale.inputs[0])
    for file,socket in [('paver-espinha.png','Base Color'),('paver-altura.png',None)]:
        t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'assets/atual-fiel-v02'/file),check_existing=True);t.image.pack();l.new(scale.outputs[0],t.inputs[0])
        if socket:l.new(t.outputs[0],p.inputs[socket])
        else:
            t.image.colorspace_settings.name='Non-Color';b=n.new('ShaderNodeBump');b.inputs['Distance'].default_value=.003;b.inputs['Strength'].default_value=.55;l.new(t.outputs[0],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])
    return m


def build():
    finishes();c=col('Exterior');paving_material()
    for pos,size in [((3.175,-2.85,-.025),(19.05,5.70,.01)),((4.78,1.02,-.025),(3.05,2.05,.01))]:
        o=box('Pavimento externo observado',pos,size,'Paver espinha de peixe',c,.001);metric_uv(o)
    # Unidades vizinhas repetidas apenas como volumetria de contexto; não é levantamento do condomínio.
    unit=col('Vizinho_Contexto')
    for source in ['ATUAL_Arquitetura','R07_Cobertura']:
        for o in bpy.data.collections[source].objects:unit.objects.link(o)
    # Retirar a coleção-modelo do cenário de construção; somente suas instâncias serão vistas.
    if unit.name in bpy.context.scene.collection.children:bpy.context.scene.collection.children.unlink(unit)
    neighbors=col('Vizinhos_Apenas_Fachada')
    for dx in [-6.35,6.35]:
        o=bpy.data.objects.new('FIEL2 Vizinho ilustrativo',None);o.instance_type='COLLECTION';o.instance_collection=unit;o.location.x=dx;neighbors.objects.link(o);o['context_status']='Cópia volumétrica ilustrativa da unidade 07; sem medidas verificadas dos vizinhos'
    # Vasos brancos altos e suportes em madeira vistos no acesso frontal.
    for x,y in [(.38,-.25),(5.82,1.68)]:
        g.lathe('FIEL2 Vaso fachada',[(0,0),(.17,0),(.23,.45),(.22,.48),(.20,.46)],(x,y,0),M['Branco laqueado'].name,c.name,segments=64)
        for j in range(10):
            t=j*math.tau/10;rod('Planta fachada ramo',(x,y,.42),(x+.18*math.cos(t),y+.18*math.sin(t),1.45+.12*math.sin(j)),.006,'Madeira suite',c)
            for k in range(3):
                z=.88+k*.21;leaf=g.sphere('FIEL2 Folha fachada',(x+.16*math.cos(t),y+.16*math.sin(t),z),(.14,.025,.017),M['Folha orquidea'],c.name);leaf.rotation_euler=(0,.5,t)
    for z in [.65,.95,1.25,1.55]:box('Suporte vasos fachada',(.163,-.08,z),(.045,.32,.045),'Madeira mel',c,.006)
    return c,neighbors
