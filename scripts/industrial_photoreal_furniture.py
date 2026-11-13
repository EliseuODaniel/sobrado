"""Refinamentos de móveis e esquadria, com malhas e materiais editáveis."""
import math

import bpy
from mathutils import Vector

import blender_primitives as g
import residence07_industrial as base
from industrial_photoreal_data import ROOT
from industrial_photoreal_details import box, rod
from industrial_photoreal_materials import MATERIALS as M


def chair_mesh(name, vertices, faces, collection, material, thickness=0):
    mesh = bpy.data.meshes.new(name); mesh.from_pydata(vertices, [], faces); mesh.update()
    mesh.materials.append(M[material]); obj = bpy.data.objects.new('PHOTO6 ' + name, mesh); collection.objects.link(obj)
    for face in mesh.polygons: face.use_smooth = True
    if thickness: obj.modifiers.new('Espessura real', 'SOLIDIFY').thickness = thickness
    return obj


def ergonomic_chair(collection, protected):
    prefixes = ('IND07 Cadeira ', 'IND07 Coluna cadeira', 'IND07 Raio cadeira', 'IND07 Rodizio')
    for obj in list(bpy.data.objects):
        if obj.name.startswith(prefixes):
            assert obj.name not in protected
            bpy.data.objects.remove(obj, do_unlink=True)
    x, y, z = 4.58, 5.60, 2.70
    rod('Pistao cadeira', (x, y, z + .12), (x, y, z + .43), .026, 'Inox escovado', collection)
    for i in range(5):
        a = i * math.tau / 5; px, py = x + .31 * math.cos(a), y + .31 * math.sin(a)
        rod('Base cadeira', (x, y, z + .16), (px, py, z + .08), .023, 'Aco pintado', collection)
        for offset in [-.021, .021]:
            wheel = g.cylinder('PHOTO6 Rodizio duplo', (px + offset, py, z + .045), .038, .018, M['Borracha'], collection.name, vertices=32)
            wheel.rotation_euler.y = math.pi / 2
    verts, faces, nu, nv = [], [], 28, 24
    for i in range(nu + 1):
        u = i / nu * 2 - 1
        for j in range(nv + 1):
            v = j / nv * 2 - 1
            verts.append((x + u * .25, y + v * .245, z + .475 + .018 * (1 - u * u) * (1 - v * v) - .02 * max(0, -u) ** 3))
    for i in range(nu):
        for j in range(nv):
            k = i * (nv + 1) + j; faces.append((k, k + 1, k + nv + 2, k + nv + 1))
    chair_mesh('Assento ergonomico', verts, faces, collection, 'Grafite acetinado', .055)
    verts, faces, nu, nv = [], [], 126, 162

    def point(u, v):
        return (x + .225 + .07 * v - .035 * math.sin(v * math.pi) - .045 * u * u,
                y + u * (.225 - .035 * v), z + .58 + v * .57)

    for i in range(nu + 1):
        for j in range(nv + 1): verts.append(point(i / nu * 2 - 1, j / nv))
    for i in range(nu):
        for j in range(nv):
            if i % 3 == 1 and j % 3 == 1: continue
            k = i * (nv + 1) + j; faces.append((k, k + 1, k + nv + 2, k + nv + 1))
    chair_mesh('Encosto de tela perfurado', verts, faces, collection, 'Borracha', .001)
    outline = [point(-1, j / 16) for j in range(17)] + [point(u / 8, 1) for u in range(-7, 9)]
    outline += [point(1, j / 16) for j in range(15, -1, -1)] + [point(u / 8, 0) for u in range(7, -9, -1)]
    g.curve('PHOTO6 Aro encosto', outline + [outline[0]], .012, M['Aco pintado'].name, collection.name)
    rod('Suporte lombar', (x + .26, y, z + .35), (x + .31, y, z + .95), .019, 'Aco pintado', collection)
    head = box('Apoio cabeca', (x + .29, y, z + 1.24), (.095, .31, .17), 'Grafite acetinado', collection, .035)
    head.rotation_euler.y = -.15
    for yy in [y - .285, y + .285]:
        rod('Suporte braco cadeira', (x + .12, yy, z + .42), (x + .12, yy, z + .69), .015, 'Aco pintado', collection)
        box('Apoio braco cadeira', (x, yy, z + .70), (.34, .065, .045), 'Borracha', collection, .018)


