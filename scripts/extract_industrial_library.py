"""Extrai componentes reutilizáveis, sem cenas ou arquitetura da revisão antiga."""
import hashlib
import json
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'projeto/industrial-v04/casa-industrial-refinada.blend'
DEST = ROOT / 'arquivos/versoes-anteriores-2026-11-14/projeto/fontes/mobiliario-industrial.blend'
REPORT = ROOT / 'relatorios/industrial'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    assert Path(bpy.data.filepath).resolve() == SOURCE
    assert not DEST.exists()
    col = bpy.data.collections['DESIGN_Sala_Objetos']
    names = sorted(o.name for o in col.all_objects)
    required = ['DESIGN Sofá contemporâneo', 'DESIGN Mesa de centro']
    required += ['DESIGN Cadeira jantar ' + str(i) for i in range(1, 5)]
    required += ['PHOTO V04 Almofadas linho', 'PHOTO V04 Planta canto',
                 'PHOTO V04 Arranjo botânico (1.72, 2.0, 0.418)',
                 'PHOTO V04 Arranjo botânico (1.52, 5.8, 0.815)']
    assert set(required) <= set(names)
    assert not any(o.get('wall_id') or o.get('opening_id') for o in col.all_objects)
    source_hash = sha(SOURCE)
    bpy.data.libraries.write(str(DEST), {col, bpy.data.materials['DESIGN Pedra natural oxidada']},
                             path_remap='RELATIVE', fake_user=True, compress=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(str(DEST), link=False) as (src, dst):
        assert not src.scenes, 'A biblioteca não deve conter a casa antiga.'
        dst.collections = ['DESIGN_Sala_Objetos']
        dst.materials = ['DESIGN Pedra natural oxidada']
    assert sorted(o.name for o in dst.collections[0].all_objects) == names
    assert dst.materials[0]
    assert sha(SOURCE) == source_hash
    record = {'source_before_discard': str(SOURCE.relative_to(ROOT)), 'source_sha256': source_hash,
              'library': str(DEST.relative_to(ROOT)), 'sha256': sha(DEST), 'objects': names,
              'required_components': required, 'checks': {'no_scenes': True, 'exact_object_set_after_reopen': True,
              'required_components': True, 'no_wall_or_opening_metadata': True, 'source_unchanged': True}}
    REPORT.mkdir(exist_ok=True)
    (REPORT / 'biblioteca-extraida.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print('FURNITURE_LIBRARY_VERIFIED', len(names), DEST.stat().st_size, flush=True)


if __name__ == '__main__':
    main()
