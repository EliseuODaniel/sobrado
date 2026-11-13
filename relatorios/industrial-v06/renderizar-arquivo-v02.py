"""Atualiza somente as seis imagens existentes do estudo arquivado v02."""
import json
from pathlib import Path
import sys
import time

import bpy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from industrial_photoreal_data import sha
from industrial_bar_policy import bar_fridges

assert not bar_fridges()
archive = ROOT / 'historico/estudos/industrial-v02'
cfg = json.loads((archive / 'config/estilo-industrial-v02.json').read_text())
scene_map = {j['file']: j['scene'] for j in cfg['jobs']}
prefs = bpy.context.preferences.addons['cycles'].preferences; prefs.compute_device_type = 'CUDA'; prefs.get_devices()
for device in prefs.devices: device.use = device.type == 'CUDA'
rows = []
for path in sorted((archive / 'renders/industrial-v02').rglob('*.png')):
    if path.name not in scene_map: continue
    scene = bpy.data.scenes[scene_map[path.name]]; bpy.context.window.scene = scene
    preview = 'previas' in path.parts
    # O gerador histórico usa 40% em prévias; manter a proporção original 1920/1200.
    scene.render.resolution_x, scene.render.resolution_y = cfg['resolution']
    scene.render.resolution_percentage = 40 if preview else 100
    width, height = [value * scene.render.resolution_percentage // 100 for value in cfg['resolution']]
    scene.cycles.device = 'GPU'; scene.cycles.samples = 24 if preview else cfg['samples']
    scene.render.filepath = str(path)
    start = time.monotonic(); bpy.ops.render.render(write_still=True, scene=scene.name)
    image = bpy.data.images.load(str(path), check_existing=False)
    assert tuple(image.size) == (width, height)
    bpy.data.images.remove(image)
    rows.append({'file': str(path.relative_to(ROOT)), 'sha256': sha(path), 'source': 'projeto/fontes/casa-base-detalhada.blend',
                 'source_sha256': sha(ROOT / 'projeto/fontes/casa-base-detalhada.blend'), 'scene': scene.name,
                 'resolution': [width, height], 'seconds': round(time.monotonic() - start, 2), 'bar_fridge_absent': True})
    (ROOT / 'relatorios/industrial-v06/arquivo-v02-sem-geladeira.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    print('ARCHIVE_BAR_UPDATED', str(path.relative_to(ROOT)), flush=True)
