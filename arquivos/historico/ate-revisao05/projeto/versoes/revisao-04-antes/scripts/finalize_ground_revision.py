"""Registrar a entrega do térreo aproximado sem promover hipóteses a medidas reais."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
from PIL import Image


root=Path(__file__).resolve().parents[1]
cfg=json.loads((root/'config/planta-casa.json').read_text())
revision=cfg['revision_number'];folder=root/'relatorios'/f'revisao-{revision:02d}'
assert revision==3
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(name):return json.loads((folder/name).read_text())
validation=read('validacao.json');audit=read('auditoria-depois.json');renders=read('renders-finais.json');start=read('inicio.json')
blend=root/'projeto/casa-reconstruida.blend';fingerprint=sha(blend)
assert fingerprint==validation['sha256']==audit['sha256']==renders['sha256']
assert validation['revision']==revision and all(c['passed'] for c in validation['checks'].values())
assert audit['all_passed'] and len(audit['checks'])==20
assert len(renders['outputs'])==12 and not renders['preview'] and renders['saved_file_unchanged']
source=root/cfg['user_layout_source']['path']
assert sha(source)==cfg['user_layout_source']['sha256']==start['source_sha256']
backup=root/'projeto/versoes/revisao-03-antes/projeto/casa-reconstruida.blend'
assert sha(backup)==start['previous_blend_sha256']
inventory=json.loads((root/'relatorios/referencias-originais/inventario.json').read_text())
assert all(sha(root/'referencias-originais'/name)==meta['sha256'] for name,meta in inventory['inputs'].items())
assert all(room['bounds'] is None for room in cfg['rooms'] if room['level']==1)
comparison=json.loads((root/'relatorios/planta-casa/comparacao.json').read_text())
assert comparison['blend_sha256']==fingerprint and comparison['revision']==revision
images=[root/name for name in renders['outputs']]+[root/name for name in comparison['outputs']]
for path in images:
    with Image.open(path) as image:image.verify()
subprocess.run(['git','diff','--check'],cwd=root,check=True)
stamp=dt.datetime.now(dt.timezone.utc).isoformat()
unknowns=['Medidas lineares reais e ângulo exato da entrada','Ligação interna do lavabo mantida sob o retorno da escada; não desenhada no croqui','Cobertura e detalhes construtivos da lavanderia','Retorno completo da escada e implantação dos cômodos superiores']
report={'timestamp_utc':stamp,'revision':revision,'status':'croqui_aproximado_aplicado_ao_terreo','scope':'Distribuição aproximada do térreo segundo o desenho do usuário. Não é levantamento métrico ou validação do superior.','blend':{'path':str(blend.relative_to(root)),'sha256':fingerprint},'source':cfg['user_layout_source'],'integrity_checks':len(validation['checks']),'geometry_checks':len(audit['checks']),'renders':renders['outputs'],'visual_review':['Vista superior confrontada com o croqui','Vista em 3D com a porta diagonal visível','Comparações com seis fotos originais'],'unknowns':unknowns,'originals_preserved':True,'previous_revision_preserved':str(backup.relative_to(root)),'external_publication':False}
(folder/'revisao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
body=f'''# Revisão 03 — térreo conforme o desenho do usuário

UTC: {stamp}

O croqui foi aplicado como orientação de distribuição aproximada, sem convertê-lo em medidas reais. A imagem recebida está preservada em `{cfg['user_layout_source']['path']}`.

| Obrigação | Evidência | Estado e limite |
| --- | --- | --- |
| Churrasqueira no canto posterior esquerdo e bancada com três bancos | Render superior, croqui e teste de posição | VERIFIED no modelo aproximado |
| Lavanderia ao lado da churrasqueira, imediatamente atrás da cozinha, com fundos alinhados | Render superior e testes de alinhamento e passagem | VERIFIED no modelo aproximado |
| Lavabo à frente da escada e acima da continuação da garagem | Render superior, louças reposicionadas e teste de divisão | VERIFIED no modelo; acesso sob a escada permanece INFERRED |
| Continuação direita da garagem aberta para a frente | Ray cast do acesso até a parede do lavabo e render | VERIFIED no modelo |
| Entrada em diagonal | Ângulo do conjunto editável e render da folha fechada | VERIFIED no modelo; ângulo métrico INFERRED |
| Arquivo editável e renders correspondentes | Reabertura do arquivo, {len(validation['checks'])} testes de integridade e hashes iguais | VERIFIED para o arquivo entregue |
| Preservação das referências e da revisão anterior | Hashes das 31 fotos, do croqui e do backup | VERIFIED |
| Dimensões reais e planta do superior | Nenhum levantamento novo fornecido | UNKNOWN |

O arquivo salvo gerou 12 renders. Os 20 testes de geometria incluem 12 relações da revisão fotográfica anterior e oito verificações do croqui; não são uma pontuação de fidelidade visual.

## Interpretações adotadas

- A área marcada como “metade da garagem” é a continuação da garagem à direita da entrada, aberta para a parte frontal.
- O lavabo ocupa a faixa marcada pelo usuário e mantém acesso pela porta fotografada junto à escada. O pequeno trecho de ligação sob o retorno é uma interpretação, porque o croqui não desenha sua porta.
- A janela da cozinha foi mantida na posição fotografada, agora voltada ao volume identificado como lavanderia. Não foi presumida cobertura para toda essa área.
- A bancada e os três bancos seguem o desenho. Materiais e marcenaria continuam simplificados.
- Sala, jantar, cozinha, primeiro lance e estudos do superior foram preservados em suas posições, com ajuste curto do rack para acomodar a entrada diagonal.

## Validação e limites

Comandos: `scripts/validate_house.py`, `scripts/house_atlas.py`, `python3 -m py_compile scripts/*.py` e `git diff --check`. A execução do Blender foi registrada em `geracao.log` e `validacao.log`; testes e renders estão em `validacao.json`, `auditoria-depois.json` e `renders-finais.json`.

O croqui e a planta foram comparados lado a lado em `renders/planta-casa/croqui-e-planta.png`. Foram revistos também o corte em 3D e seis ângulos das fotos. A maior distância até a bancada nos enquadramentos da sala acompanha a extensão posterior indicada no desenho; não foi escondida por uma falsa escala das fotografias.

Permanecem desconhecidos: {'; '.join(unknowns)}. A conclusão desta data se restringe à aplicação aproximada do croqui ao térreo. Não houve commit, push ou publicação.
'''
(folder/'RELATORIO.md').write_text(body)
for name in ['revisao.json','RELATORIO.md']:(root/'relatorios/planta-casa'/name).write_bytes((folder/name).read_bytes())
inputs=[root/'config/planta-casa.json',source,*sorted((root/'referencias-originais').glob('*.webp'))]
outputs=[blend,root/'projeto/casa-terreo-revisao03.blend',root/'README.md',*sorted((root/'scripts').glob('*.py')),*images,root/'renders/revisao-03/final/planta-terreo.png',*sorted(folder.glob('*.json')),*sorted(folder.glob('*.log')),folder/'RELATORIO.md',root/'relatorios/planta-casa/comparacao.json']
outputs=list(dict.fromkeys(path for path in outputs if path.name!='manifesto.json'))
manifest={'timestamp_utc':stamp,'scope':report['scope'],'revision':revision,'inputs':{str(path.relative_to(root)):{'sha256':sha(path),'bytes':path.stat().st_size} for path in inputs},'outputs':{str(path.relative_to(root)):{'sha256':sha(path),'bytes':path.stat().st_size} for path in outputs},'unknowns':unknowns,'deletions':[],'external_publication':False}
for dest in [folder/'manifesto.json',root/'relatorios/planta-casa/manifesto.json']:dest.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('GROUND_REVISION_DOCUMENTED',revision,len(validation['checks']),'integrity',len(audit['checks']),'geometry',len(renders['outputs']),'renders')
