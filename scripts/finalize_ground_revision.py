"""Conciliar modelo, proporções, renders e histórico da revisão atual."""
import ast
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
from PIL import Image

root=Path(__file__).resolve().parents[1];reports=root/'arquivos/versoes-anteriores-2026-11-14/relatorios/atual-anterior'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(name):return json.loads((reports/name).read_text())
cfg=json.loads((root/'config/planta-casa.json').read_text());assert cfg['revision_number']==10
validation=read('validacao.json');audit=read('auditoria-depois.json');upper=read('auditoria-superior.json');renders=read('renders-finais.json');comparison=read('comparacao.json');start=read('inicio.json');proportions=read('proporcoes.json');envelope=read('encaixe-pavimentos.json');old_envelope=read('encaixe-antes.json')
blend=root/'arquivos/versoes-anteriores-2026-11-14/projeto/casa-reconstruida.blend';fingerprint=sha(blend)
assert fingerprint==validation['sha256']==audit['sha256']==renders['sha256']==comparison['blend_sha256']
assert all(v['passed'] for v in validation['checks'].values()) and audit['all_passed'] and upper['all_passed']
assert validation['checks']['escada_e_superior_coerentes']['detail']==upper and validation['photo_geometry_audit']==audit
assert [len(validation['checks']),len(audit['checks']),len(upper['checks'])]==[18,40,16]
names={'fachada-frontal','fachada-obliqua','acesso-lavabo','sala-fundos','sala-frente','escada-acesso','cozinha','cozinha-reversa','bar','lavanderia','lavabo','escada-superior','suite','quarto-frente','quarto-fundos','terreo-3d','planta-terreo','porta-lavabo','superior-3d','planta-superior','estudos-superior','volumetria','lavabo-sob-escada'}
assert not renders['preview'] and renders['saved_file_unchanged'] and len(renders['outputs'])==23
assert set(renders['outputs'])=={'renders/atual/'+name+'.png' for name in names}
comparisons={'pavimentos-sobrepostos','comparacao-planta','antes-depois','comparacao-superior','comparacao-escada','comparacao-fotos','comparacao-fachada','comparacao-quartos','sala-frente-planta','acesso-lavabo-planta','pavimentos-alinhados'}
assert len(comparison['outputs'])==11 and set(comparison['outputs'])=={'renders/atual/'+name+'.png' for name in comparisons}
for field in ['user_layout_source','upper_layout_source']:assert sha(root/cfg[field]['path'])==cfg[field]['sha256']
assert cfg['upper_layout_source']==start['proportion_reference'] and proportions['source']==start['proportion_reference']
assert envelope['all_passed'] and len(envelope['checks'])==3
assert validation['checks']['contorno_externo_e_parede_posterior_alinhados']['detail']==envelope
assert not old_envelope['checks']['fundos_wcs_quarto_coplanares_com_cozinha']['passed']
assert old_envelope['blend_sha256']==start['previous_blend_sha256']
assert proportions['after']['max_edge_difference_fraction']<.035
assert read('moveis-antes.json')['sha256']==start['previous_blend_sha256']
assert upper['checks']['camas_cabem_nos_ambientes_reproporcionados']['detail']['dimensions_preserved']
archive_counts={}
for name in ['ate-revisao05','revisao06','revisao07','revisao08','revisao09']:
    manifest=json.loads((root/'arquivos/historico'/name/'ARQUIVAMENTO.json').read_text())
    for record in manifest['records']:assert sha(root/record['destination'])==record['sha256'],record['destination']
    archive_counts[name]=len(manifest['records'])
legacy=json.loads((root/'arquivos/historico/ate-revisao05/ARQUIVAMENTO.json').read_text());body=(root/'scripts/blender_primitives.py').read_text()
assert {n.name:hashlib.sha256(ast.get_source_segment(body,n).encode()).hexdigest() for n in ast.parse(body).body if isinstance(n,ast.FunctionDef)}==legacy['shared_helpers_unchanged_sha256']
for record in start.get('drafts',[]):assert sha(root/record['destination'])==record['sha256']
inv=json.loads((root/'arquivos/versoes-anteriores-2026-11-14/relatorios/referencias-originais/inventario.json').read_text());assert all(sha(root/'referencias-originais'/name)==meta['sha256'] for name,meta in inv['inputs'].items())
assert [p.name for p in (root/'projeto').glob('*.blend')]==['casa-reconstruida.blend']
images=list(dict.fromkeys(root/name for name in renders['outputs']+comparison['outputs']));assert set((root/'renders/atual').glob('*.png'))==set(images)
for p in images:
    with Image.open(p) as im:im.verify()
