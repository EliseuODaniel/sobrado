"""Materiais PBR e coordenadas métricas, sem modificar a geometria métrica."""
import json
import math

import bpy
from mathutils import Vector

import blender_primitives as g
from industrial_photoreal_data import ROOT, CFG, sha
from residence07_industrial import world as world_transform

MATERIALS = {}
UV_UPDATED = []


def image(asset, channel):
    records = json.loads((ROOT / CFG['asset_manifest']).read_text())['records']
    item = next(r for r in records if r['asset'] == asset and r['channel'] == channel)
    file = ROOT / item['path']
    assert sha(file) == item['sha256']
    im = bpy.data.images.load(str(file), check_existing=True)
    if channel not in {'Diffuse', 'hdri'}:
        im.colorspace_settings.name = 'Non-Color'
    im.pack()
    return im


def pbr(name, asset, *, scale=1, tint=(1, 1, 1), rough=(.8, .12), normal=.22, metallic=0, coat=0):
    mat = g.basic('PHOTO6 ' + name, (.4, .4, .4), .5, metallic)
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bs = nodes.get('Principled BSDF')
    bs.inputs['Coat Weight'].default_value = coat
    bs.inputs['Coat Roughness'].default_value = .22
    uv = nodes.new('ShaderNodeUVMap'); uv.uv_map = 'PHOTO6_Metros'
    mapping = nodes.new('ShaderNodeVectorMath'); mapping.operation = 'SCALE'; mapping.inputs['Scale'].default_value = scale
    links.new(uv.outputs['UV'], mapping.inputs[0])
    for channel in ['Diffuse', 'Rough', 'nor_gl']:
        tex = nodes.new('ShaderNodeTexImage'); tex.image = image(asset, channel)
        tex.label = f'{asset} / {channel} / 4K CC0'
        links.new(mapping.outputs[0], tex.inputs['Vector'])
        if channel == 'Diffuse':
            mul = nodes.new('ShaderNodeMixRGB'); mul.blend_type = 'MULTIPLY'; mul.inputs[0].default_value = 1
            mul.inputs[2].default_value = (*tint, 1); links.new(tex.outputs['Color'], mul.inputs[1]); links.new(mul.outputs[0], bs.inputs['Base Color'])
        elif channel == 'Rough':
            remap = nodes.new('ShaderNodeMath'); remap.operation = 'MULTIPLY_ADD'
            remap.inputs[1].default_value, remap.inputs[2].default_value = rough
            links.new(tex.outputs['Color'], remap.inputs[0]); links.new(remap.outputs[0], bs.inputs['Roughness'])
        else:
            n = nodes.new('ShaderNodeNormalMap'); n.inputs['Strength'].default_value = normal
            n.uv_map = 'PHOTO6_Metros'; links.new(tex.outputs['Color'], n.inputs['Color']); links.new(n.outputs[0], bs.inputs['Normal'])
    mat['source_asset'] = asset; mat['source_license'] = 'CC0-1.0'; mat['uv_units'] = 'meters'
    MATERIALS[name] = mat
    return mat


