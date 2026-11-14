"""Apresentação de instalações sem ático; construção apenas do Blender."""
from pathlib import Path
import sys, json, hashlib, math
import bpy
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import infrastructure_data as data
import blender_primitives as g

DEST = ROOT/'projeto/infraestrutura/instalacoes-pavimentos-forro.blend'
if '--output' in sys.argv:
    DEST = Path(sys.argv[sys.argv.index('--output')+1]).resolve()
    assert DEST.is_relative_to(ROOT), DEST
REPORT = ROOT/'relatorios/infraestrutura'
assert not DEST.exists(), DEST
assert Path(bpy.data.filepath).resolve() == ROOT/'projeto/atual/casa-07-atual-fiel.blend'
source = Path(bpy.data.filepath)
source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
REPORT.mkdir(parents=True, exist_ok=True)
DEST.parent.mkdir(parents=True, exist_ok=True)


def collection(name):
    c = bpy.data.collections.new(name); g.C[name] = c
    return c


def material(name, color, opacity=1):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    diffuse = nodes.new('ShaderNodeBsdfDiffuse'); diffuse.inputs['Color'].default_value = (*color, 1)
    if opacity < 1:
        transparent = nodes.new('ShaderNodeBsdfTransparent')
        mix = nodes.new('ShaderNodeMixShader'); mix.inputs[0].default_value = opacity
        links.new(transparent.outputs[0], mix.inputs[1]); links.new(diffuse.outputs[0], mix.inputs[2])
        links.new(mix.outputs[0], out.inputs['Surface'])
    else: links.new(diffuse.outputs[0], out.inputs['Surface'])
    m.diffuse_color = (*color, opacity); m['presentation_opacity'] = opacity
    g.M[name] = m
    return m


def line(name, points, diameter, mat, col, **props):
    curve = bpy.data.curves.new(name, 'CURVE'); curve.dimensions = '3D'
    curve.bevel_depth = diameter/2; curve.bevel_resolution = 3
    spline = curve.splines.new('POLY'); spline.points.add(len(points)-1)
    for p, xyz in zip(spline.points, points): p.co = (*xyz, 1)
    obj = bpy.data.objects.new(name, curve); col.objects.link(obj); curve.materials.append(mat)
    for key, value in props.items(): obj[key] = value
    return obj


def text(body, xyz, col, size=.25, mat=None):
    font = bpy.data.curves.new(body, 'FONT'); font.body = body; font.size = size; font.align_x = 'CENTER'
    obj = bpy.data.objects.new(body, font); col.objects.link(obj); obj.location = xyz
    font.materials.append(mat or ink)
    return obj


def copy_mesh(old, target, matrix, mat=None, prefix='INFRA '):
    obj = old.copy(); obj.name = prefix+old.name; obj.parent = None; obj.matrix_world = matrix
    obj.data = old.data.copy()
    if mat:
        obj.data.materials.clear(); obj.data.materials.append(mat)
    obj.hide_render = False; obj.hide_viewport = False
    obj['source_object'] = old.name
    target.objects.link(obj)
    return obj


