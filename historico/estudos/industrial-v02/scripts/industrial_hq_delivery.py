"""Conciliar a variante HQ e produzir comparações a partir dos renders reais."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps

root=Path(__file__).resolve().parents[1]
cfg=json.loads((root/'config/estilo-industrial-v02.json').read_text())
folder=root/cfg['report_directory'];renders=root/cfg['render_directory']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--reviewed',action='store_true');args=p.parse_args()
    model=json.loads((folder/'modelo.json').read_text());run=json.loads((folder/'renders.json').read_text())
    audit=json.loads((folder/'validacao.json').read_text());assert audit['all_passed']
    fingerprint=sha(root/cfg['output_blend']);assert fingerprint==model['blend_sha256']==run['blend_sha256']
    assert audit['blend_sha256']==fingerprint and all(audit['active_metric_uv'].values())
    assert sha(root/cfg['base_blend'])==model['base_sha256'] and not run['preview'] and run['envelope']['all_passed']
    expected={str(Path(cfg['render_directory'])/j['file']) for j in cfg['jobs']}
    assert set(run['outputs'])==expected
    for name,meta in run['outputs'].items():
        assert sha(root/name)==meta['sha256'] and (root/name).stat().st_size==meta['bytes']
        with Image.open(root/name) as im:assert list(im.size)==cfg['resolution'];im.verify()
    for asset in model['assets']:assert sha(root/asset['path'])==asset['sha256']
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',25)
    small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
    names=['Sala integrada','Cozinha','Lazer nos fundos','Quarto dos fundos']
    def tile(canvas,path,rect):
        x,y,w,h=rect
        with Image.open(path) as source:pic=ImageOps.contain(source.convert('RGB'),(w,h))
        canvas.paste(pic,(x+(w-pic.width)//2,y+(h-pic.height)//2))
    panel=Image.new('RGB',(1920,1380),'#191b1b');draw=ImageDraw.Draw(panel)
    draw.text((24,18),'CASA • INDUSTRIAL V02 • MATERIAIS E MOBILIÁRIO REFINADOS',font=font,fill='#e6cfaa')
    for i,job in enumerate(cfg['jobs']):
        x=(i%2)*960;y=70+(i//2)*650
        draw.text((x+24,y),names[i],font=font,fill='white');tile(panel,renders/job['file'],(x+12,y+45,936,585))
    panel.save(renders/'painel-ambientes.jpg',quality=94)
    comparison=Image.new('RGB',(1920,2740),'#191b1b');draw=ImageDraw.Draw(comparison)
    draw.text((24,18),'VERSÃO 01  |  VERSÃO 02 • MESMAS CÂMERAS E ARQUITETURA',font=font,fill='#e6cfaa')
    for i,job in enumerate(cfg['jobs']):
        y=70+i*660;draw.text((24,y),names[i],font=font,fill='white')
        tile(comparison,root/'renders/industrial-v01'/job['previous'],(12,y+44,936,585));tile(comparison,renders/job['file'],(972,y+44,936,585))
    comparison.save(renders/'antes-depois.jpg',quality=93)
    refs=['01-cena-final-menos-warn.png','01-cena-final-menos-warn.png','02-bar-fundo.png','escritorio2.png']
    atlas=Image.new('RGB',(1920,2740),'#191b1b');draw=ImageDraw.Draw(atlas)
    draw.text((24,18),'INSPIRAÇÃO  |  PROPOSTA V02 NA PLANTA EXISTENTE',font=font,fill='#e6cfaa')
    for i,job in enumerate(cfg['jobs']):
        y=70+i*660;draw.text((24,y),names[i],font=font,fill='white')
        tile(atlas,root/'referencias-estilo-industrial'/refs[i],(12,y+44,936,585));tile(atlas,renders/job['file'],(972,y+44,936,585))
    atlas.save(renders/'referencias-e-proposta.jpg',quality=93)
    stamp=dt.datetime.now(dt.timezone.utc).isoformat()
    if args.reviewed:
        review={'timestamp_utc':stamp,'blend_sha256':fingerprint,'renders':{k:v['sha256'] for k,v in run['outputs'].items()},'scope':'Quatro renders finais, antes/depois e inspiração inspecionados visualmente; avaliação qualitativa, não benchmark de equivalência a Unreal Engine',
                'observations':['Estofados com pregas e costuras, cadeiras detalhadas e banquetas redondas','Madeira com escala e direção de veios, tecido com trama e cimento suave','Cubas têm abertura e profundidade reais no modelo','Quarto recebe roupa de cama e telas de demonstração, mantendo o beliche','Mobiliário e arquitetura continuam aproximações e diferem das referências']}
        (folder/'revisao-visual.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
    reviewed=(folder/'revisao-visual.json').exists()
    if reviewed:
        d=json.loads((folder/'revisao-visual.json').read_text());assert d['blend_sha256']==fingerprint and d['renders']=={k:v['sha256'] for k,v in run['outputs'].items()}
    text=f'''# Industrial v02 — refinamento para maior realismo

UTC: {stamp}

Foram refinados os quatro ambientes na mesma arquitetura e nas mesmas câmeras da v01. A mudança combina materiais PBR (cor, rugosidade e normais de superfície), móveis detalhados, cubas abertas, tecidos com volume e uma nova composição de luz. Aumentar a quantidade de amostras sozinho não resolveria o aspecto simplificado da v01.

| Obrigação | Evidência | Estado |
| --- | --- | --- |
| Preservar arquitetura e escada | {len(model['geometry_before'])} geometrias herdadas comparadas ao reabrir; diferenças limitadas aos modificadores das duas bancadas | VERIFIED |
| Manter encaixe dos pisos | Três testes dos vértices das lajes e faces posteriores | VERIFIED |
| Renderizar quatro ambientes do editável salvo | Quatro PNGs em 1920 × 1200, nomes e hashes conciliados | VERIFIED |
| Preservar versão anterior | SHA-256 da v01 inalterado | VERIFIED |
| Recursos autossuficientes | Imagens empacotadas e testadas ao reabrir; ativos verificados por SHA-256 | VERIFIED |
| Inspecionar resultado e comparações | {'revisao-visual.json vinculado aos quatro hashes finais' if reviewed else 'Inspeção final pendente'} | {'VERIFIED' if reviewed else 'UNKNOWN'} |
| Equivalência a um projeto profissional no Unreal Engine | Não existe benchmark comum nem projeto Unreal comparável fornecido | UNKNOWN |

## O que mudou

- Materiais fotográficos CC0 de couro, madeira, tecido e reboco, com escala métrica e veios orientados pelas peças. As texturas foram ajustadas para não parecerem sujeira ou relevo exagerado.
- Sofá com almofadas arredondadas, afundamentos, pregas, costuras e manta; posições e projeção aproximada preservadas.
- Seis cadeiras detalhadas do Poly Haven e três banquetas redondas em madeira e aço; a planta e a circulação principal permanecem na posição anterior.
- Cubas com profundidade e ralo. Somente as duas bancadas receberam modificadores de abertura; paredes, aberturas arquitetônicas, lajes e degraus não foram deslocados.
- Roupa de cama e tecido no beliche; teclado e telas demonstrativas próprias. A TV usa mapeamento UV de parte da imagem de inspiração fornecida; o arquivo da referência não foi alterado.
- Ambiente HDRI e fontes direcionadas com contraste entre luz natural e quente. A vista de jardim do HDRI é contexto ilustrativo de iluminação, não levantamento do exterior da casa.

## Arquivos e execução

Editável: `projeto/industrial-v02/casa-industrial-hq.blend`, cenas `HQ_Sala`, `HQ_Cozinha`, `HQ_Lazer` e `HQ_Quarto`. As peças novas ficam em `HQ_Detalhes`. Cadeiras usam instâncias de uma malha detalhada na coleção `HQ_Fonte_Cadeira_CC0`. Os materiais começam por `HQ `. A v01 continua disponível como comparação.

Configuração: `config/estilo-industrial-v02.json`. Gerador e renderizador: `scripts/style_industrial_hq.py`. Render final em Cycles/CPU, até 256 amostras adaptativas (limiar 0,018), denoise e AgX. Os logs são `geracao-previas.log` e `renderizacao.log`; o arquivo foi reaberto em outro processo antes dos renders finais.

A RTX 4070 Laptop foi identificada pelo sistema, mas o Blender não enumerou dispositivos utilizáveis em OptiX ou CUDA nesta execução. Não houve alteração de drivers ou configuração global. O tempo de renderização não deve ser apresentado como execução em GPU.

## Licenças e limites

Os ativos externos são CC0 do Poly Haven; URLs, tamanhos e SHA-256 constam de `assets/industrial-v02/manifesto*.json`. O editor demonstrativo foi criado localmente sem conteúdo privado. A foto de inspiração fornecida é usada apenas no projeto solicitado.

O acabamento é mais detalhado, mas o nível de realismo é uma avaliação visual. Não há equivalência comprovada a Unreal Engine, e migrar a cena para outro motor não substitui o trabalho de modelagem, materiais e iluminação. Ainda há formas simplificadas em eletrodomésticos, plantas e marcenaria. Medidas da casa, banheiros e escada continuam com as incertezas documentadas na reconstrução. Este estudo não é projeto executivo.
'''
    (folder/'RELATORIO.md').write_text(text)
    files=[root/CFG_path for CFG_path in ['config/estilo-industrial-v02.json','scripts/style_industrial_hq.py','scripts/industrial_hq_delivery.py','README.md','assets/industrial-v02/README.md']]
    files+=[root/cfg['output_blend'],*[root/k for k in expected],*sorted(renders.glob('*.jpg')),*sorted(folder.glob('*.json')),*sorted(folder.glob('*.log')),folder/'RELATORIO.md',*[root/r['path'] for r in model['assets']],root/'assets/industrial-v02/editor-demonstrativo.png']
    files += [root/p for p in cfg['asset_manifests']]
    files=list(dict.fromkeys(p for p in files if p!=folder/'manifesto.json'))
    (folder/'manifesto.json').write_text(json.dumps({'timestamp_utc':stamp,'version':cfg['version'],'visual_review_complete':reviewed,'files':{str(p.relative_to(root)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in files}},ensure_ascii=False,indent=2)+'\n')
    print('HQ_DELIVERY_VERIFIED',len(expected),'renders; visual review:',reviewed)


if __name__=='__main__':main()
