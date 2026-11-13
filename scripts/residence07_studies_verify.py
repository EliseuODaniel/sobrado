"""Confere arquivos de entrega e registra conclusões com seus recibos."""
import datetime as dt
import json
from pathlib import Path
import re
from urllib.parse import unquote

import fitz
from PIL import Image

import residence07_geometry as geo
import residence07_studies_data as data

ROOT=geo.ROOT;REPORT=ROOT/data.CFG['report_directory']


def main():
    checks=[];models={};audits={};counts={}
    def check(name,passed,details=None):
        row={'name':name,'passed':bool(passed)}
        if details is not None:row['details']=details
        checks.append(row)
    for kind,key,total,pages in [('atual','current_renders',20,29),('instalacoes','services_renders',20,21)]:
        model=json.loads((REPORT/(kind+'-modelo.json')).read_text());models[kind]=model
        audit=json.loads((REPORT/(kind+'-validacao.json')).read_text());audits[kind]=audit
        records=json.loads((REPORT/(kind+'-renders.json')).read_text());counts[kind]=len(records)
        check('auditoria nativa completa '+kind,audit['all_passed'] and audit['renders_required'] and audit['blend_sha256']==geo.sha(ROOT/model['blend']))
        check('conjunto de imagens '+kind,len(records)==total and {r['id'] for r in records}=={j['id'] for j in model['jobs']})
        for r in records:
            path=ROOT/r['file']
            check('hash '+r['id'],geo.sha(path)==r['sha256'] and r['blend_sha256']==model['blend_sha256'])
            with Image.open(path) as im:
                check('PNG '+r['id'],im.size==tuple(data.CFG['resolution']) and im.format=='PNG');im.verify()
        out=ROOT/data.CFG[key]
        with fitz.open(out/'00-cadernos'/('caderno-'+kind+'.pdf')) as doc:check('páginas do caderno '+kind,len(doc)==pages,len(doc))
        for path in [out/'LEIA-ME.md',out/'galeria.html']:
            text=path.read_text();links=re.findall(r'\]\(([^)]+)\)',text) if path.suffix=='.md' else re.findall(r'(?:href|src)="([^"]+)"',text)
            bad=[]
            for link in links:
                if link.startswith(('http:','https:','#')):continue
                target=path.parent/unquote(link.split('#')[0])
                if not target.exists():bad.append(link)
            check('links locais '+str(path.relative_to(ROOT)),not bad,bad)
    attic_report=ROOT/'relatorios/residencia-07-atico-v05'
    latest=json.loads((attic_report/'modelo.json').read_text())
    latest_audit=json.loads((attic_report/'validacao-completa.json').read_text())
    latest_delivery=json.loads((attic_report/'validacao-entrega.json').read_text())
    latest_manifest=json.loads((attic_report/'manifesto.json').read_text())
    models['atico']=latest;audits['atico']=latest_audit;counts['atico']=len(latest['jobs'])
    check('ático vigente v05 conferido',latest_audit['all_passed'] and latest_delivery['all_passed'] and geo.sha(ROOT/latest['blend'])==latest['blend_sha256'])
    check('artefatos atuais do ático',all(geo.sha(ROOT/r['file'])==r['sha256'] for r in latest_manifest['artifacts']))
    archived=json.loads((REPORT/'atual-arquivos-anteriores.json').read_text())
    check('34 arquivos anteriores preservados',len(archived)==34 and all(geo.sha(ROOT/r['archive'])==r['sha256'] for r in archived))
    archived_reports=json.loads((REPORT/'atual-relatorios-anteriores.json').read_text())
    check('relatórios anteriores preservados',bool(archived_reports) and all(geo.sha(ROOT/r['archive'])==r['sha256'] for r in archived_reports))
    check('nenhum PNG obsoleto na raiz atual',not list((ROOT/data.CFG['current_renders']).glob('*.png')))
    check('pastas da versão atual',sorted(p.name for p in (ROOT/data.CFG['current_renders']).iterdir() if p.is_dir())==['00-cadernos','01-plantas','02-ambientes','03-exteriores','04-comparacoes','06-galerias'])
    for level in ['terreo','superior']:
        for ext in ['png','svg','pdf']:check('planta vetorial atual '+level+'.'+ext,(ROOT/data.CFG['current_renders']/'01-plantas'/('planta-atual-'+level+'.'+ext)).exists())
    photos=json.loads((ROOT/'relatorios/referencias-originais/inventario.json').read_text())
    check('31 fotos originais preservadas',len(photos['inputs'])==31 and all(geo.sha(ROOT/'referencias-originais'/p)==row['sha256'] for p,row in photos['inputs'].items()))
    comp=json.loads((REPORT/'atual-comparacoes.json').read_text())
    check('seis comparações com fotos',len(comp)==6 and all(geo.sha(ROOT/r['photo'])==r['photo_sha256'] and (ROOT/r['file']).exists() for r in comp))
    manifest=json.loads((REPORT/'entrega.json').read_text())
    check('manifesto íntegro',all(geo.sha(ROOT/r['file'])==r['sha256'] for r in manifest['artifacts']))
    base=json.loads((ROOT/'relatorios/residencia-07/validacao-completa.json').read_text())
    check('base documental continua íntegra',base['all_passed'] and base['blend_sha256']==geo.sha(ROOT/data.CFG['base_blend']))
    rows=json.loads((ROOT/'relatorios/residencia-07/renders.json').read_text())
    check('29 imagens documentais com origem verificável',len(rows)==29 and all(geo.valid_render_record(r) for r in rows))
    check('quatro estruturas atualizadas na entrega base',all(r.get('source_blend')==data.CFG['services_blend'] for r in rows if r['id'].startswith('estrutura-')))
    result={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'checks':checks,'all_passed':all(c['passed'] for c in checks),
        'browser_verification':{'status':'UNAVAILABLE','reason':'Conector sem Chrome instalado; tentativa com Chromium local excedeu 35 segundos. Links e imagens são conferidos estaticamente; filtro da galeria não foi exercitado em navegador.'},
        'native_checks':{k:len(a['checks']) for k,a in audits.items()},'images':counts,'delivery_artifacts':len(manifest['artifacts'])}
    (REPORT/'validacao-entrega.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('STUDIES_VERIFY',len(checks),'PASSED' if result['all_passed'] else 'FAILED')
    for c in checks:
        if not c['passed']:print('FAIL',c)
    if not result['all_passed']:raise RuntimeError('Entrega incompleta; consultar validacao-entrega.json')
    write_report(result,models,audits)


def write_report(result,models,audits):
    table='\n'.join(f"| {k} | {len(m['jobs'])} | {len(audits[k]['checks'])} | `{m['blend']}` |" for k,m in models.items())
    text=f'''# Residência 07 — atual, instalações 3D e ático

Conferência em {result['timestamp_utc']}. Entrega verificada para reconstrução documental e visual: {len(result['checks'])} verificações de arquivos, além das conferências nativas abaixo. Não houve levantamento presencial nem cálculo estrutural.

| Modelo | Imagens/quadros finais | Verificações nativas | Arquivo editável |
| --- | ---: | ---: | --- |
{table}

## Estado atual e refatoração

`renders/atual` foi inteiramente substituída pela reconstrução sobre a unidade 07. As 34 imagens da raiz foram preservadas em `historico/atual-pre-residencia07/renders`, com hashes em `atual-arquivos-anteriores.json`. A pasta vigente contém 20 vistas, duas plantas vetoriais em SVG/PDF/PNG, seis comparações foto/modelo, galeria navegável e caderno de 29 páginas.

A arquitetura deriva de ARQ03/04. A abertura do fundo da sala vem da instrução do usuário e das fotos; cobertura de vidro, vigas de madeira e divisão lazer/lavanderia aparecem na reconstrução posterior. A cozinha cinza, sofá cinza, mesa escura de vidro, bar com quatro banquetas e dormitórios seguem as referências disponíveis. A cama da suíte foi orientada para a parede da TV, com roupeiro ao fundo. As 31 fotos de entrada continuam com seus hashes originais.

## Estrutura e instalações tridimensionais

As quatro estruturas têm paredes em sálvia suave e materiais próprios para laje e escada. O arquivo original `casa-07.blend` continua intacto; as imagens coloridas são produzidas por `casa-07-instalacoes.blend`. A auditoria compara os vértices das cópias com os objetos do arquivo aprovado.

São 16 novas vistas das redes: elétrica, hidráulica, esgoto/ventilação e TV/telefone por pavimento e em conjunto; três sobreposições coordenadas e uma vista do reservatório. Paredes usam 12% de opacidade; lajes, 5,5%. As tubulações são curvas 3D editáveis. Diâmetros de exibição são ampliados onde necessário, mantendo o diâmetro nominal registrado nos objetos. Os recortes por pavimento são conferidos em Z.

## Proposta de ático

O ático vigente é a v05: dois lances exatamente sobre os inferiores e caixa de 1.000 L transferida para a esquerda, preservando sua cota de base. São 18 vistas gerais, seis isoladas e 24 quadros do giro. O forro tem reserva de 15 cm e as alturas são medidas sobre a geometria salva. As propostas antigas foram excluídas por solicitação do usuário. [Entrega vigente](../../../renders/residencia-07-atico-v05/LEIA-ME.md).

## Obrigações e limites

| Obrigação | Recibo observado | Situação |
| --- | --- | --- |
| Estrutura colorida sem alterar a base | `instalacoes-modelo.json`, `instalacoes-validacao.json` | VERIFICADO |
| Redes editáveis e paredes transparentes | Objetos e materiais do Blender reaberto; auditoria nativa | VERIFICADO |
| Imagens produzidas dos modelos salvos | `*-renders.json`, hashes nativos e PNG | VERIFICADO |
| Ático em projeto independente | V05 distinta, 48 cenas e auditoria de alinhamento/caixa/alturas | VERIFICADO |
| Atual com alterações e móveis | `atual-modelo.json`, imagens e comparações com as fotos | RECONSTRUÇÃO VISUAL |
| Organização e preservação do conteúdo anterior | Manifesto de 34 arquivos e hashes de arquivo | VERIFICADO |
| Medidas executadas de anexos e móveis | Fotos e inferências; sem medição local | APROXIMADAS |
| Trajetos reais das redes após a reforma | Não fornecidos em levantamento | DESCONHECIDOS |
| Fundações, armaduras, reforços e resistência da laje | Ausentes nas fontes analisadas | DESCONHECIDOS |

Os trajetos 3D de instalações são de estudo, com alturas documentadas transcritas quando disponíveis. A lavanderia posterior tem pontos inferidos das fotos, com altura de 1,00 m de estudo; a referência genérica a HID05 no grafo não confirma essa altura. Esta modelagem não atualiza os projetos de execução da reforma. As cotas da arquitetura original permanecem documentais; divergências internas dos PDFs estão no relatório principal. O vão, a laje, o suporte da caixa e a nova escada do ático precisam de dimensionamento específico.

## Reprodução e conferência

Os geradores são `residence07_current.py`, `residence07_services.py` com contrato em `config/residencia-07-estudos.json`; o ático usa `residence07_attic_v05.py` e sua configuração própria. `residence07_studies_audit.py` reabre os modelos; `residence07_studies_delivery.py` monta cadernos/galerias/plantas; `residence07_studies_verify.py` confere a entrega. Os recibos registram os hashes dos scripts que geraram cada modelo.

Os PNGs finais têm 1920 × 1440 pixels, Cycles/CUDA, 96 amostras e redução de ruído. As imagens são renders de geometria nativa, sem alterações generativas. A base documental mantém 29 imagens verificáveis, incluindo as quatro estruturas atualizadas pelo modelo complementar.

Os links e imagens das galerias HTML foram conferidos estaticamente. O conector de navegador estava sem Chrome, e a alternativa com Chromium local excedeu 35 segundos; o filtro da galeria não foi exercitado em navegador. Essa limitação não impede abrir os PNGs e os cadernos PDF diretamente.
'''
    (REPORT/'RELATORIO.md').write_text(text)
    old=json.loads((REPORT/'checkpoint.json').read_text())
    old.update(status='COMPLETE_VISUAL_AND_DOCUMENTARY',remaining=[],verification=str((REPORT/'validacao-entrega.json').relative_to(ROOT)),
        results={'images':result['images'],'native_checks':result['native_checks'],'delivery_checks':len(result['checks']),'artifacts':result['delivery_artifacts']})
    (REPORT/'checkpoint.json').write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'relatorios/atual/checkpoint.json').write_text(json.dumps({'status':old['status'],'model':models['atual']['blend'],'delivery':data.CFG['current_renders'],'verification':old['verification']},ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