def metric_uv(obj, preserve_atlas=False):
    if obj.type != 'MESH':
        return
    if obj.data.users > 1:
        obj.data = obj.data.copy()
    original = next((layer for layer in obj.data.uv_layers if layer.name != 'PHOTO6_Metros'), None)
    uv = obj.data.uv_layers.get('PHOTO6_Metros') or obj.data.uv_layers.new(name='PHOTO6_Metros')
    uv.active_render = True
    matrix = world_transform(obj)
    if preserve_atlas and original and len(obj.data.vertices) > 64:
        area_3d = 0.0; area_uv = 0.0
        for poly in obj.data.polygons:
            points = [matrix @ obj.data.vertices[obj.data.loops[i].vertex_index].co for i in poly.loop_indices]
            coords = [original.data[i].uv.copy() for i in poly.loop_indices]
            for i in range(1, len(points) - 1): area_3d += (points[i] - points[0]).cross(points[i + 1] - points[0]).length / 2
            area_uv += abs(sum(a.x * b.y - b.x * a.y for a, b in zip(coords, coords[1:] + coords[:1]))) / 2
        if area_uv > 1e-9:
            factor = math.sqrt(area_3d / area_uv)
            for index in range(len(obj.data.loops)): uv.data[index].uv = original.data[index].uv * factor
            obj['photoreal_uv_method'] = 'Original atlas retained; metric density from 3D/UV area ratio'
            UV_UPDATED.append(obj.name)
            return
    normal_matrix = matrix.to_3x3().inverted_safe().transposed()
    for poly in obj.data.polygons:
        normal = normal_matrix @ poly.normal
        dominant = max(range(3), key=lambda axis: abs(normal[axis]))
        axes = [(1, 2), (0, 2), (0, 1)][dominant]
        if 'bar frente madeira' in obj.name.lower(): axes = axes[::-1]
        for index in poly.loop_indices:
            p = matrix @ obj.data.vertices[obj.data.loops[index].vertex_index].co
            uv.data[index].uv = (p[axes[0]], p[axes[1]])
    UV_UPDATED.append(obj.name)


def floor_material():
    mat = pbr('Porcelanato acetinado', 'floor_tiles_02', scale=1 / 2.4, tint=(1, 1, 1), rough=(.12, .14), normal=.07, coat=.14)
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bs = nodes.get('Principled BSDF'); base = bs.inputs['Base Color'].links[0].from_socket
    mix = nodes.new('ShaderNodeMixRGB'); mix.inputs[0].default_value = .16; mix.inputs[1].default_value = (.42, .40, .36, 1)
    links.new(base, mix.inputs[2]); links.new(mix.outputs[0], bs.inputs['Base Color'])
    coord = nodes.new('ShaderNodeTexCoord'); brick = nodes.new('ShaderNodeTexBrick')
    brick.offset = 0; brick.inputs['Scale'].default_value = 1; brick.inputs['Brick Width'].default_value = .60
    brick.inputs['Row Height'].default_value = .60; brick.inputs['Mortar Size'].default_value = .0012
    brick.inputs['Color1'].default_value = (.42, .40, .36, 1); brick.inputs['Color2'].default_value = (.41, .39, .35, 1)
    brick.inputs['Mortar'].default_value = (.22, .21, .19, 1); links.new(coord.outputs['Object'], brick.inputs['Vector'])
    # A malha de piso foi criada em coordenadas de projeto: projeção XY em metros.
    blend = nodes.new('ShaderNodeMixRGB'); blend.blend_type = 'MIX'; blend.inputs[0].default_value = .30
    links.new(brick.outputs['Color'], blend.inputs[1]); links.new(mix.outputs[0], blend.inputs[2]); links.new(blend.outputs[0], bs.inputs['Base Color'])
    bump = nodes.new('ShaderNodeBump'); bump.inputs['Distance'].default_value = .0007; bump.inputs['Strength'].default_value = .22
    links.new(brick.outputs['Fac'], bump.inputs['Height']); links.new(bs.inputs['Normal'].links[0].from_socket, bump.inputs['Normal']); links.new(bump.outputs[0], bs.inputs['Normal'])
    return mat