# Ativar a cena completa e avaliar o grafo evita capturar posições antigas/zeradas.
source_scene = bpy.data.scenes['FIEL2_volumetria']; bpy.context.window.scene = source_scene
source_scene.frame_set(source_scene.frame_current); bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get(); dg.update()
architecture = list(bpy.data.collections['FIEL2_Apresentacao_ATUAL_Arquitetura'].all_objects)
back = list(bpy.data.collections['ATUAL_Fundos'].all_objects)
roof = list(bpy.data.collections['R07_Cobertura'].all_objects)
ceiling = list(bpy.data.collections['R07_Teto_Superior'].all_objects)
objects = {o for o in architecture+back+roof+ceiling if o.type == 'MESH'}
matrices = {o: o.evaluated_get(dg).matrix_world.copy() for o in objects}
wall_mat = material('INFRA Paredes translúcidas', (.42, .59, .52), .075)
slab_mat = material('INFRA Lajes translúcidas', (.68, .65, .53), .025)
ceiling_mat = material('INFRA Forro translúcido', (.55, .43, .72), .045)
roof_mat = material('INFRA Cobertura existente translúcida', (.40, .55, .66), .025)
ink = material('INFRA Texto', (.025, .055, .05))
colors = {key: material('INFRA '+data.LABELS[key], rgb) for key, rgb in data.COLORS.items()}
ground = collection('INFRA_Arquitetura_Terreo'); upper = collection('INFRA_Arquitetura_Superior')
forro0 = collection('INFRA_Forro_Terreo'); forro1 = collection('INFRA_Forro_Superior')
coverage = collection('INFRA_Cobertura_Original'); tankcol = collection('INFRA_Caixa_Original')
wall_counts = [0, 0]
for old in architecture+back:
    if old not in matrices: continue
    points = [matrices[old]@Vector(p) for p in old.bound_box]
    zmin = min(p.z for p in points)
    level = 1 if old.get('level') == 1 or zmin >= 2.55-1e-4 else 0
    target = upper if level else ground
    is_slab = old.get('slab') or 'Laje' in old.name or 'Piso' in old.name
    obj = copy_mesh(old, target, matrices[old], slab_mat if is_slab else wall_mat)
    obj['infrastructure_level'] = level
    if old.get('wall_id'): wall_counts[level] += 1
    # Face inferior da laje: referência visual do forro do térreo, sem alterar a laje.
    if old.get('slab') and level == 1:
        board = copy_mesh(old, forro0, matrices[old], ceiling_mat, prefix='FORRO REFERENCIA ')
        for vertex in board.data.vertices:
            p = matrices[old]@vertex.co
            p.z = 2.5375 + (p.z-2.55)*(.0125/.15)
            vertex.co = p
        board.matrix_world = Matrix.Identity(4)
        board['presentation_reference'] = 'Placa ilustrativa na face inferior da laje; não é levantamento de material/espessura'
for old in ceiling:
    if old in matrices: copy_mesh(old, forro1, matrices[old], ceiling_mat)
for old in roof:
    if old in matrices: copy_mesh(old, coverage, matrices[old], roof_mat)

# Biblioteca documental: caixa original, sem reposicionamento nem elementos do ático.
with bpy.data.libraries.load(str(ROOT/'projeto/original/casa-07-instalacoes.blend'), link=False) as (src, dst):
    dst.collections = ['INST_Reservatorio']
old_tank_col = dst.collections[0]
temp = bpy.data.scenes.new('INFRA_TEMP_AVALIACAO'); temp.collection.children.link(old_tank_col)
bpy.context.window.scene = temp; temp.frame_set(temp.frame_current); bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get(); dg.update()
for old in list(old_tank_col.all_objects):
    if old is not None and old.type in {'MESH', 'CURVE'}:
        copy_mesh(old, tankcol, old.evaluated_get(dg).matrix_world.copy())
tank = next(o for o in tankcol.objects if o.get('capacity_liters'))
assert (tank.matrix_world.translation-Vector(data.TANK)).length < 1e-4, tuple(tank.matrix_world.translation)

graph = data.graph(); nodes = {n['id']: n for n in graph['nodes']}
assert not data.hot_geometry_issues(graph), data.hot_geometry_issues(graph)
networks = {key: collection('INFRA_Rede_'+key) for key in data.COLORS}
levels = {(key, lv): collection(f'INFRA_Rede_{key}_Piso_{lv}') for key in data.COLORS for lv in [0, 1]}


def arrow(name, a, b, mat, col):
    a, b = Vector(a), Vector(b)
    if (b-a).length < .24: return
    direction = (b-a).normalized(); middle = (a+b)/2
    side = direction.cross(Vector((0, 0, 1)))
    if side.length < .01: side = direction.cross(Vector((0, 1, 0)))
    side.normalize()
    line(name, [middle-direction*.1+side*.055, middle+direction*.1,
                middle-direction*.1-side*.055], .018, mat, col, flow_direction=True)


