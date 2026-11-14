"""Galeria, comparações e caderno da reconstrução atual; sem alterar renders nativos."""
import datetime as dt
import html
import json
from pathlib import Path
import shutil
import sys
from PIL import Image,ImageOps,ImageDraw,ImageFont
import current_photoreal_data as data

ROOT,CFG,REPORT=data.ROOT,data.CFG,data.REPORT
OUT=ROOT/CFG['render_directory']
PAIRS={
 'sala-foto':'sala5.webp','sala-fundos':'sala2.webp','cozinha':'cozinha1.webp','bar':'area1.webp','lavanderia':'lavanderia1.webp',
 'suite':'quartosuite1.webp','suite-reversa':'quartosuite2.webp','quarto-frente':'quartobranco1.webp','quarto-branco-armario':'quartobranco2.webp',
 'quarto-fundos':'quartoazul2.webp','quarto-azul-bancada':'quartoazul1.webp','escada-superior':'escada1.webp','lavabo':'lavabo1.webp',
 'banheiro-social':'banheiro2.webp','banheiro-suite':'suite1.webp','fachada-frontal':'exterior2.webp'}

def font(size):
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',size)

def archive():
    target=ROOT/'arquivos/historico/estudos/atual-v01/renders'
    if target.exists():return
    shutil.copytree(OUT,target)
    files=[{'file':p.relative_to(ROOT).as_posix(),'sha256':data.sha(p)} for p in sorted(target.rglob('*')) if p.is_file()]
    (target.parent/'ARQUIVAMENTO.json').write_text(json.dumps({'reason':'Estado anterior à reconstrução atual fiel v02','files':files},ensure_ascii=False,indent=2)+'\n')
    print('CURRENT2_ARCHIVED',len(files),flush=True)

def comparisons(model):
    dest=OUT/'04-comparacoes';dest.mkdir(exist_ok=True)
    for old in dest.iterdir():
        if old.is_file():old.unlink()
    rows=[]
    for job in model['jobs']:
        photo=PAIRS.get(job['id'])
        if not photo:continue
        canvas=Image.new('RGB',(1920,860),'#171d1e');d=ImageDraw.Draw(canvas)
        for i,(p,label) in enumerate([(ROOT/'referencias-originais'/photo,'FOTO ORIGINAL · '+photo),(ROOT/job['file'],'RECONSTRUÇÃO 3D · '+job['id'])]):
            im=Image.open(p).convert('RGB');im.thumbnail((930,705));x=15+i*960+(930-im.width)//2;y=78+(705-im.height)//2;canvas.paste(im,(x,y));d.text((25+i*960,25),label,fill='#e9eeeb',font=font(21))
        d.text((25,807),'Enquadramentos aproximados por observação; móveis e anexos sem medição em campo.',fill='#bbc4bf',font=font(19))
        p=dest/(job['id']+'.jpg');canvas.save(p,quality=92);rows.append({'id':job['id'],'photo':'referencias-originais/'+photo,'file':p.relative_to(ROOT).as_posix(),'sha256':data.sha(p)})
    (REPORT/'comparacoes.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');return rows

