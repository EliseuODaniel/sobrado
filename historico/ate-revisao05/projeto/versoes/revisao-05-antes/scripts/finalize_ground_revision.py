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
assert revision==4
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(name):return json.loads((folder/name).read_text())
validation=read('validacao.json');audit=read('auditoria-depois.json');renders=read('renders-finais.json');start=read('inicio.json')
blend=root/'projeto/casa-reconstruida.blend';fingerprint=sha(blend)
assert fingerprint==validation['sha256']==audit['sha256']==renders['sha256']
assert validation['revision']==revision and all(c['passed'] for c in validation['checks'].values())
assert audit['all_passed'] and len(audit['checks'])==23
assert len(renders['outputs'])==13 and not renders['preview'] and renders['saved_file_unchanged']
source=root/cfg['user_layout_source']['path']
assert sha(source)==cfg['user_layout_source']['sha256']==start['source_sha256']
backup=root/f'projeto/versoes/revisao-{revision:02d}-antes/projeto/casa-reconstruida.blend'
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
unknowns=['Medidas lineares reais e ângulo exato da entrada','Dimensões e folgas reais sob o segundo lance; o encaixe modelado não é verificação de habitabilidade','Cobertura e detalhes construtivos da lavanderia','Dimensões exatas do retorno da escada e implantação dos cômodos superiores']
report={'timestamp_utc':stamp,'revision':revision,'status':'lavabo_sob_segundo_lance_garagem_ampliada','scope':'Correção aproximada do térreo: lavabo sob o segundo lance e garagem ampliada. Não é levantamento métrico ou validação do superior.','blend':{'path':str(blend.relative_to(root)),'sha256':fingerprint},'source':cfg['user_layout_source'],'user_correction':cfg['user_correction'],'integrity_checks':len(validation['checks']),'geometry_checks':len(audit['checks']),'renders':renders['outputs'],'visual_review':['Vista superior antes e depois da correção','Corte do lavabo sob o segundo lance','Corte em 3D do térreo e seis ângulos das fotos'],'unknowns':unknowns,'originals_preserved':True,'previous_revision_preserved':str(backup.relative_to(root)),'external_publication':False}
(folder/'revisao.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
body=f'''# Revisão 04 — lavabo sob o segundo lance e garagem ampliada

UTC: {stamp}

A mensagem posterior do usuário corrige a posição do lavabo do croqui: ele fica sob a segunda metade da escada. A área que o lavabo ocupava à frente da escada foi incorporada à garagem. O croqui anterior está preservado em `{cfg['user_layout_source']['path']}`; sua indicação do lavabo foi substituída explicitamente pela correção em `config/planta-casa.json:user_correction`.

| Obrigação | Evidência | Estado e limite |
| --- | --- | --- |
| Churrasqueira no canto posterior esquerdo e bancada com três bancos | Render superior, croqui e teste de posição | VERIFIED no modelo aproximado |
| Lavanderia ao lado da churrasqueira, imediatamente atrás da cozinha, com fundos alinhados | Render superior e testes de alinhamento e passagem | VERIFIED no modelo aproximado |
| Lavabo na projeção do segundo lance | Teste de projeção e corte específico com paredes frontal/lateral removidas | VERIFIED no modelo aproximado |
| Louças e espelho sob o forro inclinado e dentro do lavabo | Teste de todos os vértices das caixas de contorno das peças | VERIFIED no modelo; não valida folgas reais de uso |
| Garagem ampliada até o início do segundo lance | Comparação com revisão 03 e ray cast do acesso até a nova parede do lavabo | VERIFIED no modelo |
| Entrada em diagonal | Ângulo do conjunto editável e render da folha fechada | VERIFIED no modelo; ângulo métrico INFERRED |
| Arquivo editável e renders correspondentes | Reabertura do arquivo, {len(validation['checks'])} testes de integridade e hashes iguais | VERIFIED para o arquivo entregue |
| Preservação das referências e da revisão anterior | Hashes das 31 fotos, do croqui e do backup | VERIFIED |
| Dimensões reais e planta do superior | Nenhum levantamento novo fornecido | UNKNOWN |

O arquivo salvo gerou 13 renders. Os 23 testes de geometria incluem as relações fotográficas anteriores, as relações do croqui ainda válidas e três verificações da correção: projeção sob o lance, ampliação da garagem e encaixe das peças abaixo do forro. Não são uma pontuação de fidelidade visual ou certificação de uso do espaço.

## Interpretações adotadas

- A continuação direita da garagem avança até a face dianteira do volume sob o segundo lance. A antiga divisão à frente da escada foi retirada.
- O lavabo agora fica inteiramente na faixa longitudinal do segundo lance, com a porta fotografada mantida entre a TV e o primeiro lance. As louças foram deslocadas para esse volume.
- As paredes do lavabo acompanham o forro inclinado em vez de atravessar os degraus. A cena `CORTE_Lavabo_Escada` omite duas dessas paredes para mostrar o interior; elas continuam presentes nas demais cenas.
- A janela da cozinha foi mantida na posição fotografada, agora voltada ao volume identificado como lavanderia. Não foi presumida cobertura para toda essa área.
- A bancada e os três bancos seguem o desenho. Materiais e marcenaria continuam simplificados.
- A entrada diagonal e as posições de sala, jantar, cozinha, churrasqueira e lavanderia foram mantidas.

## Validação e limites

Comandos: `scripts/validate_house.py`, `scripts/house_atlas.py`, `python3 -m py_compile scripts/*.py` e `git diff --check`. A execução do Blender foi registrada em `geracao.log` e `validacao.log`; testes e renders estão em `validacao.json`, `auditoria-depois.json` e `renders-finais.json`.

As revisões 03 e 04 foram comparadas em `renders/planta-casa/comparacao-antes-depois.png`. O lavabo fica oculto pelos degraus na vista superior, por isso seu rótulo indica “sob 2º lance”. O encaixe é mostrado diretamente em `renders/revisao-04/final/lavabo-sob-escada.png`. A comparação com o croqui antigo avisa que a posição do lavabo foi corrigida posteriormente por mensagem. Foram revistos também o corte em 3D e os seis ângulos das fotos.

Permanecem desconhecidos: {'; '.join(unknowns)}. A conclusão desta data se restringe à aplicação aproximada do croqui ao térreo. Não houve commit, push ou publicação.
'''
(folder/'RELATORIO.md').write_text(body)
for name in ['revisao.json','RELATORIO.md']:(root/'relatorios/planta-casa'/name).write_bytes((folder/name).read_bytes())
inputs=[root/'config/planta-casa.json',source,*sorted((root/'referencias-originais').glob('*.webp'))]
outputs=[blend,root/f'projeto/casa-terreo-revisao{revision:02d}.blend',root/'README.md',*sorted((root/'scripts').glob('*.py')),*images,root/f'renders/revisao-{revision:02d}/final/planta-terreo.png',*sorted(folder.glob('*.json')),*sorted(folder.glob('*.log')),folder/'RELATORIO.md',root/'relatorios/planta-casa/comparacao.json']
outputs=list(dict.fromkeys(path for path in outputs if path.name!='manifesto.json'))
manifest={'timestamp_utc':stamp,'scope':report['scope'],'revision':revision,'inputs':{str(path.relative_to(root)):{'sha256':sha(path),'bytes':path.stat().st_size} for path in inputs},'outputs':{str(path.relative_to(root)):{'sha256':sha(path),'bytes':path.stat().st_size} for path in outputs},'unknowns':unknowns,'deletions':[],'external_publication':False}
for dest in [folder/'manifesto.json',root/'relatorios/planta-casa/manifesto.json']:dest.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('GROUND_REVISION_DOCUMENTED',revision,len(validation['checks']),'integrity',len(audit['checks']),'geometry',len(renders['outputs']),'renders')
