"""Recorte diagnóstico com densidade de pixels 4K; não é uma imagem final."""
import json
from pathlib import Path
import sys
import time

import bpy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from industrial_photoreal_data import sha

model = json.loads((ROOT / 'relatorios/industrial-v06/modelo.json').read_text())
assert sha(bpy.data.filepath) == model['blend_sha256']
scene = bpy.data.scenes['PHOTO6_sala-integrada-dia']; bpy.context.window.scene = scene
prefs = bpy.context.preferences.addons['cycles'].preferences; prefs.compute_device_type = 'CUDA'; prefs.get_devices()
for device in prefs.devices: device.use = device.type == 'CUDA'
scene.cycles.device = 'GPU'; scene.cycles.samples = 128; scene.cycles.adaptive_threshold = .012
scene.render.resolution_x = 3840; scene.render.resolution_y = 2880; scene.render.resolution_percentage = 100
scene.render.use_border = True; scene.render.use_crop_to_border = True
scene.render.border_min_x = 0; scene.render.border_max_x = .35
scene.render.border_min_y = .02; scene.render.border_max_y = .56
out = ROOT / 'relatorios/industrial-v06/diagnosticos'; out.mkdir(exist_ok=True)
scene.render.filepath = str(out / 'couro-linho-densidade-4k.png')
start = time.monotonic(); bpy.ops.render.render(write_still=True, scene=scene.name)
(out / 'recibo.json').write_text(json.dumps({'source_blend_sha256': model['blend_sha256'], 'reference_frame': [3840, 2880],
    'normalized_border': [0, .35, .02, .56], 'samples': 128, 'seconds': time.monotonic() - start,
    'scope': 'Recorte de diagnóstico na densidade do quadro 4K; não representa a imagem final de 512 amostras.'}, ensure_ascii=False, indent=2) + '\n')
