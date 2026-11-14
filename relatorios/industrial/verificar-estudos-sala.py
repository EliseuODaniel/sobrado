import json
from pathlib import Path
import sys
import bpy
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from industrial_bar_policy import bar_fridges
from industrial_photoreal_data import sha
rows=[]
paths=sorted((ROOT/'historico/ate-revisao05/projeto').rglob('*industrial*.blend'))
paths += [ROOT/'projeto/fontes/mobiliario-industrial.blend']
for path in paths:
    before=sha(path); bpy.ops.wm.open_mainfile(filepath=str(path))
    roots=[o.name for o in bar_fridges()]
    rows.append({'file':str(path.relative_to(ROOT)), 'sha256':before,'bar_fridge_roots':roots,'native_unchanged':before==sha(path)})
    assert not roots and before==sha(path)
(ROOT/'relatorios/industrial-v06/estudos-sala-sem-geladeira.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print('LEGACY_LIVING_STUDIES_VERIFIED',len(rows),flush=True)
