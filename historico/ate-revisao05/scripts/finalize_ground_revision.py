"""Conciliar evidências da conferência fotográfica do térreo e da fachada."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
from PIL import Image

root=Path(__file__).resolve().parents[1]
cfg=json.loads((root/'config/planta-casa.json').read_text());revision=cfg['revision_number']
folder=root/'relatorios'/f'revisao-{revision:02d}'
assert revision==5

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(name):return json.loads((folder/name).read_text())

validation=read('validacao.json');audit=read('auditoria-depois.json');before=read('auditoria-antes.json');renders=read('renders-finais.json');start=read('inicio.json')
blend=root/'projeto/casa-reconstruida.blend';fingerprint=sha(blend)
assert fingerprint==validation['sha256']==audit['sha256']==renders['sha256']
assert all(check['passed'] for check in validation['checks'].values()) and audit['all_passed']
assert len(audit['checks'])==33 and len(renders['outputs'])==len(cfg['cameras'])+7==17
assert not renders['preview'] and renders['saved_file_unchanged']
source=root/cfg['user_layout_source']['path'];assert sha(source)==start['source_sha256']==cfg['user_layout_source']['sha256']
backup=root/f'projeto/versoes/revisao-{revision:02d}-antes/projeto/casa-reconstruida.blend';assert sha(backup)==start['previous_blend_sha256']==before['sha256']
inv=json.loads((root/'relatorios/referencias-originais/inventario.json').read_text())
assert all(sha(root/'referencias-originais'/name)==meta['sha256'] for name,meta in inv['inputs'].items())
assert all(room['bounds'] is None for room in cfg['rooms'] if room['level']==1)
comparison=json.loads((root/'relatorios/planta-casa/comparacao.json').read_text());assert comparison['revision']==revision and comparison['blend_sha256']==fingerprint
images=list(dict.fromkeys(root/name for name in renders['outputs']+comparison['outputs']))
for path in images:
    with Image.open(path) as im:im.verify()
subprocess.run(['git','diff','--check'],cwd=root,check=True)
stamp=dt.datetime.now(dt.timezone.utc).isoformat()
unknowns=['Dimensões reais, espessuras, inclinação e folgas da escada','Ligação exata entre janela da cozinha, eventual pátio aberto e lavanderia; esclarecimento solicitado ao usuário, sem resposta registrada','Forma completa do telhado da unidade, aproximada pela tipologia vista nas vizinhas','Implantação dos cômodos do segundo pavimento, reservada para a próxima etapa']
limits=['Enquadramentos aproximados; nenhuma calibração métrica ou nota de similaridade','Três bancos do croqui mantidos apesar de as fotos mostrarem quatro','Retorno esquerdo da bancada da lavanderia encurtado para preservar o acesso lateral do croqui; profundidade real não demonstrada','Forro do lavabo usa envelope inclinado e ressaltos aproximados; não é uma reprodução estrutural medida','Vizinhas são contexto volumétrico aproximado apenas nas câmeras externas, sem interiores']
corrected=[name for name,result in audit['checks'].items() if result['passed'] and not before['checks'].get(name,{}).get('passed',False)]
review={'timestamp_utc':stamp,'revision':revision,'status':'terreo_e_fachada_revistos_por_evidencias_fotograficas','scope':start['scope'],'blend':{'path':str(blend.relative_to(root)),'sha256':fingerprint},'integrity_checks':len(validation['checks']),'geometry_checks':len(audit['checks']),'tested_failures_corrected':corrected,'render_count':len(renders['outputs']),'visual_review':['Oito ângulos do térreo e duas vistas externas comparados às fotos originais','Vista superior e corte em 3D do térreo','Corte do lavabo e volumetria exterior antes/depois'],'unknowns':unknowns,'known_limits':limits,'sources_preserved':True,'previous_revision_preserved':str(backup.relative_to(root)),'upper_interior_started':False,'external_publication':False}
(folder/'revisao.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
rows='\n'.join('| '+name+' | '+('PASS' if before['checks'].get(name,{}).get('passed') else 'FAIL')+' | PASS | '+', '.join(result['references'])+' |' for name,result in audit['checks'].items())
body=f'''# Revisão 05 — conferência fotográfica do térreo e da fachada

UTC: {stamp}

O térreo e a fachada foram confrontados com as referências originais. Foram removidas contradições específicas e preservadas as correções explícitas do usuário: entrada diagonal, garagem ampliada, lavabo sob o segundo lance e posição relativa da lavanderia. As divisões do segundo pavimento não foram iniciadas.

## Resultado por parte

| Parte | Evidência e ajuste | Estado da conclusão |
| --- | --- | --- |
| Fachada | `exterior1.webp` e `exterior2.webp`: garagem sob a laje superior, laterais contínuas, varanda recuada, rede, molduras e grades, janela posterior, revestimento claro e pavimento externo | VERIFIED para essas relações no modelo; proporções INFERRED |
| Garagem e lavabo | Parede externa vertical oculta a escada, mantendo janela pequena e lavabo sob o segundo lance | VERIFIED no modelo e nos ângulos de controle; folgas reais UNKNOWN |
| Sala e jantar | Painel com fundo cinza, rack amarelo, mesa escura, pendente inclinado e detalhes dos encostos | VERIFIED como ajustes visuais aproximados; marcenaria não medida |
| Cozinha | `cozinha1/2.webp`: bancada separada no vão do fogão, micro-ondas, aéreo lateral, puxadores, azulejos e lava-louças | VERIFIED para presença e relações; proporções INFERRED |
| Churrasqueira | `area2/4.webp`: revestimento em madeira e boca lateral substituem a coifa de alvenaria exposta | VERIFIED como correção da contradição visual; construção interna UNKNOWN |
| Lavanderia | `lavanderia1.webp`: retorno à esquerda, tanque, aéreos, puxadores e tampo livre sobre máquina superior | VERIFIED para relações; extensão do retorno e ligação ao pátio INFERRED/UNKNOWN |
| Integridade e preservação | Arquivo reaberto, hashes das 31 referências e do backup conferidos; {len(validation['checks'])} verificações de integridade e {len(audit['checks'])} relações geométricas | VERIFIED para o arquivo entregue |
| Segundo pavimento | Estudos separados e parâmetros de distribuição mantidos | VERIFIED: nenhuma distribuição nova; planta interna UNKNOWN |

## Comparação e testes

O mesmo arquivo salvo gerou 17 renders. Oito ângulos internos e dois externos foram comparados com as fotos; as montagens são `renders/planta-casa/comparacao-originais.png` e `fachada-comparacao.png`. A comparação de volumetria externa antes/depois está em `fachada-antes-depois.png`.

A versão anterior preservada foi submetida à mesma auditoria. {len(corrected)} falhas específicas deixaram de ocorrer. As verificações abrangem vãos, posições, oclusão da escada na fachada, fogão livre da bancada e máquina superior livre do tampo. Elas não constituem prova de identidade métrica da planta. A ausência de uma câmera de controle na versão anterior também é registrada como falha de evidência; a contagem não corresponde a uma nota de semelhança ou a nove erros construtivos comprovados.

| Relação testada | Revisão anterior | Revisão 05 | Fontes |
| --- | --- | --- | --- |
{rows}

## Limites conhecidos

'''+ '\n'.join('- '+item for item in limits)+'''

## Desconhecidos e evidência que falta

'''+ '\n'.join('- '+item for item in unknowns)+'''

A matrícula original continua não conferida; a análise do ChatGPT recebida não foi promovida a dado oficial. Para concluir dimensões reais, são necessárias medidas ou planta cotada. A pergunta sobre eventual pátio entre cozinha e lavanderia ficou pendente; foi preservada a organização geral do croqui em vez de acrescentar uma divisória sem evidência.

Validação executada: `validate_house.py`, `audit_photo_geometry.py --baseline`, `house_atlas.py`, `python3 -m py_compile scripts/*.py` e `git diff --check`. Os recibos são `validacao.json`, `auditoria-antes.json`, `auditoria-depois.json`, `renders-finais.json` e os logs do Blender. Não houve commit, push ou publicação.
'''
(folder/'RELATORIO.md').write_text(body)
for name in ['revisao.json','RELATORIO.md']:(root/'relatorios/planta-casa'/name).write_bytes((folder/name).read_bytes())
inputs=[root/'config/planta-casa.json',source,*sorted((root/'referencias-originais').glob('*.webp'))]
outputs=[blend,root/f'projeto/casa-terreo-revisao{revision:02d}.blend',root/'README.md',*sorted((root/'scripts').glob('*.py')),*images,root/f'renders/revisao-{revision:02d}/final/planta-terreo.png',*sorted(folder.glob('*.json')),*sorted(folder.glob('*.log')),folder/'RELATORIO.md',root/'relatorios/planta-casa/comparacao.json']
outputs=list(dict.fromkeys(p for p in outputs if p.name!='manifesto.json'))
manifest={'timestamp_utc':stamp,'revision':revision,'scope':review['scope'],'inputs':{str(p.relative_to(root)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in inputs},'outputs':{str(p.relative_to(root)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in outputs},'unknowns':unknowns,'known_limits':limits,'deletions':[],'external_publication':False}
for dest in [folder/'manifesto.json',root/'relatorios/planta-casa/manifesto.json']:dest.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('PHOTOGRAPHIC_REVISION_DOCUMENTED',revision,len(validation['checks']),'integrity',len(audit['checks']),'geometry',len(renders['outputs']),'renders;',len(corrected),'tested failures corrected')
