"""Dados e contrato de vistas da revisão industrial fotográfica."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'config/estilo-industrial-v06.json'
CFG = json.loads(CONFIG.read_text())


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def jobs():
    base = json.loads((ROOT / 'relatorios/industrial-v05/modelo.json').read_text())
    result = []
    for original in base['jobs']:
        result.append({**original, 'source_scene': original['scene'], 'scene': 'PHOTO6_' + original['id'],
                       'lighting': 'day', 'file': str(Path(CFG['render_directory']) / Path(original['file']).parent.name / (original['id'] + '.png'))})
    heroes = [
        ('sala-integrada', 'Sala integrada · couro, madeira e cimento', 'sala-fundos', [1.66, .40, 1.48], [1.65, 6.30, 1.31], 20),
        ('bar', 'Bar · pedra oxidada e marcenaria', 'bar', [2.86, 7.01, 1.46], [1.51, 9.97, 1.37], 24),
        ('escritorio', 'Escritório · madeira, telas e luz indireta', 'escritorio-alternativa', [5.89, 4.37, 4.18], [4.03, 5.71, 3.99], 22),
    ]
    by_id = {j['id']: j for j in result}
    for name, title, source_id, pos, target, lens in heroes:
        for lighting in ['day', 'night']:
            id_ = name + ('-dia' if lighting == 'day' else '-noite')
            result.append({**by_id[source_id], 'id': id_, 'title': title + (' · dia' if lighting == 'day' else ' · noite'),
                           'scene': 'PHOTO6_' + id_, 'pos': pos, 'target': target, 'lens': lens,
                           'lighting': lighting, 'pilot': True,
                           'file': str(Path(CFG['render_directory']) / '07-dia-noite' / (id_ + '.png'))})
    return result


def validate():
    views = jobs()
    assert len(views) == 31
    assert len({j['id'] for j in views}) == len(views)
    assert len({j['file'] for j in views}) == len(views)
    assert CFG['output_blend'] != CFG['base_blend']
    assert CFG['resolution'][0] / CFG['resolution'][1] == 4 / 3
    return views