def office_screens(collection):
    screens = sorted((o for o in bpy.data.objects if o.name.startswith('IND07 Monitor tela')), key=lambda o: o.name)
    for i, obj in enumerate(screens):
        mat = g.basic('PHOTO6 Interface monitor ' + str(i), (.12, .15, .18), .25)
        nodes, links = mat.node_tree.nodes, mat.node_tree.links; bs = nodes.get('Principled BSDF')
        image = bpy.data.images.load(str(ROOT / 'assets/fotorrealismo-industrial/telas' / ('editor-' + str(i) + '.png'))); image.pack()
        tex = nodes.new('ShaderNodeTexImage'); tex.image = image
        links.new(tex.outputs['Color'], bs.inputs['Base Color']); links.new(tex.outputs['Color'], bs.inputs['Emission Color'])
        bs.inputs['Emission Strength'].default_value = .75
        obj.data = obj.data.copy(); obj.data.materials.clear(); obj.data.materials.append(mat)
        uv = obj.data.uv_layers.new(name='PHOTO6_Tela'); uv.active_render = True
        lo = [min(v.co[a] for v in obj.data.vertices) for a in range(3)]
        hi = [max(v.co[a] for v in obj.data.vertices) for a in range(3)]
        for k, loop in enumerate(obj.data.loops):
            p = obj.data.vertices[loop.vertex_index].co
            uv.data[k].uv = ((p.y - lo[1]) / (hi[1] - lo[1]), (p.z - lo[2]) / (hi[2] - lo[2]))
    for obj in list(bpy.data.objects):
        if obj.name.startswith('IND07 Linha de codigo'): bpy.data.objects.remove(obj, do_unlink=True)
    box('Mousepad', (3.99, 5.6, 3.496), (.23, .69, .003), 'Borracha', collection, .012)
    mouse = g.sphere('PHOTO6 Mouse', (4.02, 6.01, 3.52), (.052, .034, .022), M['Grafite acetinado'], collection.name)
    rod('Cabo mouse', (4.0, 6.01, 3.51), (3.75, 6.05, 3.51), .0015, 'Borracha', collection)
    for i in range(5):
        for j in range(12): box('Tecla', (3.947 + i * .028, 5.444 + j * .029, 3.527), (.022, .024, .005), 'Grafite acetinado', collection, .002)


def window(upper):
    # Vão J3-quarto-fundos, exatamente nas coordenadas oficiais; acabamento independente.
    x, y, bottom, width, height = 4.75, 7.125, 3.60, 1.50, 1.20
    for zz in [bottom + .022, bottom + height - .022]:
        box('Janela fundos travessa', (x, y, zz), (width, .065, .044), 'Aco pintado', upper, .002)
    for xx in [x - width / 2 + .022, x, x + width / 2 - .022]:
        box('Janela fundos montante', (xx, y, bottom + height / 2), (.035, .065, height), 'Aco pintado', upper, .002)
    for sign in [-1, 1]:
        box('Janela fundos vidro', (x + sign * width / 4, y + sign * .009, bottom + height / 2), (width / 2 - .052, .006, height - .065), 'Vidro incolor', upper, .0005)
        box('Janela fundos puxador', (x + sign * .035, y - .040, bottom + height / 2), (.012, .018, .13), 'Aco pintado', upper, .003)


def table_and_glassware(collection, protected):
    for obj in list(bpy.data.objects):
        if 'bar frente madeira' in obj.name.lower():
            points = [base.world(obj) @ v.co for v in obj.data.vertices]
            lo = [min(p[i] for p in points) for i in range(3)]; hi = [max(p[i] for p in points) for i in range(3)]
            for i in range(1, 6):
                box('Junta entre tabuas bar', ((lo[0] + hi[0]) / 2, lo[1] - .0008, lo[2] + (hi[2] - lo[2]) * i / 6), (hi[0] - lo[0] - .005, .001, .0015), 'Grafite acetinado', collection, 0)
    for obj in list(bpy.data.objects):
        if obj.name.startswith('IND07 Pe torneado mesa'):
            assert obj.name not in protected
            center = base.world(obj).translation.copy()
            profile = [(.035, 0), (.035, .04), (.030, .06), (.034, .24), (.048, .56), (.052, .62), (.052, .75)]
            verts = [(center.x + sx * radius, center.y + sy * radius, center.z + z) for radius, z in profile for sx, sy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]
            faces = [(3, 2, 1, 0)] + [(i * 4 + j, i * 4 + (j + 1) % 4, (i + 1) * 4 + (j + 1) % 4, (i + 1) * 4 + j) for i in range(len(profile) - 1) for j in range(4)]
            faces.append(tuple(range(len(verts) - 4, len(verts))))
            leg = chair_mesh('Pe mesa torneado quadrado', verts, faces, collection, 'Carvalho quente')
            from industrial_photoreal_materials import metric_uv
            metric_uv(leg); bevel = leg.modifiers.new('Quinas de madeira', 'BEVEL'); bevel.width = .003; bevel.segments = 3
            bpy.data.objects.remove(obj, do_unlink=True)
    shelves = [o for o in bpy.data.objects if 'Armário bar prateleira' in o.name]
    for obj in shelves:
        matrix = base.world(obj); points = [matrix @ v.co for v in obj.data.vertices]
        if max(p.z for p in points) > 2.05: continue
        x = sum(p.x for p in points) / len(points); y = sum(p.y for p in points) / len(points); z = max(p.z for p in points)
        for dx in [-.14, .05]:
            profile = [(.031, 0), (.033, .003), (.030, .007), (.005, .011), (.003, .085), (.025, .10), (.035, .135), (.032, .18), (.026, .205), (.0245, .205), (.030, .18), (.033, .135), (.023, .102), (.002, .087), (.002, .010), (.031, 0)]
            g.lathe('PHOTO6 Taca de vidro', profile, (x + dx, y - .015, z + .002), M['Vidro incolor'].name, collection.name, segments=48)


