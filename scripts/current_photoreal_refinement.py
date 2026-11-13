"""Refinamento em escala de imagem: tecidos capturados e flores de orquídea finas."""
import json
import math
import random
import bpy
from mathutils import Vector
import blender_primitives as g
from current_photoreal_data import ROOT,sha
from current_photoreal_materials import M,metric_uv
from current_photoreal_geometry import mesh,line,sphere


def fabric_material(name,asset,color,normal_strength,sheen):
    records=json.loads((ROOT/'assets/atual-fiel-v02/tecidos/manifesto.json').read_text())['records'];items={r['channel']:r for r in records if r['asset']==asset}
    mat=bpy.data.materials['FIEL2 '+name];nodes,links=mat.node_tree.nodes,mat.node_tree.links;nodes.clear();bs=nodes.new('ShaderNodeBsdfPrincipled');out=nodes.new('ShaderNodeOutputMaterial');links.new(bs.outputs[0],out.inputs[0])
    bs.inputs['Sheen Weight'].default_value=sheen;bs.inputs['Sheen Roughness'].default_value=.68;bs.inputs['IOR'].default_value=1.46
    uv=nodes.new('ShaderNodeUVMap');uv.uv_map='FIEL2_Metros';scale=nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';dims=items['Diffuse']['dimensions_m'];scale.inputs[1].default_value=(1/dims[0],1/dims[1],1);links.new(uv.outputs[0],scale.inputs[0])
    for channel,r in items.items():
        path=ROOT/r['path'];assert sha(path)==r['sha256'];tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(path),check_existing=True);tex.image.pack();tex.label=asset+' / '+channel+' / '+r['resolution'].upper()+' CC0';links.new(scale.outputs[0],tex.inputs[0])
        if channel!='Diffuse':tex.image.colorspace_settings.name='Non-Color'
        if channel=='Diffuse':
            # A captura mantém a trama e a variação de cor; o tom é aproximado ao tecido fotografado.
            bw=nodes.new('ShaderNodeRGBToBW');links.new(tex.outputs[0],bw.inputs[0]);mean=r['luminance_linear_mean'];divide=nodes.new('ShaderNodeMath');divide.operation='DIVIDE';divide.inputs[1].default_value=mean;links.new(bw.outputs[0],divide.inputs[0])
            ramp=nodes.new('ShaderNodeMapRange');ramp.inputs['From Min'].default_value=.55;ramp.inputs['From Max'].default_value=1.5;ramp.inputs['To Min'].default_value=.72;ramp.inputs['To Max'].default_value=1.25;links.new(divide.outputs[0],ramp.inputs[0])
            mul=nodes.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;mul.inputs[1].default_value=(*color,1);links.new(ramp.outputs[0],mul.inputs[2]);links.new(mul.outputs[0],bs.inputs['Base Color'])
        elif channel=='nor_gl':
            normal=nodes.new('ShaderNodeNormalMap');normal.uv_map='FIEL2_Metros';normal.inputs['Strength'].default_value=normal_strength;links.new(tex.outputs[0],normal.inputs['Color']);links.new(normal.outputs[0],bs.inputs['Normal'])
        elif channel=='Rough':
            links.new(tex.outputs[0],bs.inputs['Roughness'])
            if bs.inputs.get('Diffuse Roughness'):links.new(tex.outputs[0],bs.inputs['Diffuse Roughness'])
        elif channel=='anisotropy_strength':links.new(tex.outputs[0],bs.inputs['Anisotropic'])
        elif channel=='anisotropy_rotation':links.new(tex.outputs[0],bs.inputs['Anisotropic Rotation'])
        elif channel=='spec_ior':links.new(tex.outputs[0],bs.inputs['Specular IOR Level'])
    mat['source_asset']=asset;mat['source_license']='CC0-1.0';mat['measured_capture_dimensions_m']=dims;mat['color_status']='Cor ajustada visualmente às fotos; sem medição colorimétrica do móvel.'
    return mat


def fabrics():
    used=[]
    for name,asset,color,normal,sheen in [
        ('Sofa camurca cinza','scuba_suede',(.105,.11,.115),1.0,.52),
        ('Cadeiras tecido cinza','bi_stretch',(.115,.135,.15),1.0,.45),
        ('Colcha branca','waffle_pique_cotton',(.74,.735,.70),.80,.38),
    ]:used.append(fabric_material(name,asset,color,normal,sheen).name)
    for o in bpy.data.objects:
        if o.type=='MESH' and any(s.material and s.material.name in used for s in o.material_slots):metric_uv(o)
    return used


def material(name,color,rough,subsurface=0):
    mat=bpy.data.materials.get('FIEL2 '+name) or g.basic('FIEL2 '+name,color,rough)
    nodes,links=mat.node_tree.nodes,mat.node_tree.links;nodes.clear();bs=nodes.new('ShaderNodeBsdfPrincipled');out=nodes.new('ShaderNodeOutputMaterial');links.new(bs.outputs[0],out.inputs[0]);bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Subsurface Weight'].default_value=subsurface
    if bs.inputs.get('Subsurface Scale'):bs.inputs['Subsurface Scale'].default_value=.002
    if bs.inputs.get('Thin Wall'):bs.inputs['Thin Wall'].default_value=True
    M[name]=mat;g.M[mat.name]=mat;return mat


