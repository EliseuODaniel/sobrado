"""Finaliza galeria e caderno quando todos os renders íntegros estiverem disponíveis."""
import json
from pathlib import Path
import subprocess
import time
import current_photoreal_data as data

m=json.loads((data.REPORT/'modelo.json').read_text());expected=m['blend_sha256'];ids={j['id'] for j in m['jobs']};start=time.monotonic()
while True:
    current=json.loads((data.REPORT/'modelo.json').read_text());assert current['blend_sha256']==expected,'Modelo mudou enquanto aguardava os renders.'
    file=data.REPORT/'renders.json'
    try:rows=json.loads(file.read_text()) if file.exists() else []
    except json.JSONDecodeError:rows=[]
    rows=[r for r in rows if r['blend_sha256']==expected and not r['preview']]
    if len(rows)==len(ids) and {r['id'] for r in rows}==ids:
        assert all(data.sha(data.ROOT/r['file'])==r['sha256'] for r in rows)
        break
    if time.monotonic()-start>18000:raise TimeoutError('Ainda faltam renders; nenhuma entrega parcial foi publicada pelo finalizador.')
    time.sleep(15)
python=data.ROOT/'.tools/planta-venv/bin/python'
for script in ['scripts/deliver_current_photoreal.py','scripts/validate_current_delivery.py']:
    subprocess.run([str(python),str(data.ROOT/script)],cwd=data.ROOT,check=True)
print('CURRENT2_FILES_FINALIZED; visual review and browser validation remain separate.',flush=True)