for i, edge in enumerate(graph['edges']):
    if edge['geometry'] == 'junction': continue
    a, b = nodes[edge['a']]['xyz'], nodes[edge['b']]['xyz']; key = edge['system']
    diameter = max(edge['nominal_diameter_m'], .042)
    props = dict(system=key, node_a=edge['a'], node_b=edge['b'],
                 nominal_diameter_m=edge['nominal_diameter_m'], source=edge['source'],
                 proposed_segment=edge.get('proposed', False), graph_edge_index=i)
    line(f'INFRA {key} {i:03}', [a, b], diameter, colors[key], networks[key], **props)
    for lv, (lo, hi) in enumerate([(-.35, 2.65), (2.7, 5.4)]):
        clipped = data.clip_segment(a, b, lo, hi)
        if clipped: line(f'INFRA {key} {i:03} piso {lv}', clipped, diameter, colors[key], levels[key, lv], **props)
    if key != 'electric' and (edge['a'] in {'AF-MONTANTE', 'AF-SAIDA', 'AF-DISTRIB', 'AF-PISO-1', 'EX-1', 'LP-1'}):
        arrow('Sentido '+edge['a'], a, b, colors[key], networks[key])
for node in graph['nodes']:
    if node['kind'] == 'junction': continue
    key = node['system']; xyz = node['xyz']; col = networks[key]; mat = colors[key]
    if node['kind'] in {'panel', 'distribution'}:
        obj = g.box('INFRA Ponto '+node['id'], xyz, (.09, .26, .34), mat.name, col.name, 0)
    else:
        obj = g.sphere('INFRA Ponto '+node['id'], xyz, (.06,)*3, mat.name, col.name)
    obj['network_node'] = node['id']; obj['system'] = key; obj['kind'] = node['kind']; obj['source'] = node['source']
    for lv, (lo, hi) in enumerate([(-.35, 2.65), (2.7, 5.4)]):
        if lo <= xyz[2] <= hi: levels[key, lv].objects.link(obj)

lights = collection('INFRA_Luzes')
for name, pos, power in [('Principal', (-4, -8, 15), 2200), ('Fundos', (9, 12, 15), 1800)]:
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = power; ld.size = 8
    obj = bpy.data.objects.new(name, ld); lights.objects.link(obj); obj.location = pos
    obj.rotation_euler = (Vector((3.175, 4.4, 3.5))-obj.location).to_track_quat('-Z', 'Y').to_euler()
world = bpy.data.worlds.new('INFRA Fundo claro'); world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs['Color'].default_value = (.76, .8, .84, 1); bg.inputs['Strength'].default_value = .6
scenes = []; jobs = []


