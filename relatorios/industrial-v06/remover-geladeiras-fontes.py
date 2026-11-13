"""Manutenção explícita autorizada dos arquivos industriais existentes."""
import hashlib
import json
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import residence07_industrial as model
from industrial_bar_policy import remove_bar_fridges, bar_fridges


def sha(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()


rows = []
files = ['projeto/industrial-v01/casa-industrial.blend', 'projeto/fontes/casa-base-detalhada.blend',
         'projeto/industrial-v03/casa-fotografica.blend', 'projeto/industrial-v05/casa-industrial-residencia07-atual.blend']
for relative in files:
    path = ROOT / relative; before_hash = sha(path); bpy.ops.wm.open_mainfile(filepath=str(path))
    kitchens = [obj for obj in bpy.data.objects if obj.type == 'EMPTY' and 'geladeira cozinha' in obj.name.casefold()]
    kitchen_members = {o.name: model.geometry_fingerprint(o) for root in kitchens for o in [root, *root.children_recursive]}
    protected = model.protected() if '/industrial-v05/' in relative else None
    removed = remove_bar_fridges()
    assert removed and kitchens, (relative, removed, kitchens)
    assert all(model.geometry_fingerprint(bpy.data.objects[n]) == fingerprint for n, fingerprint in kitchen_members.items())
    if protected is not None: assert protected == model.protected()
    temporary = path.with_name(path.stem + '.sem-geladeira-bar.blend')
    bpy.ops.wm.save_as_mainfile(filepath=str(temporary), compress=True); temporary.replace(path)
    bpy.ops.wm.open_mainfile(filepath=str(path)); assert not bar_fridges()
    assert all(model.geometry_fingerprint(bpy.data.objects[n]) == fingerprint for n, fingerprint in kitchen_members.items())
    rows.append({'file': relative, 'before_sha256': before_hash, 'after_sha256': sha(path), 'removed': removed,
                 'kitchen_members_unchanged': kitchen_members, 'bar_fridge_absent_after_reopen': True,
                 'architecture_protected_unchanged': protected is not None})
    (ROOT / 'relatorios/industrial-v06/remocao-geladeiras-fontes.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    print('INDUSTRIAL_BAR_FRIDGE_REMOVED', relative, len(removed), flush=True)
