"""Contrato da reconstrução fotográfica da casa atual."""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'config/atual-fiel-v02.json'
CFG = json.loads(CONFIG.read_text())
REPORT = ROOT / CFG['report_directory']

def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def jobs():
    original = json.loads((ROOT / 'relatorios/original/estudo-instalacoes-atico/atual-modelo.json').read_text())['jobs']
    # Enquadramentos próximos das referências, mantendo a câmera dentro dos ambientes.
    cameras = {
        'sala-fundos': ([2.65, .55, 1.48], [1.45, 5.50, 1.30], 21),
        'sala-frente': ([2.88, 5.58, 1.47], [1.50, 1.2, 1.30], 22),
        'cozinha': ([3.70, 4.62, 1.49], [5.19, 6.48, 1.37], 21),
        'cozinha-reversa': ([5.46, 6.12, 1.49], [3.58, 4.67, 1.32], 20),
        'bar': ([2.89, 6.92, 1.49], [1.62, 9.84, 1.42], 23),
        'lavanderia': ([3.73, 8.00, 1.48], [5.02, 10.05, 1.33], 21),
        'suite': ([2.93, .30, 4.20], [.70, 1.10, 4.00], 22),
        'quarto-frente': ([4.46, 1.65, 4.17], [5.56, .17, 3.98], 20),
        'quarto-fundos': ([5.00, 4.56, 4.17], [4.50, 6.30, 4.04], 19),
        'escada-superior': ([4.16, 3.61, 4.28], [5.58, 3.15, 2.25], 20),
    }
    result = []
    for item in original:
        j = dict(item, source_scene=item['scene'], scene='FIEL2_' + item['id'])
        if j['id'] in cameras:
            j['pos'], j['target'], j['lens'] = cameras[j['id']]
        result.append(j)
    for id_, title, source, photo, pos, target, lens in [
        ('sala-foto', 'Jantar e sala · enquadramento das fotos', 'sala-frente', 'sala5.webp', [2.70, 5.65, 1.48], [1.55, 1.60, 1.37], 23),
        ('suite-reversa', 'Suíte · roupeiro, TV e lareira', 'suite', 'quartosuite2.webp', [.75, .36, 4.17], [2.30, 2.30, 4.01], 22),
        ('quarto-azul-bancada', 'Quarto azul · bancada e papel geométrico', 'quarto-fundos', 'quartoazul1.webp', [4.68, 6.55, 4.14], [3.64, 5.10, 4.11], 22),
        ('quarto-branco-armario', 'Quarto branco · armários e corações', 'quarto-frente', 'quartobranco2.webp', [5.75, -.34, 4.14], [4.12, 1.05, 4.05], 21),
        ('banheiro-social', 'Banheiro · granito, louça e vidro', 'suite', 'banheiro2.webp', [3.18, 3.80, 4.18], [2.05, 4.80, 3.94], 16),
        ('banheiro-suite', 'Banheiro da suíte', 'suite', 'suite1.webp', [1.53, 3.80, 4.18], [.40, 4.80, 3.94], 16),
    ]:
        parent = next(j for j in result if j['id'] == source)
        result.append(dict(parent, id=id_, title='Atual · '+title, scene='FIEL2_'+id_, photo=photo,
                           pos=pos, target=target, lens=lens, file=CFG['render_directory']+'/02-ambientes/'+id_+'.png'))
    assert len(result) == 26 and len({j['id'] for j in result}) == 26
    return result