def scene(name, groups, target=(3.175, 4.4, 3.7), position=(17, -20, 23), ortho=18, wide=False):
    s = bpy.data.scenes.new(name); s.use_fake_user = True; s.world = world
    for col in [*groups, lights]: s.collection.children.link(col)
    camera_data = bpy.data.cameras.new(name); camera = bpy.data.objects.new(name, camera_data)
    s.collection.objects.link(camera); s.camera = camera; camera.location = position
    camera.rotation_euler = (Vector(target)-camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera_data.type = 'ORTHO'; camera_data.ortho_scale = ortho; camera_data.clip_end = 200
    s.render.engine = 'CYCLES'; s.cycles.samples = 48; s.cycles.use_denoising = True; s.cycles.transparent_max_bounces = 64
    s.render.resolution_x = 2400 if wide else 1600; s.render.resolution_y = 1500
    s.render.image_settings.file_format = 'PNG'; s.render.filepath = str(ROOT/'renders/infraestrutura'/(name+'.png'))
    s.view_settings.view_transform = 'AgX'; s.view_settings.look = 'AgX - Medium High Contrast'
    s['scope'] = 'Casa sem ático. Caixa original. Traçados 3D interpretativos; não é projeto executivo ou levantamento.'
    scenes.append(s); jobs.append(dict(scene=name, file=Path(s.render.filepath).relative_to(ROOT).as_posix()))
    return s


allkeys = list(data.COLORS)
hydraulic = [k for k in allkeys if k != 'electric']
full_arch = [ground, upper, forro0, forro1]
scene('INFRA_04_CONJUNTO_FORRO_CAIXA', [*full_arch, coverage, tankcol, *networks.values()])
scene('INFRA_05_CAIXA_ENTRADA_SAIDAS', [upper, forro1, coverage, tankcol, *[networks[k] for k in hydraulic]],
      target=(4.75, 3.75, 5.6), position=(12, -5, 12), ortho=8)
scene('INFRA_06_TERREO', [ground, forro0, *[levels[k, 0] for k in allkeys]], target=(3.175, 4.4, 1.3), ortho=15)
scene('INFRA_07_SUPERIOR', [upper, forro1, *[levels[k, 1] for k in allkeys]], target=(3.175, 3, 3.9), ortho=13)
for suffix, keys in [('01_COMPARACAO_GERAL', allkeys), ('02_COMPARACAO_ELETRICA', ['electric']), ('03_COMPARACAO_HIDRAULICA', hydraulic)]:
    panels = []
    for label, offset, groups in [
        ('TERREO', -5.2, [ground, forro0, *[levels[k, 0] for k in keys]]),
        ('DOIS_PAVIMENTOS', 5.2, [*full_arch, coverage, tankcol, *[networks[k] for k in keys]])]:
        panel = collection('INFRA_'+suffix+'_'+label)
        for col in groups:
            for old in list(col.objects):
                obj = old.copy(); obj.parent = None
                assert old.parent is None
                obj.matrix_world = Matrix.Translation((offset, 0, 0))@old.matrix_basis
                obj.name = suffix+' '+label+' '+old.name; panel.objects.link(obj)
        text('SOMENTE TÉRREO' if label == 'TERREO' else 'DOIS PAVIMENTOS / FORRO / CAIXA ORIGINAL',
             (3.175+offset, -2.1, .05), panel, .30)
        panels.append(panel)
    legend = collection('INFRA_Legenda_'+suffix)
    for i, key in enumerate(keys):
        text(data.LABELS[key], (-5.1+i*4.1, -3.2, .05), legend, .18, colors[key])
    text('ESTUDO 3D / PERCURSOS EMBUTIDOS NÃO LEVANTADOS / SEM ÁTICO', (3.175, -3.9, .05), legend, .20)
    scene('INFRA_'+suffix, [*panels, legend], position=(3.175, -29, 36), ortho=26, wide=True)

default = bpy.data.scenes['INFRA_01_COMPARACAO_GERAL']; bpy.context.window.scene = default
default.frame_set(default.frame_current); bpy.context.view_layer.update()
for s in list(bpy.data.scenes):
    if s not in scenes: bpy.data.scenes.remove(s)
# Estrutura independente e leve: não carregar móveis/texturas históricos sem uso.
for col in list(bpy.data.collections):
    if not col.name.startswith('INFRA_'): bpy.data.collections.remove(col)
for group in [bpy.data.materials, bpy.data.images, bpy.data.meshes, bpy.data.curves]:
    for item in group: item.use_fake_user = False
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
            area.spaces.active.shading.type = 'MATERIAL'
assert all(wall_counts)
assert len(scenes) == 7
assert not any(o.name.startswith(('ATC', 'V05')) for s in scenes for o in s.objects)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(DEST), compress=True)
assert hashlib.sha256(source.read_bytes()).hexdigest() == source_sha
record = dict(blend=DEST.relative_to(ROOT).as_posix(), source=source.relative_to(ROOT).as_posix(),
              source_sha256=source_sha, tank_original_xyz=list(data.TANK),
              tank_capacity_liters=1000, wall_objects_by_level=wall_counts,
              graph=graph, jobs=jobs, default_scene=default.name, attic_included=False,
              images_rendered=False, notes=[
                  'Arquitetura atual sem construção do ático; caixa na posição documental original.',
                  'Paredes laterais completas, lajes e forros translúcidos para ler as redes.',
                  'Rede 3D interpretativa existente; novas ligações esquemáticas identificadas.',
                  'Água quente com coluna compartilhada e distribuição comum, sem trechos coincidentes.',
                  'HID04 indica distribuição sob a laje; Z=5,15 m é altura de apresentação, não cota documental.',
                  'Limpeza/extravasor terminam em conexão externa pendente; não ligados ao esgoto.',
                  'Sem cálculo de pressão, carga, circuitos, queda de tensão ou interferências.'])
(REPORT/'modelo.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
print('INFRAESTRUTURA_BLENDER_OK', DEST, '7 cenas, caixa original e sem ático', flush=True)
