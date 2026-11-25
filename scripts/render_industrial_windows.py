"""Fila com staging temporário no Windows para render OptiX e recibos locais."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import tempfile

import industrial_photoreal_data as data
from render_industrial_photoreal_queue import memory

ROOT, CFG = data.ROOT, data.CFG
REPORT = ROOT / CFG['report_directory']
if os.name == 'nt':
    BLENDER = Path(os.environ['ProgramFiles']) / 'Blender Foundation/Blender 5.2/blender.exe'
    STAGE = Path(tempfile.gettempdir()) / 'CasaInteriores/industrial-v06'
else:
    BLENDER = Path('/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe')
    STAGE = Path('/mnt/c/Users/edann/AppData/Local/Temp/CasaInteriores/industrial-v06')


def windows(path):
    if os.name == 'nt':
        return str(path.resolve())
    return subprocess.check_output(['wslpath', '-w', str(path)], text=True).strip()


def prepare(model):
    files = {model['blend'], 'config/estilo-industrial-v06.json', 'relatorios/industrial/modelo.json',
             'scripts/industrial_photoreal_data.py', 'scripts/industrial_photoreal_render_native.py', *model['generators']}
    for relative in files:
        source, dest = ROOT / relative, STAGE / relative
        if not dest.exists() or data.sha(source) != data.sha(dest):
            dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(source, dest)
        assert data.sha(source) == data.sha(dest)
    (REPORT / 'staging-windows.json').write_text(json.dumps({'root': str(STAGE), 'files_verified': sorted(files),
        'blend_sha256': model['blend_sha256'], 'note': 'Cópias locais temporárias; os resultados são conferidos e copiados de volta ao projeto.'}, ensure_ascii=False, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--only'); parser.add_argument('--preview', action='store_true')
    parser.add_argument('--resume', action='store_true'); parser.add_argument('--stop-after', type=int)
    args = parser.parse_args(); assert BLENDER.is_file()
    model = json.loads((REPORT / 'modelo.json').read_text()); prepare(model)
    target = REPORT / ('previas.json' if args.preview else 'renders.json')
    rows = json.loads(target.read_text()) if target.exists() else []
    merged = {r['id']: r for r in rows if r['blend_sha256'] == model['blend_sha256']}
    selected = set(args.only.split(',')) if args.only else {j['id'] for j in model['jobs']}
    assert selected <= {j['id'] for j in model['jobs']}
    gpu_file = REPORT / 'gpu-render.json'; metrics = json.loads(gpu_file.read_text()) if gpu_file.exists() else []
    count = 0
    for job in sorted(model['jobs'], key=lambda item: not item.get('pilot', False)):
        if job['id'] not in selected: continue
        previous = merged.get(job['id'])
        if args.resume and previous and previous.get('backend') == 'OPTIX' and (ROOT / previous['file']).is_file() and data.sha(ROOT / previous['file']) == previous['sha256']: continue
        cmd = [str(BLENDER), '--background', windows(STAGE / model['blend']), '--python-exit-code', '1',
               '--python', windows(STAGE / 'scripts/industrial_photoreal_render_native.py'), '--', '--only', job['id']]
        if args.preview: cmd.append('--preview')
        folder = REPORT / 'logs'; folder.mkdir(exist_ok=True)
        log = folder / (job['id'] + ('-preview' if args.preview else '') + '-optix.log')
        start = time.monotonic(); samples = []; baseline = memory()
        print('OPTIX_START', job['id'], flush=True)
        with log.open('w') as stream:
            process = subprocess.Popen(cmd, cwd=str(STAGE), stdout=stream, stderr=subprocess.STDOUT)
            while True:
                try: code = process.wait(timeout=4); break
                except subprocess.TimeoutExpired:
                    value = memory()
                    if value is not None: samples.append(value)
                    if time.monotonic() - start > 1200:
                        process.terminate()
                        try: process.wait(timeout=10)
                        except subprocess.TimeoutExpired: process.kill(); process.wait()
                        raise TimeoutError(job['id'])
        if code:
            print(log.read_text(errors='replace')[-3500:]); raise SystemExit(code)
        row = json.loads((STAGE / CFG['report_directory'] / (job['id'] + '-native.json')).read_text())
        assert row['blend_sha256'] == model['blend_sha256'] and row['backend'] == 'OPTIX'
        source, dest = STAGE / row['file'], ROOT / row['file']; dest.parent.mkdir(parents=True, exist_ok=True)
        assert data.sha(source) == row['sha256']; shutil.copy2(source, dest); assert data.sha(dest) == row['sha256']
        merged[row['id']] = row; target.write_text(json.dumps(list(merged.values()), ensure_ascii=False, indent=2) + '\n')
        metrics.append({'id': row['id'], 'blend_sha256': model['blend_sha256'], 'backend': 'OPTIX', 'preview': args.preview,
                        'seconds_process': round(time.monotonic() - start, 2), 'baseline_gpu_MiB': baseline,
                        'peak_global_gpu_MiB': max(samples) if samples else None, 'samples_of_gpu_memory': len(samples),
                        'note': 'Memória global da GPU; inclui Windows e outros processos. Amostrada a cada ~4 segundos.',
                        'exit_code': code, 'log': str(log.relative_to(ROOT))})
        gpu_file.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + '\n')
        print('OPTIX_DONE', row['id'], row['seconds'], metrics[-1]['peak_global_gpu_MiB'], flush=True)
        count += 1
        if args.stop_after and count >= args.stop_after: break


if __name__ == '__main__': main()