def gallery(model,pairs):
    thumbs=OUT/'06-galerias/miniaturas';thumbs.mkdir(parents=True,exist_ok=True)
    cards=[]
    for j in model['jobs']:
        im=Image.open(ROOT/j['file']).convert('RGB');im.thumbnail((960,720));im.save(thumbs/(j['id']+'.jpg'),quality=89)
        href=Path(j['file']).relative_to(CFG['render_directory']).as_posix()
        cards.append(f'<article id="{j["id"]}"><a href="{href}" target="_blank"><img loading="lazy" src="06-galerias/miniaturas/{j["id"]}.jpg" alt="{html.escape(j["title"])}"></a><h3>{html.escape(j["title"])}</h3><a href="{href}" download>PNG nativo · 3840 × 2880</a></article>')
    # As comparações usam os arquivos gerados, com margens para preservar a proporção das fotos.
    comps=''.join(f'<article><a target="_blank" href="04-comparacoes/{p["id"]}.jpg"><img loading="lazy" src="04-comparacoes/{p["id"]}.jpg" alt="Foto e 3D: {p["id"]}"></a><h3>{p["id"]}</h3></article>' for p in pairs)
    page='''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Residência 07 · Casa atual pelas fotos</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#121a1c;color:#eef2ef;font:16px/1.55 system-ui,sans-serif}main{max-width:1600px;margin:auto;padding:32px}h1{font-size:clamp(28px,4vw,52px);line-height:1.1;margin:20px 0}p{max-width:950px;color:#c2cbc7}a{color:#c7dbbd;text-underline-offset:4px}nav{display:flex;gap:24px;flex-wrap:wrap;margin:24px 0 48px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,380px),1fr));gap:28px}article{background:#1b2527;padding:12px;border:1px solid #334244;border-radius:12px}article img{width:100%;height:auto;display:block;border-radius:6px}h3{font-size:17px;font-weight:550;margin:16px 4px 8px}article>a:last-child{font-size:14px;display:block;margin:6px 4px 10px}section{margin:60px 0}.note{border-left:3px solid #b5cda9;padding:12px 20px;background:#1b2527}footer{color:#a7b3af;font-size:13px;margin:64px 0 16px}a:focus-visible{outline:3px solid #e3cc8b;outline-offset:5px}@media(max-width:600px){main{padding:20px}.grid{gap:18px}}
</style><main><p>RESIDÊNCIA 07 / ESTADO ATUAL / RECONSTRUÇÃO V02</p><h1>A casa atual, reconstruída pelas fotos</h1><p>Sofá e cadeiras cinza, painel branco com LEDs, marcenaria mel, cortinas, cozinha, bar e dormitórios com os elementos observados nas referências. Clique nas imagens para abrir os PNGs nativos.</p><nav><a href="#imagens">26 vistas 3D</a><a href="#comparacoes">Fotos × modelo</a><a href="00-cadernos/caderno-atual.pdf">Caderno PDF</a><a href="../../projeto/atual/casa-07-atual-fiel.blend">Modelo Blender</a></nav><p class="note">A arquitetura usa a base oficial da residência 07 e as alterações já informadas. Dimensões dos móveis e anexos são aproximadas pelas fotos; esta visualização não substitui um levantamento em campo. A geladeira do bar permanece conforme a casa fotografada.</p><section id="imagens"><h2>Vistas da casa</h2><div class="grid">'''+''.join(cards)+'''</div></section><section id="comparacoes"><h2>Comparações com as referências</h2><p>As fotografias e o modelo têm enquadramentos aproximados; abra cada par para conferir o mobiliário e os acabamentos.</p><div class="grid">'''+comps+'''</div></section><footer>Cycles / OptiX · PNG 3840 × 2880 · recursos empacotados no modelo. Fotografias originais preservadas. Modelo anterior guardado no histórico. Sem teste executado no Unreal.</footer></main></html>'''
    (OUT/'galeria.html').write_text(page)
    panel=Image.new('RGB',(1920,((len(model['jobs'])+3)//4)*390),'#171d1e');d=ImageDraw.Draw(panel)
    for i,j in enumerate(model['jobs']):
        im=Image.open(thumbs/(j['id']+'.jpg'));im.thumbnail((470,350));x=i%4*480;y=i//4*390;panel.paste(im,(x,y));d.text((x+7,y+357),j['id'],font=font(16),fill='white')
    panel.save(OUT/'06-galerias/painel-geral.jpg',quality=92)

def pdf(model,pairs):
    import fitz
    doc=fitz.open();W,H=960,720
    page=doc.new_page(width=W,height=H);page.draw_rect(page.rect,color=None,fill=(.07,.10,.11))
    page.insert_text((50,85),'RESIDENCIA 07 / CASA ATUAL',fontsize=16,color=(.8,.85,.79))
    page.insert_textbox(fitz.Rect(50,135,900,290),'Reconstrucao pelas fotos\nRevisao fiel v02',fontsize=38,color=(.95,.96,.94))
    page.insert_textbox(fitz.Rect(50,350,890,620),'Arquitetura da residencia 07 com o fundo aberto e a divisao posterior ja informados. Mobilia, cortinas, revestimentos e eletrodomesticos reconstruidos por observacao das fotos originais.\n\nAs medidas dos moveis e anexos continuam aproximadas. Cotas oficiais da arquitetura preservadas. Renderizacao Cycles/OptiX; sem comparacao executada no Unreal.',fontsize=18,lineheight=1.5,color=(.77,.81,.79))
    for j in model['jobs']:
        page=doc.new_page(width=W,height=H);page.insert_text((26,30),j['title'].replace('·','/'),fontsize=16)
        im=Image.open(ROOT/j['file']).convert('RGB');im.thumbnail((2400,1800));import io
        stream=io.BytesIO();im.save(stream,format='JPEG',quality=92);page.insert_image(fitz.Rect(20,48,940,694),stream=stream.getvalue(),keep_proportion=True)
    for pair in pairs:
        page=doc.new_page(width=W,height=H);page.insert_text((26,30),'FOTO ORIGINAL / RECONSTRUCAO 3D - '+pair['id'],fontsize=16)
        page.insert_image(fitz.Rect(20,70,940,675),filename=str(ROOT/pair['file']),keep_proportion=True)
    # Plantas cotadas anteriores permanecem como base documental das dimensões.
    for file in ['planta-atual-terreo.pdf','planta-atual-superior.pdf']:
        source=fitz.open(OUT/'01-plantas'/file);doc.insert_pdf(source);source.close()
    dest=OUT/'00-cadernos/caderno-atual.pdf';dest.parent.mkdir(exist_ok=True);doc.save(dest,garbage=4,deflate=True);pages=len(doc);doc.close();return pages

def main():
    if '--archive' in sys.argv:archive();return
    m=json.loads((REPORT/'modelo.json').read_text());renders=json.loads((REPORT/'renders.json').read_text())
    assert {r['id'] for r in renders}=={j['id'] for j in m['jobs']}
    assert all(r['blend_sha256']==m['blend_sha256'] and data.sha(ROOT/r['file'])==r['sha256'] for r in renders)
    pairs=comparisons(m);gallery(m,pairs);pages=pdf(m,pairs)
    text='# Casa atual / reconstrução fiel v02\n\n[Abra a galeria](galeria.html) · [Caderno PDF](00-cadernos/caderno-atual.pdf) · [Modelo 3D](../../'+m['blend']+')\n\n26 imagens nativas 3840 × 2880, com novas comparações entre as fotos e o modelo. O mobiliário e os acabamentos foram reconstruídos pelas referências: sofá e cadeiras cinza, cortinas, painel de TV com LEDs, rack mel/branco, cozinha detalhada, bar com quatro cadeiras altas, lavanderia e quartos com os papéis de parede observados.\n\nAs esquadrias que perderam a posição na cópia anterior foram restauradas a partir do modelo oficial da residência 07. A geometria estrutural e as alterações dos fundos permanecem preservadas. As dimensões dos móveis e anexos continuam aproximadas pelas fotos, sem levantamento em campo. A geladeira do bar atual foi mantida conforme as referências; a remoção pedida era das propostas industriais.\n\nO estado anterior dos renders foi guardado em `arquivos/historico/estudos/atual-v01`. O arquivo base anterior não foi modificado. As plantas vetoriais cotadas mantêm a base documental anterior; as imagens 3D mostram a nova reconstrução visual.\n\nRenderização Cycles/OptiX. Unreal não instalado: sem alegação de teste comparativo.\n\n[Recibo do modelo](../../relatorios/atual/modelo.json) · [Validação nativa](../../relatorios/atual/validacao-nativa.json) · [Conferência da entrega](../../relatorios/atual/entrega-validacao.json)\n'
    (OUT/'LEIA-ME.md').write_text(text)
    receipt={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'model_sha256':m['blend_sha256'],'renders':len(renders),'comparisons':len(pairs),'pdf_pages':pages,'artifacts':[{'file':p.relative_to(ROOT).as_posix(),'sha256':data.sha(p)} for p in sorted(OUT.rglob('*')) if p.is_file()]}
    (REPORT/'entrega.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print('CURRENT2_DELIVERY_OK',len(renders),'renders',len(pairs),'pairs',pages,'pages',flush=True)

if __name__=='__main__':main()
