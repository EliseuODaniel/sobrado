"""Fila retomável de renders CUDA; logs por imagem e consumo global da GPU."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

import industrial_photoreal_data as data

ROOT, CFG = data.ROOT, data.CFG
REPORT = ROOT / CFG['report_directory']


def memory():
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader,nounits'],
                                capture_output=True, text=True, timeout=8, check=True)
        return int(result.stdout.splitlines()[0])
    except (subprocess.SubprocessError, ValueError, IndexError):
        return None


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--only'); parser.add_argument('--preview', action='store_true')
    parser.add_argument('--resume', action='store_true'); parser.add_argument('--stop-after', type=int)
    args = parser.parse_args()
    model = json.loads((REPORT / 'modelo.json').read_text())
    records_file = REPORT / ('previas.json' if args.preview else 'renders.json')
    old = json.loads(records_file.read_text()) if records_file.exists() else []
    done = {r['id'] for r in old if r['blend_sha256'] == model['blend_sha256'] and
            (ROOT / r['file']).is_file() and data.sha(ROOT / r['file']) == r['sha256']}
    selected = set(args.only.split(',')) if args.only else {j['id'] for j in model['jobs']}
    assert selected <= {j['id'] for j in model['jobs']}
    metrics_file = REPORT / 'gpu-render.json'
    metrics = json.loads(metrics_file.read_text()) if metrics_file.exists() else []
    count = 0
    for job in model['jobs']:
        if job['id'] not in selected or (args.resume and job['id'] in done): continue
        cmd = [sys.executable, str(ROOT / 'scripts/run_blender.py'), '--wsl-gpu', '--background', str(ROOT / model['blend']),
               '--python', str(ROOT / 'scripts/industrial_photoreal.py'), '--', '--render-only', '--only', job['id']]
        if args.preview: cmd.append('--preview')
        logs = REPORT / 'logs'; logs.mkdir(exist_ok=True)
        suffix = '-preview' if args.preview else ''
        log_path = logs / (job['id'] + suffix + '.log')
        baseline = memory(); readings = []; start = time.monotonic()
        print('RENDER_START', job['id'], flush=True)
        with log_path.open('w') as stream:
            process = subprocess.Popen(cmd, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
            while True:
                try:
                    result = process.wait(timeout=4)
                    break
                except subprocess.TimeoutExpired:
                    value = memory()
                    if value is not None: readings.append(value)
                    if time.monotonic() - start > 1200:
                        process.terminate()
                        try: process.wait(timeout=10)
                        except subprocess.TimeoutExpired: process.kill(); process.wait()
                        raise TimeoutError(f'Render excedeu 20 minutos: {job["id"]}')
        metrics.append({'id': job['id'], 'blend_sha256': model['blend_sha256'], 'preview': args.preview,
                        'seconds_process': round(time.monotonic() - start, 2), 'baseline_gpu_MiB': baseline,
                        'peak_global_gpu_MiB': max(readings) if readings else None, 'samples_of_gpu_memory': len(readings),
                        'note': 'Memória global da GPU, inclui outros processos; amostragem a cada ~4s, não pico exato do Blender.',
                        'exit_code': result, 'log': str(log_path.relative_to(ROOT))})
        metrics_file.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + '\n')
        if result:
            print(log_path.read_text()[-3500:]); raise SystemExit(result)
        print('RENDER_DONE', job['id'], metrics[-1]['seconds_process'], metrics[-1]['peak_global_gpu_MiB'], flush=True)
        count += 1
        if args.stop_after and count >= args.stop_after: break


if __name__ == '__main__':
    main()
