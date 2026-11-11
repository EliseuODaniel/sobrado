"""Conciliar modelo, proporções, renders e histórico da revisão atual."""
import ast
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
from PIL import Image

root=Path(__file__).resolve().parents[1];reports=root/'relatorios/atual'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(name):return json.loads((reports/name).read_text())
cfg=json.loads((root/'config/planta-casa.json').read_text());assert cfg['revision_number']==9
validation=read('validacao.json');audit=read('auditoria-depois.json');upper=read('auditoria-superior.json');renders=read('renders-finais.json');comparison=read('comparacao.json');start=read('inicio.json');proportions=read('proporcoes.json')
blend=root/'projeto/casa-reconstruida.blend';fingerprint=sha(blend)
assert fingerprint==validation['sha256']==audit['sha256']==renders['sha256']==comparison['blend_sha256']
assert all(v['passed'] for v in validation['checks'].values()) and audit['all_passed'] and upper['all_passed']
assert validation['checks']['escada_e_superior_coerentes']['detail']==upper and validation['photo_geometry_audit']==audit
assert [len(validation['checks']),len(audit['checks']),len(upper['checks'])]==[17,40,16]
names={'fachada-frontal','fachada-obliqua','acesso-lavabo','sala-fundos','sala-frente','escada-acesso','cozinha','cozinha-reversa','bar','lavanderia','lavabo','escada-superior','suite','quarto-frente','quarto-fundos','terreo-3d','planta-terreo','porta-lavabo','superior-3d','planta-superior','estudos-superior','volumetria','lavabo-sob-escada'}
assert not renders['preview'] and renders['saved_file_unchanged'] and len(renders['outputs'])==23
assert set(renders['outputs'])=={'renders/atual/'+name+'.png' for name in names}
comparisons={'comparacao-planta','antes-depois','comparacao-superior','comparacao-escada','comparacao-fotos','comparacao-fachada','comparacao-quartos','sala-frente-planta','acesso-lavabo-planta','pavimentos-alinhados'}
assert len(comparison['outputs'])==10 and set(comparison['outputs'])=={'renders/atual/'+name+'.png' for name in comparisons}
for field in ['user_layout_source','upper_layout_source']:assert sha(root/cfg[field]['path'])==cfg[field]['sha256']
assert cfg['upper_layout_source']==start['source'] and proportions['source']==start['source']
assert proportions['improved_relative_to_sketch'] and proportions['after']['max_edge_difference_fraction']<.025
assert read('moveis-antes.json')['sha256']==start['previous_blend_sha256']
assert upper['checks']['camas_cabem_nos_ambientes_reproporcionados']['detail']['dimensions_preserved']
archive_counts={}
for name in ['ate-revisao05','revisao06','revisao07','revisao08']:
    manifest=json.loads((root/'historico'/name/'ARQUIVAMENTO.json').read_text())
    for record in manifest['records']:assert sha(root/record['destination'])==record['sha256'],record['destination']
    archive_counts[name]=len(manifest['records'])
legacy=json.loads((root/'historico/ate-revisao05/ARQUIVAMENTO.json').read_text());body=(root/'scripts/blender_primitives.py').read_text()
assert {n.name:hashlib.sha256(ast.get_source_segment(body,n).encode()).hexdigest() for n in ast.parse(body).body if isinstance(n,ast.FunctionDef)}==legacy['shared_helpers_unchanged_sha256']
for record in start.get('drafts',[]):assert sha(root/record['destination'])==record['sha256']
inv=json.loads((root/'relatorios/referencias-originais/inventario.json').read_text());assert all(sha(root/'referencias-originais'/name)==meta['sha256'] for name,meta in inv['inputs'].items())
assert [p.name for p in (root/'projeto').glob('*.blend')]==['casa-reconstruida.blend']
images=list(dict.fromkeys(root/name for name in renders['outputs']+comparison['outputs']));assert set((root/'renders/atual').glob('*.png'))==set(images)
for p in images:
    with Image.open(p) as im:im.verify()
