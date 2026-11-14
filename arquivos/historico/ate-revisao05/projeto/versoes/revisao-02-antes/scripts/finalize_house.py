"""Reconciliar saídas, referências e validação após renderizar e inspecionar as imagens."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess

from PIL import Image

root=Path(__file__).resolve().parents[1]
report_dir=root/'relatorios/planta-casa'
validation=json.loads((report_dir/'validacao.json').read_text(encoding='utf-8'))
config=json.loads((root/'config/planta-casa.json').read_text(encoding='utf-8'))
inventory=json.loads((root/'relatorios/referencias-originais/inventario.json').read_text(encoding='utf-8'))


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


assert all(c['passed'] for c in validation['checks'].values())
assert validation['sha256']==digest(root/'projeto/casa-reconstruida.blend')
assert len(validation['renders'])==8
for name,meta in inventory['inputs'].items():assert digest(root/'referencias-originais'/name)==meta['sha256']
for name in validation['renders']:
    with Image.open(root/name) as im:im.verify()
for name in ['planta-3d.png','plantas-superiores.png','comparacao-originais.png']:
    with Image.open(root/'renders/planta-casa'/name) as im:im.verify()
subprocess.run(['git','diff','--check'],cwd=root,check=True)
stamp=dt.datetime.now(dt.timezone.utc).isoformat()
review={
    'timestamp_utc':stamp,
    'scope':'Entrega de modelo preliminar editável dos dois pavimentos com base em fotos. Não é validação da planta real nem da matrícula.',
    'model':{'file':'projeto/casa-reconstruida.blend','sha256':validation['sha256'],'blender_version':validation['version'],'scenes':8,'rooms_and_zones':len(config['rooms']),'device':validation['device']},
    'receipts':[
        {'obligation':'Usar as fotografias originais','status':'VERIFIED','receipt':'relatorios/referencias-originais/inventario.json; 31 arquivos, 26 imagens únicas empacotadas'},
        {'obligation':'Entregar dois pavimentos editáveis e preservar oito cenas','status':'VERIFIED','receipt':'relatorios/planta-casa/validacao.json; cenas, níveis, ambientes e recorte da escada'},
        {'obligation':'Reabrir e renderizar do arquivo salvo','status':'VERIFIED','receipt':'relatorios/planta-casa/validacao.log; oito renders e hash final preservado'},
        {'obligation':'Comparar a organização com fotos em dois sentidos e cozinha','status':'VERIFIED','receipt':'renders/planta-casa/comparacao-originais.png; inspeção visual registrada'},
        {'obligation':'Determinar dimensões lineares reais','status':'UNKNOWN','receipt':'Nenhuma medida ou planta cotada foi fornecida; dimensões explicitamente estimadas'},
        {'obligation':'Confirmar a implantação exata do superior e do serviço','status':'UNKNOWN','receipt':'Fotos isoladas não mostram ligações contínuas; posição dos cômodos e acessos marcada como hipótese'},
        {'obligation':'Verificar áreas da matrícula original','status':'UNKNOWN','receipt':'Usuário esclareceu que enviou análise do ChatGPT; documento não recebido nem conferido'},
        {'obligation':'Preservar fotografias e proposta anterior','status':'VERIFIED','receipt':'Hashes das 31 fotos conferidos; projeto/sala-industrial.blend e docs/SALA-INDUSTRIAL-ANTERIOR.md preservados'}
    ],
    'visual_review':{
        'plans':'Vistas dos pisos mostram o conjunto completo; vistas superiores incluem garagem, anexos e cotas estimadas. Superior tem disposição hipotética identificada.',
        'comparison':'Mantidas relações gerais entre estar, jantar, bar, escada e cozinha. Perspectivas e proporções não coincidem exatamente; escada, aberturas, marcenaria e detalhes são simplificados.',
        'iterations':['Comparação inicial das 26 fotos únicas e identificação de duplicatas','Abertura lateral da escada e reposicionamento de TV da suíte para liberar a porta','Preservação dos presets ao reabrir a cena em background','Ampliação das câmeras ortográficas para incluir todo o perímetro','Reposicionamento da câmera da cozinha para fora da geladeira','Porta de entrada fechada conforme as fotografias, liberando a vista da sala'],
        'limits':['Sem levantamento métrico ou fotogrametria','Escada completa em U é hipótese; os dois trechos fotografados não definem sua forma integral','Fachada, cobertura da garagem, posição da lavanderia e distribuição superior dependem de confirmação','Não foi feita validação executiva de circulação, estrutura, acessibilidade ou colisões de todos os triângulos']
    },
    'area_comparison':validation['area_comparison'],
    'checks':{'scene_checks_passed':len(validation['checks']),'renders_from_saved_file':len(validation['renders']),'inputs_hashes_preserved':True,'blend_hash_preserved_after_render':True,'git_diff_check':'passed'},
    'git_publication':'Nenhum commit, push ou publicação nesta etapa.'
}
(report_dir/'revisao.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows='\n'.join('| '+r['obligation']+' | '+r['status']+' | '+r['receipt']+' |' for r in review['receipts'])
body=f'''# Reconstrução preliminar da casa — validação e limites

UTC: {stamp}

Entregue `projeto/casa-reconstruida.blend` com os dois pavimentos, oito cenas de inspeção e recursos empacotados. O arquivo foi reaberto e originou oito renders. Os {len(validation['checks'])} checks passaram, incluindo preservação do arquivo e das 31 fotos originais. O render usou Blender {validation['version']}, Cycles e {validation['device']['backend']}.

| Obrigação / afirmação | Estado da evidência | Recibo |
| --- | --- | --- |
{rows}

## Comparação visual

Foram conferidas a planta 3D dos dois pavimentos, as vistas superiores completas, as perspectivas em sentidos opostos da sala, a cozinha e a volumetria. A montagem `renders/planta-casa/comparacao-originais.png` permite revisar a organização em relação às fotos. Há diferenças de proporção, câmera, posição das aberturas, forma da escada e detalhamento. A distribuição superior é hipotética e o acesso à lavanderia não está documentado por fotos contínuas.

## Escala e áreas

Os retângulos-base de 42,50 m² e 51,00 m² seguem as dimensões hipotéticas sugeridas na análise secundária. Não são comprovação de área construída ou exclusiva. A laje superior tem recorte para a escada; paredes, varanda, garagem, bar e lavanderia não foram conciliados com critérios de matrícula. Os 1,74 m² mencionados como comuns não foram atribuídos a uma posição inventada.

O usuário esclareceu que o texto de áreas era uma análise do ChatGPT. A matrícula original não foi conferida. A quota de terreno citada não foi tratada como área integralmente privativa.

## Escopo do resultado

Modelo preliminar editável, renderizado e comparado com as fotos disponíveis. A correspondência métrica e a implantação exata do imóvel continuam desconhecidas. Uma planta cotada ou medidas reais, com posições de portas, janelas e escada, permitem substituir as hipóteses. Nenhuma alegação de projeto executivo ou validação documental acompanha esta entrega.
'''
(report_dir/'RELATORIO.md').write_text(body,encoding='utf-8')

inputs=[root/'config/planta-casa.json',*sorted((root/'referencias-originais').glob('*.webp'))]
outputs=[root/'README.md',root/'projeto/casa-reconstruida.blend',*sorted((root/'renders/planta-casa').glob('*.png')),*sorted((root/'scripts').glob('*.py')),*sorted(report_dir.glob('*.json')),*sorted(report_dir.glob('*.log')),report_dir/'RELATORIO.md']
outputs=[p for p in outputs if p.name!='manifesto.json']
manifest={'schema_version':1,'timestamp_utc':stamp,'scope':review['scope'],'source_status':config['secondary_analysis']['verification'],'inputs':{str(p.relative_to(root)):{'bytes':p.stat().st_size,'sha256':digest(p)} for p in inputs},'outputs':{str(p.relative_to(root)):{'bytes':p.stat().st_size,'sha256':digest(p)} for p in outputs},'validation':review['checks'],'preserved_previous_model':'projeto/sala-industrial.blend','deletions':[],'external_publication':False}
(report_dir/'manifesto.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('HOUSE_FINALIZED',len(inputs),'inputs',len(outputs),'outputs',len(validation['checks']),'checks')
