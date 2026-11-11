"""Reconciliar os recibos da revisão, preservando os desconhecidos como desconhecidos."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
from PIL import Image

root=Path(__file__).resolve().parents[1];reports=root/'relatorios/revisao-02'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
validation=json.loads((root/'relatorios/planta-casa/validacao.json').read_text())
audit=json.loads((reports/'auditoria-depois.json').read_text());before=json.loads((reports/'auditoria-antes.json').read_text());renders=json.loads((reports/'renders-finais.json').read_text());cfg=json.loads((root/'config/planta-casa.json').read_text());inventory=json.loads((root/'relatorios/referencias-originais/inventario.json').read_text())
blend=root/'projeto/casa-reconstruida.blend';fingerprint=sha(blend)
assert validation['revision']==2 and all(c['passed'] for c in validation['checks'].values())
assert audit['all_passed'] and fingerprint==audit['sha256']==validation['sha256']==renders['sha256']
assert not renders['preview'] and len(renders['outputs'])==12 and renders['saved_file_unchanged']
assert all(sha(root/'referencias-originais'/name)==meta['sha256'] for name,meta in inventory['inputs'].items())
assert all(r['bounds'] is None for r in cfg['rooms'] if r['level']==1)
for file in renders['outputs']:
    with Image.open(root/file) as image:image.verify()
for file in ['planta-3d.png','plantas-superiores.png','comparacao-originais.png','comparacao-antes-depois.png']:
    with Image.open(root/'renders/planta-casa'/file) as image:image.verify()
subprocess.run(['git','diff','--check'],cwd=root,check=True)
stamp=dt.datetime.now(dt.timezone.utc).isoformat()
corrected=[name for name,result in audit['checks'].items() if result['passed'] and name in before['checks'] and not before['checks'][name]['passed']]
review={
 'timestamp_utc':stamp,'revision':2,'status':'contradicoes_especificas_corrigidas_superior_pendente',
 'scope':'Revisão das contradições observáveis da reconstrução. Não constitui aprovação da planta completa nem levantamento métrico.',
 'blend':{'path':str(blend.relative_to(root)),'sha256':fingerprint,'version':renders['version']},
 'integrity_checks':len(validation['checks']),'photo_geometry_checks':len(audit['checks']),'render_count':len(renders['outputs']),
 'baseline_tests_failed':[name for name,result in before['checks'].items() if not result['passed']],
 'tested_contradictions_corrected':corrected,
 'visual_review':{
  'reviewed':'Seis comparações com as fotos originais, planta em 3D, vista superior e estudos separados do superior.',
  'actual_changes':['Espinha lateral interna comum à TV, lavabo, escada e cozinha','Porta do lavabo fechada; louça isolada da sala','Primeiro lance transversal e recuado, visível pelos ângulos de sala1/sala4 e oculto pelo de sala7','Entrada lateral da cozinha e janela para o pátio','Espelho e pedra do bar trazidos para fora do volume das paredes','Distribuição não demonstrada do superior retirada; cinco módulos separados, fora da casa'],
  'remaining_differences':['Enquadramento e proporções ainda aproximados','Móveis, marcenaria e texturas simplificados','Forma integral do retorno da escada não demonstrada','Implantação do serviço, alinhamentos externos e dimensões não confirmados']},
 'unknowns':{'superior_layout':'UNKNOWN — faltam frente/fundos dos quartos e ligações entre portas','full_stair_return':'INFERRED — U transversal é solução provisória, não levantamento','real_dimensions':'UNKNOWN — nenhuma medida linear confirmada','registry_areas':'UNKNOWN — análise do ChatGPT é fonte secundária, matrícula não conferida'},
 'evidence_limits':'Os testes demonstram remoção das contradições enumeradas e integridade do arquivo. Não provam equivalência fotográfica ou métrica da casa inteira.',
 'inputs_preserved':True,'baseline_preserved':'projeto/versoes/revisao-02-antes/','external_publication':False}
(reports/'revisao.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
(root/'relatorios/planta-casa/revisao.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
rows='\n'.join('| '+name+' | '+('PASS' if before['checks'].get(name,{}).get('passed') else 'FAIL')+' | PASS | '+', '.join(result['references'])+' |' for name,result in audit['checks'].items())
body=f'''# Revisão 02 — contradições fotográficas e limites

UTC: {stamp}

Foram corrigidas contradições concretas da versão rejeitada. O arquivo foi reaberto e gerou {len(renders['outputs'])} renders em Cycles. Passaram {len(validation['checks'])} verificações de integridade e {len(audit['checks'])} verificações de implantação/visibilidade. Os recibos são `auditoria-antes.json`, `auditoria-depois.json`, `renders-finais.json` e `relatorios/planta-casa/validacao.json`.

Esses resultados não validam a planta completa. O superior permanece sem implantação demonstrada pelas fotos.

## Evidência dos testes

| Relação ou erro testado | Versão rejeitada | Revisão 02 | Fotos de controle |
| --- | --- | --- | --- |
{rows}

O teste da versão anterior utiliza o arquivo preservado. Ausência de uma vista requerida também aparece como falha e está detalhada no JSON; a tabela não é uma pontuação de semelhança fotográfica.

## Conferência visual

As montagens mostram foto, versão rejeitada e revisão em dois sentidos da sala, além de seis ângulos comparados. As câmeras foram reajustadas por marcos aproximados selecionados pelo agente ao inspecionar as imagens; isso não é avaliação humana nem fotogrametria. Persistem diferenças de proporção, enquadramento, acabamento e detalhes.

No térreo, TV e acessos foram reunidos na espinha lateral; a porta do lavabo fica fechada; o primeiro lance deixa de invadir longitudinalmente o estar. Espelho e pedra estavam embutidos nas paredes e agora estão expostos. A vista superior inclui as paredes externas e oculta as vergas para permitir ler os vãos. O corte 3D usa outro lado de observação para mostrar a face interna da parede da TV.

## Desconhecidos que impedem afirmar a planta inteira

| Afirmação | Estado | Evidência necessária |
| --- | --- | --- |
| Quartos e banheiros na posição correta do superior | UNKNOWN | Confirmar quais ficam na frente/fundos e como se conectam à circulação |
| Retorno completo da escada em U | INFERRED | Fotos contínuas ou planta do percurso completo |
| Dimensões lineares reais | UNKNOWN | Medidas ou planta cotada |
| Áreas da matrícula conciliadas | UNKNOWN | Documento original; o texto recebido foi identificado como análise do ChatGPT |

As divisões internas do superior foram retiradas da envoltória principal. Cômodos editáveis continuam como módulos na cena `ESTUDOS_Superior`, sem conexão presumida com a casa. O perímetro do serviço e a atribuição da pequena janela frontal a um cômodo também não foram confirmados.

## Escopo da conclusão

Nesta data, a revisão remove as contradições específicas testadas e fornece arquivo editável, renders e comparações. Não se declara a planta completa fiel ao imóvel. As 31 fotos originais e a versão rejeitada estão preservadas. Não houve commit, push ou publicação.
'''
(reports/'RELATORIO.md').write_text(body)
(root/'relatorios/planta-casa/RELATORIO.md').write_text(body)
inputs=[root/'config/planta-casa.json',*sorted((root/'referencias-originais').glob('*.webp'))]
outputs=[blend,root/'README.md',*sorted((root/'scripts').glob('*.py')),*[root/f for f in renders['outputs']],*sorted((root/'renders/planta-casa').glob('*.png')),*sorted(reports.glob('*.json')),*sorted(reports.glob('*.log')),reports/'RELATORIO.md',root/'relatorios/planta-casa/validacao.json',root/'relatorios/planta-casa/comparacao.json']
outputs=list(dict.fromkeys(p for p in outputs if p.name!='manifesto.json'))
manifest={'timestamp_utc':stamp,'revision':2,'status':review['status'],'scope':review['scope'],'inputs':{str(p.relative_to(root)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in inputs},'outputs':{str(p.relative_to(root)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in outputs},'unknowns':review['unknowns'],'deletions':[],'external_publication':False}
(reports/'manifesto.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
(root/'relatorios/planta-casa/manifesto.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('REVISION_DOCUMENTED',len(validation['checks']),'integrity',len(audit['checks']),'photographic relation checks;',len(corrected),'failures removed; upper layout remains unknown')
