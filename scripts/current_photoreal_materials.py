"""Acabamentos da casa fotografada, com escala em metros e relevos discretos."""
import math
import bpy
import blender_primitives as g
from current_photoreal_data import ROOT
from residence07_current import world_matrix
M = {}

def basic(name, color, rough=.5, metal=0, transmission=0, emission=0):
    m = g.basic('FIEL2 '+name, color, rough, metal, transmission, emission)
    M[name] = m
    return m

def noise_finish(m, scale, distance, strength=.15):
    n,l=m.node_tree.nodes,m.node_tree.links; p=n.get('Principled BSDF')
    t=n.new('ShaderNodeTexCoord'); noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale
    l.new(t.outputs['Object'],noise.inputs['Vector'])
    bump=n.new('ShaderNodeBump');bump.inputs['Distance'].default_value=distance;bump.inputs['Strength'].default_value=strength
    l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
    return noise

def fabric(name,color):
    m=basic(name,color,.88);n,l=m.node_tree.nodes,m.node_tree.links;p=n.get('Principled BSDF')
    p.inputs['Sheen Weight'].default_value=.45;p.inputs['Sheen Roughness'].default_value=.65
    tex=n.new('ShaderNodeTexCoord');vor=n.new('ShaderNodeTexNoise');vor.inputs['Scale'].default_value=1500;vor.inputs['Roughness'].default_value=.73
    l.new(tex.outputs['Object'],vor.inputs['Vector'])
    bump=n.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.00020;bump.inputs['Strength'].default_value=.35
    l.new(vor.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(*(v*.76 for v in color),1);ramp.color_ramp.elements[1].color=(*(v*1.18 for v in color),1)
    l.new(vor.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
    m['texture_scale_m']=.00067
    return m

def wood(name,low,high):
    m=basic(name,low,.32);n,l=m.node_tree.nodes,m.node_tree.links;p=n.get('Principled BSDF')
    p.inputs['Coat Weight'].default_value=.22;p.inputs['Coat Roughness'].default_value=.26
    uv=n.new('ShaderNodeTexCoord');mp=n.new('ShaderNodeVectorMath');mp.operation='MULTIPLY';mp.inputs[1].default_value=(25,25,.7)
    l.new(uv.outputs['Object'],mp.inputs[0]);noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=3.4;noise.inputs['Detail'].default_value=3
    l.new(mp.outputs[0],noise.inputs['Vector']);r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(*low,1);r.color_ramp.elements[1].color=(*high,1)
    l.new(noise.outputs['Fac'],r.inputs[0]);l.new(r.outputs[0],p.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.00015;bump.inputs['Strength'].default_value=.18
    l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
    return m

def granite(name,light=False):
    m=basic(name,(.025,.026,.023) if not light else (.28,.26,.22),.16)
    n,l=m.node_tree.nodes,m.node_tree.links;p=n.get('Principled BSDF');p.inputs['Coat Weight'].default_value=.18
    t=n.new('ShaderNodeTexCoord');v=n.new('ShaderNodeTexVoronoi');v.inputs['Scale'].default_value=390;l.new(t.outputs['Object'],v.inputs['Vector'])
    r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.22;r.color_ramp.elements[1].position=.73
    r.color_ramp.elements[0].color=(.0025,.003,.0025,1) if not light else (.08,.075,.060,1)
    r.color_ramp.elements[1].color=(.022,.024,.021,1) if not light else (.55,.51,.41,1)
    l.new(v.outputs['Distance'],r.inputs[0]);l.new(r.outputs[0],p.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.00005;bump.inputs['Strength'].default_value=.1
    l.new(v.outputs['Distance'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal']);return m

def floor():
    m=basic('Porcelanato bege polido',(.54,.49,.41),.16);n,l=m.node_tree.nodes,m.node_tree.links;p=n.get('Principled BSDF');p.inputs['Coat Weight'].default_value=.25
    uv=n.new('ShaderNodeUVMap');uv.uv_map='FIEL2_Metros'
    b=n.new('ShaderNodeTexBrick');b.offset=0;b.inputs['Scale'].default_value=1;b.inputs['Brick Width'].default_value=.60;b.inputs['Row Height'].default_value=.60
    b.inputs['Mortar Size'].default_value=.0011;b.inputs['Mortar Smooth'].default_value=.0004
    b.inputs['Color1'].default_value=(.56,.51,.43,1);b.inputs['Color2'].default_value=(.53,.485,.405,1);b.inputs['Mortar'].default_value=(.35,.32,.26,1)
    l.new(uv.outputs['UV'],b.inputs['Vector']);l.new(b.outputs['Color'],p.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.invert=True;bump.inputs['Strength'].default_value=.30;bump.inputs['Distance'].default_value=.0008
    l.new(b.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal']);return m

def paper(name,file,repeat):
    m=basic(name,(.6,.6,.6),.85);n,l=m.node_tree.nodes,m.node_tree.links;p=n.get('Principled BSDF')
    t=n.new('ShaderNodeUVMap');t.uv_map='FIEL2_Metros';v=n.new('ShaderNodeVectorMath');v.operation='SCALE';v.inputs['Scale'].default_value=repeat;l.new(t.outputs[0],v.inputs[0])
    tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'assets/atual-fiel-v02'/file),check_existing=True);tex.image.pack();l.new(v.outputs[0],tex.inputs[0]);l.new(tex.outputs[0],p.inputs['Base Color'])
    return m

def metric_uv(o, axes=None):
    if o.type!='MESH':return
    if o.data.users>1:o.data=o.data.copy()
    uv=o.data.uv_layers.get('FIEL2_Metros') or o.data.uv_layers.new(name='FIEL2_Metros');uv.active_render=True;mat=world_matrix(o);norm=mat.to_3x3().inverted_safe().transposed()
    for face in o.data.polygons:
        normal=norm@face.normal;dominant=max(range(3),key=lambda i:abs(normal[i]));ab=axes or [(1,2),(0,2),(0,1)][dominant]
        for i in face.loop_indices:
            p=mat@o.data.vertices[o.data.loops[i].vertex_index].co;uv.data[i].uv=(p[ab[0]],p[ab[1]])

def assign(o,m):
    if o.type not in {'MESH','CURVE'}:return
    o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(M[m] if isinstance(m,str) else m)
    if o.type=='MESH':metric_uv(o)

def build():
    for name,c,r,metal in [('Parede branco quente',(.76,.75,.72),.78,0),('Branco laqueado',(.78,.78,.75),.27,0),('Branco fosco',(.74,.74,.70),.65,0),('Parede TV cinza',(.29,.30,.30),.8,0),('Cozinha cinza azulado',(.12,.16,.18),.38,0),('Grafite ripado',(.055,.063,.065),.40,0),('Inox',(.53,.56,.58),.25,1),('Cromado',(.70,.72,.74),.13,1),('Ouro pendente',(.66,.39,.095),.23,.88),('Borracha',(.009,.011,.012),.76,0),('Tela',(.004,.007,.009),.12,.15),('Azul parede',(.055,.13,.19),.8,0),('Taupe suite',(.29,.285,.275),.75,0),('Ceramica',(.80,.80,.76),.17,0)]:basic(name,c,r,metal)
    noise_finish(M['Parede branco quente'],140,.00013,.13);noise_finish(M['Inox'],700,.000025,.15);M['Inox'].node_tree.nodes.get('Principled BSDF').inputs['Anisotropic'].default_value=.4
    fabric('Sofa camurca cinza',(.12,.125,.12));fabric('Cadeiras tecido cinza',(.115,.135,.15));fabric('Colcha branca',(.77,.77,.73));fabric('Cabeceira bege',(.56,.52,.44));fabric('Cortina branca',(.70,.69,.65))
    wood('Madeira mel',(.17,.075,.024),(.47,.26,.09));wood('Madeira cadeiras',(.035,.009,.004),(.11,.035,.015));wood('Madeira suite',(.13,.065,.027),(.39,.25,.12))
    granite('Granito preto');granite('Granito cinza',True);floor()
    glass=basic('Vidro',(.97,.985,.98),.025,transmission=1);glass.node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.52
    basic('Vidro fumê mesa',(.035,.045,.044),.065,transmission=.35);M['Vidro fumê mesa'].node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.52
    basic('LED quente',(1,.67,.31),.3,emission=6)
    basic('Petala branca',(.80,.80,.76),.47);M['Petala branca'].node_tree.nodes.get('Principled BSDF').inputs['Subsurface Weight'].default_value=.045
    basic('Miolo orquidea',(.54,.29,.05),.55)
    # Tecido translúcido de cortina, sem apagar a trama no contraluz.
    c=M['Cortina branca'];n,l=c.node_tree.nodes,c.node_tree.links;bs=n.get('Principled BSDF');trans=n.new('ShaderNodeBsdfTranslucent');trans.inputs[0].default_value=(.78,.77,.73,1);mix=n.new('ShaderNodeMixShader');mix.inputs[0].default_value=.38;l.new(bs.outputs[0],mix.inputs[1]);l.new(trans.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],n.get('Material Output').inputs[0])
    paper('Papel geometrico azul','triangulos.png',1/1.20);paper('Papel coracoes','coracoes.png',1/.65);paper('Papel lavabo','aneis.png',1/.48)
    paper('Cortina suite padrao','aneis.png',1/.60);M['Cortina suite padrao'].node_tree.nodes.get('Principled BSDF').inputs['Sheen Weight'].default_value=.4
    scanned_surface(M['Madeira mel'],'wood_table_001',(.12,.050,.014),(.40,.22,.075),.7,.12)
    scanned_surface(M['Madeira suite'],'wood_table_001',(.10,.055,.023),(.36,.23,.11),.7,.10)
    scanned_surface(M['Madeira cadeiras'],'wood_table_001',(.025,.006,.003),(.10,.033,.012),1.2,.08)
    return M

def apply_original():
    mapping={'ATUAL Parede':'Parede branco quente','ATUAL Branco':'Branco laqueado','ATUAL Piso':'Porcelanato bege polido','ATUAL Pedra':'Granito preto','ATUAL Cinza':'Grafite ripado','ATUAL Tela':'Tela','Sofa cinza':'Sofa camurca cinza','Estofado cadeira cinza':'Cadeiras tecido cinza','Armario cozinha cinza':'Cozinha cinza azulado','Inox':'Inox','Cromado':'Cromado','Granito preto':'Granito preto','Granito escada':'Granito cinza','Madeira bar':'Madeira mel','Armario branco':'Branco laqueado','Louca branca':'Ceramica','Louca':'Ceramica','Lencol':'Colcha branca','Vidro transparente':'Vidro','Vidro':'Vidro','Vidro mesa':'Vidro fumê mesa','TV desligada':'Tela','Parede azul':'Azul parede'}
    changes=[]
    for o in bpy.data.objects:
        if o.type not in {'MESH','CURVE'}:continue
        changed=False
        for slot in o.material_slots:
            if not slot.material:continue
            name=slot.material.name.split('.')[0]
            if name in mapping:
                if not changed:o.data=o.data.copy();changed=True
                slot.material=M[mapping[name]]
        if changed:metric_uv(o);changes.append(o.name)
    for key in ['ATUAL_Escada','R07_Escada']:
        for o in bpy.data.collections[key].objects:
            if 'Degrau' in o.name:assign(o,'Granito cinza');metric_uv(o)
            elif 'Corrimao' in o.name or 'Montante' in o.name:assign(o,'Inox')
    return changes


def scanned_surface(m,asset,low,high,scale=1,normal_strength=.18):
    """Reutiliza captura CC0 verificada, remapeando apenas a cor ao acabamento real."""
    import json
    from current_photoreal_data import sha
    records=json.loads((ROOT/'assets/fotorrealismo-industrial/manifesto.json').read_text())['records']
    n,l=m.node_tree.nodes,m.node_tree.links;p=n.get('Principled BSDF');uv=n.new('ShaderNodeUVMap');uv.uv_map='FIEL2_Metros'
    mult=n.new('ShaderNodeVectorMath');mult.operation='SCALE';mult.inputs['Scale'].default_value=scale;l.new(uv.outputs[0],mult.inputs[0])
    for channel in ['Diffuse','Rough','nor_gl']:
        r=next(r for r in records if r['asset']==asset and r['channel']==channel);assert sha(ROOT/r['path'])==r['sha256']
        tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/r['path']),check_existing=True);tex.image.pack();l.new(mult.outputs[0],tex.inputs[0])
        if channel!='Diffuse':tex.image.colorspace_settings.name='Non-Color'
        if channel=='Diffuse':
            bw=n.new('ShaderNodeRGBToBW');l.new(tex.outputs[0],bw.inputs[0]);ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.006;ramp.color_ramp.elements[1].position=.16;ramp.color_ramp.elements[0].color=(*low,1);ramp.color_ramp.elements[1].color=(*high,1);l.new(bw.outputs[0],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
        elif channel=='nor_gl':
            normal=n.new('ShaderNodeNormalMap');normal.uv_map='FIEL2_Metros';normal.inputs['Strength'].default_value=normal_strength;l.new(tex.outputs[0],normal.inputs['Color']);l.new(normal.outputs[0],p.inputs['Normal'])
        else:
            mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY_ADD';mul.inputs[1].default_value=.25;mul.inputs[2].default_value=.30;l.new(tex.outputs[0],mul.inputs[0]);l.new(mul.outputs[0],p.inputs['Roughness'])
    m['source_asset']=asset;m['source_license']='CC0-1.0';m['texture_coordinates']='FIEL2_Metros'
