"""Acabamentos e mobiliário adicional, separados da arquitetura protegida."""
import math
import json

import bpy
from mathutils import Matrix, Vector

import blender_primitives as g
import residence07_industrial as base
from industrial_photoreal_materials import MATERIALS as M, metric_uv


def col(name):
    collection = bpy.data.collections.new('PHOTO6_' + name)
    g.C[collection.name] = collection
    return collection


def box(name, loc, size, material, collection, bevel=.003):
    obj = g.box('PHOTO6 ' + name, loc, size, M[material], collection.name, bevel)
    if material in {'Carvalho quente', 'Cimento fino', 'Linho natural'}:
        metric_uv(obj)
    obj['photoreal_detail'] = True
    return obj


def rod(name, start, end, radius, material, collection):
    obj = g.rod('PHOTO6 ' + name, start, end, radius, M[material], collection.name)
    obj['photoreal_detail'] = True
    return obj


def skirting(ground, upper, protected):
    count = 0
    for name in protected:
        obj = bpy.data.objects[name]
        if obj.type != 'MESH' or not obj.get('wall_id') or 'CORTE' in name.upper():
            continue
        coords = [base.world(obj) @ v.co for v in obj.data.vertices]
        lo = min(v.z for v in coords)
        if min(abs(lo - z) for z in [0, 2.7]) > .002:
            continue
        collection = ground if lo < 1 else upper
        matrix = base.world(obj)
        for face in obj.data.polygons:
            points = [matrix @ obj.data.vertices[i].co for i in face.vertices]
            lower = [p for p in points if abs(p.z - lo) < .002]
            if len(lower) != 2:
                continue
            a, b = lower
            delta = b - a; length = Vector((delta.x, delta.y)).length
            if length < .20:
                continue
            normal = matrix.to_3x3().inverted_safe().transposed() @ face.normal
            if abs(normal.z) > .01:
                continue
            center = (a + b) / 2 + normal.normalized() * .007
            trim = box('Rodape ' + str(count), (center.x, center.y, lo + .045), (length, .014, .09), 'Grafite acetinado', collection, .0015)
            trim.rotation_euler.z = math.atan2(delta.y, delta.x)
            count += 1
    return count


def rack(ground, protected):
    for name in ['ATUAL Rack branco', 'ATUAL Rack tampo']:
        assert name not in protected
        obj = bpy.data.objects.get(name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)
    x, y = 3.01, 1.40
    box('Rack tampo carvalho', (x, y, .54), (.44, 1.17, .045), 'Carvalho quente', ground, .007)
    box('Rack fundo', (3.215, y, .34), (.018, 1.12, .32), 'Aco pintado', ground)
    box('Rack prateleira', (x, y, .19), (.40, 1.12, .022), 'Carvalho quente', ground)
    for xx in [2.82, 3.20]:
        for yy in [.86, 1.94]:
            box('Rack pe metal', (xx, yy, .28), (.025, .025, .46), 'Aco pintado', ground, .002)
    for yy in [.84, 1.40, 1.96]:
        box('Rack divisor', (x, yy, .35), (.40, .018, .31), 'Aco pintado', ground)
    # Tela de metal com aberturas reais: evita uma face opaca fingindo ser grade.
    for i in range(40):
        yy = .86 + i * 1.08 / 39
        rod('Rack grade vertical', (2.806, yy, .22), (2.806, yy, .48), .0018, 'Aco pintado', ground)
    for i in range(11):
        zz = .22 + i * .026
        rod('Rack grade horizontal', (2.806, .86, zz), (2.806, 1.94, zz), .0018, 'Aco pintado', ground)
    for yy in [1.14, 1.68]:
        rod('Rack puxador', (2.785, yy - .055, .44), (2.785, yy + .055, .44), .004, 'Inox escovado', ground)
    for i in range(3):
        box('Livro rack', (2.99, 1.67, .215 + i * .022), (.28, .30, .019), 'Carvalho quente' if i == 0 else 'Grafite acetinado', ground, .001)


