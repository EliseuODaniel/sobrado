"""Acabamento fotográfico sobre industrial v05; construção e render verificáveis."""
import argparse
import datetime as dt
import json
import math
from pathlib import Path
import sys
import time

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blender_primitives as g
import residence07_industrial as base
import industrial_photoreal_data as data
import industrial_photoreal_materials as materials
import industrial_photoreal_details as details
import industrial_photoreal_furniture as furniture
import industrial_bar_policy

ROOT, CFG = data.ROOT, data.CFG
REPORT = ROOT / CFG['report_directory']


def stamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def world(lighting):
    w = bpy.data.worlds.new('PHOTO6 Mundo ' + lighting); w.use_nodes = True
    nodes, links = w.node_tree.nodes, w.node_tree.links
    nodes.clear(); output = nodes.new('ShaderNodeOutputWorld'); bg = nodes.new('ShaderNodeBackground')
    tex = nodes.new('ShaderNodeTexEnvironment'); tex.image = materials.image('garden_nook', 'hdri')
    uv = nodes.new('ShaderNodeTexCoord'); mapping = nodes.new('ShaderNodeMapping'); mapping.inputs['Rotation'].default_value.z = 1.15
    links.new(uv.outputs['Generated'], mapping.inputs['Vector']); links.new(mapping.outputs[0], tex.inputs['Vector'])
    bg.inputs['Strength'].default_value = CFG[lighting + '_world_strength']
    links.new(tex.outputs[0], bg.inputs['Color']); links.new(bg.outputs[0], output.inputs['Surface'])
    w['context_status'] = 'Entorno ilustrativo CC0, não levantamento da vizinhança'
    return w


