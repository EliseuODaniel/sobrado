"""Reconstrução procedural editável. Executar com o Python do Blender 5.2 LTS.

Não abre nem modifica um .blend existente. Saídas já existentes são preservadas.
Os objetos mantêm geometria, materiais, luzes e hierarquia editáveis na interface.
"""
import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import random
import sys

import bpy
from mathutils import Vector

COLLECTIONS = ('Arquitetura', 'Estar', 'Jantar', 'Bar', 'Cozinha', 'Iluminacao', 'Cameras', 'Referencias')
C = {}
M = {}
RNG = random.Random()
ROOT = None
CFG = None


def args_parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', type=Path, default=Path('.'))
    p.add_argument('--quality', choices=('preview', 'final'), default='preview')
    p.add_argument('--device', choices=('auto', 'cpu'), default='auto')
    p.add_argument('--output', type=Path, help='Destino alternativo; nunca sobrescreve arquivo existente.')
    p.add_argument('--no-render', action='store_true')
    return p


def move_to(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    C[collection].objects.link(obj)
    return obj


def parent(name, collection, loc=(0, 0, 0), **props):
    obj = bpy.data.objects.new(name, None)
    C[collection].objects.link(obj)
    obj.location = loc
    obj.empty_display_type = 'PLAIN_AXES'
    obj.empty_display_size = .15
    for k, v in props.items():
        obj[k] = v
    return obj


def finish(obj, name, collection, material=None, par=None):
    obj.name = name
    move_to(obj, collection)
    if material:
        obj.data.materials.append(M[material] if isinstance(material, str) else material)
    if par:
        obj.parent = par
    return obj


def box(name, loc, size, mat, col, bevel=.01, par=None, rotation=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    finish(obj, name, col, mat, par)
    if rotation:
        obj.rotation_euler = rotation
    if bevel:
        m = obj.modifiers.new('Cantos suavizados — editável', 'BEVEL')
        m.width = bevel
        m.segments = 4 if bevel > .035 else 2
        m = obj.modifiers.new('Normais ponderadas', 'WEIGHTED_NORMAL')
    return obj


def sphere(name, loc, scale, mat, col, par=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, location=loc)
    o = bpy.context.object
    o.scale = scale
    finish(o, name, col, mat, par)
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def cylinder(name, loc, radius, depth, mat, col, par=None, vertices=32, rotation=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    finish(o, name, col, mat, par)
    if rotation:
        o.rotation_euler = rotation
    b = o.modifiers.new('Bordas', 'BEVEL')
    b.width = min(.008, radius / 5, depth / 4)
    b.segments = 2
    for p in o.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    return o


def rod(name, start, end, radius, mat, col, par=None):
    delta = Vector(end) - Vector(start)
    o = cylinder(name, (Vector(start) + Vector(end)) / 2, radius, delta.length, mat, col, par, 12)
    o.rotation_euler = delta.to_track_quat('Z', 'Y').to_euler()
    return o


def curve(name, points, radius, mat, col, par=None):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.resolution_u = 10
    data.bevel_depth = radius
    data.bevel_resolution = 2
    s = data.splines.new('BEZIER')
    s.bezier_points.add(len(points) - 1)
    for p, co in zip(s.bezier_points, points):
        p.co = co
        p.handle_left_type = p.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, data)
    C[col].objects.link(o)
    data.materials.append(M[mat])
    if par:
        o.parent = par
    return o


def lathe(name, profile, loc, mat, col, par=None, segments=40):
    verts = [(r * math.cos(i * math.tau / segments), r * math.sin(i * math.tau / segments), z)
             for r, z in profile for i in range(segments)]
    faces = []
    for j in range(len(profile) - 1):
        for i in range(segments):
            a = j * segments + i
            b = j * segments + (i + 1) % segments
            faces.append((a, b, b + segments, a + segments))
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts, [], faces)
    data.update()
    o = bpy.data.objects.new(name, data)
    C[col].objects.link(o)
    o.location = loc
    o.data.materials.append(M[mat])
    if par:
        o.parent = par
    for p in data.polygons:
        p.use_smooth = True
    return o


def basic(name, color, rough=.5, metal=0, transmission=0, emission=0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    p.inputs['Transmission Weight'].default_value = transmission
    p.inputs['IOR'].default_value = 1.46
    if emission:
        p.inputs['Emission Color'].default_value = (*color, 1)
        p.inputs['Emission Strength'].default_value = emission
    M[name] = m
    return m


def textured(name, colors, kind, rough=.5, bump=.005):
    m = basic(name, colors[0], rough)
    n, l = m.node_tree.nodes, m.node_tree.links
    bsdf = n.get('Principled BSDF')
    bsdf.location = (650, 40)
    out = n.get('Material Output')
    out.location = (920, 40)
    coord = n.new('ShaderNodeTexCoord')
    coord.location = (-1000, 0)
    mapping = n.new('ShaderNodeVectorMath')
    mapping.operation = 'MULTIPLY'
    mapping.label = 'Escala e direção da textura'
    mapping.location = (-800, 0)
    mapping.inputs[1].default_value = ((6, .42, 8) if kind == 'wood' else (1, 1, 1))
    l.new(coord.outputs['Generated' if kind == 'wood' else 'Object'], mapping.inputs[0])
    noise = n.new('ShaderNodeTexNoise')
    noise.location = (-550, 50)
    noise.inputs['Scale'].default_value = 5 if kind == 'wood' else (38 if kind == 'leather' else 5)
    noise.inputs['Detail'].default_value = 5
    noise.inputs['Roughness'].default_value = .75
    noise.label = 'Veios / pátina / variação do revestimento'
    l.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    ramp = n.new('ShaderNodeValToRGB')
    ramp.location = (-260, 120)
    ramp.label = 'Cores ajustáveis'
    ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
    for i, col in enumerate(colors):
        e = ramp.color_ramp.elements[0] if i == 0 else ramp.color_ramp.elements.new(i / (len(colors) - 1))
        e.position = .2 + .63 * i / (len(colors) - 1)
        e.color = (*col, 1)
    l.new(noise.outputs['Fac'], ramp.inputs[0])
    l.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    fine = n.new('ShaderNodeTexNoise')
    fine.location = (-510, -200)
    fine.inputs['Scale'].default_value = 100 if kind == 'leather' else 75
    fine.inputs['Detail'].default_value = 3
    l.new(mapping.outputs[0], fine.inputs['Vector'])
    mix = n.new('ShaderNodeMath')
    mix.operation = 'MULTIPLY_ADD'
    mix.inputs[1].default_value = .3
    l.new(noise.outputs['Fac'], mix.inputs[0])
    l.new(fine.outputs['Fac'], mix.inputs[2])
    relief = n.new('ShaderNodeBump')
    relief.location = (360, -150)
    relief.label = 'Relevo ajustável — metros'
    relief.inputs['Strength'].default_value = .26 if kind != 'leather' else .16
    relief.inputs['Distance'].default_value = bump
    l.new(mix.outputs[0], relief.inputs['Height'])
    l.new(relief.outputs[0], bsdf.inputs['Normal'])
    m['tipo'] = kind
    return m


def materials():
    textured('Concreto quente', [(.22, .20, .17), (.38, .35, .30), (.48, .44, .38)], 'concrete', .89, .012)
    textured('Reboco painel TV', [(.22, .19, .15), (.34, .30, .25), (.45, .40, .32)], 'concrete', .9, .014)
    textured('Madeira demolicao', [(.09, .027, .009), (.23, .077, .024), (.43, .21, .077), (.18, .063, .019)], 'wood', .43, .008)
    textured('Madeira clara tampo', [(.12, .048, .017), (.38, .17, .055), (.52, .28, .11), (.25, .10, .03)], 'wood', .4, .006)
    textured('Couro caramelo', [(.11, .027, .009), (.28, .082, .025), (.42, .16, .055), (.23, .055, .013)], 'leather', .36, .003)
    M['Couro caramelo'].node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value = .15
    textured('Linho cru', [(.27, .22, .15), (.50, .43, .31)], 'cloth', .96, .004)
    textured('Linho grafite', [(.027, .026, .022), (.13, .11, .08)], 'cloth', .97, .004)
    textured('Tapete juta', [(.14, .088, .043), (.37, .27, .15), (.54, .42, .25)], 'cloth', .95, .009)
    for i in range(8):
        f = .78 + i * .045
        textured(f'Pedra quadrada {i+1:02}', [(c*f, c*.74*f, c*.48*f) for c in [.035, .11, .20, .065]], 'stone', .7, .024)
    textured('Porcelanato acetinado', [(.34, .31, .265), (.48, .44, .38), (.56, .51, .44)], 'stone', .22, .001)
    textured('Granito preto polido', [(.005, .006, .005), (.025, .026, .023), (.08, .075, .06)], 'stone', .14, .002)
    basic('Metal preto', (.012, .014, .013), .28, .68)
    basic('Metal fosco', (.018, .02, .018), .48, .4)
    basic('Bronze', (.22, .12, .035), .27, .8)
    basic('Cromado', (.5, .54, .55), .12, .95)
    basic('Espelho fisico', (.97, .97, .97), .003, 1)
    basic('Vidro transparente', (.95, .985, 1), .06, transmission=1)
    basic('Agua', (.92, .96, .95), .03, transmission=1)
    M['Agua'].node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value = 1.333
    basic('Ceramica preta', (.014, .018, .015), .28)
    basic('Ceramica creme', (.76, .70, .57), .22)
    basic('Papel livros', (.64, .58, .45), .8)
    basic('Livro capa preta', (.02, .023, .022), .48)
    basic('Livro capa creme', (.52, .47, .36), .65)
    basic('Teto off-white', (.60, .56, .49), .87)
    basic('Porta marfim', (.62, .60, .53), .4)
    basic('Rejunte', (.15, .14, .12), .9)
    basic('Luz ambar', (1, .40, .075), .3, emission=5)
    basic('Lampada quente', (1, .60, .22), .25, emission=7)
    basic('Terra', (.018, .012, .007), .95)
    for i, color in enumerate([(.055, .13, .012), (.12, .22, .022), (.20, .30, .035), (.033, .095, .01)]):
        basic(f'Folha {i}', color, .48)
    # Variações físicas separadas da exposição: cores podem ser mudadas no Shader Editor.
    for name, m in M.items():
        factor=CFG.get('material_color_multipliers',{}).get('Pedra quadrada' if name.startswith('Pedra quadrada') else name,1)
        for node in m.node_tree.nodes:
            if node.type=='VALTORGB':
                for e in node.color_ramp.elements:e.color=tuple(c*factor for c in e.color[:3])+(1,)
    # Veios horizontais para a face do bar; y continua longitudinal nas tábuas da mesa.
    horizontal=M['Madeira demolicao'].copy();horizontal.name='Madeira horizontal bar';M[horizontal.name]=horizontal
    next(n for n in horizontal.node_tree.nodes if n.type=='VECT_MATH').inputs[1].default_value=(.35,8,10)
    for name in ['Madeira demolicao','Madeira clara tampo']:
        next(n for n in M[name].node_tree.nodes if n.type=='VECT_MATH').inputs[1].default_value=(14,.30,10)


def light(name, loc, energy, color=(1, .62, .32), kind='AREA', target=None, size=1, par=None):
    data = bpy.data.lights.new(name, kind)
    data.energy = energy
    data.color = color
    if kind == 'AREA':
        data.shape = 'DISK'
        data.size = size
    elif kind == 'POINT':
        data.shadow_soft_size = size
    else:
        data.spot_size = math.radians(65)
        data.spot_blend = .65
        data.shadow_soft_size = .05
    o = bpy.data.objects.new(name, data)
    C['Iluminacao'].objects.link(o)
    o.location = loc
    if target:
        o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    if par:
        o.parent = par
    return o


LEAF_MESHES = []


def leaf(loc, scale, col, par=None, direction=None):
    if not LEAF_MESHES:
        for i in range(4):
            m = bpy.data.meshes.new(f'Folha lanceolada malha {i}')
            verts=[];faces=[]
            for j in range(13):
                t=j/12;w=.033*math.sin(math.pi*t)**.8;z=.017*math.sin(math.pi*t)
                verts.extend([(-w,.15*t,z*.35),(0,.15*t,z),(w,.15*t,z*.35)])
            for j in range(12):
                a=j*3;faces.extend([(a,a+3,a+4,a+1),(a+1,a+4,a+5,a+2)])
            m.from_pydata(verts,[],faces)
            for poly in m.polygons:poly.use_smooth=True
            m.materials.append(M[f'Folha {i}'])
            LEAF_MESHES.append(m)
    o = bpy.data.objects.new('Folhagem', RNG.choice(LEAF_MESHES))
    C[col].objects.link(o)
    o.location = loc
    o.scale = (scale, scale, scale)
    o.rotation_euler = (RNG.uniform(-.8, 1.1), RNG.uniform(-.5, .5), RNG.uniform(0, math.tau))
    if direction:
        o.rotation_euler = Vector(direction).to_track_quat('Y', 'Z').to_euler()
    if par:
        o.parent = par
    return o


def plant(name, loc, size, col, pot='Ceramica preta', hanging=False):
    p = parent(name, col, loc)
    lathe('Vaso '+name, [(0, 0), (.10*size, 0), (.14*size, .06*size), (.13*size, .20*size),
                       (.075*size, .29*size), (.078*size, .31*size), (.064*size, .31*size),
                       (.061*size, .28*size)], (0, 0, 0), pot, col, p)
    cylinder('Terra '+name, (0, 0, .27*size), .063*size, .012, 'Terra', col, p)
    for i in range(10 if not hanging else 7):
        angle = i * 2.4
        h = size * RNG.uniform(.34, .75)
        end = (.30*size*math.cos(angle), .30*size*math.sin(angle), .27*size + h)
        if hanging:
            end = (.25*size*math.cos(angle), .27*size*math.sin(angle), -.9*size*RNG.random())
        points = [(0, 0, .26*size), (end[0]*.6, end[1]*.6, .40*size), end]
        curve('Ramo '+name, points, .003*size, 'Folha 0', col, p)
        for j in range(8):
            t = (j + 1) / 9
            pos = (end[0]*t, end[1]*t, .30*size + (end[2]-.30*size)*t)
            for side in [-1, 1]:
                off = (.07*size*math.cos(angle+side), .07*size*math.sin(angle+side), .025*size)
                leaf(tuple(pos[k]+off[k] for k in range(3)), RNG.uniform(.7, 1.2)*size, col, p)
    return p


def architecture():
    d = CFG['estimated_dimensions_m']
    w, dep, h = d['room_width'], d['room_depth'], d['ceiling_height']
    front=d.get('room_front_y',0)
    a = parent('ENV_Arquitetura estimada — selecao bloqueada', 'Arquitetura', hipotese=True)
    box('Contrapiso', (w/2, (dep+front)/2, -.08), (w+.3, dep-front+.3, .15), 'Rejunte', 'Arquitetura', par=a)
    tile = d['floor_tile']
    for ix in range(math.ceil(w/tile)):
        for iy in range(math.ceil((dep-front)/tile)):
            sx, sy = min(tile-.003, w-ix*tile), min(tile-.003, dep-front-iy*tile)
            if sx > 0 and sy > 0:
                box(f'Piso {ix:02}-{iy:02}', (ix*tile+sx/2, front+iy*tile+sy/2, -.012), (sx, sy, .025), 'Porcelanato acetinado', 'Arquitetura', .002, a)
    box('Parede esquerda cimento', (-.1, (dep+front)/2, h/2), (.2, dep-front, h), 'Concreto quente', 'Arquitetura', .006, a)
    box('Parede TV direita', (w+.1, (6.15+front)/2, h/2), (.2, 6.15-front, h), 'Concreto quente', 'Arquitetura', .005, a)
    box('Parede fundo bar', (2.2, dep+.08, h/2), (4.4, .16, h), 'Concreto quente', 'Arquitetura', .006, a)
    box('Parede lateral fundo', (w+.1, 7.4, h/2), (.2, 2.6, h), 'Concreto quente', 'Arquitetura', .006, a)
    for x in [.028, w-.028]:
        box('Rodape cimento', (x, (dep+front)/2, .055), (.04, dep-front, .11), 'Concreto quente', 'Arquitetura', .004, a)
    ceil = box('Teto principal — ocultar para planta', (w/2, d['ceiling_front_depth']/2, h+.09), (w, d['ceiling_front_depth'], .18), 'Teto off-white', 'Arquitetura', .008, a)
    ceil['hide_in_top_view'] = True
    box('Pilar junto ao espelho', (.34, 7.25, h/2), (.28, .28, h), 'Concreto quente', 'Arquitetura', .008, a)
    mir = CFG['furniture']['mirror']
    if mir.get('wall_return_hypothesis'):
        wall=box('HIPOTESE_Ressalto de parede suporte do espelho', (mir['x']-.08, (mir['y_min']+mir['y_max'])/2, h/2), (.13,mir['y_max']-mir['y_min'],h),'Concreto quente','Arquitetura',.004,a)
        wall['hipotese']=True
        box('HIPOTESE_Retorno lateral do ressalto', (mir['x']/2,mir['y_min']-.04,h/2), (mir['x'],.08,h),'Concreto quente','Arquitetura',.004,a)
    box('Espelho — reflexao Cycles de objetos reais', (mir['x'], (mir['y_min']+mir['y_max'])/2, mir['height']/2), (.014, mir['y_max']-mir['y_min'], mir['height']), 'Espelho fisico', 'Arquitetura', .001, a)
    for y in [mir['y_min'], mir['y_max']]:
        box('Perfil espelho', (mir['x']+.016, y, h/2), (.022, .018, h), 'Metal preto', 'Arquitetura', .002, a)
    roof = parent('HIPOTESE_Cobertura envidracada — sem fotos reais', 'Arquitetura', hipotese=True)
    front_z=h+.015;back_z=d['glass_roof_back_height']
    for ix in range(6):
        x = .15 + ix * .80
        rod('Viga cobertura madeira', (x, 6.05, front_z), (x, 8.7, back_z), .063, 'Madeira demolicao', 'Arquitetura', roof)
    angle = math.atan2(back_z-front_z, 2.65)
    for ix in range(5):
        pane = box('Vidro cobertura hipotetica', (.55+ix*.8, 7.37, (front_z+back_z)/2), (.70, 2.65, .018), 'Vidro transparente', 'Arquitetura', .002, roof, (angle, 0, 0))
        pane['hide_in_top_view'] = True
    for y, z in [(6.08, front_z), (7.35, (front_z+back_z)/2), (8.68, back_z)]:
        rod('Travessa cobertura', (.06, y, z), (4.3, y, z), .05, 'Metal preto', 'Arquitetura', roof)
    vegetation = parent('HIPOTESE_Vegetacao externa acima da cobertura', 'Arquitetura', hipotese=True)
    for i in range(650):
        leaf((RNG.uniform(-.6, 5), RNG.uniform(6, 10), RNG.uniform(back_z+.18, back_z+1.1)), RNG.uniform(2, 5), 'Arquitetura', vegetation)
    # Porta do detalhe ao lado direito do bar. Sem abertura de geladeira.
    for x in [4.40, 5.15]:
        box('Batente porta lateral', (x, 8.52, 1.11), (.06, .11, 2.22), 'Porta marfim', 'Arquitetura', .008, a)
    box('Verga porta lateral', (4.77, 8.52, 2.22), (.81, .11, .07), 'Porta marfim', 'Arquitetura', .005, a)
    box('Porta lateral paineis', (4.77, 8.58, 1.1), (.70, .055, 2.12), 'Porta marfim', 'Arquitetura', .008, a)
    for z in [.52, 1.52]:
        box('Painel rebaixado porta', (4.77, 8.54, z), (.62, .02, .85), 'Ceramica creme', 'Arquitetura', .012, a)
    cylinder('Macaneta porta', (4.99, 8.48, 1.03), .021, .10, 'Cromado', 'Arquitetura', a, rotation=(math.pi/2, 0, 0))


def tapered_leg(name, x, y, height, col, par):
    # Uma malha explícita com seção inferior menor; quatro pés independentes.
    z0, z1, low, top = .055, height-.105, .034, .052
    verts = [(x+dx*r, y+dy*r, z) for z, r in [(z0, low), (z1, top)] for dx, dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    o = bpy.data.objects.new(name, me)
    C[col].objects.link(o)
    me.materials.append(M['Madeira demolicao'])
    o.parent = par
    b=o.modifiers.new('Arestas trabalhadas','BEVEL'); b.width=.006; b.segments=3
    for z, s in [(.05, .083), (.105,.075), (height-.16,.12), (height-.11,.12)]:
        box(name+' ressalto', (x,y,z), (s,s,.03), 'Madeira demolicao',col,.006,par)


def dining():
    f = CFG['furniture']['dining_table']
    w, length, h = f['width'], f['length'], f['height']
    p = parent('MESA_Jantar — mover conjunto', 'Jantar', f['position'], tabuas_longitudinais=3, medidas='estimadas')
    border = .065
    for i in range(3):
        pw = (w-2*border)/3
        box(f'Tampo tabua longitudinal {i+1} de 3', (-w/2+border+pw*(i+.5),0,h-.025), (pw-.003,length-2*border,.05), 'Madeira clara tampo','Jantar',.006,p)
    for x in [-w/2+border/2,w/2-border/2]:
        box('Moldura longitudinal tampo', (x,0,h-.025),(border,length,.055),'Madeira demolicao','Jantar',.007,p)
    for y in [-length/2+border/2,length/2-border/2]:
        box('Moldura transversal tampo', (0,y,h-.025),(w-2*border,border,.055),'Madeira demolicao','Jantar',.007,p)
    for x in [-w/2+.10,w/2-.10]:
        box('Saia lateral mesa', (x,0,h-.12),(.055,length-.17,.14),'Madeira demolicao','Jantar',.005,p)
        for y in [-length/2+.105,length/2-.105]:
            tapered_leg('Pe afunilado mesa',x,y,h,'Jantar',p)
    for y in [-length/2+.10,length/2-.10]:
        box('Saia cabeceira mesa',(0,y,h-.12),(w-.16,.055,.14),'Madeira demolicao','Jantar',.004,p)
    for side in [-1,1]:
        for j, y in enumerate([-.43,.43]):
            cp = parent(f'CADEIRA_{"Esquerda" if side<0 else "Direita"}_{j+1} — mover conjunto','Jantar',
                        (f['position'][0]+side*(w/2+.28),f['position'][1]+y,0), categoria='cadeira_jantar', lado='esquerdo' if side<0 else 'direito')
            cp.rotation_euler[2] = -side*math.pi/2
            box('Assento couro cadeira',(0,0,.465),(.46,.46,.11),'Couro caramelo','Jantar',.055,cp)
            box('Encosto couro cadeira',(0,.205,.72),(.46,.105,.53),'Couro caramelo','Jantar',.06,cp,(-.10,0,0))
            for x in [-.185,.185]:
                for y0 in [-.17,.17]:
                    rod('Perna preta cadeira',(x,y0, .40),(x*1.13,y0*1.14,.02),.017,'Metal preto','Jantar',cp)
                rod('Suporte encosto',(x,.18,.30),(x,.24,.89),.016,'Metal preto','Jantar',cp)
                rod('Travessa lateral cadeira',(x,-.18,.20),(x,.2,.20),.012,'Metal preto','Jantar',cp)
    plant('Arranjo centro jantar',(f['position'][0],f['position'][1],h+.002),CFG['plant_scales']['dining'],'Jantar')
    pendant('Pendente principal jantar',(f['position'][0],f['position'][1],2.26),.34,3.15,'Iluminacao',125)
    light('Banho quente teto jantar',(f['position'][0],f['position'][1],2.93),28,color=(1,.42,.13),kind='POINT',size=.30)


def pendant(name, loc, radius, ceiling, col, power):
    p=parent(name,col,loc)
    r=radius
    lathe('Cupula preta '+name,[(r,0),(r*.99,.025),(r*.95,.09),(r*.82,.18),(r*.60,.27),(r*.25,.34),(r*.21,.43)],(0,0,0),'Metal preto',col,p)
    cylinder('Interior claro cupula',(0,0,.026),r*.94,.012,'Lampada quente',col,p)
    rod('Cabo pendente',(0,0,.40),(0,0,ceiling-loc[2]),.008,'Metal preto',col,p)
    cylinder('Canopla pendente',(0,0,ceiling-loc[2]-.012),.065,.025,'Metal preto',col,p)
    sphere('Lampada visivel',(0,0,.01),(.047,.047,.055),'Lampada quente',col,p)
    light('Luz '+name,(loc[0],loc[1],loc[2]-.04),power,size=r*1.1,target=(loc[0],loc[1],0))


def bar():
    f=CFG['furniture']['bar']; y=f['counter_y']; back=f['back_y']; x0=f['x_min']; x1=f['x_max']; h=f['height']
    p=parent('BAR_Bancada e marcenaria','Bar')
    box('Frente amadeirada bar',((x0+x1)/2,y+.12,.49),(x1-x0,.18,.98),'Madeira horizontal bar','Bar',.007,p)
    box('Rodape preto bar',((x0+x1)/2,y+.01,.05),(x1-x0,.045,.10),'Metal preto','Bar',.002,p)
    # O recorte real da cuba usa quatro peças, sem tampo atravessando a cuba.
    sinkx=2.85; sinkw=.53; sinkd=.36; cy=y+.36; ymin=y-.19; ymax=y+.72
    for start,end in [(x0-.08,sinkx-sinkw/2),(sinkx+sinkw/2,x1+.08)]:
        box('Tampo granito lateral',((start+end)/2,(ymin+ymax)/2,h),(end-start,ymax-ymin,.045),'Granito preto polido','Bar',.008,p)
    for start,end in [(ymin,cy-sinkd/2),(cy+sinkd/2,ymax)]:
        box('Tampo granito frente cuba',(sinkx,(start+end)/2,h),(sinkw,end-start,.045),'Granito preto polido','Bar',.005,p)
    box('Fundo cuba inox',(sinkx,cy,h-.16),(sinkw-.02,sinkd-.02,.016),'Cromado','Bar',.005,p)
    for x in [sinkx-sinkw/2,sinkx+sinkw/2]:
        box('Lateral cuba inox',(x,cy,h-.08),(.014,sinkd,.16),'Cromado','Bar',.005,p)
    for yy in [cy-sinkd/2,cy+sinkd/2]:
        box('Lateral cuba inox',(sinkx,yy,h-.08),(sinkw,.014,.16),'Cromado','Bar',.005,p)
    curve('Torneira bar',[(sinkx,cy+.25,h),(sinkx,cy+.25,h+.28),(sinkx,cy+.12,h+.38),(sinkx,cy,h+.26)],.014,'Cromado','Bar',p)
    # Pedra quadrada com junta contínua e variação de ferrugem, sem tijolos.
    box('Fundo juntas pedra',(2.48,back,1.58),(3.65,.06,1.12),'Rejunte','Bar',.001,p)
    tile=.285
    for ix in range(13):
        for iz in range(4):
            box(f'Pedra quadrada {ix:02}-{iz:02}',(.61+ix*tile,back-.044,1.15+iz*tile),(tile-.006,.035,tile-.006),f'Pedra quadrada {RNG.randint(1,8):02}','Bar',.006,p)
    box('Painel madeira vertical esquerda',(.55,back-.045,2.25),(1.08,.10,2.8),'Madeira horizontal bar','Bar',.004,p)
    for z in [1.08+i*.20 for i in range(13)]:
        box('Junta madeira parede',(.55,back-.103,z),(1.06,.005,.004),'Metal fosco','Bar',0,p)
    for k in range(3):
        cx=1.62+k*.91
        cabinet=parent(f'Armario superior {k+1}','Bar',(cx,back-.24,2.49))
        box('Fundo armario',(0,.18,0),(.89,.07,.88),'Madeira demolicao','Bar',.006,cabinet)
        for z in [-.44,0,.44]:
            box('Prateleira armario',(0,0,z),(.90,.41,.035),'Madeira clara tampo','Bar',.004,cabinet)
        for xx in [-.45,.45]:
            box('Lateral armario',(xx,0,0),(.03,.42,.91),'Metal preto','Bar',.003,cabinet)
        if k<2:
            box('Porta vidro armario',(0,-.218,0),(.84,.008,.84),'Vidro transparente','Bar',.002,cabinet)
        for z in [-.43,.43]:
            box('Perfil porta armario',(0,-.23,z),(.90,.018,.025),'Cromado','Bar',.002,cabinet)
        for xx in [-.44,.44]:
            box('Perfil vertical armario',(xx,-.23,0),(.025,.018,.88),'Cromado','Bar',.002,cabinet)
        if k<2:
            for z in [-.405,.035]:
                for j in range(5):
                    glass=lathe('Taca haste vidro',[(0,0),(.035,0),(.035,.006),(.007,.014),(.006,.10),(.037,.12),(.045,.16),(.038,.205),(.034,.215),(.031,.21),(.038,.16),(.030,.125)],(-.32+j*.16,-.02,z),'Vidro transparente','Bar',cabinet,24)
        else:
            for z in [-.40,.035]:
                for j in [-.23,.23]:
                    for n in range(6):
                        lathe('Prato empilhado',[(0,0),(.085,0),(.103,.012),(.115,.020),(.115,.025),(.09,.018),(0,.015)],(j,0,z+n*.019),'Ceramica creme','Bar',cabinet,24)
    rod('Fita LED sob armarios',(1.17,back-.38,2.015),(4.28,back-.38,2.015),.008,'Luz ambar','Bar',p)
    for x in [1.5,2.5,3.5,4.1]:
        light('LED bar',(x,back-.34,1.98),CFG['lighting']['bar_led_power'],color=(1,.43,.12),size=.50,target=(x,back-.06,1.35))
    for i in range(4):
        x=.98+i*.99
        st=parent(f'BANQUETA_{i+1:02} — mover conjunto','Bar',(x,y-.63,0),categoria='banqueta_bar')
        cylinder('Assento redondo madeira',(0,0,.755),.22,.055,'Madeira clara tampo','Bar',st,48)
        for angle in [.785+i*math.pi/2 for i in range(4)]:
            rod('Perna preta banqueta',(.15*math.cos(angle),.15*math.sin(angle),.73),(.22*math.cos(angle),.22*math.sin(angle),.025),.015,'Metal preto','Bar',st)
        bpy.ops.mesh.primitive_torus_add(major_radius=.181,minor_radius=.009,major_segments=40,minor_segments=8,location=(0,0,.275))
        finish(bpy.context.object,'Apoio circular pes banqueta','Bar','Metal preto',st)
    plant('Planta bancada bar',(.82,y+.22,h+.025),.90,'Bar',hanging=True)
    probe=lathe('OBJETO_TESTE_ESPELHO — vaso do bar',[(0,0),(.075,0),(.085,.04),(.065,.13),(.035,.18),(.035,.22)],f['mirror_probe_position'],'Ceramica creme','Bar',p)
    probe['mirror_probe']=True
    pendant('Pendente pequeno bar',(1.15,7.76,2.41),.16,3.40,'Iluminacao',45)


def sofa_and_rug():
    f=CFG['furniture']['sofa']; p=parent('SOFA_Couro caramelo — mover conjunto','Estar',f['position'])
    p.scale.x=f.get('depth_scale',1)
    length=f['length']
    box('Base sofa',(0,0,.27),(1.0,length,.36),'Couro caramelo','Estar',.11,p)
    box('Encosto sofa',(-.40,0,.70),(.25,length-.10,.72),'Couro caramelo','Estar',.12,p,(0,-.10,0))
    for i in range(3):
        yy=-length/2+.19+(i+.5)*(length-.38)/3
        box(f'Almofada assento sofa {i+1}',(.08,yy,.47),(.88,(length-.42)/3-.018,.22),'Couro caramelo','Estar',.10,p)
        box(f'Almofada encosto sofa {i+1}',(-.26,yy,.80),(.24,(length-.4)/3-.025,.60),'Couro caramelo','Estar',.10,p,(0,-.18,0))
        for x0 in [-.31,.46]:
            curve('Vivo couro assento',[(x0,yy-.43,.52),(x0+.007,yy,.56),(x0,yy+.43,.52)],.0025,'Couro caramelo','Estar',p)
        curve('Costura encosto', [(-.10,yy-.42,.64),(-.09,yy,.61),(-.10,yy+.42,.64)],.002,'Madeira clara tampo','Estar',p)
    for yy in [-length/2+.09,length/2-.09]:
        box('Braco sofa',(.02,yy,.54),(1.02,.19,.42),'Couro caramelo','Estar',.09,p)
    for x in [-.32,.36]:
        for yy in [-length/2+.22,length/2-.22]:
            box('Pe sofa',(x,yy,.065),(.07,.10,.13),'Metal preto','Estar',.006,p)
    for yy,mat in [(-.45,'Linho cru'),(.22,'Linho cru'),(.85,'Linho grafite')]:
        pillow=box('Almofada decorativa',(.04,yy,.78),(.25,.58,.53),mat,'Estar',.115,p,(.12,-.22,.12))
    # Manta como malha ondulada de verdade, pendente na frente do assento.
    verts=[]; faces=[]
    for i in range(25):
        t=i/24
        x=-.16+t*.72
        z=.61 if t<.74 else .61-(t-.74)*1.8
        for j in range(30):
            yy=-1.23+j/29*.94
            verts.append((x,yy,z+.025*math.sin(j*1.65+i*.35)))
    for i in range(24):
        for j in range(29):
            a=i*30+j;faces.append((a,a+1,a+31,a+30))
    me=bpy.data.meshes.new('Manta trama');me.from_pydata(verts,[],faces);me.materials.append(M['Linho cru'])
    ob=bpy.data.objects.new('Manta ondulada sofa',me);C['Estar'].objects.link(ob);ob.parent=p
    solid=ob.modifiers.new('Espessura tecido','SOLIDIFY');solid.thickness=.006
    for j in range(22):
        yy=-1.23+j*.045
        curve('Franja manta',[(.56,yy,.15),(.58,yy+.012,.11),(.59,yy+.02,.08)],.003,'Linho cru','Estar',p)
    rug=box('Tapete juta natural',(3.35,2.15,.012),(3.25,3.10,.018),'Tapete juta','Estar',.012)
    # Ondas perpendiculares para a trama visível em escala física.
    mat=M['Tapete juta'];n=mat.node_tree.nodes;l=mat.node_tree.links
    coord=n.new('ShaderNodeTexCoord'); waves=[]
    for direction in ['X','Y']:
        wave=n.new('ShaderNodeTexWave');wave.bands_direction=direction;wave.inputs['Scale'].default_value=105;wave.inputs['Distortion'].default_value=.7
        l.new(coord.outputs['Generated'],wave.inputs['Vector']);waves.append(wave)
    mix=n.new('ShaderNodeMath');mix.operation='MULTIPLY';l.new(waves[0].outputs['Fac'],mix.inputs[0]);l.new(waves[1].outputs['Fac'],mix.inputs[1])
    b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.4;b.inputs['Distance'].default_value=.008;l.new(mix.outputs[0],b.inputs['Height']);l.new(b.outputs[0],n.get('Principled BSDF').inputs['Normal'])
    for i in range(80):
        x=1.75+i*.041
        for y,dy in [(.60,-.10),(3.70,.10)]:
            curve('Franja tapete',[(x,y,.02),(x+.006,y+dy,.018)],.002,'Linho cru','Estar')
    # Prateleira, quadro e arandela na parede esquerda.
    box('Prateleira preta plantas',(.20,3.75,2.33),(.43,1.47,.045),'Metal preto','Estar',.004)
    for yy in [3.15,4.34]:
        box('Suporte prateleira',(.018,yy,2.42),(.035,.035,.28),'Metal preto','Estar',.002)
    plant('Jiboia pendente esquerda',(.25,3.48,2.35),.85,'Estar',hanging=True)
    plant('Vaso menor prateleira',(.24,4.20,2.35),.55,'Estar','Ceramica creme')
    wall_art('Quadro floresta esquerda',(.035,3.60,1.64),(.90,1.10),'Estar',left=True)
    curve('Braco arandela esquerda',[(.05,3.70,1.94),(.35,3.70,1.94),(.56,3.70,2.28),(.70,3.70,2.28)],.018,'Metal preto','Estar')
    cylinder('Base arandela esquerda',(.045,3.70,1.93),.085,.035,'Metal preto','Estar',rotation=(0,math.pi/2,0))
    lathe('Cupula arandela esquerda',[(.20,0),(.19,.05),(.14,.15),(.05,.23),(.04,.29)],(.70,3.70,2.02),'Metal preto','Estar')
    sphere('Bulbo arandela esquerda',(.70,3.70,2.01),(.035,.035,.045),'Lampada quente','Estar')
    light('Arandela sofa',(.70,3.70,1.98),65,size=.12,target=(0,3.70,1.3))


def image_texture(name, kind):
    """Arte original algorítmica, empacotada; nenhuma foto de referência vira cenário."""
    import numpy as np
    width,height=(1024,576) if kind=='landscape' else (400,560)
    rng=np.random.default_rng(27)
    xx=np.linspace(0,1,width)[None,:];yy=np.linspace(0,1,height)[:,None]
    # Blender pixels têm origem inferior; montanhas e céu ao pôr do sol.
    if kind=='landscape':
        top=np.array([.055,.10,.17]);bot=np.array([.96,.31,.045])
        t=np.clip((yy-.32)/.68,0,1)[...,None]
        pixels=np.broadcast_to(bot*(1-t)+top*t,(height,width,3)).copy()
        sun=np.exp(-(((xx-.78)/.12)**2+((yy-.51)/.06)**2))
        pixels+=sun[...,None]*np.array([.7,.4,.12])
        for i in range(6):
            xs=np.linspace(0,1,18)
            peaks=rng.uniform(.26,.52,18)*(1-i*.075)-i*.018
            if i==2:peaks=np.array([.31,.36,.40,.54,.69,.56,.47,.44,.36,.39,.29,.31,.28,.32,.28,.26,.32,.30])
            ridge=np.interp(xx[0],xs,peaks)
            for n,amplitude in [(70,.015),(250,.005),(700,.0015)]:
                ridge+=np.interp(xx[0],np.linspace(0,1,n),rng.normal(0,amplitude,n))
            horizon=ridge[None,:]
            mask=yy<horizon
            slope=np.clip(np.gradient(ridge)*width,-2,2)[None,:]
            shade=np.clip(.65+slope*.17+(horizon-yy)*.45,.30,1.0)
            col=np.array([.16-i*.019,.18-i*.022,.21-i*.027])
            tone=np.broadcast_to(col*shade[...,None],pixels.shape).copy()
            snow=(horizon-yy<.04)&(horizon>.58)&(slope<.15)
            tone[snow]=(.42,.35,.28)
            pixels[mask]=tone[mask]
        lake=(yy<.29)&(xx>.29+(.29-yy)*.85)&(xx<.88-(.29-yy)*1.6)
        shimmer=(np.sin(yy*1600+xx*8)*.012+rng.uniform(-.007,.007,(height,width)))[...,None]
        water=np.broadcast_to(np.array([.22,.23,.235])+(yy*.16)[...,None],pixels.shape)+shimmer
        pixels[lake]=water[lake]
        for j in range(48):
            tx=rng.uniform(0,1);base=rng.uniform(0,.07);th=rng.uniform(.05,.17)
            tree=(yy>=base)&(yy<base+th)&(abs(xx-tx)<(base+th-yy)*.13)
            pixels[tree]=(.025,.035,.027)
    else:
        pixels=np.ones((height,width,3))*.65
        for i in range(95):
            px=rng.uniform(0,1);base=rng.uniform(0,.40);h=rng.uniform(.13,.56)
            tree=(yy>=base)&(yy<base+h)&(abs(xx-px)<(base+h-yy)*.12)
            pixels[tree]=rng.uniform(.018,.14)
        path=(yy<.50)&(abs(xx-.53)<(.50-yy)*.31)
        pixels[path]=.48
    rgba=np.ones((height,width,4),dtype=np.float32);rgba[:,:,:3]=np.clip(pixels,0,1)
    image=bpy.data.images.new(name,width=width,height=height)
    image.pixels.foreach_set(rgba.reshape(-1))
    image.pack()
    return image


def art_material(name, kind, strength=.0):
    m=basic(name,(.3,.3,.3),.58)
    n=m.node_tree.nodes;l=m.node_tree.links
    tex=n.new('ShaderNodeTexImage');tex.image=image_texture(name,kind)
    l.new(tex.outputs['Color'],n.get('Principled BSDF').inputs['Base Color'])
    if strength:
        l.new(tex.outputs['Color'],n.get('Principled BSDF').inputs['Emission Color'])
        n.get('Principled BSDF').inputs['Emission Strength'].default_value=strength
    return m


def image_plane(name,loc,w,h,material,col,normal='-X',par=None):
    # Quatro vértices/UV explícitos evitam mapear a imagem seis vezes num cubo.
    if normal in ['-X','X']:
        verts=[(0,-w/2,-h/2),(0,w/2,-h/2),(0,w/2,h/2),(0,-w/2,h/2)]
        if normal=='X': verts=list(reversed(verts))
    else:
        verts=[(-w/2,0,-h/2),(w/2,0,-h/2),(w/2,0,h/2),(-w/2,0,h/2)]
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],[(0,1,2,3)]);uv=me.uv_layers.new()
    for i,co in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=co
    o=bpy.data.objects.new(name,me);C[col].objects.link(o);o.location=loc;me.materials.append(material)
    if par:o.parent=par
    return o


def wall_art(name,loc,size,col,left=False):
    p=parent(name,col,loc)
    w,h=size
    box('Moldura preta quadro',(0,0,0),(.045,w,h),'Metal preto',col,.007,p)
    box('Passepartout quadro',(.028 if left else -.028,0,0),(.012,w-.055,h-.055),'Ceramica creme',col,.001,p)
    image_plane('Gravura original floresta',(.036 if left else -.036,0,0),w-.18,h-.18,art_material('Arte '+name,'forest'),col,'X' if left else '-X',p)


def coffee_table():
    f=CFG['furniture']['coffee_table'];w,l,h=f['width'],f['length'],f['height']
    p=parent('MESA_Centro — mover conjunto','Estar',f['position'])
    for i in range(5):
        box('Tabua mesa centro',(-w/2+(i+.5)*w/5,0,h-.025),(w/5-.004,l,.052),'Madeira clara tampo','Estar',.006,p)
    for x in [-w/2+.03,w/2-.03]:
        for y in [-l/2+.03,l/2-.03]:
            box('Pe metal mesa centro',(x,y,h/2-.03),(.04,.04,h-.05),'Metal preto','Estar',.004,p)
        for z in [.07,h-.06]:
            box('Travessa metal mesa centro',(x,0,z),(.04,l,.035),'Metal preto','Estar',.003,p)
    for y in [-l/2+.03,l/2-.03]:
        for z in [.07,h-.06]:
            box('Travessa longa mesa centro',(0,y,z),(w,.035,.035),'Metal preto','Estar',.003,p)
    books('Livros mesa centro',(f['position'][0]+.4,f['position'][1]-.12,h+.006),'Estar')
    bowl('Tigela mesa centro',(f['position'][0]+.44,f['position'][1]-.10,h+.14),'Estar')
    plant('Arranjo vaso vidro centro',(f['position'][0]-.34,f['position'][1]+.10,h+.005),CFG['plant_scales']['coffee'],'Estar','Vidro transparente')


def books(name,loc,col):
    p=parent(name,col,loc)
    for j in range(2):
        w=.37+j*.04;l=.25-j*.015;z=j*.052
        box('Capa livro',(0,0,z+.007),(w,l,.014),'Livro capa preta' if j==0 else 'Livro capa creme',col,.002,p)
        box('Paginas livro',(0,.003,z+.026),(w-.012,l-.012,.028),'Papel livros',col,.001,p)
        box('Capa livro superior',(0,0,z+.047),(w,l,.012),'Livro capa preta' if j==0 else 'Livro capa creme',col,.002,p)


def bowl(name,loc,col):
    lathe(name,[(0,0),(.08,0),(.12,.025),(.15,.065),(.15,.072),(.135,.067),(.10,.035),(.055,.02),(0,.02)],loc,'Bronze',col)


def tv_wall_and_kitchen():
    f=CFG['furniture']['tv'];x=f['wall_x'];cy=f['center_y'];z=f['center_z']
    p=parent('TV_Painel e rack','Estar')
    # Extrusão de contorno com cantos superiores arredondados, em plano YZ.
    ymin,ymax=1.80,6.02;bottom,top=.38,2.66;r=.22
    yz=[(ymin,bottom),(ymax,bottom),(ymax,top-r)]
    yz += [(ymax-r+r*math.cos(a),top-r+r*math.sin(a)) for a in [i*math.pi/2/12 for i in range(13)]]
    yz += [(ymin+r+r*math.cos(a),top-r+r*math.sin(a)) for a in [math.pi/2+i*math.pi/2/12 for i in range(13)]]
    verts=[(xx,yy,zz) for xx in [x+.035,x+.085] for yy,zz in yz];n=len(yz)
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    me=bpy.data.meshes.new('Painel contorno arredondado');me.from_pydata(verts,[],faces);me.materials.append(M['Reboco painel TV'])
    ob=bpy.data.objects.new('Painel TV cantos superiores arredondados',me);C['Estar'].objects.link(ob);ob.parent=p
    box('Televisor independente',(x-.018,cy,z),(.075,f['width'],f['height']),'Metal preto','Estar',.014,p)
    image_plane('Tela TV — paisagem original',(x-.061,cy,z),f['width']-.055,f['height']-.055,art_material('Tela paisagem original','landscape',.35),'Estar',par=p)
    for y in [2.12,5.77]:
        box('Perfil barra vertical ambar',(x-.03,y,1.57),(.045,.038,1.85),'Bronze','Estar',.008,p)
        box('Difusor barra vertical ambar',(x-.055,y,1.57),(.025,.019,1.82),'Luz ambar','Estar',.006,p)
        for zz in [.85,1.55,2.25]:
            light('Luz barra ambar',(x-.08,y,zz),13,kind='POINT',size=.12)
    rackx=x-.30;racky=4.05;racklen=3.90
    box('Rack estrutura',(rackx,racky,.34),(.55,racklen,.58),'Metal fosco','Estar',.01,p)
    box('Rack tampo madeira',(rackx-.01,racky,.66),(.62,racklen+.06,.07),'Madeira clara tampo','Estar',.008,p)
    for i in range(5):
        yy=racky-racklen/2+(i+.5)*racklen/5
        framex=rackx-.285;dw=racklen/5-.028
        for y0 in [yy-dw/2,yy+dw/2]:box('Montante porta rack',(framex,y0,.35),(.025,.025,.49),'Metal preto','Estar',.002,p)
        for zz in [.105,.59]:box('Travessa porta rack',(framex,yy,zz),(.025,dw,.025),'Metal preto','Estar',.002,p)
        # Tela metálica construída com fios reais e interior visível.
        for j in range(22):
            y0=yy-dw/2+.015+j*(dw-.03)/21
            rod('Fio vertical tela rack',(framex-.005,y0,.12),(framex-.005,y0,.575),.0018,'Metal preto','Estar',p)
        for j in range(16):
            zz=.12+j*.03
            rod('Fio horizontal tela rack',(framex-.007,yy-dw/2,zz),(framex-.007,yy+dw/2,zz),.0016,'Metal preto','Estar',p)
        for j in range(3):
            box('Livro interior rack',(rackx-.09,yy+(j-1)*.13,.21),(.25,.08,.20),'Madeira demolicao','Estar',.006,p)
        light('Luz interior rack',(rackx-.08,yy,.40),4,kind='POINT',size=.10)
    for yy in [racky-racklen/2+.08,racky+racklen/2-.08]:
        for xx in [rackx-.21,rackx+.21]:box('Pe rack',(xx,yy,.055),(.04,.04,.11),'Metal preto','Estar',.003,p)
    plant('Vaso alto sobre rack',(rackx-.05,2.61,.70),CFG['plant_scales']['rack'],'Estar')
    books('Livros rack',(rackx-.04,4.94,.70),'Estar')
    bowl('Tigela rack',(rackx-.03,4.94,.81),'Estar')
    lamp=parent('Luminaria vidro rack','Estar',(rackx-.07,5.55,.70))
    cylinder('Base luminaria vidro',(0,0,.015),.115,.03,'Metal preto','Estar',lamp)
    lathe('Campanula vidro',[(.115,.025),(.13,.08),(.13,.24),(.09,.33),(0,.35)],(0,0,0),'Vidro transparente','Estar',lamp)
    cylinder('Haste bulbo',(0,0,.07),.023,.10,'Bronze','Estar',lamp)
    sphere('Bulbo filamento',(0,0,.18),(.035,.035,.07),'Lampada quente','Estar',lamp)
    light('Luminaria vidro rack',(rackx-.07,5.55,.90),14,kind='POINT',size=.035)
    # Divisória frontal ripada, com uma face lateral também ripada.
    part=parent('DIVISORIA_Ripada escura','Cozinha')
    box('Fundo divisoria',(4.68,6.55,1.54),(.93,.42,3.08),'Metal fosco','Cozinha',.005,part)
    for i in range(19):
        box('Ripa vertical frontal',(4.24+i*.048,6.31,1.54),(.022,.065,3.08),'Metal preto','Cozinha',.003,part)
    for i in range(9):
        box('Ripa vertical lateral',(5.16,6.35+i*.046,1.54),(.05,.023,3.08),'Metal preto','Cozinha',.002,part)
    frame=parent('Quadro divisoria','Cozinha',(4.68,6.255,1.77))
    box('Moldura quadro divisoria',(0,0,0),(.49,.035,.83),'Madeira clara tampo','Cozinha',.006,frame)
    image_plane('Gravura divisoria',(0,-.023,0),.43,.77,art_material('Arte divisoria','forest'),'Cozinha','-Y',frame)
    # Cozinha visível pela passagem à direita.
    box('Parede fundo cozinha',(5.77,8.78,1.55),(1.70,.15,3.1),'Concreto quente','Cozinha',.004)
    for i in range(3):
        cx=5.15+i*.45
        box('Armario inferior cozinha',(cx,8.38,.46),(.44,.64,.88),'Metal fosco','Cozinha',.009)
        box('Frente armario cozinha',(cx,8.048,.47),(.415,.025,.82),'Metal fosco','Cozinha',.008)
        rod('Puxador cozinha',(cx-.10,8.025,.76),(cx+.10,8.025,.76),.008,'Metal preto','Cozinha')
    box('Bancada cozinha',(5.65,8.37,.93),(1.54,.72,.045),'Granito preto polido','Cozinha',.006)
    box('Cuba cozinha visivel',(5.77,8.32,.957),(.43,.30,.015),'Cromado','Cozinha',.025)
    curve('Torneira cozinha',[(5.77,8.53,.95),(5.77,8.53,1.22),(5.77,8.35,1.30),(5.77,8.30,1.16)],.012,'Metal preto','Cozinha')
    # Janela usa vão com fundo claro, caixilho e persiana de lâminas reais.
    box('Vidro janela cozinha',(5.73,8.68,1.91),(1.32,.025,1.30),'Vidro transparente','Cozinha',.002)
    box('Vista externa luminosa janela',(5.73,8.70,1.91),(1.29,.015,1.26),'Ceramica creme','Cozinha',.001)
    for xx in [5.05,5.73,6.41]:box('Caixilho vertical janela',(xx,8.63,1.91),(.034,.075,1.37),'Metal preto','Cozinha',.003)
    for zz in [1.24,2.58]:box('Caixilho horizontal janela',(5.73,8.63,zz),(1.39,.075,.035),'Metal preto','Cozinha',.003)
    for i in range(13):box('Lamina persiana',(5.73,8.58,2.54-i*.043),(1.29,.064,.024),'Porta marfim','Cozinha',.002,rotation=(.3,0,0))
    for xx in [5.40,6.05]:rod('Cordao persiana',(xx,8.53,2.58),(xx,8.53,1.98),.002,'Metal preto','Cozinha')
    plant('Planta fora janela cozinha',(5.73,8.66,1.25),.85,'Cozinha')
    light('Luz natural janela cozinha',(5.73,8.35,2.1),160,color=(.88,.94,1),target=(5.5,6.0,1),size=1.0)


def lighting():
    power=CFG['lighting'];w=CFG['estimated_dimensions_m']['room_width']
    for yy in [.75,1.75,2.75,3.75,4.75,5.6]:
        cylinder('Spot embutido aro',(w-.35,yy,3.14),.056,.022,'Metal preto','Iluminacao')
        cylinder('Spot embutido difusor',(w-.35,yy,3.125),.041,.01,'Lampada quente','Iluminacao')
        light('Facho parede TV',(w-.35,yy,3.10),55,color=(1,.51,.20),kind='SPOT',target=(w-.02,yy,1.80))
    light('Claridade cobertura',(2.55,7.3,3.75),power['daylight_power'],color=(.86,.92,1),size=3.2,target=(2.7,6.3,.5)).visible_glossy=False
    light('Preenchimento sala',(3.25,.4,2.9),power['room_fill_power'],color=(1,.78,.53),size=4.0,target=(3.2,4.2,1.1)).visible_glossy=False
    light('Preenchimento estar',(1.7,3.2,2.75),45,color=(1,.61,.32),size=2.0,target=(.4,1.8,.5))
    light('Luz natural frontal',(3,-1.7,2.5),power['front_fill_power'],color=(.88,.93,1),size=4,target=(3,3,1)).visible_glossy=False
    world=bpy.data.worlds.new('Ambiente diurno suave');world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=(.48,.61,.78,1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=.28
    bpy.context.scene.world=world


def cameras_and_references():
    cfg=CFG['camera']
    for name,loc,target in [('CAM_Referencia',cfg['position'],cfg['target']),('CAM_Superior',(3.2,4.35,14),(3.2,4.35,0))]:
        data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);C['Cameras'].objects.link(o);o.location=loc
        o.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
        if name=='CAM_Referencia':
            data.lens=cfg['lens_mm'];data.shift_x=cfg['shift_x'];data.shift_y=cfg['shift_y'];data.clip_start=.05;data.clip_end=100
            bpy.context.scene.camera=o
        else:
            data.type='ORTHO';data.ortho_scale=10.4
    for label,path in CFG['references'].items():
        im=bpy.data.images.load(str(ROOT/path),check_existing=True);im.pack()
        o=bpy.data.objects.new('REF_'+label,None);o.empty_display_type='IMAGE';o.data=im;o.empty_display_size=3
        o.location=(10,{'main':0,'bar':3,'table':6}[label],1.8);o.rotation_euler=(math.pi/2,0,0)
        C['Referencias'].objects.link(o);o.hide_render=True
    C['Referencias'].hide_render=True


def configure_device(requested):
    scene=bpy.context.scene
    scene.render.engine='CYCLES'
    info={'requested':requested,'backend':'CPU','devices':[],'fallback_reason':None}
    scene.cycles.device='CPU'
    prefs=bpy.context.preferences.addons['cycles'].preferences
    if requested=='auto':
        try:
            prefs.compute_device_type='OPTIX';prefs.get_devices()
            gpu=[d for d in prefs.devices if d.type=='OPTIX']
            if gpu:
                for d in prefs.devices:d.use=d.type=='OPTIX'
                scene.cycles.device='GPU'
                info.update(backend='OPTIX',devices=[d.name for d in gpu])
            else:info['fallback_reason']='Nenhum dispositivo OptiX enumerado pelo Blender neste processo.'
        except (RuntimeError,TypeError) as e:info['fallback_reason']=str(e)
    if info['backend']=='CPU':info['devices']=[d.name for d in prefs.devices if d.type=='CPU'] or ['CPU']
    print('RENDER_DEVICE',json.dumps(info),flush=True)
    return info


def ground_contacts():
    """Sapatas com contato no piso sem alterar a altura de assentos e tampos."""
    for p in list(bpy.context.scene.objects):
        if p.get('categoria')=='cadeira_jantar':
            for x in [-.185*1.13,.185*1.13]:
                for y in [-.17*1.14,.17*1.14]:
                    cylinder('Sapata apoio cadeira',(x,y,.013),.019,.026,'Metal fosco','Jantar',p,16)
        elif p.get('categoria')=='banqueta_bar':
            for angle in [.785+i*math.pi/2 for i in range(4)]:
                cylinder('Sapata apoio banqueta',(.22*math.cos(angle),.22*math.sin(angle),.013),.018,.026,'Metal fosco','Bar',p,16)
        elif p.name.startswith('MESA_Jantar'):
            f=CFG['furniture']['dining_table']
            for x in [-f['width']/2+.10,f['width']/2-.10]:
                for y in [-f['length']/2+.105,f['length']/2-.105]:
                    box('Base inferior pe mesa',(x,y,.025),(.083,.083,.05),'Madeira demolicao','Jantar',.003,p)
        elif p.name.startswith('MESA_Centro'):
            for obj in p.children:
                if obj.name.startswith('Pe metal mesa centro'):obj.location.z+=.005


def unique_path(path):
    if not path.exists():return path
    stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    return path.with_name(path.stem+'-'+stamp+path.suffix)


def main():
    global ROOT,CFG
    argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    args=args_parser().parse_args(argv);ROOT=args.project_root.resolve()
    CFG=json.loads((ROOT/'config/cena.json').read_text(encoding='utf-8'))
    assert CFG['schema_version']==1 and CFG['units']=='METERS'
    assert set(CFG['references'])=={'main','bar','table'}
    for file in CFG['references'].values():
        path=(ROOT/file).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():raise ValueError('Referência inválida: '+file)
    assert all(float(CFG['estimated_dimensions_m'][k])>0 for k in ['room_width','room_depth','ceiling_height'])
    RNG.seed(CFG['seed'])
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections):
        if c.name not in COLLECTIONS:bpy.data.collections.remove(c)
    for name in COLLECTIONS:
        C[name]=bpy.data.collections.get(name) or bpy.data.collections.new(name)
        if C[name].name not in bpy.context.scene.collection.children:bpy.context.scene.collection.children.link(C[name])
    materials();architecture();dining();bar();sofa_and_rug();coffee_table();tv_wall_and_kitchen();lighting();ground_contacts();cameras_and_references()
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.length_unit='METERS';scene.unit_settings.scale_length=1
    device=configure_device(args.device)
    render=CFG['render'];scene.render.resolution_x=render['width'];scene.render.resolution_y=render['height'];scene.render.resolution_percentage=render['preview_percent'] if args.quality=='preview' else 100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8'
    scene.cycles.samples=render['preview_samples'] if args.quality=='preview' else render['final_samples']
    scene.cycles.use_denoising=True;scene.cycles.seed=render['seed'];scene.cycles.max_bounces=10;scene.cycles.transmission_bounces=8;scene.cycles.glossy_bounces=6
    scene.cycles.adaptive_threshold=.035 if args.quality=='preview' else .015
    scene.view_settings.view_transform='AgX';scene.view_settings.exposure=CFG['lighting']['exposure']
    C['Arquitetura'].hide_select=True
    for o in C['Arquitetura'].objects:o.hide_select=True
    stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    output=args.output
    if output is None:output=Path('projeto/versoes')/f'sala-industrial-preview-{stamp}.blend' if args.quality=='preview' else Path('projeto/sala-industrial.blend')
    if not output.is_absolute():output=ROOT/output
    output=output.resolve()
    if output.suffix.lower()!='.blend':raise ValueError('O destino deve terminar em .blend')
    if output.is_relative_to(ROOT/'referencias'):raise ValueError('Não grave modelos na pasta de referências')
    output=unique_path(output);output.parent.mkdir(parents=True,exist_ok=True)
    render_path=ROOT/'renders'/('previa-'+stamp+'.png' if args.quality=='preview' else 'geracao-final-'+stamp+'.png')
    render_path.parent.mkdir(parents=True,exist_ok=True)
    scene.render.filepath=str(render_path)
    scene['origem_medidas']=CFG['scale_basis'];scene['gerado_utc']=stamp;scene['quality']=args.quality
    scene['device_info']=json.dumps(device);scene['config_sha256']=hashlib.sha256((ROOT/'config/cena.json').read_bytes()).hexdigest()
    scene['instrucao_edicao']='Mova os objetos pai MESA_, CADEIRA_, BANQUETA_, SOFA_. Arquitetura bloqueada: reative a seta no Outliner.'
    bpy.ops.object.select_all(action='DESELECT')
    for area in bpy.context.screen.areas if bpy.context.screen else []:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.shading.type='MATERIAL'
    bpy.ops.wm.save_as_mainfile(filepath=str(output))
    if not args.no_render:
        try:bpy.ops.render.render(write_still=True)
        except RuntimeError as e:
            if device['backend']!='OPTIX':raise
            device={'requested':args.device,'backend':'CPU','devices':['CPU'],'fallback_reason':'Falha no render OptiX: '+str(e)}
            scene.cycles.device='CPU';scene['device_info']=json.dumps(device)
            bpy.ops.wm.save_as_mainfile(filepath=str(output))
            bpy.ops.render.render(write_still=True)
    report={'timestamp_utc':stamp,'blender_version':bpy.app.version_string,'blend':str(output.relative_to(ROOT)) if output.is_relative_to(ROOT) else str(output),'render':str(render_path.relative_to(ROOT)) if not args.no_render else None,'device':device,'object_count':len(scene.objects),'mesh_count':sum(o.type=='MESH' for o in scene.objects),'collections':list(C),'config_sha256':scene['config_sha256'],'quality':args.quality,'hypotheses':CFG['architecture_hypotheses']}
    out=ROOT/'relatorios'/f'geracao-{stamp}.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('BUILD_COMPLETE',json.dumps(report,ensure_ascii=False),flush=True)


if __name__=='__main__':main()
