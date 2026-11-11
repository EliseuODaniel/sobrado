"""Primitivas Blender compartilhadas, extraídas sem alteração dos helpers anteriores."""

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

def unique_path(path):
    if not path.exists():return path
    stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    return path.with_name(path.stem+'-'+stamp+path.suffix)