def lights(lighting):
    col = bpy.data.collections.new('PHOTO6_Luz_' + lighting); g.C[col.name] = col; g.C['Iluminacao'] = col

    def area(name, pos, target, power, size, color=(1, .72, .47), kind='AREA'):
        if kind == 'SUN':
            light_data = bpy.data.lights.new('PHOTO6 ' + lighting + ' ' + name, 'SUN')
            light_data.energy = power; light_data.color = color
            obj = bpy.data.objects.new(light_data.name, light_data); col.objects.link(obj)
            obj.location = pos; obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()
        else:
            obj = g.light('PHOTO6 ' + lighting + ' ' + name, pos, power, color, kind, target, size)
        if kind == 'AREA':
            obj.data.shape = 'DISK'
            obj.visible_camera = False; obj.visible_glossy = False; obj.visible_transmission = False
        obj['lighting_role'] = name
        return obj

    # Fontes artificiais junto às luminárias modeladas, comuns às duas condições.
    for name, pos, target, watts, size in [
        ('pendente jantar A', (1.6, 4.05, 2.10), (1.6, 4.05, .75), 30, .20),
        ('pendente jantar B', (1.6, 4.95, 2.10), (1.6, 4.95, .75), 30, .20),
        ('pendente bar A', (.65, 9.3, 2.10), (.65, 9.3, .9), 35, .18),
        ('pendente bar B', (1.95, 9.3, 2.10), (1.95, 9.3, .9), 35, .18),
        ('LED louceiro', (1.70, 10.03, 1.90), (1.70, 10.17, 1.25), 18, .8),
        ('LED cozinha', (5.96, 5.88, 1.57), (5.95, 5.88, .9), 16, .9),
        ('LED estante escritorio', (5.68, 5.5, 4.46), (5.95, 5.5, 3.8), 16, .8),
        ('LED estante escritorio baixa', (5.68, 5.5, 3.87), (5.95, 5.5, 3.4), 10, .8),
        ('mesa escritorio', (4.2, 5.6, 5.17), (3.9, 5.6, 3.45), 40, 1.0),
        ('TV esquerda', (3.14, .88, 1.45), (3.28, .88, 1.45), 5, .65),
        ('TV direita', (3.14, 2.12, 1.45), (3.28, 2.12, 1.45), 5, .65),
        ('plafon cozinha', (4.80, 5.75, 2.48), (4.80, 5.75, .80), 55, .8),
        ('plafon lavanderia', (4.80, 8.90, 2.68), (4.80, 8.90, .60), 45, .65),
        ('plafon hall terreo', (4.45, 3.60, 2.48), (5.0, 3.10, .60), 30, .5),
        ('plafon hall superior', (4.45, 3.55, 5.18), (4.45, 3.55, 3.0), 35, .5),
        ('plafon quarto frente', (4.80, 1.40, 5.18), (4.80, 1.40, 2.9), 55, .8),
        ('arandela lavabo', (4.80, 2.99, 1.65), (4.80, 2.40, .8), 18, .35),
    ]:
        area(name, pos, target, watts, size)
    for y in [1.16, 2.12]:
        area('arandela sofa', (.43, y, 1.78), (.43, y, .65), 12, .08)
    for x, y in [(1.05, 3.2), (2.60, 3.2), (4.80, 5.50), (1.00, 6.1)]:
        obj = area('downlight', (x, y, 2.515), (x, y, 0), 15, .05, kind='SPOT')
        obj.data.spot_size = math.radians(65); obj.data.spot_blend = .65
    for z, x, y in [(5.17, 1.5, 1.0), (5.17, 4.8, 5.6), (5.17, 1.6, 3.2)]:
        area('ambiente superior', (x, y, z), (x, y, z - 2), 35, 1.0, (1, .82, .65))
    if lighting == 'day':
        sun = area('sol', (4, -5, 12), (2, 7, 0), 1.6, 1, (1, .92, .79), kind='SUN')
        sun.data.angle = math.radians(4)
        area('janela frontal', (1.5, -.13, 1.75), (1.6, 3.8, 1.1), 100, 1.6, (.76, .86, 1))
        area('claraboia posterior', (1.6, 9.0, 3.0), (1.5, 8.6, 0), 80, 1.8, (.81, .90, 1))
        area('rebate sala', (1.7, 2.8, 2.50), (1.6, 3.0, .5), 20, 2, (1, .90, .75))
        area('janela escritorio', (4.75, 7.28, 4.3), (4.4, 5.2, 3.6), 140, 1.25, (.80, .88, 1))
    else:
        area('lua difusa frontal', (1.5, -.2, 1.8), (1.5, 3, 1), 3, 1.6, (.35, .52, 1))
        area('rebate sala', (1.7, 2.8, 2.50), (1.6, 3.0, .5), 8, 1.8, (1, .78, .55))
    return col