def sink(collection, protected):
    counter = bpy.data.objects.get('ATUAL Bar tampo granito'); old = bpy.data.objects.get('ATUAL Cuba bar')
    if not counter or not old: return
    assert counter.name not in protected and old.name not in protected
    points = [base.world(counter) @ v.co for v in counter.data.vertices]; top = max(p.z for p in points)
    center = base.world(old).translation
    cutter = g.box('PHOTO6 Recorte temporario cuba', (center.x, center.y, top - .04), (.392, .282, .30), M['Borracha'], counter.users_collection[0].name, .022)
    modifier = counter.modifiers.new('Vao real da cuba', 'BOOLEAN'); modifier.operation = 'DIFFERENCE'; modifier.object = cutter
    bpy.context.view_layer.objects.active = counter; counter.select_set(True)
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter, do_unlink=True); bpy.data.objects.remove(old, do_unlink=True)
    front = next((o for o in bpy.data.objects if 'bar frente madeira' in o.name.lower()), None)
    if front:
        assert front.name not in protected
        bpy.context.view_layer.update(); depth = front.dimensions.y
        front.dimensions.y = .025; front.location.y -= (depth - .025) / 2
    rings = [(.416, .306, .028, top + .003), (.390, .280, .025, top + .001),
             (.375, .265, .030, top - .04), (.320, .210, .035, top - .15)]
    vertices = []
    for width, depth, radius, z in rings:
        for sx, sy, start in [(1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)]:
            for step in range(8):
                a = math.radians(start + step * 90 / 7)
                vertices.append((center.x + sx * (width / 2 - radius) + radius * math.cos(a),
                                 center.y + sy * (depth / 2 - radius) + radius * math.sin(a), z))
    n = 32
    faces = [(ring * n + j, ring * n + (j + 1) % n, (ring + 1) * n + (j + 1) % n, (ring + 1) * n + j) for ring in range(len(rings) - 1) for j in range(n)]
    faces.append(tuple(range((len(rings) - 1) * n, len(rings) * n)))
    chair_mesh('Cuba inox profunda', vertices, faces, collection, 'Inox escovado', .0012)
    g.cylinder('PHOTO6 Valvula cuba', (center.x, center.y, top - .148), .022, .003, M['Inox escovado'], collection.name, vertices=48)
    g.cylinder('PHOTO6 Ralo cuba', (center.x, center.y, top - .146), .012, .001, M['Borracha'], collection.name, vertices=32)


def build(collections, protected):
    ergonomic_chair(collections['office'], protected)
    office_screens(collections['office']); window(collections['upper'])
    table_and_glassware(collections['ground'], protected)
    sink(collections['ground'], protected)
    for name, y_size, z_size in [('ATUAL Painel TV', 2.0, 1.65), ('ATUAL TV', 1.47, .85), ('IND07 Tela TV paisagem', 1.40, .78)]:
        obj = bpy.data.objects.get(name)
        if obj:
            assert name not in protected
            bpy.context.view_layer.update()
            obj.dimensions.y = y_size; obj.dimensions.z = z_size
    return {'chair': 'Encosto perfurado e assento curvo com rodízios duplos', 'screens': 3, 'window': 'J3-quarto-fundos'}