def build_materials():
    pbr('Cimento fino', 'grey_plaster', scale=.85, tint=(.77, .75, .70), rough=(.36, .45), normal=.09)
    pbr('Carvalho quente', 'wood_table_001', scale=.70, tint=(1.0, .83, .63), rough=(.27, .29), normal=.15, coat=.07)
    pbr('Couro caramelo', 'brown_leather', scale=12.0, tint=(1.18, .75, .43), rough=(.22, .39), normal=.12, coat=.05)
    pbr('Linho natural', 'denim_fabric', scale=10.0, tint=(1.0, .91, .76), rough=(.25, .65), normal=.25)
    MATERIALS['Linho natural'].node_tree.nodes.get('Principled BSDF').inputs['Sheen Weight'].default_value = .45
    pbr('Petroleo mineral', 'grey_plaster', scale=.65, tint=(.12, .24, .29), rough=(.30, .46), normal=.15)
    pbr('Pedra oxidada', 'slate_floor_03', scale=1.0, tint=(1.0, .85, .68), rough=(.5, .24), normal=.42)
    stone = MATERIALS['Pedra oxidada']; nodes, links = stone.node_tree.nodes, stone.node_tree.links; bs = nodes.get('Principled BSDF')
    source = bs.inputs['Base Color'].links[0].from_socket
    hue = nodes.new('ShaderNodeHueSaturation'); hue.inputs['Saturation'].default_value = .45; hue.inputs['Value'].default_value = .50
    links.new(source, hue.inputs['Color'])
    mix = nodes.new('ShaderNodeMixRGB'); mix.inputs[0].default_value = .70; mix.inputs[1].default_value = (.08, .09, .085, 1)
    links.new(hue.outputs[0], mix.inputs[2]); links.new(mix.outputs[0], bs.inputs['Base Color'])
    for key, color, amount in [('Cimento fino', (.33, .32, .30), .16), ('Petroleo mineral', (.032, .065, .077), .13), ('Linho natural', (.39, .36, .30), .12)]:
        mat = MATERIALS[key]; nodes, links = mat.node_tree.nodes, mat.node_tree.links; bs = nodes.get('Principled BSDF')
        source = bs.inputs['Base Color'].links[0].from_socket
        bw = nodes.new('ShaderNodeRGBToBW'); links.new(source, bw.inputs[0])
        tint = nodes.new('ShaderNodeMixRGB'); tint.blend_type = 'MULTIPLY'; tint.inputs[0].default_value = 1
        links.new(bw.outputs[0], tint.inputs[1]); tint.inputs[2].default_value = (*color, 1)
        mix = nodes.new('ShaderNodeMixRGB'); mix.inputs[0].default_value = amount; mix.inputs[1].default_value = (*color, 1)
        links.new(tint.outputs[0], mix.inputs[2]); links.new(mix.outputs[0], bs.inputs['Base Color'])
    for key, low, high in [('Carvalho quente', (.13, .065, .027), (.46, .29, .15)), ('Couro caramelo', (.17, .060, .024), (.38, .19, .085))]:
        mat = MATERIALS[key]; nodes, links = mat.node_tree.nodes, mat.node_tree.links; bs = nodes.get('Principled BSDF')
        source = bs.inputs['Base Color'].links[0].from_socket
        bw = nodes.new('ShaderNodeRGBToBW'); links.new(source, bw.inputs[0])
        minimum, maximum = (.006, .030) if key == 'Carvalho quente' else (.015, .055)
        ramp = nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position = minimum; ramp.color_ramp.elements[0].color = (*low, 1)
        ramp.color_ramp.elements[1].position = maximum; ramp.color_ramp.elements[1].color = (*high, 1)
        links.new(bw.outputs[0], ramp.inputs[0]); links.new(ramp.outputs[0], bs.inputs['Base Color'])
    floor_material()
    for name, color, rough, metal in [('Aco pintado', (.012, .016, .018), .34, 0),
                                     ('Grafite acetinado', (.035, .043, .044), .31, 0),
                                     ('Teto fosco', (.75, .73, .68), .82, 0),
                                     ('Borracha', (.009, .011, .010), .78, 0),
                                     ('Granito escuro', (.019, .022, .020), .19, 0),
                                     ('Inox escovado', (.52, .55, .56), .27, 1),
                                     ('Costura', (.22, .105, .046), .65, 0)]:
        mat = g.basic('PHOTO6 ' + name, color, rough, metal); MATERIALS[name] = mat
        if name in {'Aco pintado', 'Grafite acetinado', 'Granito escuro', 'Inox escovado'}:
            nodes, links = mat.node_tree.nodes, mat.node_tree.links; bs = nodes.get('Principled BSDF')
            noise = nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 190
            bump = nodes.new('ShaderNodeBump'); bump.inputs['Distance'].default_value = .00006; bump.inputs['Strength'].default_value = .10
            links.new(noise.outputs['Fac'], bump.inputs['Height']); links.new(bump.outputs[0], bs.inputs['Normal'])
            if name == 'Inox escovado': bs.inputs['Anisotropic'].default_value = .35
    glass = g.basic('PHOTO6 Vidro incolor', (.96, .98, .97), .025, transmission=1)
    glass.node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value = 1.52; MATERIALS['Vidro incolor'] = glass
    MATERIALS['Luz ambar'] = g.basic('PHOTO6 Luz ambar', (1, .49, .17), .25, emission=5)
    MATERIALS['Tela desligada'] = g.basic('PHOTO6 Tela desligada', (.004, .006, .008), .14, .18)


