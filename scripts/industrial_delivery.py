"""Validar recibos e produzir a galeria/comparação da proposta industrial."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT=Path(__file__).resolve().parents[1]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reviewed',action='store_true',help='Registrar inspeção visual já realizada dos renders finais')
    args=parser.parse_args()
    cfg=json.loads((ROOT/'config/estilo-industrial-v01.json').read_text())
    reports=ROOT/cfg['report_directory'];renders=ROOT/cfg['render_directory']
    model=json.loads((reports/'modelo.json').read_text());run=json.loads((reports/'renders.json').read_text())
    audit=json.loads((reports/'validacao.json').read_text())
    assert audit['all_passed'] and audit['blend_sha256']==model['blend_sha256']
    assert run['blend_sha256']==model['blend_sha256']==sha(ROOT/cfg['output_blend'])
    assert sha(ROOT/cfg['base_blend'])==model['base_sha256']
    assert run['original_geometry_preserved'] and run['base_preserved'] and not run['preview']
    assert not run['camera_collisions'] and not model['geometry_differences']
    assert run['envelope']['all_passed'] and model['envelope']['all_passed']
    expected={str(Path(cfg['render_directory'])/j['file']) for j in cfg['jobs']}
    assert set(run['outputs'])==expected and len(expected)==7
    for path,meta in run['outputs'].items():
        p=ROOT/path;assert sha(p)==meta['sha256'] and p.stat().st_size==meta['bytes']
        with Image.open(p) as im:assert list(im.size)==cfg['resolution'];im.verify()
    for path,h in model['references'].items():assert sha(ROOT/path)==h
    fontpath=str(ROOT/'assets/fonts/DejaVuSans.ttf')
    font=ImageFont.truetype(fontpath,22);small=ImageFont.truetype(fontpath,17)
    def tile(canvas,path,x,y,w,h):
        with Image.open(path) as source:
            pic=ImageOps.contain(source.convert('RGB'),(w,h))
            canvas.paste(pic,(x+(w-pic.width)//2,y+(h-pic.height)//2))
    labels=[('Sala integrada','sala-integrada.png'),('Sala / entrada','sala-frente.png'),
            ('Cozinha','cozinha.png'),('Cozinha / acesso','cozinha-reversa.png'),
            ('Lazer nos fundos','lazer-fundos.png'),('Quarto dos fundos','quarto-fundos.png'),
            ('Bancada e escritório','quarto-escritorio.png')]
    panel=Image.new('RGB',(1600,1740),'#171b1c');draw=ImageDraw.Draw(panel)
    draw.text((24,18),'CASA • PROPOSTA INDUSTRIAL V01',font=font,fill='#ead6b3')
    for i,(label,file) in enumerate(labels):
        x=(i%2)*800;y=70+(i//2)*415
        draw.text((x+20,y),label,font=font,fill='white');tile(panel,renders/file,x+12,y+35,776,360)
    draw.text((820,1390),'Planta da revisão 10 preservada.',font=small,fill='#ead6b3')
    draw.text((820,1420),'Cimento • aço preto • madeira • couro',font=small,fill='white')
    draw.text((820,1450),'Referências de estilo, sem medidas levantadas.',font=small,fill='white')
    panel.save(renders/'painel-ambientes.jpg',quality=92)
    pairs=[('Sala • materiais e iluminação','01-cena-final-menos-warn.png','sala-integrada.png'),
           ('Cozinha • linguagem integrada da referência','01-cena-final-menos-warn.png','cozinha.png'),
           ('Lazer • bar e cobertura','02-bar-fundo.png','lazer-fundos.png'),
           ('Quarto • bancada e detalhes de escritório','escritorio2.png','quarto-escritorio.png'),
           ('Mesa • madeira e tábuas','03-mesa-jantar.png','sala-integrada.png')]
    comparison=Image.new('RGB',(1600,2240),'#171b1c');draw=ImageDraw.Draw(comparison)
    draw.text((22,16),'REFERÊNCIAS DE ESTILO  |  PROPOSTA NA PLANTA EXISTENTE',font=font,fill='#ead6b3')
    for i,(label,ref,file) in enumerate(pairs):
        y=65+i*430;draw.text((20,y),label,font=font,fill='white')
        tile(comparison,ROOT/cfg['references']/ref,12,y+38,776,375)
        tile(comparison,renders/file,812,y+38,776,375)
    comparison.save(renders/'referencias-e-proposta.jpg',quality=92)
    stamp=dt.datetime.now(dt.timezone.utc).isoformat()
    if args.reviewed:
        review={'timestamp_utc':stamp,'reviewer':'Codex','scope':'Inspeção visual das sete imagens finais e comparação com as quatro referências; enquadramento, materiais, iluminação e móveis visíveis',
                'blend_sha256':model['blend_sha256'],'render_sha256':{p:v['sha256'] for p,v in run['outputs'].items()},
                'findings':['Cimento, aço escuro, madeira e couro presentes nos ambientes pedidos','Arquitetura mantida: o estilo adapta-se à reconstrução existente','Quarto mantém beliche e a bancada, com monitores e prateleiras','Mobiliário e texturas simplificados em relação às imagens de inspiração']}
        (reports/'revisao-visual.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
    reviewpath=reports/'revisao-visual.json';reviewed=reviewpath.exists()
    if reviewed:
        review=json.loads(reviewpath.read_text());assert review['blend_sha256']==model['blend_sha256']
        assert review['render_sha256']=={p:v['sha256'] for p,v in run['outputs'].items()}
    report=f'''# Proposta industrial v01

UTC: {stamp}

Sala/jantar, cozinha, lazer nos fundos e quarto dos fundos receberam uma proposta de acabamento inspirada nas quatro imagens de `referencias-estilo-industrial/`. O Blender industrial é uma variante separada da reconstrução da revisão 10. As dimensões permanecem estimadas.

| Obrigação | Recibo observado | Estado |
| --- | --- | --- |
| Arquitetura, aberturas e escada preservadas | {model['geometry_objects_preserved']} hashes de malhas/curvas, transformações locais, pais e modificadores herdados iguais antes/depois; zero diferenças ao reabrir | VERIFIED |
| Encaixe dos pavimentos | Três verificações dos vértices das lajes e faces posteriores, no arquivo salvo | VERIFIED |
| Quatro ambientes renderizados | Sete PNGs, com reconciliação exata dos nomes, dimensões e SHA-256 | VERIFIED |
| Editável sincronizado aos renders | Reabertura em outro processo; SHA-256 do `.blend` antes/depois da renderização igual | VERIFIED |
| Recursos e cenas editáveis | Nove verificações independentes ao reabrir o Blender em `validacao.json` | VERIFIED |
| Reconstrução e imagens inspiradoras intactas | SHA-256 do modelo base e das quatro referências preservados | VERIFIED |
| Câmeras fora de sólidos | Nenhuma interseção detectada com caixas locais das malhas visíveis | VERIFIED |
| Conferência visual final | {'revisao-visual.json vinculado aos hashes finais' if reviewed else 'Pendente de inspeção final'} | {'VERIFIED' if reviewed else 'UNKNOWN'} |
| Medidas do imóvel e dimensionamento construtivo | Sem levantamento novo | UNKNOWN |

## Decisões de estilo

- **Sala/jantar:** cimento cinza, couro caramelo, rack escuro com tampo de madeira, mesa de centro e tapete. A mesa de jantar recebe três tábuas e quatro pés de madeira; pendentes e trilhos complementam a luz ambiente. O espelho existente fica livre de prateleiras.
- **Cozinha:** marcenaria grafite, revestimento escuro, metais pretos, detalhes de madeira e luz de bancada. Bancadas, pia, fogão, geladeira, janelas e acessos mantêm suas posições.
- **Lazer:** bar em nogueira e metal, revestimento de pedra oxidada, prateleiras iluminadas, taças, cerâmica e arandelas. A cobertura acompanha a geometria existente; as travessas adicionais são elementos da proposta.
- **Quarto dos fundos:** beliche com estrutura escura e estrados de madeira, linho neutro, azul petróleo na parede da bancada, prateleiras, monitores, cadeira e iluminação de trabalho. A inspiração de escritório não transforma o ambiente em outro cômodo.

## Organização e reprodução

Editável: `arquivos/versoes-anteriores-2026-11-14/projeto/industrial-v01/casa-industrial.blend`. Cenas: `IND_…`. Novas peças: coleções `IND_Decor_…`. Materiais: `IND …`. As quatro referências acompanham o repositório, sem serem necessárias para renderizar; os revestimentos são procedurais e ajustáveis. As 26 fotos originais únicas herdadas continuam empacotadas. A configuração `config/estilo-industrial-v01.json` define câmeras, versão e saídas; cores e texturas ficam nos materiais do Blender e na função `materials()` do gerador.

O arquivo base e a geometria herdada ficam preservados. Na variante, o pendente de anéis, o pé central da mesa e a TV antiga do quarto ficam ocultos no render para receber as peças da proposta, sem excluir os objetos. A apresentação não é uma reprodução literal das imagens: proporções, mobiliário simplificado e incidência de luz obedecem ao modelo da casa.

Os renders foram produzidos pelo Blender em Cycles/CPU, 96 amostras, AgX e denoise, em 1600 × 1000. O log da execução está em `renderizacao.log`. Houve uma rodada de prévias e refinamento de câmera, cimento, madeira, iluminação e posição das prateleiras; as prévias iniciais estão preservadas localmente em `arquivos/historico/rascunhos/industrial-v01/rodada01/`.

Os binários antigos e rascunhos continuam no disco, ignorados pelo Git. Apenas modelos/renders atuais, referências, código, configuração e documentos/recibos históricos são publicados. A comprovação do push fica no SHA retornado por `git ls-remote origin refs/heads/main`, conferido após publicar; este relatório não antecipa esse resultado.

## Limites

O modelo é um estudo visual com móveis simplificados, não um projeto executivo. Persistem as incertezas de escala, banheiros superiores e degraus já registradas na revisão 10. As referências inspiram materiais e iluminação; não comprovam a arquitetura nem o mobiliário real da casa. A conferência geométrica não substitui levantamento nem cálculo estrutural.
'''
    (reports/'RELATORIO.md').write_text(report)
    paths=[ROOT/cfg['base_blend'],ROOT/cfg['output_blend'],ROOT/'config/planta-casa.json',ROOT/'config/estilo-industrial-v01.json',ROOT/'scripts/style_industrial.py',ROOT/'scripts/audit_industrial.py',ROOT/'scripts/industrial_delivery.py',ROOT/'README.md',ROOT/'.gitignore',*sorted((ROOT/cfg['references']).glob('*.png')),*[ROOT/p for p in expected],renders/'painel-ambientes.jpg',renders/'referencias-e-proposta.jpg',*sorted(reports.glob('*.json')),*sorted(reports.glob('*.log')),reports/'RELATORIO.md']
    paths=list(dict.fromkeys(p for p in paths if p.name!='manifesto.json'))
    manifest={'timestamp_utc':stamp,'version':cfg['version'],'visual_review_complete':reviewed,'files':{str(p.relative_to(ROOT)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in paths}}
    (reports/'manifesto.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print('INDUSTRIAL_DELIVERY_VERIFIED',len(expected),'renders; visual review:',reviewed)


if __name__=='__main__':main()