def setup_scene(job, collections, light_col, world_):
    source = bpy.data.scenes[job['source_scene']]
    scene = source.copy(); scene.name = job['scene']; scene.use_fake_user = True; scene.world = world_
    if 'R07_Contexto' in scene.collection.children:
        scene.collection.children.unlink(bpy.data.collections['R07_Contexto'])
        scene.collection.children.link(collections['context_proxy'])
    cam = source.camera.copy(); cam.data = source.camera.data.copy(); cam.name = job['scene'] + '_Camera'
    scene.collection.objects.link(cam); scene.camera = cam
    cam.location = job['pos']; cam.rotation_euler = (Vector(job['target']) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    if job.get('top'): cam.rotation_euler = (0, 0, 0)
    if 'ortho' in job: cam.data.type = 'ORTHO'; cam.data.ortho_scale = job['ortho']
    else: cam.data.type = 'PERSP'; cam.data.lens = job['lens']
    cam.data.clip_start = .03; cam.data.clip_end = 300
    cam.data.dof.use_dof = False
    mode = job['mode']
    upper = mode in {'plan1', 'iso1', 'office'} or (mode == 'photo' and job['pos'][2] > 2.7)
    chosen = [collections['upper'] if upper else collections['ground'], light_col]
    # Vasos apoiados no terreno não pertencem ao recorte isolado dos pavimentos.
    if not mode.startswith(('plan', 'iso')):
        chosen.append(collections['exterior'])
    if mode == 'exterior': chosen.append(collections['upper'])
    if mode == 'office': chosen.append(collections['office'])
    for collection in dict.fromkeys(chosen):
        scene.collection.children.link(collection)
    scene.render.engine = 'CYCLES'; scene.cycles.samples = CFG['samples']
    scene.cycles.use_adaptive_sampling = True; scene.cycles.adaptive_threshold = CFG['adaptive_threshold']
    scene.cycles.use_denoising = True; scene.cycles.use_light_tree = True
    scene.cycles.max_bounces = 12; scene.cycles.diffuse_bounces = 5; scene.cycles.glossy_bounces = 8
    scene.cycles.transmission_bounces = 12; scene.cycles.transparent_max_bounces = 12
    scene.cycles.sample_clamp_indirect = 8
    scene.render.resolution_x, scene.render.resolution_y = CFG['resolution']; scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'; scene.render.image_settings.color_mode = 'RGB'; scene.render.image_settings.color_depth = '16'
    scene.render.filepath = str(ROOT / job['file'])
    scene.view_settings.view_transform = 'AgX'; scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = CFG[job['lighting'] + '_exposure']
    if mode.startswith(('plan', 'iso')): scene.view_settings.exposure = -.4
    scene['photoreal_config_sha256'] = data.sha(data.CONFIG); scene['photoreal_view'] = job['id']
    scene['photoreal_lighting'] = job['lighting']; scene['photoreal_source'] = CFG['base_blend']
    return scene


def build():
    jobs = data.validate(); dest = ROOT / CFG['output_blend']
    if dest.exists():
        receipt = json.loads((REPORT / 'modelo.json').read_text())
        assert data.sha(dest) == receipt['blend_sha256'], 'Modelo editado externamente; preservar edição.'
    assert Path(bpy.data.filepath).resolve() == ROOT / CFG['base_blend']
    source_hash = data.sha(ROOT / CFG['base_blend']); before = base.protected()
    industrial_bar_policy.remove_bar_fridges()
    bpy.context.view_layer.update()
    g.C.update({c.name: c for c in bpy.data.collections}); g.M.update({m.name: m for m in bpy.data.materials})
    materials.build_materials(); changes = materials.apply_materials()
    collections, detail_receipt = details.build(before)
    detail_receipt.update(furniture.build(collections, before))
    for obj in list(bpy.data.objects):
        if obj.type == 'LIGHT':
            assert obj.name not in before
            bpy.data.objects.remove(obj, do_unlink=True)
    worlds = {key: world(key) for key in ['day', 'night']}
    lighting = {key: lights(key) for key in ['day', 'night']}
    for job in jobs: setup_scene(job, collections, lighting[job['lighting']], worlds[job['lighting']])
    for scene in list(bpy.data.scenes):
        if scene.name not in {j['scene'] for j in jobs}: bpy.data.scenes.remove(scene)
    bpy.context.window.scene = bpy.data.scenes['PHOTO6_sala-integrada-dia']; bpy.context.view_layer.update()
    assert before == base.protected(), 'Arquitetura modificada durante acabamento.'
    bpy.ops.file.pack_all(); dest.parent.mkdir(parents=True, exist_ok=True)
    temporary = dest.with_name(dest.stem + '.building.blend')
    bpy.ops.wm.save_as_mainfile(filepath=str(temporary), compress=True)
    temporary.replace(dest)
    assert data.sha(ROOT / CFG['base_blend']) == source_hash
    receipt = {'timestamp_utc': stamp(), 'version': CFG['version'], 'blend': CFG['output_blend'], 'blend_sha256': data.sha(dest),
               'source_blend': CFG['base_blend'], 'source_sha256': source_hash, 'config_sha256': data.sha(data.CONFIG),
               'protected_geometry': before, 'geometry_differences': [], 'jobs': jobs,
               'materials_changed': changes, 'metric_uv_objects': sorted(materials.UV_UPDATED), 'details': detail_receipt,
               'asset_manifest_sha256': data.sha(ROOT / CFG['asset_manifest']),
               'authored_screens': [{'file': str(p.relative_to(ROOT)), 'sha256': data.sha(p)} for p in sorted((ROOT / 'assets/fotorrealismo-industrial/telas').iterdir())],
               'generators': {str(p.relative_to(ROOT)): data.sha(p) for p in [Path(__file__), ROOT / 'scripts/industrial_photoreal_materials.py', ROOT / 'scripts/industrial_photoreal_details.py', ROOT / 'scripts/industrial_photoreal_furniture.py', ROOT / 'scripts/industrial_photoreal_data.py', ROOT / 'scripts/industrial_bar_policy.py']},
               'references': [{'file': str(p.relative_to(ROOT)), 'sha256': data.sha(p)} for p in sorted((ROOT / CFG['references']).iterdir()) if p.suffix.lower() in {'.png', '.jpg'}],
               'renderer': 'Cycles; Unreal comparison not executed', 'notes': CFG['notes']}
    (REPORT / 'modelo.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print('PHOTO6_BUILD_OK', len(jobs), 'scenes', len(before), 'protected', len(changes), 'materials updated', flush=True)


def render(preview=False, only=None):
    receipt = json.loads((REPORT / 'modelo.json').read_text())
    assert data.sha(bpy.data.filepath) == receipt['blend_sha256']
    assert data.sha(data.CONFIG) == receipt['config_sha256']
    assert all(data.sha(ROOT / p) == h for p, h in receipt['generators'].items())
    selected = set(only.split(',')) if only else {j['id'] for j in receipt['jobs']}
    assert selected <= {j['id'] for j in receipt['jobs']}
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'CUDA'; prefs.get_devices()
    assert any(d.type == 'CUDA' for d in prefs.devices)
    for device in prefs.devices: device.use = device.type == 'CUDA'
    target = REPORT / ('previas.json' if preview else 'renders.json')
    records = json.loads(target.read_text()) if target.exists() else []
    merged = {r['id']: r for r in records if r['blend_sha256'] == receipt['blend_sha256']}
    for job in receipt['jobs']:
        if job['id'] not in selected: continue
        scene = bpy.data.scenes[job['scene']]; bpy.context.window.scene = scene; scene.cycles.device = 'GPU'
        scene.render.resolution_percentage = CFG['preview_percentage'] if preview else 100
        scene.cycles.samples = CFG['preview_samples'] if preview else CFG['samples']
        scene.cycles.adaptive_threshold = .035 if preview else CFG['adaptive_threshold']
        dest = REPORT / 'previas' / (job['id'] + '.png') if preview else ROOT / job['file']
        dest.parent.mkdir(parents=True, exist_ok=True); scene.render.filepath = str(dest)
        start = time.monotonic(); bpy.ops.render.render(write_still=True, scene=scene.name)
        row = {'id': job['id'], 'file': str(dest.relative_to(ROOT)), 'sha256': data.sha(dest), 'preview': preview,
               'blend_sha256': receipt['blend_sha256'], 'backend': 'CUDA', 'samples': scene.cycles.samples,
               'adaptive_threshold': scene.cycles.adaptive_threshold,
               'resolution': [scene.render.resolution_x * scene.render.resolution_percentage // 100, scene.render.resolution_y * scene.render.resolution_percentage // 100],
               'seconds': round(time.monotonic() - start, 2), 'lighting': job['lighting'], 'timestamp_utc': stamp()}
        merged[job['id']] = row
        temporary = target.with_suffix('.tmp'); temporary.write_text(json.dumps(list(merged.values()), ensure_ascii=False, indent=2) + '\n'); temporary.replace(target)
        print('PHOTO6_RENDER_OK', job['id'], row['seconds'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--render-only', action='store_true')
    parser.add_argument('--preview', action='store_true'); parser.add_argument('--only')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    if args.render_only: render(args.preview, args.only)
    else: build()
