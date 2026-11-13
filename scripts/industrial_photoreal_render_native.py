"""Render de cópia íntegra no Windows/OptiX; sem salvar o modelo."""
import argparse
import datetime as dt
import json
from pathlib import Path
import sys
import time

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import industrial_photoreal_data as data

ROOT, CFG = data.ROOT, data.CFG
REPORT = ROOT / CFG['report_directory']


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--only', required=True); parser.add_argument('--preview', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    model = json.loads((REPORT / 'modelo.json').read_text())
    assert data.sha(bpy.data.filepath) == model['blend_sha256']
    assert data.sha(data.CONFIG) == model['config_sha256']
    assert all(data.sha(ROOT / p) == h for p, h in model['generators'].items())
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'OPTIX'; prefs.get_devices()
    assert any(device.type == 'OPTIX' for device in prefs.devices), 'OptiX indisponível'
    for device in prefs.devices: device.use = device.type == 'OPTIX'
    job = next(j for j in model['jobs'] if j['id'] == args.only)
    scene = bpy.data.scenes[job['scene']]; bpy.context.window.scene = scene
    scene.cycles.device = 'GPU'; scene.cycles.samples = CFG['preview_samples'] if args.preview else CFG['samples']
    scene.cycles.adaptive_threshold = .035 if args.preview else CFG['adaptive_threshold']
    scene.render.resolution_percentage = CFG['preview_percentage'] if args.preview else 100
    dest = REPORT / 'previas' / (job['id'] + '.png') if args.preview else ROOT / job['file']
    dest.parent.mkdir(parents=True, exist_ok=True); scene.render.filepath = str(dest)
    start = time.monotonic(); bpy.ops.render.render(write_still=True, scene=scene.name)
    row = {'id': job['id'], 'file': dest.relative_to(ROOT).as_posix(), 'sha256': data.sha(dest),
           'blend_sha256': model['blend_sha256'], 'source_blend': model['blend'], 'backend': 'OPTIX',
           'platform': 'Windows native', 'blender_version': bpy.app.version_string,
           'blender_build_hash': bpy.app.build_hash.decode(), 'preview': args.preview,
           'samples': scene.cycles.samples, 'adaptive_threshold': scene.cycles.adaptive_threshold,
           'resolution': [scene.render.resolution_x * scene.render.resolution_percentage // 100, scene.render.resolution_y * scene.render.resolution_percentage // 100],
           'lighting': job['lighting'], 'seconds': round(time.monotonic() - start, 2),
           'timestamp_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'native_input_copy_verified': True}
    (REPORT / (job['id'] + '-native.json')).write_text(json.dumps(row, ensure_ascii=False, indent=2) + '\n')
    print('PHOTO6_OPTIX_RENDER_OK', job['id'], row['seconds'], flush=True)


if __name__ == '__main__': main()