def apply_materials():
    mappings = {
        'IND07 Cimento': 'Cimento fino', 'IND07 Cimento PBR': 'Cimento fino',
        'IND07 Piso cimento': 'Porcelanato acetinado', 'IND07 Madeira quente': 'Carvalho quente',
        'IND07 Carvalho PBR': 'Carvalho quente', 'DESIGN Carvalho mel': 'Carvalho quente', 'HQ Madeira': 'Carvalho quente',
        'IND07 Couro PBR': 'Couro caramelo', 'IND07 Couro': 'Couro caramelo',
        'DESIGN Couro conhaque': 'Couro caramelo', 'IND07 Linho': 'Linho natural',
        'IND07 Juta': 'Linho natural', 'DESIGN Manta linho': 'Linho natural', 'HQ Tecido': 'Linho natural',
        'IND07 Aco': 'Aco pintado', 'IND07 Grafite': 'Grafite acetinado', 'IND07 Petroleo': 'Petroleo mineral',
        'IND07 Pedra': 'Granito escuro', 'Granito preto': 'Granito escuro', 'IND07 Teto': 'Teto fosco',
        'Inox': 'Inox escovado', 'Cromado': 'Inox escovado', 'DESIGN Costura couro': 'Costura',
        'IND07 Tela paisagem': 'Tela desligada', 'IND07 LED': 'Luz ambar',
        'Vidro': 'Vidro incolor',
        'Vidro transparente': 'Vidro incolor', 'IND07 Pedra oxidada': 'Pedra oxidada',
    }
    changed = []
    for obj in bpy.data.objects:
        if obj.type not in {'MESH', 'CURVE'}:
            continue
        if obj.type == 'MESH' and any(key in obj.name.lower() for key in ['throw_pillows', 'almofadas linho', 'manta com']):
            obj.data = obj.data.copy()
            for slot in obj.material_slots: slot.material = MATERIALS['Linho natural']
            metric_uv(obj, preserve_atlas=True)
            if 'throw_pillows' in obj.name.lower():
                smooth = obj.modifiers.new('Acabamento suave do tecido', 'SUBSURF')
                smooth.levels = 1; smooth.render_levels = 2
        if any(slot.material and slot.material.name in mappings for slot in obj.material_slots):
            obj.data = obj.data.copy()
        used = []
        if obj.type == 'MESH' and (obj.name == 'ATUAL Cama suite.001' or 'travesseiro suite' in obj.name.lower()):
            obj.data = obj.data.copy()
            for slot in obj.material_slots: slot.material = MATERIALS['Linho natural']
            used.append('Linho natural')
        for slot in obj.material_slots:
            target = mappings.get(slot.material.name) if slot.material else None
            if target:
                slot.material = MATERIALS[target]; used.append(target)
        if any(target in {'Cimento fino', 'Porcelanato acetinado', 'Carvalho quente', 'Couro caramelo', 'Linho natural', 'Petroleo mineral', 'Pedra oxidada'} for target in used):
            metric_uv(obj, preserve_atlas=any(target in {'Couro caramelo', 'Linho natural'} for target in used))
        if used:
            changed.append({'object': obj.name, 'materials': used})
    return changed
