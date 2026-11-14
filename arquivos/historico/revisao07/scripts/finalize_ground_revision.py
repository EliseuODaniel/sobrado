"""Conciliar revisão 07, fontes e históricos sem apagar versões anteriores."""
import ast
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
from PIL import Image

root = Path(__file__).resolve().parents[1]
reports = root / 'relatorios/atual'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(name):
    return json.loads((reports / name).read_text())

def check_archive(path):
    archive = json.loads(path.read_text())
    for record in archive['records']:
        assert sha(root / record['destination']) == record['sha256'], record['destination']
    return archive

cfg = json.loads((root / 'config/planta-casa.json').read_text())
assert cfg['revision_number'] == 7
validation, audit = read('validacao.json'), read('auditoria-depois.json')
renders, comparison, start = read('renders-finais.json'), read('comparacao.json'), read('inicio.json')
blend = root / 'projeto/casa-reconstruida.blend'
fingerprint = sha(blend)
assert fingerprint == validation['sha256'] == audit['sha256'] == renders['sha256'] == comparison['blend_sha256']
assert len(validation['checks']) == 16 and all(c['passed'] for c in validation['checks'].values())
assert len(audit['checks']) == 40 and audit['all_passed']
assert not renders['preview'] and len(renders['outputs']) == 19 and renders['saved_file_unchanged']
assert len(comparison['outputs']) == 6
expected_images = {
    'fachada-frontal', 'fachada-obliqua', 'acesso-lavabo', 'sala-fundos', 'sala-frente',
    'escada-acesso', 'cozinha', 'cozinha-reversa', 'bar', 'lavanderia', 'lavabo',
    'terreo-3d', 'planta-terreo', 'porta-lavabo', 'superior-pendente',
    'superior-envoltoria', 'estudos-superior', 'volumetria', 'lavabo-sob-escada',
}
assert set(renders['outputs']) == {'renders/atual/' + name + '.png' for name in expected_images}
assert set(comparison['outputs']) == {'renders/atual/' + name + '.png' for name in (
    'comparacao-planta', 'antes-depois', 'comparacao-fotos', 'comparacao-fachada',
    'sala-frente-planta', 'acesso-lavabo-planta')}
source = root / cfg['user_layout_source']['path']
assert sha(source) == cfg['user_layout_source']['sha256'] == start['source']['sha256']
history = root / cfg['previous_delivery']['root']
archive = check_archive(history / 'ARQUIVAMENTO.json')
legacy_path = root / 'historico/ate-revisao05/ARQUIVAMENTO.json'
legacy = check_archive(legacy_path)
assert all(op['status'] == 'complete' for op in legacy['operations'])
for record in start['additional_archives']:
    assert sha(root / record['destination']) == record['sha256']
body = (root / 'scripts/blender_primitives.py').read_text()
functions = {node.name: hashlib.sha256(ast.get_source_segment(body, node).encode()).hexdigest()
             for node in ast.parse(body).body if isinstance(node, ast.FunctionDef)}
assert functions == legacy['shared_helpers_unchanged_sha256']
inv = json.loads((root / 'relatorios/referencias-originais/inventario.json').read_text())
assert all(sha(root / 'referencias-originais' / name) == meta['sha256'] for name, meta in inv['inputs'].items())
assert all(room['bounds'] is None for room in cfg['rooms'] if room['level'] == 1)
assert [p.name for p in (root / 'projeto').glob('*.blend')] == ['casa-reconstruida.blend']
assert not any((root / 'renders').glob('revisao-*')) and not any((root / 'relatorios').glob('revisao-*'))
coherence = read('coerencia-anterior.json')
assert coherence['previous_output_receipts_checked'] == 45 and coherence['changed_outputs'] == []
images = list(dict.fromkeys(root / name for name in renders['outputs'] + comparison['outputs']))
for path in images:
    with Image.open(path) as im:
        im.verify()
