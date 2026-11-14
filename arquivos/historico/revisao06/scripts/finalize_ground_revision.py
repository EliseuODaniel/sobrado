"""Conciliar a entrega atual e verificar o arquivamento, sem apagar histórico."""
import ast
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
from PIL import Image

root=Path(__file__).resolve().parents[1];reports=root/'relatorios/atual';cfg=json.loads((root/'config/planta-casa.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):return json.loads((reports/name).read_text())

assert cfg['revision_number']==6
validation=read('validacao.json');audit=read('auditoria-depois.json');renders=read('renders-finais.json');comparison=read('comparacao.json');start=read('inicio.json')
blend=root/'projeto/casa-reconstruida.blend';fingerprint=sha(blend)
assert fingerprint==validation['sha256']==audit['sha256']==renders['sha256']==comparison['blend_sha256']
assert all(c['passed'] for c in validation['checks'].values()) and audit['all_passed']
assert len(audit['checks'])==38 and not renders['preview'] and len(renders['outputs'])==18
assert renders['saved_file_unchanged']
source=root/cfg['user_layout_source']['path'];assert sha(source)==cfg['user_layout_source']['sha256']==start['source']['sha256']
history=root/cfg['previous_delivery']['root'];archive=json.loads((history/'ARQUIVAMENTO.json').read_text())
for record in archive['records']:assert sha(root/record['destination'])==record['sha256'],record['destination']
assert all(op['status']=='complete' for op in archive['operations'])
for record in start['additional_archives']:assert sha(root/record['destination'])==record['sha256']
helper=root/'scripts/blender_primitives.py';body=helper.read_text()
for node in ast.parse(body).body:
    if isinstance(node,ast.FunctionDef):assert hashlib.sha256(ast.get_source_segment(body,node).encode()).hexdigest()==archive['shared_helpers_unchanged_sha256'][node.name]
inv=json.loads((root/'relatorios/referencias-originais/inventario.json').read_text())
assert all(sha(root/'referencias-originais'/name)==meta['sha256'] for name,meta in inv['inputs'].items())
assert all(room['bounds'] is None for room in cfg['rooms'] if room['level']==1)
assert [p.name for p in (root/'projeto').glob('*.blend')]==['casa-reconstruida.blend']
assert not any((root/'renders').glob('revisao-*')) and not any((root/'relatorios').glob('revisao-*'))
images=list(dict.fromkeys(root/name for name in renders['outputs']+comparison['outputs']))
for p in images:
    with Image.open(p) as im:im.verify()
subprocess.run(['git','diff','--check'],cwd=root,check=True)
stamp=dt.datetime.now(dt.timezone.utc).isoformat()
unknowns=['Medidas reais, profundidade dos degraus e inclinação da escada; implantação visual aproximada','Lado da dobradiça e sentido definitivo de abertura da porta; folha mostrada fechada','Planta interna do segundo pavimento e detalhes ainda não medidos da área de serviço e telhado']
review={'timestamp_utc':stamp,'revision':6,'status':'nova_planta_aplicada_e_anteriores_arquivados','scope':'Porta na marcação preta da planta confirmada, limite vermelho do lavabo e acesso pela área branca. Arquivamento recuperável dos anteriores.','blend':{'path':str(blend.relative_to(root)),'sha256':fingerprint},'authoritative_source':cfg['user_layout_source'],'user_confirmation':cfg['user_correction'],'integrity_checks':len(validation['checks']),'geometry_checks':len(audit['checks']),'renders':len(renders['outputs']),'visual_review':['Planta anotada × vista atual da porta com escada oculta','Planta completa, corte em 3D e oito fotos internas','Fachada e duas referências externas'],'archive':{'path':str(history.relative_to(root)),'records_verified':len(archive['records']),'moves_verified':len(archive['operations']),'shared_helpers_identical':len(archive['shared_helpers_unchanged_sha256']),'deletions':[]},'unknowns':unknowns,'original_photos_preserved':True,'upper_interior_started':False,'external_publication':False}
(reports/'revisao.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
text=f'''# Térreo atual — revisão 06

UTC: {stamp}

A nova planta anotada e a confirmação textual do usuário substituem a interpretação anterior da porta. A abertura fica na parede horizontal superior do lavabo, no traço preto. O antigo vão na lateral da sala foi fechado. O limite do lavabo segue o retângulo vermelho até a lateral direita da casa, sob o segundo lance e o patamar. O início do primeiro lance foi recuado para representar a área branca de acesso.

| Obrigação | Evidência | Estado e limite |
| --- | --- | --- |
| Porta na marcação preta | Planta recebida, confirmação do usuário e posição/orientação da folha no modelo | VERIFIED no modelo aproximado |
| Vão lateral anterior fechado | Ray cast na posição antiga | VERIFIED |
| Passagem até a porta | Ray casts com a escada presente e oculta | VERIFIED nos pontos amostrados; não é validação dimensional de circulação |
| Limite vermelho do lavabo | Configuração e planta atual com escada oculta | VERIFIED na implantação aproximada |
| Modelos, renders, scripts e documentação atuais | 18 cenas reabertas, 18 renders do mesmo arquivo, hashes e links conferidos | VERIFIED |
| Arquivos antigos arquivados | {len(archive['records'])} registros e {len(archive['operations'])} movimentos conferidos em `historico/ate-revisao05/ARQUIVAMENTO.json` | VERIFIED; nada apagado |
| Helpers compartilhados preservados | SHA-256 de {len(archive['shared_helpers_unchanged_sha256'])} funções extraídas do antigo gerador | VERIFIED; gerador decorativo arquivado |
| Dimensões reais e sentido da porta | Não informados pelo usuário | UNKNOWN |

## Comparações

A imagem original recebida está preservada em `{cfg['user_layout_source']['path']}`. `renders/atual/comparacao-planta.png` coloca essa imagem ao lado da vista da porta. Em `porta-lavabo.png`, a escada foi ocultada apenas para mostrar paredes, folha e louças; ela continua presente no modelo e na planta completa. Uma chamada gráfica marca a porta nas vistas de planta, sem representar um novo elemento construtivo.

A comparação anterior/atual é `antes-depois.png`. `comparacao-fotos.png` contém oito ângulos internos e `comparacao-fachada.png` contém dois externos. A nova planta confirmada prevalece onde corrige a interpretação anterior das fotografias. Não se declara equivalência métrica com as fotos.

## Arquivamento e arquivos ativos

A entrega ativa tem um único modelo em `projeto/casa-reconstruida.blend`, renders em `renders/atual/`, configuração em `config/planta-casa.json` e recibos em `relatorios/atual/`. As versões 02 a 05, renders rejeitados, testes e scripts legados de decoração foram retirados das pastas ativas e preservados em `historico/ate-revisao05/`.

O script antigo `build_scene.py` era também uma dependência de primitivas. Suas funções compartilhadas foram extraídas sem alteração para `blender_primitives.py` antes de arquivar o fluxo decorativo. As fotos originais, as referências do usuário e os prompts foram preservados.

## Validação e limites

Passaram {len(validation['checks'])} verificações de integridade e {len(audit['checks'])} relações geométricas. Comandos: `validate_house.py`, `house_atlas.py`, `python3 -m py_compile scripts/*.py` e `git diff --check`. O manifesto concilia o arquivo editável, a configuração, os renders e os relatórios; os hashes do histórico foram verificados separadamente.

'''+ '\n'.join('- '+item for item in unknowns)+'''

O recuo e os degraus da escada seguem a representação visual do desenho; profundidade e inclinação não foram levantadas ou certificadas. O lado da dobradiça não foi confirmado; não foi desenhado arco de abertura presumido. O segundo pavimento continua como envoltória e estudos separados. Não houve commit, push ou publicação.
'''
(reports/'RELATORIO.md').write_text(text)
inputs=[root/'config/planta-casa.json',source,history/'ARQUIVAMENTO.json',*sorted((root/'referencias-originais').glob('*.webp'))]
outputs=[blend,root/'README.md',*sorted((root/'scripts').glob('*.py')),*images,*sorted(reports.glob('*.json')),*sorted(reports.glob('*.log')),reports/'RELATORIO.md']
outputs=list(dict.fromkeys(p for p in outputs if p.name!='manifesto.json'))
manifest={'timestamp_utc':stamp,'revision':6,'scope':review['scope'],'inputs':{str(p.relative_to(root)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in inputs},'outputs':{str(p.relative_to(root)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in outputs},'archive_manifest':str((history/'ARQUIVAMENTO.json').relative_to(root)),'unknowns':unknowns,'deletions':[],'external_publication':False}
(reports/'manifesto.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('CURRENT_DELIVERY_VERIFIED',len(validation['checks']),len(audit['checks']),len(renders['outputs']),len(archive['records']))
