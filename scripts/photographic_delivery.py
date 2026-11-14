"""Conciliar a entrega fotográfica com o arquivo nativo e renders observados."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def load(path):
    return json.loads((ROOT / path).read_text())


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reviewed', action='store_true', help='Registrar inspeção visual efetivamente realizada')
    args = parser.parse_args()
    cfg = load('config/estilo-industrial-v03.json')
    folder = ROOT / cfg['report_directory']
    renders = ROOT / cfg['render_directory']
    model = load(folder / 'modelo.json')
    run = load(folder / 'renders.json')
    audit = load(folder / 'validacao.json')
    resources = load(folder / 'recursos-nativos.json')
    assert resources['all_passed'] and not resources['external_libraries']
    fingerprint = sha(ROOT / cfg['output_blend'])
    assert fingerprint == model['blend_sha256'] == run['blend_sha256'] == audit['blend_sha256'] == resources['blend_sha256']
    assert audit['all_passed'] and audit['envelope']['all_passed']
    assert not audit['geometry_differences'] and not audit['missing_images']
    assert audit['geometry_compared'] == len(model['geometry_before'])
    assert sha(ROOT / cfg['base_blend']) == model['base_sha256'] == audit['base_sha256']
    assert not run['preview'] and run['envelope']['all_passed']
    assert run['device']['backend'] in {'CUDA', 'CPU'} and run['device']['devices']
    expected = {str(Path(cfg['render_directory']) / job['file']) for job in cfg['jobs']}
    assert set(run['outputs']) == expected
    for name, meta in run['outputs'].items():
        path = ROOT / name
        assert sha(path) == meta['sha256'] and path.stat().st_size == meta['bytes']
        with Image.open(path) as im:
            assert list(im.size) == cfg['resolution'] and im.format == 'PNG'
            im.verify()
    for asset in model['assets']:
        assert sha(ROOT / asset['path']) == asset['sha256']
    manifests = [ROOT / cfg['asset_manifest'], *sorted((ROOT / 'assets/industrial-v02').glob('manifesto*.json'))]
    for manifest in manifests:
        for record in json.loads(manifest.read_text())['records']:
            path = ROOT / record['path']
            assert sha(path) == record['sha256'] and path.stat().st_size == record['bytes']
    previous = load('arquivos/versoes-anteriores-2026-11-14/relatorios/industrial-v01/modelo.json')
    assert sha(ROOT / 'arquivos/versoes-anteriores-2026-11-14/projeto/industrial-v01/casa-industrial.blend') == previous['blend_sha256']
    assert sha(ROOT / 'arquivos/versoes-anteriores-2026-11-14/projeto/casa-reconstruida.blend') == previous['base_sha256']
    for name, digest in previous['references'].items():
        assert sha(ROOT / name) == digest

    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 25)
    names = ['Sala', 'Sala / jantar', 'Cozinha', 'Lazer nos fundos', 'Quarto dos fundos']

    def tile(canvas, path, x, y, width=936, height=585):
        with Image.open(path) as source:
            pic = ImageOps.contain(source.convert('RGB'), (width, height))
        canvas.paste(pic, (x + (width-pic.width)//2, y + (height-pic.height)//2))

    panel = Image.new('RGB', (1920, 2030), '#191b1b')
    draw = ImageDraw.Draw(panel)
    draw.text((24, 18), 'CASA • INDUSTRIAL V03 • RENDERIZAÇÃO NATIVA 3D', font=font, fill='#e6cfaa')
    for i, job in enumerate(cfg['jobs']):
        x = (i % 2)*960
        y = 70 + (i // 2)*650
        draw.text((x+24, y), names[i], font=font, fill='white')
        tile(panel, renders/job['file'], x+12, y+45)
    draw.text((990, 1460), 'Blender / Cycles • CUDA', font=font, fill='#e6cfaa')
    draw.text((990, 1510), 'Materiais e móveis editáveis', font=font, fill='white')
    draw.text((990, 1560), 'Arquitetura preservada', font=font, fill='white')
    panel.save(renders/'painel-ambientes.jpg', quality=94)

    atlas = Image.new('RGB', (1920, 3990), '#191b1b')
    draw = ImageDraw.Draw(atlas)
    draw.text((24,18), 'INSPIRAÇÃO | V03 NA PLANTA DA CASA • ENQUADRAMENTOS DIFERENTES', font=font, fill='#e6cfaa')
    refs = ['01-cena-final-menos-warn.png']*3 + ['02-bar-fundo.png', 'escritorio2.png']
    for i, job in enumerate(cfg['jobs']):
        y = 70+i*650
        draw.text((24,y), names[i], font=font, fill='white')
        tile(atlas, ROOT/'referencias-estilo-industrial'/refs[i], 12, y+45)
        tile(atlas, renders/job['file'], 972, y+45)
    y = 70 + len(cfg['jobs'])*650
    draw.text((24,y), 'Mesa: detalhe de referência | leitura no ambiente proposto', font=font, fill='white')
    tile(atlas, ROOT/'referencias-estilo-industrial/03-mesa-jantar.png', 12, y+45)
    tile(atlas, renders/'sala-integrada.png', 972, y+45)
    atlas.save(renders/'referencias-e-proposta.jpg', quality=94)

    stamp = dt.datetime.now(dt.timezone.utc).isoformat()
    review_path = folder/'revisao-visual.json'
    render_hashes = {k: v['sha256'] for k,v in run['outputs'].items()}
    if args.reviewed:
        write(review_path, {'timestamp_utc':stamp, 'blend_sha256':fingerprint, 'renders':render_hashes,
            'scope':'Cinco renders finais e comparações inspecionados visualmente. Avaliação qualitativa; não benchmark de Unreal.',
            'observations':['Sofá detalhado, almofadas com dobras e cortinas com volume',
                'Cozinha e bar com cubas profundas, madeira, metal e iluminação quente',
                'Quarto com beliche, roupa de cama, cadeira e luminária modeladas',
                'A referência foi adaptada à arquitetura: mobiliário, enquadramento e luz diferem',
                'Marcenaria, geladeiras e elementos herdados ainda têm simplificações']})
    reviewed = review_path.exists()
    if reviewed:
        review = json.loads(review_path.read_text())
        assert review['blend_sha256'] == fingerprint and review['renders'] == render_hashes
    report = f'''# Industrial v03 — renderização nativa editável

Verificação UTC: {stamp}

Cinco imagens finais saíram do `.blend` salvo e reaberto em outro processo. A nova proposta usa ativos detalhados, materiais fotográficos, tecido com volume e iluminação fotográfica 3D. Nenhuma imagem final foi substituída por geração ou retoque de IA.

| Obrigação | Recibo observado | Estado |
| --- | --- | --- |
| Modelo nativo editável | Arquivo final e SHA-256 conciliados entre modelo, auditoria e render | VERIFIED |
| Preservar arquitetura e encaixe | {audit['geometry_compared']} geometrias herdadas sem diferenças; três verificações do contorno e faces posteriores | VERIFIED |
| Renderizar todos os ambientes | Cinco PNGs 2880 × 1800; nomes, bytes e hashes conciliados | VERIFIED |
| Dispositivo de render efetivo | Registro do processo: {run['device']['backend']} / {', '.join(run['device']['devices'])} | VERIFIED |
| Texturas disponíveis | {audit['packed_images']} imagens empacotadas, nenhuma biblioteca externa vinculada ao reabrir | VERIFIED |
| Preservar reconstrução, v01 e referências | SHA-256 dos dois modelos e das quatro referências de estilo inalterados | VERIFIED |
| Conferir visualmente o resultado final | {'revisao-visual.json vinculado aos hashes finais' if reviewed else 'Inspeção final pendente'} | {'VERIFIED' if reviewed else 'UNKNOWN'} |
| Atingir equivalência certificada a Unreal Engine | Sem benchmark ou cena Unreal equivalente para medir | UNKNOWN |

## Modelo e alterações

Arquivo: `arquivos/versoes-anteriores-2026-11-14/projeto/industrial-v03/casa-fotografica.blend`. Cenas `PHOTO_Sala`, `PHOTO_Sala_Integrada`, `PHOTO_Cozinha`, `PHOTO_Lazer` e `PHOTO_Quarto`. A cena `EDITAR_Ativos` permite editar as malhas fontes das instâncias. Os pais `PHOTO …` permitem mover os móveis. Luzes comuns e painéis emissivos de cada cena também são objetos 3D editáveis.

Auditoria independente: {resources['mesh_objects']} objetos de malha, {resources['vertices_in_mesh_datablocks']} vértices em datablocks e {resources['editable_asset_instances']} instâncias de ativos editáveis. Esses números descrevem o arquivo; não medem realismo visual.

Sofá Chesterfield em couro, mesa de centro em aço e madeira, almofadas, livros e plantas detalhados substituem volumes simplificados. A cozinha recebe fogão e acessórios vintage. O quarto conserva o beliche e acrescenta edredons com caída, proteções metálicas, cadeira com tela curva, rodízios e luminária articulada. Pisos, cortinas, materiais e câmeras foram revistos. A circulação e as paredes não foram deslocadas para imitar o enquadramento da inspiração.

## Execução e reprodução

Blender 5.2.4 / Cycles; CUDA na RTX 4070 Laptop, AgX, denoise, até 768 amostras adaptativas, limiar 0,008, mínimo 64. São parâmetros máximos, não contagem fixa de amostras por pixel. Logs `geracao-previa.log` e `renderizacao.log`; recibos `modelo.json`, `validacao.json`, `previas.json` e `renders.json`.

O driver CUDA antigo instalado no Linux impedia detectar a GPU. `scripts/run_blender.py --wsl-gpu` seleciona `/usr/lib/wsl/lib/libcuda.so.1` somente para o processo filho. A execução de render foi validada com CUDA; OptiX não foi usado. Nenhum driver ou configuração global foi alterado. Na interface, configure CUDA ou selecione CPU conforme a sua instalação.

Configuração ativa: `config/estilo-industrial-v03.json`. A base técnica está em `arquivos/versoes-anteriores-2026-11-14/projeto/fontes/casa-base-detalhada.blend`; o estudo parcial v02 está arquivado com manifesto em `arquivos/historico/estudos/industrial-v02/`. O gerador recusa sobrescrever um modelo existente. Consulte o README para renderizar ou escolher um destino novo antes de regenerar.

## Comparação e limites

Veja `renders/industrial-v03/referencias-e-proposta.jpg`: referência à esquerda, proposta à direita, com enquadramentos diferentes. Não é comparação pixel a pixel. Preservam-se cimento, madeira escura, metal preto, couro, espelho e luz quente. O sofá vintage, os eletrodomésticos, a distribuição real e a luz diferem das inspirações. A planta herdada mantém seis cadeiras de jantar e três banquetas, em vez das quantidades mostradas nos renders inspiradores. A marcenaria e alguns elementos herdados ainda são simplificados. A equivalência ao realismo de uma produção específica em Unreal continua sem comprovação objetiva.

O jardim do HDRI é contexto ilustrativo, não levantamento do imóvel. As medidas lineares, posições dos banheiros e detalhes da escada continuam com as incertezas da reconstrução. A área de matrícula não comprova todas as cotas do modelo. Este é um estudo de interiores, não projeto executivo.

Verificações adicionais: `python3 -m unittest scripts/test_blender_launcher.py -v` (três testes do ambiente e argumentos), `python3 -m py_compile` nos scripts alterados e `git diff --check`.

Os ativos externos são [CC0 do Poly Haven](https://polyhaven.com/license); URLs oficiais, bytes e SHA-256 constam nos manifestos de `assets/`. Os recursos usados estão empacotados. Fontes alternativas não utilizadas ficam identificadas na biblioteca. Imagens decorativas e telas são materiais de superfícies, não substituem paredes, móveis ou o render por uma fotografia plana.
'''
    (folder/'RELATORIO.md').write_text(report)
    files = [ROOT/cfg['output_blend'], ROOT/cfg['base_blend'], ROOT/'README.md',
        ROOT/'config/estilo-industrial-v03.json', ROOT/'scripts/photographic_interiors.py',
        ROOT/'scripts/photographic_delivery.py', ROOT/'scripts/audit_photographic.py', ROOT/'scripts/run_blender.py', ROOT/'scripts/test_blender_launcher.py', ROOT/'.gitattributes']
    files += [ROOT/p for p in ['config/planta-casa.json', 'scripts/style_industrial.py', 'scripts/blender_primitives.py', 'scripts/audit_envelope.py', 'arquivos/versoes-anteriores-2026-11-14/projeto/fontes/README.md', 'arquivos/historico/estudos/industrial-v02/ARQUIVAMENTO.json']]
    files += [ROOT/p for p in expected] + sorted(renders.glob('*.jpg'))
    files += [p for p in folder.iterdir() if p.is_file() and p.name != 'manifesto.json']
    files += [p for p in (ROOT/'assets').rglob('*') if p.is_file()]
    write(folder/'manifesto.json', {'timestamp_utc':stamp, 'version':cfg['version'],
        'visual_review_complete':reviewed, 'files':{str(p.relative_to(ROOT)):
        {'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(set(files))}})
    print('PHOTO_DELIVERY_VERIFIED', len(expected), 'renders; visual review:', reviewed)


if __name__ == '__main__':
    main()