subprocess.run(['git', 'diff', '--check'], cwd=root, check=True)
stamp = dt.datetime.now(dt.timezone.utc).isoformat()
unknowns = [
    'Medidas reais, profundidade dos degraus e inclinação da escada; implantação visual aproximada',
    'Lado da dobradiça e sentido definitivo da porta; folha mostrada fechada',
    'Planta interna do segundo pavimento, detalhes da área de serviço e telhado sem levantamento',
]
review = {
    'timestamp_utc': stamp, 'revision': 7,
    'status': 'acesso_corrigido_e_vistas_regeneradas',
    'scope': 'Coerência do térreo aproximado entre planta, modelo e perspectivas; porta horizontal sob a escada.',
    'blend': {'path': str(blend.relative_to(root)), 'sha256': fingerprint},
    'authoritative_source': cfg['user_layout_source'],
    'integrity_checks': len(validation['checks']), 'geometry_checks': len(audit['checks']),
    'renders': len(renders['outputs']),
    'visual_review': ['Sala e acesso ao lavabo com a escada presente',
                      'Posição das câmeras sobre a planta da porta',
                      'Planta anotada, corte da escada e perspectivas internas e externas'],
    'archive': {'path': str(history.relative_to(root)), 'records_verified': len(archive['records']),
                'older_records_verified': len(legacy['records']), 'shared_helpers_identical': len(functions), 'deletions': []},
    'unknowns': unknowns, 'original_photos_preserved': True,
    'upper_interior_started': False, 'external_publication': False,
}
(reports / 'revisao.json').write_text(json.dumps(review, ensure_ascii=False, indent=2) + '\n')
text = f'''# Térreo atual — revisão 07

UTC: {stamp}

O modelo aproximado foi corrigido para conectar a cozinha ao acesso da porta horizontal do lavabo. A antiga divisória atravessava essa passagem. O trecho foi encurtado, o retorno da cozinha foi alinhado à escada e a laje preenchida acima da faixa liberada. A porta continua na marca preta confirmada pelo usuário. O lavabo permanece sob o segundo lance e o patamar.

| Obrigação | Recibo observado | Estado e limite |
| --- | --- | --- |
| Porta na posição confirmada | Fonte anotada preservada; orientação e posição da folha verificadas | VERIFIED no modelo aproximado |
| Ligação da cozinha até a porta | Diagnóstico anterior atingia a divisória; ray cast atual atinge a folha | VERIFIED na linha amostrada; não certifica dimensões reais |
| Cobertura da passagem liberada | Ray cast vertical atinge a laje | VERIFIED no ponto amostrado |
| Perspectivas e planta usam a mesma arquitetura | Identidade dos objetos, transformações e visibilidade nas cenas FOTO verificadas | VERIFIED para o conjunto arquitetônico auditado |
| Vistas atualizadas | 19 cenas renderizadas do mesmo SHA-256 do Blender editável; seis comparações | VERIFIED |
| Hipótese de imagem antiga fora de sincronia | 45 arquivos da revisão 06 conferidos, sem divergências | REFUTED nesse conjunto; o defeito estava na geometria e no enquadramento |
| Preservação das versões anteriores | {len(archive['records'])} hashes da revisão 06 e {len(legacy['records'])} do histórico anterior conferidos | VERIFIED; nenhuma exclusão |
| Dimensões reais e fidelidade métrica às fotos | Levantamento não fornecido | UNKNOWN |

## Revisão visual

`sala-frente.png` usa um novo enquadramento para reduzir a obstrução da cadeira de jantar. A nova `acesso-lavabo.png` mostra porta e primeiro lance a partir da circulação da sala. As montagens `sala-frente-planta.png` e `acesso-lavabo-planta.png` relacionam a posição e direção dessas câmeras à planta: vermelho marca a câmera; laranja marca a porta.

A escada fica oculta somente na planta de leitura dos vãos (`porta-lavabo.png`) e nas vistas de corte indicadas. Está presente nas perspectivas internas. A fotografia `sala4.webp` continua sendo referência dos elementos e relações do ambiente; a câmera atual tem outra posição. Não se declara reprodução métrica das fotos.

`comparacao-planta.png` mantém a planta anotada ao lado da vista dos vãos. `antes-depois.png` compara as plantas 06 e 07. `comparacao-fotos.png` reúne oito referências internas e `comparacao-fachada.png`, duas externas. A anotação do usuário prevalece nas correções da porta, lavabo e passagem. Fachada e demais ambientes foram novamente renderizados da geometria compartilhada.

## Preservação e validação

Modelo ativo: `projeto/casa-reconstruida.blend`. Renders: `renders/atual/`. Fontes, configuração e scripts ficam nas pastas correspondentes da raiz. A revisão 06 completa está em `historico/revisao06/`; versões anteriores, em `historico/ate-revisao05/`. Prévias e enquadramentos preliminares estão em `historico/rascunhos/revisao07/`. As 31 imagens originais permanecem intactas. As {len(functions)} funções compartilhadas preservam seus hashes anteriores.

Passaram {len(validation['checks'])} verificações de integridade e {len(audit['checks'])} relações geométricas. Comandos: `validate_house.py`, `house_atlas.py`, `python3 -m py_compile scripts/*.py` e `git diff --check`. O manifesto liga configuração, scripts, Blender e imagens pelos hashes; os recibos dos comandos registram a execução sobre o arquivo de trabalho antes de sua promoção para o caminho ativo.

A checagem de cenas considera a laje superior intencionalmente oculta no corte da planta: identidade e geometria são compartilhadas, e a transformação mundial é comparada nas cenas em que o objeto está incluído. O primeiro teste desse corte foi ajustado, conforme `integridade-ajuste-corte.log`; a verificação final passou em `integridade-final.log`. O launcher também foi verificado para retornar erro quando um script Python falha (`launcher.json`).

## Limites

''' + '\n'.join('- ' + item for item in unknowns) + '''

A escada representa o croqui aproximado; os degraus não foram dimensionados ou certificados para execução. A distribuição do segundo pavimento continua pendente. Não houve commit, push ou publicação.
'''
(reports / 'RELATORIO.md').write_text(text)
inputs = [root / 'config/planta-casa.json', source, history / 'ARQUIVAMENTO.json', legacy_path,
          root / start['diagnostic_before'], *sorted((root / 'referencias-originais').glob('*.webp'))]
outputs = [blend, root / 'README.md', root / 'historico/README.md', root / 'relatorios/progresso.json',
           *sorted((root / 'scripts').glob('*.py')), *images,
           *sorted(reports.glob('*.json')), *sorted(reports.glob('*.log')), reports / 'RELATORIO.md']
outputs = list(dict.fromkeys(path for path in outputs if path.name != 'manifesto.json'))
def metadata(paths):
    return {str(path.relative_to(root)): {'sha256': sha(path), 'bytes': path.stat().st_size} for path in paths}
manifest = {'timestamp_utc': stamp, 'revision': 7, 'scope': review['scope'],
            'inputs': metadata(inputs), 'outputs': metadata(outputs),
            'archive_manifest': str((history / 'ARQUIVAMENTO.json').relative_to(root)),
            'unknowns': unknowns, 'deletions': [], 'external_publication': False}
(reports / 'manifesto.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print('CURRENT_DELIVERY_VERIFIED', len(validation['checks']), len(audit['checks']), len(renders['outputs']), len(archive['records']))