subprocess.run(['git','diff','--check'],cwd=root,check=True)
stamp=dt.datetime.now(dt.timezone.utc).isoformat();unknowns=start['unknowns']+['Banheiros ainda são proposta, não localização levantada','Compatibilidade estrutural, cargas e dimensionamento construtivo não estudados','Projeção retangular não equivale à área exclusiva da análise registral secundária']
review={'timestamp_utc':stamp,'revision':9,'status':'estudo_proporcional_dos_dois_pavimentos_validado','scope':'Coerência geométrica e proporcional com o novo croqui, mantendo móveis e relações entre escada, lavabo, garagem, cozinha e superior','blend':{'path':str(blend.relative_to(root)),'sha256':fingerprint},'source':start['source'],'checks':{'integrity':17,'ground_geometry':40,'upper_geometry':16},'renders':23,'comparisons':10,'visual_review':['23 prévias em contato, incluindo todos os interiores, plantas e cortes','Nova proporção do superior comparada ao croqui','Térreo e superior registrados na mesma escala e origem','Quarto da frente sem porta obstruindo a câmera','Escada encostada, lavabo e fachada após deslocamento'],'archives_verified':archive_counts,'original_photos_preserved':True,'unknowns':unknowns,'external_publication':False}
(reports/'revisao.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
previous=json.loads((root/cfg['previous_delivery']['config']).read_text());old_rooms={r['id']:r for r in previous['rooms']};rows=[]
for room in cfg['rooms']:
    if room['level']!=1:continue
    x0,x1,y0,y1=room['bounds'];old=old_rooms[room['id']]['bounds'];w=x1-x0-.15;depth=y1-y0-.15;old_depth=old[3]-old[2]-.15
    rows.append(f"| {room['name']} | ≈ {w:.2f} × {depth:.2f} m | {old_depth:.2f} → {depth:.2f} m |")
d=cfg['estimated_dimensions_m'];s=cfg['layout']['stairs'];before=proportions['before']['max_edge_difference_fraction']*100;after=proportions['after']['max_edge_difference_fraction']*100
text=f'''# Revisão 09 — proporções dos dois pavimentos

UTC: {stamp}

O novo recorte do usuário foi interpretado pelas linhas das paredes: banheiros e quarto dos fundos mais profundos; quartos da frente mais curtos. Móveis, camas e louças preservam dimensões aproximadas próprias, sem reproduzir as distorções dos pixels. A escada, o lavabo e a divisão da garagem foram deslocados 0,89 m para a frente, e a cozinha começa 0,90 m antes. O limite posterior do superior foi ajustado de y=6,95 para y=6,75 m. Todos esses valores pertencem à escala estimada do estudo.

| Obrigação | Evidência | Estado e limite |
| --- | --- | --- |
| Proporções mais próximas do novo croqui | `proporcoes.json`, linhas manuais preservadas e comparação visual | VERIFIED como aproximação relativa ao desenho |
| Escada alinhada nos dois pisos e com lavabo/garagem | Vértices dos degraus, paredes e vãos, auditados no Blender | VERIFIED geometricamente |
| 7 degraus iniciais, curva e 4 finais, lances colados | Contagem e limites laterais dos meshes | VERIFIED na representação; curva ainda estimada |
| Camas cabem sem serem deformadas | Bounding boxes reais versus limites dos quartos e dimensões da revisão 08 | VERIFIED nas amostras auditadas |
| Portas e circulação do hall | Ray casts aos três quartos e aos dois WCs | VERIFIED nos percursos amostrados |
| Arquivo editável e imagens sincronizados | SHA-256 único, 23 renders e dez comparações | VERIFIED |
| Projeção dos pisos na mesma escala | Registro das duas câmeras ortográficas em `pavimentos-alinhados.png` | VERIFIED para revisão visual geométrica |
| Fontes e versões anteriores preservadas | Hashes de fotos, croqui e quatro históricos | VERIFIED |
| Medidas reais, escada executável e estrutura | Sem levantamento e sem cálculo estrutural | UNKNOWN |

## Dimensões de estudo

| Ambiente superior | Dimensões internas aproximadas | Profundidade anterior → atual |
| --- | --- | --- |
'''+'\n'.join(rows)+f'''

As dimensões descontam uma espessura de parede do retângulo nominal. A largura externa continua estimada em {d['width']:.2f} m. A projeção retangular superior é de {d['width']*(d['upper_back_y']-d['upper_front_y']):.2f} m² incluindo varanda e vãos. Isso não comprova nem substitui os 51,03 m² exclusivos citados na análise secundária da matrícula.

Os limites lidos manualmente no recorte foram normalizados pelo contorno externo. A maior diferença de borda caiu aproximadamente de {before:.1f}% para {after:.1f}% desse contorno. Esse indicador mostra aproximação ao croqui; não mede o imóvel ou avalia o programa arquitetônico. Os banheiros ficaram longos e estreitos (aproximadamente 1,25 × 3,70 m), conforme a proporção proposta, e precisam ser conferidos no local.

## Efeito no térreo

A nova posição mantém o lavabo sob a faixa do último lance, com porta horizontal e acesso pela lateral da sala. A continuação direita da garagem termina em y=1,90 m (antes 2,79 m); a cozinha começa em y=4,00 m (antes 4,90 m). Sala/jantar, mesa, geladeira e marcenaria foram reposicionados para esse encaixe. O tamanho das camas e dos móveis soltos foi preservado. A fachada, a janela pequena, a vegetação e a cobertura posterior acompanham os novos limites.

A escada tem sete degraus iniciais, seis de curva provisórios e quatro finais. A laje cobre o trecho baixo junto ao hall. O avanço reto continua comprimido em aproximadamente {s['first_run']/s['first_steps']:.2f} m por degrau na escala herdada; ele depende de uma medida real do comprimento do lance. O alinhamento e os testes não aprovam esse valor para execução.

## Arquivos e validação

Editável: `projeto/casa-reconstruida.blend`. Plantas e perspectivas: `renders/atual/`. `pavimentos-alinhados.png` coloca os dois pisos na mesma escala; `comparacao-superior.png` mantém o novo recorte ao lado do modelo; `antes-depois.png` mostra a mudança no térreo. Os 23 enquadramentos foram inspecionados em prévia antes da renderização final.

Passaram 17 verificações de integridade, 40 de relações do térreo e 16 de escada/superior. Comandos: `compare_proportions.py --landmarks referencias-ajustes/proporcoes-r09-linhas.json`, `validate_house.py`, `house_atlas.py`, `python3 -m py_compile scripts/*.py` e `git diff --check`. O novo modelo foi reaberto e renderizado em CPU no Blender 5.2.4 LTS. A revisão 08 foi preservada em `historico/revisao08/`, com {archive_counts['revisao08']} registros. Nada foi publicado no GitHub nesta etapa.

## Limites

'''+'\n'.join('- '+item for item in unknowns)+'\n'
(reports/'RELATORIO.md').write_text(text)
inputs=[root/'config/planta-casa.json',root/cfg['upper_layout_source']['path'],root/cfg['user_layout_source']['path'],root/'referencias-ajustes/proporcoes-r09-linhas.json',*sorted((root/'referencias-originais').glob('*.webp')),*[root/'historico'/name/'ARQUIVAMENTO.json' for name in archive_counts]]
outputs=[blend,root/'README.md',root/'historico/README.md',root/'relatorios/progresso.json',*sorted((root/'scripts').glob('*.py')),*images,*sorted(reports.glob('*.json')),*sorted(reports.glob('*.log')),reports/'RELATORIO.md'];outputs=list(dict.fromkeys(p for p in outputs if p.name!='manifesto.json'))
def metadata(paths):return {str(p.relative_to(root)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in paths}
(reports/'manifesto.json').write_text(json.dumps({'timestamp_utc':stamp,'revision':9,'scope':review['scope'],'inputs':metadata(inputs),'outputs':metadata(outputs),'unknowns':unknowns,'deletions':[],'external_publication':False},ensure_ascii=False,indent=2)+'\n')
print('CURRENT_DELIVERY_VERIFIED',17,40,16,23,10)
