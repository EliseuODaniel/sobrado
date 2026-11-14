"""Manutenção autorizada das cópias industriais arquivadas e suas prévias."""
import datetime as dt
import json
from pathlib import Path
import sys
import time

import bpy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from industrial_photoreal_data import sha
from industrial_bar_policy import bar_fridges, remove_bar_fridges
from residence07_industrial import geometry_fingerprint

REPORT = ROOT / 'relatorios/industrial-v06'
plan = json.loads((REPORT / 'rascunhos-industriais-inventario.json').read_text())
receipt = REPORT / 'rascunhos-industriais-sem-geladeira.json'
rows = json.loads(receipt.read_text()) if receipt.exists() else []
done = {r['file']: r for r in rows}


def save():
    receipt.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')


for item in plan:
    path = ROOT / item['file']
    previous = done.get(item['file'])
    if previous:
        assert sha(path) == previous['after_sha256'], path
    else:
        assert sha(path) == item['before_sha256'], path
    bpy.ops.wm.open_mainfile(filepath=str(path))
    version = path.parts[-3]
    config_path = ROOT / ('historico/estudos/industrial-v02/config/estilo-industrial-v02.json' if version == 'industrial-v02' else 'config/estilo-' + version + '.json')
    configuration = json.loads(config_path.read_text()) if item['images'] else {}
    configured_scenes = {j['file']: j['scene'] for j in configuration.get('jobs', [])}
    # Resolver todos os destinos antes de alterar o arquivo fonte.
    scenes = {}
    for image in item['images']:
        name = Path(image['file']).name
        candidates = [s for s in bpy.data.scenes if s.name == configured_scenes.get(name)]
        assert len(candidates) == 1, (name, [s.name for s in candidates])
        scenes[image['file']] = candidates[0].name
    if previous is None:
        families = {o for root in bar_fridges() for o in [root, *root.children_recursive]}
        before = {o.name: geometry_fingerprint(o) for o in bpy.data.objects if o not in families}
        kitchens = [o.name for o in bpy.data.objects if o.type == 'EMPTY' and 'geladeira cozinha' in o.name.casefold()]
        assert kitchens, path
        removed = remove_bar_fridges()
        assert removed, path
        assert before == {o.name: geometry_fingerprint(o) for o in bpy.data.objects}
        scene_count = len(bpy.data.scenes)
        collection_count = len(bpy.data.collections)
        for scene in bpy.data.scenes: scene.use_fake_user = True
        for collection in bpy.data.collections: collection.use_fake_user = True
        bpy.context.window.scene = next(iter(bpy.data.scenes))
        temporary = path.with_name(path.stem + '.sem-geladeira-bar.blend')
        assert not temporary.exists(), temporary
        bpy.ops.wm.save_as_mainfile(filepath=str(temporary), compress=True)
        bpy.ops.wm.open_mainfile(filepath=str(temporary))
        assert not bar_fridges() and all(n in bpy.data.objects for n in kitchens)
        assert before == {o.name: geometry_fingerprint(o) for o in bpy.data.objects}
        assert len(bpy.data.scenes) == scene_count and len(bpy.data.collections) == collection_count
        temporary.replace(path)
        previous = {'file': item['file'], 'before_sha256': item['before_sha256'], 'after_sha256': sha(path),
                    'removed': removed, 'non_bar_geometry_unchanged': True, 'kitchen_roots_preserved': kitchens,
                    'verified_after_reopen': True, 'images': [], 'timestamp_utc': dt.datetime.now(dt.timezone.utc).isoformat()}
        rows.append(previous); save()
    assert not bar_fridges()
    completed = {a['file']: a for a in previous['images']}
    for image in item['images']:
        dest = ROOT / image['file']
        if image['file'] in completed:
            assert sha(dest) == completed[image['file']]['sha256']; continue
        assert sha(dest) == image['before_sha256']
        scene = bpy.data.scenes[scenes[image['file']]]; bpy.context.window.scene = scene
        scene.render.resolution_x, scene.render.resolution_y = image['resolution']
        scene.render.resolution_percentage = 100
        scene.render.threads_mode = 'FIXED'; scene.render.threads = 6
        scene.render.filepath = str(dest)
        scene.cycles.device = 'CPU'
        scene.cycles.samples = {'industrial-v01': 16, 'industrial-v02': 24, 'industrial-v03': 64}[path.parts[-3]]
        started = time.monotonic(); bpy.ops.render.render(write_still=True, scene=scene.name)
        rendered = bpy.data.images.load(str(dest), check_existing=False)
        assert list(rendered.size) == image['resolution']; bpy.data.images.remove(rendered)
        assert sha(path) == previous['after_sha256']
        previous['images'].append({'file': image['file'], 'before_sha256': image['before_sha256'], 'sha256': sha(dest),
                                   'scene': scene.name, 'resolution': image['resolution'], 'samples': scene.cycles.samples,
                                   'seconds': round(time.monotonic() - started, 2), 'bar_fridge_absent': True})
        save(); print('ARCHIVE_DRAFT_UPDATED', image['file'], flush=True)
    print('ARCHIVE_DRAFT_MODEL_VERIFIED', item['file'], flush=True)
print('ARCHIVE_DRAFTS_COMPLETE', len(rows), sum(len(r['images']) for r in rows), flush=True)