def sheet(name,center,radial,cross,normal,length,width,curl,mat,c,*,roundness=.62):
    nu,nv=16,22;verts=[];faces=[]
    for j in range(nv+1):
        v=j/nv;w=width*math.sin(math.pi*v)**roundness
        for i in range(nu+1):
            u=-1+2*i/nu;point=center+radial*(.004+length*v)+cross*(w*u)+normal*(curl*v*v+.003*u*u*math.sin(math.pi*v))
            verts.append(tuple(point))
    for j in range(nv):
        for i in range(nu):
            q=j*(nu+1)+i;faces.append((q,q+nu+1,q+nu+2,q+1))
    o=mesh(name,verts,faces,mat,c,True);uv=o.data.uv_layers.new(name='Botanica')
    for i,loop in enumerate(o.data.loops):
        index=loop.vertex_index;uv.data[i].uv=(index%(nu+1)/nu,index//(nu+1)/nv)
    solid=o.modifiers.new('Membrana botanica','SOLIDIFY');solid.thickness=.00018
    return o


def orchids():
    c=bpy.data.collections['FIEL2_Mobiliario_Terreo'];g.C[c.name]=c
    M.update({m.name.removeprefix('FIEL2 '):m for m in bpy.data.materials if m.name.startswith('FIEL2 ')})
    removed=[]
    for o in list(bpy.data.objects):
        if o.name.startswith('FIEL2 Orquidea '):removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
    material('Petala branca',(.83,.815,.78),.48,.11);material('Garganta orquidea',(.58,.36,.055),.46,.05);material('Miolo rosa orquidea',(.31,.06,.10),.5,.03)
    leaf=material('Folha orquidea',(.016,.055,.012),.43,.035)
    petal=M['Petala branca'];n,l=petal.node_tree.nodes,petal.node_tree.links;p=n.get('Principled BSDF');uv=n.new('ShaderNodeUVMap');uv.uv_map='Botanica';wave=n.new('ShaderNodeTexWave');wave.wave_type='BANDS';wave.bands_direction='X';wave.inputs['Scale'].default_value=8;wave.inputs['Distortion'].default_value=2.4;l.new(uv.outputs[0],wave.inputs[0]);bump=n.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.000025;bump.inputs['Strength'].default_value=.13;l.new(wave.outputs[0],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
    # Folhas carnosas com curvatura, nervura central e extremidade arredondada.
    rng=random.Random(73);base=Vector((1.6,4.5,.968))
    for k in range(6):
        a=k*math.tau/6+.18;radial=Vector((math.cos(a),math.sin(a),-.06));cross=Vector((-math.sin(a),math.cos(a),0));normal=Vector((0,0,1))
        sheet('Orquidea folha carnosa',base,radial,cross,normal,.17+rng.uniform(-.025,.025),.042,-.027,'Folha orquidea',c,roundness=.38)
        line('Orquidea nervura folha',[tuple(base+radial*(.01+.16*i/24)+Vector((0,0,-.027*(i/24)**2+.002))) for i in range(25)],.00065,'Folha orquidea',c)
    flowers=0
    for k in range(7):
        a=k*math.tau/7;radius=[.23,.14,.035,.18,.22,.07,.16][k]+rng.uniform(-.012,.012);height=[.29,.34,.36,.28,.33,.35,.30][k]+rng.uniform(-.008,.008)
        def stem(t):return base+Vector((radius*math.cos(a)*t,radius*math.sin(a)*t,.015+height*math.sin(t*1.68)))
        line('Orquidea haste natural',[tuple(stem(i/50)) for i in range(51)],.0023,'Folha orquidea',c)
        for j in range(5):
            t=.48+j*.115;center=stem(t);azimuth=a+.14*math.sin(j*2+k);N=Vector((math.cos(azimuth),math.sin(azimuth),.10)).normalized();H=Vector((-math.sin(azimuth),math.cos(azimuth),0));V=N.cross(H).normalized()
            line('Orquidea pedicelo',[tuple(center-N*.015),tuple(center),tuple(center+N*.007)],.0012,'Folha orquidea',c)
            # Duas pétalas laterais largas, três sépalas e labelo dobrado.
            for angle,length,width,roundness in [(0,.035,.028,.55),(math.pi,.035,.028,.55),(math.pi/2,.041,.014,.80),(7*math.pi/6,.039,.012,.8),(11*math.pi/6,.039,.012,.8)]:
                angle+=rng.uniform(-.065,.065);radial=H*math.cos(angle)+V*math.sin(angle);cross=-H*math.sin(angle)+V*math.cos(angle)
                sheet('Orquidea petala botanica',center,radial,cross,N,length*rng.uniform(.91,1.08),width,.010+rng.uniform(-.003,.003),'Petala branca',c,roundness=roundness)
            sheet('Orquidea labelo',center+N*.005-V*.005,-V,H,N,.019,.010,.017,'Petala branca',c,roundness=.55)
            throat=center+N*.011-V*.006;sphere('Orquidea garganta',throat,(.004,.004,.005),'Garganta orquidea',c)
            spot=center+N*.018-V*.013;sphere('Orquidea mancha labelo',spot,(.003,.002,.003),'Miolo rosa orquidea',c)
            flowers+=1
    return {'replaced_objects':removed,'flower_count':flowers,'stem_count':7,'top_height_m_approx':1.35,'status':'Geometria botânica aproximada pela orquídea branca das fotos; não é escaneamento da planta real.'}