subprocess.run(['git','diff','--check'],cwd=root,check=True)
stamp=dt.datetime.now(dt.timezone.utc).isoformat();unknowns=start['unknowns']+['Banheiros ainda são proposta, não localização levantada','Compatibilidade estrutural, cargas e dimensionamento construtivo não estudados','Projeção retangular não equivale à área exclusiva da análise registral secundária']
review={'timestamp_utc':stamp,'revision':10,'status':'contorno_comum_e_fundos_alinhados_no_modelo','scope':start['scope'],'blend':{'path':str(blend.relative_to(root)),'sha256':fingerprint},'authorizing_instruction':start['user_instruction'],'proportion_reference':start['proportion_reference'],'checks':{'integrity':18,'ground_geometry':40,'upper_geometry':16,'envelope':3},'renders':23,'comparisons':11,'main_volume':cfg['main_volume'],'visual_review':['23 prévias de todos os ambientes, plantas, cortes e fachada','Fundos superiores no plano da cozinha','Pavimentos na mesma escala e sobreposição com contorno comum','Móveis sem deformação e circulação da escada preservada'],'archives_verified':archive_counts,'original_photos_preserved':True,'unknowns':unknowns,'external_publication':False}
(reports/'revisao.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
previous=json.loads((root/cfg['previous_delivery']['config']).read_text());old_rooms={r['id']:r for r in previous['rooms']};rows=[]
for room in cfg['rooms']:
    if room['level']!=1:continue
    x0,x1,y0,y1=room['bounds'];old=old_rooms[room['id']]['bounds'];w=x1-x0-.15;depth=y1-y0-.15;old_depth=old[3]-old[2]-.15
    rows.append(f"| {room['name']} | ≈ {w:.2f} × {depth:.2f} m | {old_depth:.2f} → {depth:.2f} m |")
d=cfg['estimated_dimensions_m'];s=cfg['layout']['stairs'];before=proportions['before']['max_edge_difference_fraction']*100;after=proportions['after']['max_edge_difference_fraction']*100
text=f'''# Revisão 10 — contorno comum dos pavimentos

UTC: {stamp}

Foi corrigido um desencontro real de 0,85 m no modelo anterior: o superior terminava em y=6,75 m e a cozinha em y=7,60 m. Agora o fundo dos dois WCs e do quarto superior é uma parede contínua no mesmo plano da cozinha. A laje dos dois pisos tem o mesmo contorno no corpo principal: x=0 a 5,60 m e y=−1,65 a 7,60 m, ou aproximadamente 5,60 × 9,25 m na escala estimada.

Esse contorno inclui a garagem sob o volume superior no térreo e a varanda no superior. O pátio frontal e a churrasqueira/lavanderia posteriores são anexos térreos, fora do corpo principal. O vão da escada é retirado da laje superior; igualdade de contorno não significa igualdade de área líquida ou área registral.

| Obrigação | Evidência | Estado e limite |
| --- | --- | --- |
| Contorno externo comum | Extensões dos vértices das lajes dos dois pisos, reabertas do Blender | VERIFIED no corpo principal |
| Fundos dos WCs/quarto no plano da cozinha | Faces externas nativas em y=7,675 m, nas duas alturas | VERIFIED; eixos coincidem em y=7,60 m |
| Ausência de faixas de laje faltantes | Comparação célula a célula da cobertura real, com exceção explícita do vão da escada | VERIFIED |
| Escada, lavabo, garagem e quarto frontal alinhados | Vértices e paredes reais, percursos do hall e acesso ao lavabo | VERIFIED nas amostras auditadas |
| Distribuição proporcional e camas preservadas | Limites internos redistribuídos e dimensões das camas comparadas à revisão anterior | VERIFIED no estudo |
| Geometria, renders e editável sincronizados | Mesmo SHA-256, 23 renders e 11 comparações | VERIFIED |
| Dimensões reais e solução estrutural | Sem levantamento ou cálculo de estrutura | UNKNOWN |

## Antes e depois

`encaixe-antes.json` registra os três testes novos aplicados à revisão 09. O contorno e as faces posteriores não coincidiam. `encaixe-pavimentos.json` registra os mesmos testes no arquivo novo, todos aprovados. Esses recibos avaliam vértices e faces reais do modelo, não apenas valores escritos na configuração ou o zoom das imagens.

`pavimentos-alinhados.png` apresenta as plantas na mesma escala e origem. `pavimentos-sobrepostos.png` combina os dois pisos e marca o contorno comum em branco. A linha dos fundos mostra o alinhamento da cozinha com os dois banheiros e o quarto do superior.

## Redistribuição interna

| Ambiente superior | Dimensões internas aproximadas | Profundidade anterior → atual |
| --- | --- | --- |
'''+ '\n'.join(rows)+f'''

A profundidade adicional foi distribuída entre os quartos e banheiros. A escada foi deslocada 0,30 m junto com o lavabo e a divisão da garagem, mantendo largura, contato entre os lances e degraus. A cozinha passa a começar em y=4,30 m; seu fundo permanece em y=7,60 m. A porta horizontal do lavabo e o acesso lateral acompanham esse encaixe.

As posições relativas do croqui foram preservadas. O critério explícito mais recente do usuário — fundos no plano da cozinha — controla o contorno. A comparação com o desenho manual continua sendo uma referência proporcional, sem escala levantada. Os banheiros permanecem compridos e estreitos, com aproximadamente 1,25 × 4,15 m, e requerem medição.

O corpo principal tem projeção retangular de {d['width']*(d['upper_back_y']-d['upper_front_y']):.2f} m² na hipótese atual. Isso não comprova os 51,03 m² de área exclusiva citados na análise secundária da matrícula: varanda, vãos, paredes e critérios de área não foram conciliados com o documento original.

## Validação e arquivos

Passaram 18 verificações de integridade, 40 de relações do térreo, 16 de escada/superior e os três testes específicos de contorno e coplanaridade. Comandos: `validate_house.py`, `house_atlas.py`, `compare_proportions.py --landmarks referencias-ajustes/proporcoes-r09-linhas.json`, `python3 -m py_compile scripts/*.py` e `git diff --check`.

O arquivo atual é `arquivos/versoes-anteriores-2026-11-14/projeto/casa-reconstruida.blend`. As 23 prévias foram inspecionadas antes dos renders finais em CPU no Blender 5.2.4 LTS. A revisão 09 está preservada em `arquivos/historico/revisao09/`, com {archive_counts['revisao09']} registros. Fotos originais e referências foram preservadas. Não houve commit, push ou publicação.

## Limites

O avanço do primeiro lance ainda está comprimido em cerca de {s['first_run']/s['first_steps']:.2f} m por degrau na escala herdada; exige uma medida real do comprimento do lance. A curva de seis degraus também permanece estimada. O alinhamento corrigido é geométrico e não aprova a escada para execução.

'''+ '\n'.join('- '+item for item in unknowns)+'\n'
(reports/'RELATORIO.md').write_text(text)
inputs=[root/'config/planta-casa.json',root/cfg['upper_layout_source']['path'],root/cfg['user_layout_source']['path'],root/'referencias-ajustes/proporcoes-r09-linhas.json',*sorted((root/'referencias-originais').glob('*.webp')),*[root/'arquivos/historico'/name/'ARQUIVAMENTO.json' for name in archive_counts]]
outputs=[blend,root/'README.md',root/'arquivos/historico/README.md',root/'arquivos/versoes-anteriores-2026-11-14/relatorios/progresso.json',*sorted((root/'scripts').glob('*.py')),*images,*sorted(reports.glob('*.json')),*sorted(reports.glob('*.log')),reports/'RELATORIO.md'];outputs=list(dict.fromkeys(p for p in outputs if p.name!='manifesto.json'))
def metadata(paths):return {str(p.relative_to(root)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in paths}
(reports/'manifesto.json').write_text(json.dumps({'timestamp_utc':stamp,'revision':10,'scope':review['scope'],'inputs':metadata(inputs),'outputs':metadata(outputs),'unknowns':unknowns,'deletions':[],'external_publication':False},ensure_ascii=False,indent=2)+'\n')
print('CURRENT_DELIVERY_VERIFIED',18,40,16,23,11,3)
