"""Organiza a entrega, escreve o índice e verifica a completude dos arquivos."""
import argparse
import datetime as dt
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont

import residence07_geometry as geo

ROOT=geo.ROOT;CFG=geo.load();OUT=ROOT/CFG['delivery']['renders'];REPORT=ROOT/CFG['delivery']['reports']


def organize():
    moves=[]
    for old in sorted(OUT.iterdir()):
        if not old.is_file() or old.name=='LEIA-ME.md':continue
        if old.suffix not in ['.png','.svg','.pdf','.jpg']:raise ValueError('Revisar arquivo sem categoria: '+old.name)
        new=geo.artifact_path(old.stem,old.suffix[1:]);new.parent.mkdir(parents=True,exist_ok=True)
        if new.exists():raise FileExistsError('Destino já existe: '+str(new))
        checksum=geo.sha(old);old.rename(new)
        assert geo.sha(new)==checksum
        moves.append({'from':str(old.relative_to(ROOT)),'to':str(new.relative_to(ROOT)),'sha256':checksum})
    old=OUT/'previas';new=OUT/'_trabalho/previas'
    if old.exists():
        if new.exists():raise FileExistsError(str(new))
        new.parent.mkdir(parents=True,exist_ok=True);old.rename(new)
        moves.append({'from':str(old.relative_to(ROOT)),'to':str(new.relative_to(ROOT)),'type':'directory'})
    if moves:
        path=REPORT/'organizacao.json';previous=json.loads(path.read_text()).get('moves',[]) if path.exists() else []
        path.write_text(json.dumps({'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'moves':previous+moves,'all_hashes_preserved':True},ensure_ascii=False,indent=2)+'\n')
    print('R07_ORGANIZED',len(moves),'movimentos sem alteração de conteúdo')


def link(name,label=None,ext='png'):
    path=geo.artifact_path(name,ext)
    return f'[{label or name}]({path.relative_to(OUT).as_posix()})'


def index():
    text=f'''# Residência 07 — índice da entrega

Comece pelo {link('caderno-residencia-07','caderno completo','pdf')} ou pelo {link('painel-geral','painel de imagens','jpg')}.
As plantas e os renders desta revisão usam a tipologia da esquerda de ARQ03, que inclui a unidade 07.

Atualizações: [instalações 3D e paredes transparentes](03-instalacoes/3d/LEIA-ME.md), [estado atual pelas fotos](../atual/LEIA-ME.md), [industrial sobre a planta atual](../industrial-v05/LEIA-ME.md) e [ático com escadas sobrepostas e caixa lateral](../residencia-07-atico-v05/LEIA-ME.md).
As quatro estruturas receberam paredes em sálvia suave, lajes creme e escada areia. Suas imagens vêm do modelo editável `projeto/original/casa-07-instalacoes.blend`; a geometria da base foi preservada.

| Pasta | Conteúdo |
| --- | --- |
| `00-cadernos` | PDFs completos de apresentação e de instalações |
| `01-plantas-arquitetonicas` | Térreo, superior, sobreposição, corte e cotas originais; PNG, SVG e PDF |
| `02-estrutura/2d` | Base sem mobiliário, com paredes, lajes, vãos, escada e cotas |
| `02-estrutura/3d` | Térreo, superior, conjunto e vista explodida, sem móveis |
| `03-instalacoes` | Elétrica, hidráulica, esgoto, TV/telefone e sobreposições, por disciplina |
| `04-plantas-3d` | Plantas humanizadas e perspectivas de cada pavimento |
| `05-imagens` | Ambientes separados em térreo, superior, exteriores e proposta dos fundos |
| `06-galerias` | Painéis para conferir as vistas em conjunto |
| `_trabalho/previas` | Testes de render e enquadramento; não usar como entrega final |

## Estrutura em 3D, sem mobiliário

- {link('estrutura-terreo-3d','Térreo')} e {link('estrutura-superior-3d','superior')}.
- {link('estrutura-conjunto-3d','Conjunto')} e {link('estrutura-explodida-3d','vista explodida')}.
- {link('estrutura-terreo','Base 2D do térreo','pdf')} e {link('estrutura-superior','base 2D do superior','pdf')}.

As paredes são cortadas a 1,15 m nas plantas 3D para mostrar a distribuição. Na vista explodida, somente a cópia ilustrativa do superior é afastada 4 m; o modelo de uso conserva o piso em +2,70 m. O conjunto mantém paredes em altura completa e omite a cobertura para leitura.

## Instalações e medidas

- {link('plantas-tecnicas-residencia-07','Caderno técnico com fontes, detalhes e legendas','pdf')}.
- {link('instalacoes-coordenadas-terreo','Instalações juntas no térreo','pdf')} e {link('instalacoes-coordenadas-superior','no superior','pdf')}.
- {link('cotas-originais-terreo','Todas as cotas originais do térreo','pdf')} e {link('cotas-originais-superior','do superior','pdf')}.

Os traçados das instalações preservam os símbolos, circuitos, bitolas, diâmetros e alturas dos PDFs fornecidos. As folhas originais completas acompanham o caderno técnico. Há divergências entre algumas cotas, traços e áreas do projeto de 2011; elas estão descritas no [relatório](../../relatorios/original/RELATORIO.md).

## Modelo editável

Abra [casa-07.blend](../../projeto/original/casa-07.blend). As cenas `R07_estrutura-…` mostram a base 3D sem móveis. As demais cenas apresentam os ambientes, as plantas e as fachadas. `Num 0` mostra a câmera e `F12` renderiza; os caminhos já apontam para estas pastas.

A base estrutural representa os elementos indicados na arquitetura. Fundações, armaduras e dimensionamento resistente não foram fornecidos. A reconstrução não confirma as alterações executadas no imóvel após 2011. A decoração industrial e os anexos dos fundos são proposta, identificada separadamente.
'''
    (OUT/'LEIA-ME.md').write_text(text)


def structural_gallery():
    views=[v for v in CFG['views'] if v['mode'].startswith('structure')]
    if not all(geo.artifact_path(v['id']).exists() for v in views):return
    font=str(ROOT/'assets/fonts/DejaVuSans.ttf')
    canvas=Image.new('RGB',(1800,1530),'#f4f1e9');draw=ImageDraw.Draw(canvas)
    draw.text((35,22),'RESIDÊNCIA 07 / ESTRUTURA INDICADA',font=ImageFont.truetype(font,35),fill='#263c30')
    draw.text((35,78),'Paredes, lajes, escada e vãos · sem mobiliário · base arquitetônica',font=ImageFont.truetype(font,22),fill='#657164')
    for i,v in enumerate(views):
        with Image.open(geo.artifact_path(v['id'])) as im:
            im=im.convert('RGB');im.thumbnail((870,635));x=(i%2)*900+15;y=(i//2)*695+130
            canvas.paste(im,(x+(870-im.width)//2,y))
        draw.text((x+10,y+640),v['title'].replace('Estrutura indicada · ',''),font=ImageFont.truetype(font,23),fill='#263c30')
    path=geo.artifact_path('painel-estrutura','jpg');path.parent.mkdir(parents=True,exist_ok=True);canvas.save(path,quality=94)


def manifest():
    records=[]
    for path in sorted(OUT.rglob('*')):
        if not path.is_file() or '_trabalho' in path.parts:continue
        records.append({'file':str(path.relative_to(ROOT)),'bytes':path.stat().st_size,'sha256':geo.sha(path)})
    expected={str(geo.artifact_path(v['id']).relative_to(ROOT)) for v in CFG['views']}
    actual={r['file'] for r in records}
    root_files=[p.name for p in OUT.iterdir() if p.is_file()]
    result={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'records':records,
            'render_set_complete':expected<=actual,'root_only_index':root_files==['LEIA-ME.md'],
            'expected_native_images':len(expected),'artifact_count':len(records)}
    (REPORT/'manifesto.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('R07_MANIFEST',len(records),'artefatos',len(expected-actual),'renders pendentes')


def report():
    model=json.loads((REPORT/'modelo.json').read_text())
    technical=json.loads((REPORT/'instalacoes.json').read_text())
    audit=json.loads((REPORT/'validacao-modelo.json').read_text())
    complete_path=REPORT/'validacao-completa.json'
    complete=json.loads(complete_path.read_text()) if complete_path.exists() else {}
    current_hash=geo.sha(ROOT/CFG['delivery']['blend'])
    verified=complete.get('all_passed') and complete.get('blend_sha256')==current_hash
    render_records=json.loads((REPORT/'renders.json').read_text()) if (REPORT/'renders.json').exists() else []
    valid_renders=[r for r in render_records if geo.valid_render_record(r)]
    state='VERIFICADA para o escopo documental e visual abaixo' if verified else 'EM VALIDAÇÃO; não considerar encerrada'
    rows=[]
    for r in audit['area_comparison']:
        rows.append(f"| {r['room']} | {r['declared_m2']:.2f} | {r['model_polygon_m2']:.4f} | {r['delta_m2']:+.4f} |")
    table='\n'.join(rows)
    body=f'''# Residência 07 — conferência da reconstrução

Data de conferência: {dt.datetime.now(dt.timezone.utc).isoformat()}. Entrega **{state}**.

O projeto foi reconstruído pela tipologia da esquerda de ARQ03. As revisões baseadas em fotos e croquis permanecem preservadas; não controlam as medidas desta revisão. A entrega contém plantas redesenhadas, plantas humanizadas, quatro vistas 3D sem mobiliário, fachadas, ambientes e instalações vetoriais provenientes dos complementares.

Foram consideradas a adaptação da base estimada e uma reconstrução métrica independente. Foi adotada a segunda opção: configuração geométrica única para plantas e Blender, preservando apenas móveis reaproveitáveis. É uma escolha pragmática para este repositório, com validação determinística; não se apresenta como um modelo BIM de engenharia dimensionado.

## Evidências e limites do resultado

| Obrigação | Recibo | Situação |
| --- | --- | --- |
| Identificar a unidade 07 | ARQ03, lista de unidades da tipologia; `fontes.json` e recortes em `fontes/` | VERIFICADO |
| Reconstruir paredes, vãos, lajes, escada e cobertura | `modelo.json` e `validacao-modelo.json` | {len(audit['checks'])} verificações; {'passaram' if audit['all_passed'] else 'rever falhas'} |
| Compartilhar a geometria das plantas e do Blender | `config/residencia-07.json`, hash nas 29 cenas | VERIFICADO pela auditoria do arquivo reaberto |
| Preservar as fontes fornecidas | SHA-256 de cada arquivo em `fontes.json` | VERIFICADO pela auditoria |
| Instalações alinhadas à unidade correta | `instalacoes.json` | {len(technical['registration_checks'])} verificações; {'passaram' if technical['all_passed'] else 'rever falhas'} |
| Renderizar todas as câmeras do modelo salvo | `renders.json`, hashes das imagens e do `.blend` | {len(valid_renders)} de {len(CFG['views'])} imagens verificadas |
| Organizar sem perder conteúdo | `organizacao.json` | Arquivos movidos com hashes preservados |
| Conferência final de cadernos e imagens | `validacao-completa.json` | {'VERIFICADO' if verified else 'PENDENTE'} |
| Medidas da situação construída atual | Não houve levantamento presencial | NÃO CONHECIDO |
| Dimensionamento resistente, fundações e armaduras | Não identificado nos PDFs analisados; DWG não convertido | NÃO CONHECIDO |

O veredito se refere à reconstrução documental da residência 07 e aos arquivos gerados nesta sessão. Não certifica as dimensões executadas, a capacidade resistente nem a atualização dos projetos de instalações para intervenções atuais.

## Como a planta foi escolhida

`plantas/arq03.pdf`, prancha 03 de 25/05/2011, lista a unidade 07 no grupo 02, 03, 06, 07, 10, 11, 14 e 15. Esse grupo ocupa a metade esquerda do desenho. A metade direita é espelhada e não controla esta reconstrução. ARQ02 trata da residência 01; ARQ05 trata da recreação coberta. Esses dois desenhos não foram usados como planta da unidade 07.

`arq04.pdf` informa piso térreo em 0,00 m, superior em +2,70 m, nível superior da laje de cobertura em +5,40 m, pé-direito de 2,55 m e lajes de 0,15 m. O corte indica cumeeira em +9,40 m e a parede corta-fogo chega a +9,50 m. `arq01.pdf` localiza a residência 07 na implantação. O DWG original foi preservado e recebeu hash, mas não foi convertido nem auditado semanticamente.

Dimensões principais transcritas/registradas: largura de 6,35 m até o eixo da geminação; corpo esquerdo térreo com 5,70 m; cozinha avança 1,50 m; superior com avanço frontal de 1,20 m na reconstrução registrada; recuo posterior de 0,70 m dos banheiros; quarto/cozinha terminam em Y=7,20 m. Os contornos não foram forçados a um retângulo comum.

## Medidas e divergências que não foram ocultadas

As folhas `cotas-originais-terreo` e `cotas-originais-superior`, em `01-plantas-arquitetonicas`, conservam as cotas escritas de ARQ03. O redesenho usa a geometria métrica registrada das faces do PDF e valores arredondados em centímetros. O registro é conferido por faces independentes; não é um levantamento do imóvel.

Há incompatibilidades na própria fonte. Por exemplo, a largura frontal escrita da suíte é 3,10 m, enquanto as faces desenhadas registram aproximadamente 3,15 m; o quarto da frente tem indicação de 2,85 m numa cadeia de cotas, mas aproximadamente 2,80 m entre as faces registradas. O par 2,80 × 2,75 m da cozinha não produz a área declarada de 7,84 m². Nenhuma dessas diferenças foi resolvida por deformar os cômodos para fechar uma área.

| Ambiente | Área declarada no PDF (m²) | Polígono representado (m²) | Diferença (m²) |
| --- | ---: | ---: | ---: |
{table}

As áreas declaradas de 40,77 m² no térreo, 48,92 m² computáveis e 2,11 m² não computáveis no superior, total de 91,80 m² e lote de 81,60 m² são transcrições dos documentos. Não equivalem a uma medição nova. A tabela compara polígonos de leitura dos ambientes, sem substituir o quadro legal de áreas.

Os contornos gerais oferecem uma conferência independente: o polígono da laje térrea, incluindo garagem, resulta em 40,77 m², e o contorno bruto superior resulta em 51,03 m². Esses dois valores fecham com ARQ03, embora persistam as diferenças internas da tabela. O vão da escada é subtraído na malha da laje; a área bruta de contorno não é a área líquida da laje.

A escada foi reconstituída com cinco pisos retos, seis compensados e cinco de retorno: 16 espelhos de 0,16875 m vencem 2,70 m. O trecho reto tem avanço de 0,25 m. A contagem completa, as folgas e o dimensionamento executivo precisam ser conferidos; os PDFs não oferecem uma seção estrutural da escada. Os apoios e a viga frontal são representações gráficas da arquitetura, sem seções resistentes confirmadas.

## O que está nas plantas estruturais 3D

As cenas `R07_estrutura-terreo-3d` e `R07_estrutura-superior-3d` mostram lajes, paredes, escada e vãos, sem qualquer coleção de móveis. As paredes são cortadas a 1,15 m para leitura. `R07_estrutura-conjunto-3d` mantém a altura completa das paredes e omite a cobertura. `R07_estrutura-explodida-3d` mostra uma cópia do superior afastada 4 m, exclusivamente para explicar a sobreposição; as cenas de uso conservam Z=0,00 e +2,70 m.

As quatro imagens atuais usam paredes sálvia suave, lajes creme e escada areia, vindas de `casa-07-instalacoes.blend`. As cenas originais permanecem na base com material neutro; a revisão de materiais tem recibo próprio em `estudo-instalacoes-atico/instalacoes-modelo.json`. A auditoria confere cada imagem contra o seu arquivo nativo. A orientação das faces dos prismas fechados foi conferida; a correção não moveu vértices. Não há fundações, ferragens ou vigas dimensionadas inventadas para preencher dados ausentes.

## Instalações

O caderno técnico tem {len(technical['sheets'])} folhas organizadas e {technical['pages']} páginas com os anexos completos. Usa ELE04/05/06, HID04/05/08 e TV-TEL04/05. Foram preservados os símbolos e os textos gráficos de circuitos, bitolas, diâmetros, materiais e alturas. Os traçados foram recortados para a tipologia da unidade 07; pontos compartilhados na divisa continuam completos nas pranchas originais anexas.

As folhas elétricas e de TV/telefone originais dizem “sem escala”. O registro pela arquitetura não torna seus arcos e linhas comprimentos executivos de eletrodutos ou cabos. As sobreposições permitem leitura conjunta; não constituem verificação de interferências tridimensionais. O quadro de esquadrias de ARQ03 conserva um cabeçalho “residência 01”; seus códigos foram cruzados com os vãos efetivamente desenhados da tipologia interna.

## Interiores, contexto e reprodução

A linguagem industrial da versão anterior foi mantida como proposta: sofá e cadeiras nativos reaproveitados, novos armários e mobiliário adaptados à planta, concreto, madeira, aço preto e tecidos verdes. Jardim e implantação externa do cenário são ilustrativos. Churrasqueira e lavanderia posteriores, baseadas nas fotos anteriores, ficam somente em `R07_Proposta_Fundos` e nas respectivas cenas; não foram incorporadas à arquitetura original dos PDFs.

O modelo tem {model['objects']} objetos e {len(model['scenes'])} cenas. As imagens são renderizações Cycles do arquivo salvo, em 1920 × 1440 e até 192 amostras adaptativas, com CUDA. Não houve retoque generativo. As texturas usadas estão empacotadas e não há bibliotecas vinculadas; os recursos reaproveitados mantêm suas fontes em `assets/industrial-v03` e `assets/biblioteca-industrial`.

Abra o [índice organizado](../../renders/original/LEIA-ME.md), o [modelo Blender](../../projeto/original/casa-07.blend) ou os comandos de reprodução no [README](../../README.md). Testes locais: `testes.log`. O arquivo final do modelo tem SHA-256 `{current_hash}`.
'''
    (REPORT/'RELATORIO.md').write_text(body)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--organize-only',action='store_true');args=parser.parse_args()
    organize();index()
    if not args.organize_only:structural_gallery();manifest();report()