def fixtures(ground, upper, office):
    for x, y, z, collection, axis in [(3.274, 3.12, 1.10, ground, 'X'), (.162, 2.90, .28, ground, 'X'),
                                     (3.49, 5.0, 3.80, office, 'X'), (5.40, 6.39, 1.12, ground, 'Y')]:
        size = (.008, .075, .115) if axis == 'X' else (.075, .008, .115)
        box('Placa interruptor', (x, y, z), size, 'Grafite acetinado', collection, .004)
        for dz in [-.027, .027]:
            slot_size = (.010, .025, .012) if axis == 'X' else (.025, .010, .012)
            box('Modulo interruptor', (x, y, z + dz), slot_size, 'Aco pintado', collection, .002)
    for xx in [3.75, 4.36, 4.98, 5.94]:
        rod('Puxador cozinha', (xx - .085, 6.385, .77), (xx + .085, 6.385, .77), .005, 'Aco pintado', ground)
        for px in [xx - .085, xx + .085]:
            rod('Suporte puxador', (px, 6.39, .77), (px, 6.415, .77), .004, 'Aco pintado', ground)
    for y in [1.16, 2.12]:
        box('Base arandela sofa', (.168, y, 1.93), (.025, .10, .16), 'Aco pintado', ground)
        rod('Braco arandela', (.19, y, 1.97), (.43, y, 1.97), .012, 'Aco pintado', ground)
        g.lathe('PHOTO6 Cupula arandela', [(.11, 0), (.11, .008), (.075, .10), (.025, .13)], (.43, y, 1.79), M['Aco pintado'].name, ground.name, segments=64)
        g.sphere('PHOTO6 Lampada arandela', (.43, y, 1.80), (.029, .029, .018), M['Luz ambar'], ground.name)
    for xy in [(1.05, 3.2), (2.60, 3.2), (4.80, 5.50), (1.00, 6.1)]:
        g.cylinder('PHOTO6 Aro teto', (*xy, 2.535), .044, .015, M['Aco pintado'], ground.name, vertices=48)
        g.cylinder('PHOTO6 Difusor teto', (*xy, 2.525), .030, .003, M['Luz ambar'], ground.name, vertices=48)
    for name, x, y, z, collection in [
        ('cozinha', 4.80, 5.75, 2.52, ground),
        ('lavanderia', 4.80, 8.90, 2.72, ground),
        ('hall terreo', 4.45, 3.60, 2.52, ground),
        ('hall superior', 4.45, 3.55, 5.22, upper),
        ('quarto frente', 4.80, 1.40, 5.22, upper),
    ]:
        box('Plafon ' + name, (x, y, z), (.32, .32, .035), 'Aco pintado', collection, .008)
        box('Difusor plafon ' + name, (x, y, z - .020), (.28, .28, .004), 'Luz ambar', collection, .004)
    box('Arandela lavabo base', (4.80, 3.04, 1.68), (.50, .025, .065), 'Aco pintado', ground, .006)
    box('Arandela lavabo difusor', (4.80, 3.022, 1.68), (.46, .008, .035), 'Luz ambar', ground, .003)
    # Fixações visíveis da mesa, proporcionais às peças existentes.
    for xx in [1.17, 2.03]:
        for yy in [3.75, 5.25]:
            g.cylinder('PHOTO6 Parafuso mesa', (xx, yy, .8055), .004, .001, M['Aco pintado'], ground.name, vertices=16)
    # Borracha de vedação nas portas envidraçadas posteriores, sem deslocar caixilhos.
    for yy in [7.67, 8.43]:
        rod('Vedacao divisao', (3.339, yy, .03), (3.339, yy, 2.05), .003, 'Borracha', ground)
    for zz in [3.49, 4.49]:
        rod('Perfil estante escritorio', (5.70, 4.64, zz), (5.70, 6.31, zz), .006, 'Aco pintado', office)


