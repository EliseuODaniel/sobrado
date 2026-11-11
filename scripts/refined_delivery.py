"""Confere entrega, comparação e proveniência da proposta industrial v04."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parents[1]


def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def load(path):return json.loads(path.read_text())


def write(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reviewed',action='store_true');args=parser.parse_args()
    cfg=load(ROOT/'config/estilo-industrial-v04.json');folder=ROOT/cfg['report_directory'];renders=ROOT/cfg['render_directory']
    model=load(folder/'modelo.json');run=load(folder/'renders.json');audit=load(folder/'recursos-nativos.json');validation=load(folder/'validacao.json')
    digest=sha(ROOT/cfg['output_blend'])
    assert digest==model['blend_sha256']==run['blend_sha256']==audit['blend_sha256']==validation['blend_sha256']
    assert sha(ROOT/cfg['base_blend'])==model['base_sha256']==audit['base_sha256']
    assert audit['all_passed'] and validation['all_passed'] and validation['envelope']['all_passed']
    assert audit['dining_chairs_visible']==4 and audit['sofa_seats']==3 and audit['bedroom_pillows_preserved']
    assert not audit['external_libraries'] and not validation['geometry_differences']
    assert not run['preview'] and run['device']['backend']=='CUDA'
    expected={str(Path(cfg['render_directory'])/j['file']) for j in cfg['jobs']};assert set(run['outputs'])==expected
    for name,meta in run['outputs'].items():
        path=ROOT/name;assert sha(path)==meta['sha256'] and path.stat().st_size==meta['bytes']
        assert meta['resolution_percentage']==100 and meta['samples_max']==cfg['samples']
        with Image.open(path) as im:
            assert list(im.size)==cfg['resolution'] and im.format=='PNG';assert im.width*941==im.height*1671;im.verify()
    for item in model['new_assets']:
        p=ROOT/item['path'];assert sha(p)==item['sha256'] and p.stat().st_size==item['bytes']
        assert hashlib.md5(p.read_bytes()).hexdigest()==item['md5']
    reference=ROOT/'referencias-estilo-industrial/01-cena-final-menos-warn.png'
    assert sha(reference)==model['reference_sha256']
    baseline=load(ROOT/'relatorios/industrial-v01/modelo.json')
    for path,checksum in baseline['references'].items():assert sha(ROOT/path)==checksum
    assert sha(ROOT/'projeto/casa-reconstruida.blend')==baseline['base_sha256']
    assert sha(ROOT/'projeto/industrial-v01/casa-industrial.blend')==baseline['blend_sha256']
    old_run=load(ROOT/'relatorios/industrial-v03/renders.json')
    for path,metadata in old_run['outputs'].items():assert sha(ROOT/path)==metadata['sha256']

    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24)
    labels=['Sala integrada','Sofá contemporâneo','Parede da TV','Cozinha','Lazer nos fundos','Quarto dos fundos']

    def tile(canvas,path,x,y):
        with Image.open(path) as source:pic=ImageOps.contain(source.convert('RGB'),(936,528))
        canvas.paste(pic,(x+(936-pic.width)//2,y+(528-pic.height)//2))

    panel=Image.new('RGB',(1920,1900),'#191b1b');draw=ImageDraw.Draw(panel)
    draw.text((24,18),'CASA • INDUSTRIAL V04 • MAIS PRÓXIMA DA INSPIRAÇÃO',font=font,fill='#e6cfaa')
    for i,job in enumerate(cfg['jobs']):
        x=i%2*960;y=70+i//2*600;draw.text((x+24,y),labels[i],font=font,fill='white');tile(panel,renders/job['file'],x+12,y+45)
    panel.save(renders/'painel-ambientes.jpg',quality=95)
    refs=['01-cena-final-menos-warn.png']*4+['02-bar-fundo.png','escritorio2.png']
    atlas=Image.new('RGB',(1920,3710),'#191b1b');draw=ImageDraw.Draw(atlas)
    draw.text((24,18),'INSPIRAÇÃO | V04 ADAPTADA À PLANTA DA CASA',font=font,fill='#e6cfaa')
    for i,job in enumerate(cfg['jobs']):
        y=70+i*600;draw.text((24,y),labels[i],font=font,fill='white');tile(atlas,ROOT/'referencias-estilo-industrial'/refs[i],12,y+45);tile(atlas,renders/job['file'],972,y+45)
    atlas.save(renders/'referencias-e-proposta.jpg',quality=94)
    evolution=Image.new('RGB',(1920,3110),'#191b1b');draw=ImageDraw.Draw(evolution)
    draw.text((24,18),'V03 | V04 • ENQUADRAMENTOS DIFERENTES',font=font,fill='#e6cfaa')
    for i,name in enumerate(['sala-integrada.png','sala.png','cozinha.png','lazer-fundos.png','quarto-fundos.png']):
        y=70+i*600;draw.text((24,y),name,font=font,fill='white');tile(evolution,ROOT/'renders/industrial-v03'/name,12,y+45);tile(evolution,renders/name,972,y+45)
    evolution.save(renders/'evolucao-v03-v04.jpg',quality=94)
    now=dt.datetime.now(dt.timezone.utc).isoformat();hashes={name:meta['sha256'] for name,meta in run['outputs'].items()}
    review_path=folder/'revisao-visual.json'
    if args.reviewed:
        write(review_path,{'timestamp_utc':now,'blend_sha256':digest,'renders':hashes,
            'scope':'Seis renders finais, painel e comparações inspecionados visualmente. Avaliação qualitativa.',
            'observations':['Sofá contemporâneo caramelo com pregas, manta e almofadas neutras',
                'Quatro cadeiras e cabeceiras livres, mesa de madeira mais quente',
                'Vegetação com mapas PBR e painel da TV arredondado com luz quente',
                'Iluminação compartilhada nas vistas; sem discos de preenchimento aparentes',
                'A profundidade da casa e os elementos fixos diferem da imagem inspiradora',
                'Aparelhos e partes da marcenaria permanecem simplificados']})
    reviewed=review_path.exists()
    if reviewed:
        review=load(review_path);assert review['blend_sha256']==digest and review['renders']==hashes
    total_seconds=sum(item['seconds'] for item in run['outputs'].values())
    report=f'''# Industrial v04 — direção de arte mais próxima da referência

UTC: {now}

Foram produzidas seis imagens nativas em 3342 × 1882, duas vezes cada dimensão da referência principal. A proposta aproxima móveis, materiais e iluminação da inspiração sem alterar paredes, aberturas, escada ou encaixe dos pavimentos. Tudo continua no `.blend` editável; não houve retoque generativo das imagens finais.

| Obrigação | Recibo observado | Estado |
| --- | --- | --- |
| Nativo editável e autossuficiente | Modelo salvo/reaberto; {audit['packed_file_images']} imagens empacotadas e zero bibliotecas externas | VERIFIED |
| Preservar planta e fonte v03 | {audit['geometry_compared']} hashes de geometrias herdadas sem diferenças; SHA da base inalterado | VERIFIED |
| Manter alinhamento dos pavimentos | Três verificações do contorno e faces posteriores | VERIFIED |
| Móveis próximos da composição | Três assentos no sofá, quatro cadeiras em 2 + 2, cabeceiras livres; conferência nativa | VERIFIED |
| Gerar todas as imagens a partir do arquivo salvo | Seis PNGs com nomes, dimensões, bytes e hashes conciliados | VERIFIED |
| Dispositivo efetivo | {run['device']['backend']}: {', '.join(run['device']['devices'])} | VERIFIED |
| Preservar reconstrução, v01, v03 e referências | Hashes dos modelos, imagens anteriores e referências conferidos | VERIFIED |
| Inspeção dos finais e comparações | {'revisao-visual.json vinculado aos seis hashes' if reviewed else 'Inspeção ainda pendente'} | {'VERIFIED' if reviewed else 'UNKNOWN'} |
| Certificar equivalência estética a Unreal | Sem benchmark comparável; o critério é visual | UNKNOWN |

## O que mudou

O sofá clássico foi substituído por estrutura contemporânea própria, com almofadas derivadas do ativo detalhado Modern Arm Chair 01, preservando seus UVs e pregas. O couro foi ajustado para caramelo; a manta tem geometria de caída e UV de tecido. Há três assentos e encostos, braços arredondados, costuras e pés metálicos.

As seis cadeiras antigas foram ocultadas e preservadas. Quatro cadeiras novas usam assento e encosto em couro sobre estrutura de aço, mantendo as cabeceiras livres. A mesa original continua na mesma posição. A mesa de centro tem três tábuas, quadro de metal, livros, tigela e arranjo. Madeira, piso e pedra do bar foram revistos. O painel da TV tem cantos com raio no plano da parede, UV próprio e quatro downlights.

As plantas usam geometrias e mapas PBR CC0. Uma folha com UV foi isolada para as pendentes; a calathea usa apenas uma touceira do conjunto original. A iluminação comum em `DESIGN_Iluminacao` combina spots e painéis emissivos de fotografia 3D. Estes painéis são editáveis, emitem pelo lado voltado ao ambiente e ficam fora da câmera/reflexos diretos. Não são luminárias confirmadas do imóvel. O espelho continua refletindo a cena 3D.

## Arquivo, execução e edição

Modelo: `projeto/industrial-v04/casa-industrial-refinada.blend`. Cenas: {', '.join(job['scene'] for job in cfg['jobs'])}. Coleção principal: `DESIGN04`. Pais `DESIGN Sofá contemporâneo`, `DESIGN Mesa de centro` e `DESIGN Cadeira jantar …` permitem mover os móveis. Os materiais `DESIGN …` ficam no Shader Editor; as fontes estão em `EDITAR_Ativos_V04`. O README descreve a edição e os comandos.

Blender {audit['blender_version']}; Cycles/CUDA, Light Tree, AgX, denoise e até {cfg['samples']} amostras adaptativas, limiar {cfg['adaptive_threshold']}. O total registrado para renderizar as seis vistas foi {total_seconds/60:.1f} minutos, incluindo preparação por vista; não é benchmark entre motores. A configuração está em `config/estilo-industrial-v04.json`; o gerador é `scripts/refine_industrial.py`. Ele recusa sobrescrever o modelo de destino.

Recibos: `modelo.json`, `validacao.json`, `recursos-nativos.json`, `previas.json`, `renders.json`, `testes.log` e os logs de geração/renderização. A auditoria independente reabriu o arquivo e conferiu recursos, móveis, câmeras e resolução. Sete testes verificaram o launcher e o download de ativos, incluindo integridade, retomada e proteção de arquivos existentes. Os recursos são [CC0 do Poly Haven](https://polyhaven.com/license), com MD5 do fornecedor e SHA-256 em `assets/industrial-v04/manifesto.json`.

## Comparação e limites

`referencias-e-proposta.jpg` mostra inspiração à esquerda e proposta à direita. `evolucao-v03-v04.jpg` mostra a evolução com enquadramentos diferentes; não é comparação pixel a pixel. A casa é mais profunda do que a composição sugerida na referência. Escada, entrada diagonal, aberturas e aparelhos condicionam o resultado. Não foram deslocados elementos fixos para falsear essa correspondência.

A marcenaria e alguns aparelhos ainda têm simplificações. O jardim do HDRI é ilustrativo. As medidas, detalhes da escada e posições dos banheiros superiores mantêm as incertezas da reconstrução. A proposta é um estudo de interiores, não projeto executivo ou certificação de equivalência visual a Unreal.

A v03 foi preservada como base e comparação. Os rascunhos v04 foram guardados localmente em `historico/rascunhos/industrial-v04/`, fora do Git. O manifesto desta entrega registra arquivos e hashes; publicação é verificada após o commit para evitar autorreferência do SHA.
'''
    (folder/'RELATORIO.md').write_text(report)
    files=[ROOT/cfg['output_blend'],ROOT/cfg['base_blend'],ROOT/'README.md',ROOT/'.gitattributes',ROOT/'config/estilo-industrial-v04.json',ROOT/'config/planta-casa.json']
    files += [ROOT/'scripts'/name for name in ['refine_industrial.py','refined_delivery.py','audit_refined.py','fetch_industrial_v04_assets.py','test_industrial_assets.py','test_blender_launcher.py','run_blender.py','blender_primitives.py','style_industrial.py','photographic_interiors.py','audit_envelope.py']]
    files += [ROOT/path for path in expected]+list(renders.glob('*.jpg'))
    files += [p for p in folder.iterdir() if p.is_file() and p.name!='manifesto.json']
    files += [p for p in (ROOT/'assets').rglob('*') if p.is_file()]
    files += [ROOT/path for path in baseline['references']]
    write(folder/'manifesto.json',{'timestamp_utc':now,'version':cfg['version'],'visual_review_complete':reviewed,
        'files':{str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(set(files))}})
    print('DESIGN_DELIVERY_VERIFIED',len(expected),'renders; visual review:',reviewed)


if __name__=='__main__':main()
