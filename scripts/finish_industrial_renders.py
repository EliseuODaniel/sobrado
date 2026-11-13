"""Etapas sequenciais da GPU e fechamento verificável da entrega industrial."""
import datetime as dt
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'relatorios/industrial-v06'


def main():
    steps = [
        ('v06-previas-validacao', [sys.executable, 'scripts/render_industrial_windows.py', '--preview', '--only',
          'sala-integrada-dia,sala-integrada-noite,bar-dia,bar-noite,escritorio-dia,escritorio-noite', '--resume']),
        ('v06-finais-4k', [sys.executable, 'scripts/render_industrial_windows.py', '--resume']),
        ('v06-auditoria-final', [sys.executable, 'scripts/run_blender.py', '--background',
          'projeto/industrial-v06/casa-industrial-fotorrealista.blend', '--python', 'scripts/industrial_photoreal_audit.py', '--', '--require-renders']),
        ('v06-entrega', [str(ROOT / '.tools/planta-venv/bin/python'), 'scripts/industrial_photoreal_delivery.py']),
    ]
    history = []
    for name, command in steps:
        row = {'phase': name, 'started_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'status': 'running', 'command': command}
        history.append(row)
        (REPORT / 'pipeline.json').write_text(json.dumps(history, ensure_ascii=False, indent=2) + '\n')
        print('PIPELINE_START', name, flush=True)
        result = subprocess.run(command, cwd=ROOT)
        row.update(status='passed' if result.returncode == 0 else 'failed', exit_code=result.returncode,
                   completed_utc=dt.datetime.now(dt.timezone.utc).isoformat())
        (REPORT / 'pipeline.json').write_text(json.dumps(history, ensure_ascii=False, indent=2) + '\n')
        print('PIPELINE_END', name, result.returncode, flush=True)
        if result.returncode: raise SystemExit(result.returncode)


if __name__ == '__main__': main()