def environment(exterior):
    import photographic_interiors as photo
    from industrial_photoreal_data import ROOT
    photo.ASSETS += json.loads((ROOT / 'assets/biblioteca-industrial/manifesto.json').read_text())['records']
    photo.COL = exterior.name
    # Plantas nativas detalhadas e instanciadas, fora dos contornos de circulação.
    for i, (x, y, height) in enumerate([(-.6, -1.5, 1.5), (6.8, 11.0, 1.7), (-.5, 10.9, 2.0)]):
        photo.place('potted_plant_02', 'PHOTO6 entorno ' + str(i), (x, y, 0), height=height, angle=i * 1.1)


def bathroom_parents(protected):
    """Restaurar famílias copiadas sem seus pais, mantendo coordenadas locais."""
    repaired = {}
    for suffix in ['.001', '.002']:
        for root_name, children in [
            ('Vaso sanitario', ['Louca base', 'Louca assento', 'Louca abertura']),
            ('Lavatorio', ['Gabinete banho', 'Bancada banho', 'Cuba banho', 'Espelho banho']),
        ]:
            parent = bpy.data.objects['ATUAL R07 ' + root_name + suffix]
            for child_name in children:
                child = bpy.data.objects['ATUAL R07 ' + child_name + suffix]
                assert child.name not in protected and parent.name not in protected
                assert child.parent is None, child.name
                local = child.matrix_basis.copy()
                child.parent = parent
                child.matrix_parent_inverse = Matrix.Identity(4)
                child.matrix_basis = local
                repaired[child.name] = parent.name
    return repaired


def build(protected):
    ground, upper, office, exterior = [col(n) for n in ['Acabamento_Terreo', 'Acabamento_Superior', 'Acabamento_Escritorio', 'Entorno']]
    repaired = bathroom_parents(protected)
    trims = skirting(ground, upper, protected)
    rack(ground, protected); fixtures(ground, upper, office); environment(exterior)
    import photographic_interiors as photo
    # Trocar vegetação esquemática por ativos com folhas e materiais fotografados.
    replacements = [('IND07 Planta escritorio', office, .36), ('IND07 Planta prateleira', ground, .36)]
    replacements += [(o.name, ground, .30) for o in list(bpy.data.objects) if o.type == 'EMPTY' and o.name.startswith('ATUAL Planta janela cozinha')]
    for name, target, height in replacements:
        original = bpy.data.objects.get(name)
        if not original: continue
        family = [original, *original.children_recursive]
        assert not any(o.name in protected for o in family)
        position = list(base.world(original).translation)
        for obj in reversed(family): bpy.data.objects.remove(obj, do_unlink=True)
        photo.COL = target.name; photo.place('potted_plant_04', 'PHOTO6 ' + name, position, height=height)
    # O jardim da base documental ficou dentro do bar após a reforma atual.
    # Preservar os dados fonte e usar uma coleção de apresentação sem esse proxy.
    original_context = bpy.data.collections['R07_Contexto']; original_context.use_fake_user = True
    old_plant = bpy.data.objects.get('R07 Jardim contexto')
    omitted = {old_plant, *old_plant.children_recursive} if old_plant else set()
    proxy = col('Contexto_Apresentacao')
    for obj in original_context.objects:
        if obj not in omitted: proxy.objects.link(obj)
    photo.COL = ground.name
    photo.place('potted_plant_04', 'PHOTO6 Planta bancada bar', (.32, 9.49, 1.025), height=.38)
    return {'ground': ground, 'upper': upper, 'office': office, 'exterior': exterior, 'context_proxy': proxy}, {
        'skirting_segments': trims, 'vegetation_replacements': len(replacements) + 1,
        'bathroom_parents_repaired': repaired,
        'presentation_omitted_context_vegetation': sorted(o.name for o in omitted),
        'vegetation_note': 'Dados do jardim documental preservados, omitidos apenas da apresentação da reforma; planta detalhada sobre a bancada em seu lugar.'}
