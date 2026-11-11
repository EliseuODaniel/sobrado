"""Conciliar o estudo atual com os renders, referências e históricos preservados."""
import ast
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
from PIL import Image

root=Path(__file__).resolve().parents[1]
reports=root/'relatorios/atual'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(name):return json.loads((reports/name).read_text())
cfg=json.loads((root/'config/planta-casa.json').read_text())
assert cfg['revision_number']==8
validation=read('validacao.json');audit=read('auditoria-depois.json');upper=read('auditoria-superior.json')
renders=read('renders-finais.json');comparison=read('comparacao.json');start=read('inicio.json')
blend=root/'projeto/casa-reconstruida.blend';fingerprint=sha(blend)
assert read('camera-quarto-frente.json')['sha256']==fingerprint
assert fingerprint==validation['sha256']==audit['sha256']==renders['sha256']==comparison['blend_sha256']
assert all(v['passed'] for v in validation['checks'].values()) and audit['all_passed'] and upper['all_passed']
assert validation['checks']['escada_e_superior_coerentes']['detail']==upper
assert validation['photo_geometry_audit']==audit
assert len(validation['checks'])==17 and len(audit['checks'])==40 and len(upper['checks'])==14
names={'fachada-frontal','fachada-obliqua','acesso-lavabo','sala-fundos','sala-frente','escada-acesso','cozinha','cozinha-reversa','bar','lavanderia','lavabo','escada-superior','suite','quarto-frente','quarto-fundos','terreo-3d','planta-terreo','porta-lavabo','superior-3d','planta-superior','estudos-superior','volumetria','lavabo-sob-escada'}
assert not renders['preview'] and renders['saved_file_unchanged'] and len(renders['outputs'])==23
assert set(renders['outputs'])=={'renders/atual/'+name+'.png' for name in names}
comparisons={'comparacao-planta','antes-depois','comparacao-superior','comparacao-escada','comparacao-fotos','comparacao-fachada','comparacao-quartos','sala-frente-planta','acesso-lavabo-planta'}
assert len(comparison['outputs'])==9 and set(comparison['outputs'])=={'renders/atual/'+name+'.png' for name in comparisons}
for field in ['user_layout_source','upper_layout_source']:
    assert sha(root/cfg[field]['path'])==cfg[field]['sha256']
archive_counts={}
for name in ['ate-revisao05','revisao06','revisao07']:
    manifest=json.loads((root/'historico'/name/'ARQUIVAMENTO.json').read_text())
    for record in manifest['records']:assert sha(root/record['destination'])==record['sha256'],record['destination']
    archive_counts[name]=len(manifest['records'])
legacy=json.loads((root/'historico/ate-revisao05/ARQUIVAMENTO.json').read_text())
body=(root/'scripts/blender_primitives.py').read_text()
functions={n.name:hashlib.sha256(ast.get_source_segment(body,n).encode()).hexdigest() for n in ast.parse(body).body if isinstance(n,ast.FunctionDef)}
assert functions==legacy['shared_helpers_unchanged_sha256']
for record in start.get('drafts',[])+start.get('preview_archives',[])+start.get('superseded_archives',[]):assert sha(root/record['destination'])==record['sha256']
inv=json.loads((root/'relatorios/referencias-originais/inventario.json').read_text())
assert all(sha(root/'referencias-originais'/name)==meta['sha256'] for name,meta in inv['inputs'].items())
assert [p.name for p in (root/'projeto').glob('*.blend')]==['casa-reconstruida.blend']
images=list(dict.fromkeys(root/name for name in renders['outputs']+comparison['outputs']))
assert set((root/'renders/atual').glob('*.png'))==set(images)
for p in images:
    with Image.open(p) as im:im.verify()
subprocess.run(['git','diff','--check'],cwd=root,check=True)
stamp=dt.datetime.now(dt.timezone.utc).isoformat()
unknowns=['Contagem e forma reais dos degraus na curva; seis adotados provisoriamente','Comprimento real do primeiro lance e escala linear: avanço reto comprimido de aproximadamente 0,14 m na escala anterior; demais medidas também estimadas','Posições e dimensões reais dos banheiros; agora seguem a proposta do último croqui','Associação do quarto branco à frente e azul aos fundos; posições dos três quartos confirmadas, identidade fotográfica inferida','Portas superiores, janelas posteriores e sentido definitivo da porta do lavabo']
review={'timestamp_utc':stamp,'revision':8,'status':'estudo_aproximado_renderizado_e_verificado','scope':'Último croqui superior: quartos, WCs paralelos, portas e hall sobre o lance baixo; lances colados e dimensões provisórias','blend':{'path':str(blend.relative_to(root)),'sha256':fingerprint},'checks':{'integrity':17,'ground_geometry':40,'upper_geometry':14},'renders':23,'comparisons':9,'visual_review':['Planta superior versus croqui','Lance final menor, curva e chegada na laje','Perspectivas dos três quartos versus fotos originais','Planta térrea e porta do lavabo preservada; demais vistas regeneradas'],'archives_verified':archive_counts,'original_photos_preserved':True,'unknowns':unknowns,'external_publication':False}
(reports/'revisao.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
s=cfg['layout']['stairs'];d=cfg['estimated_dimensions_m']
rows=[]
for room in cfg['rooms']:
    if room['level']!=1:continue
    x0,x1,y0,y1=room['bounds'];w=x1-x0-.15;depth=y1-y0-.15
    rows.append(f"| {room['name']} | ≈ {w:.2f} × {depth:.2f} m | ≈ {w*depth:.2f} m² |")
text=f'''# Estudo atual — revisão 08

UTC: {stamp}

A escada passou a ter sete degraus no primeiro lance, seis degraus provisórios na curva e quatro no lance final. A chegada final termina antes do início do primeiro lance em planta. Os dois lances são colados lateralmente, sem faixa, laje ou parede entre eles; o vidro fica somente na borda do hall, perpendicular aos lances. Os quartos foram implantados conforme o croqui `{cfg['upper_layout_source']['path']}`: suíte à frente esquerda, quarto à frente direita e quarto nos fundos. Os dois banheiros seguem a proposta mais recente, lado a lado à esquerda até os fundos, sem a faixa de uso desconhecido do estudo anterior. O WC suíte é acessado pela suíte e o WC social, pela lateral do hall. A suíte foi alongada e sua porta de entrada deslocada para a parede lateral junto do hall.

| Obrigação | Recibo observado | Estado e limite |
| --- | --- | --- |
| Sete degraus iniciais e quatro finais | Contagem dos objetos e vértices, alturas e conexão dos degraus | VERIFIED no modelo |
| Lances colados | Limites laterais dos vértices coincidem sem intervalo; vazio da laje contínuo | VERIFIED |
| Lance final mais curto | Extensões dos vértices dos lances na auditoria superior | VERIFIED |
| Chegada conectada ao hall | Ray cast na laje e percursos aos três quartos | VERIFIED nas amostras; não certifica circulação completa |
| Hall sobre o trecho baixo do primeiro lance | Ray cast no piso superior sobre a projeção dos primeiros degraus | VERIFIED na hipótese de escala |
| Laje não atravessa a escada | Interseção com vãos e folgas acima dos primeiros degraus | VERIFIED na hipótese geométrica |
| Posições dos três quartos | Croqui preservado, camas na frente esquerda, frente direita e fundos | VERIFIED como implantação relativa do croqui |
| Banheiros e portas seguem o último croqui | Limites paralelos e ray casts nos acessos privativo e social | VERIFIED como proposta desenhada; medidas e localização real UNKNOWN |
| Seis degraus na curva correspondem ao imóvel | Sem confirmação da contagem | UNKNOWN; seis provisórios |
| Modelo e vistas sincronizados | 23 renders do mesmo SHA-256 do editável, nove comparações | VERIFIED |
| Fontes e versões anteriores preservadas | Hashes das 31 fotos e históricos 05/06/07 | VERIFIED |
| Dimensões reais, identidade dos dois quartos e perímetro | Sem escala medida; fotos sem planta cotada | UNKNOWN / INFERRED conforme configuração |

## Proporções propostas

| Ambiente | Dimensões internas aproximadas | Área aproximada do retângulo |
| --- | --- | --- |
'''+'\n'.join(rows)+f'''

Essas dimensões descontam uma espessura de parede do retângulo de cada ambiente. Não são levantamento nem áreas registrais. Portas, shafts e medidas finais dos banheiros ainda podem alterar a distribuição.

A largura externa estimada permanece {d['width']:.2f} m e o limite posterior superior está em y={d['upper_back_y']:.2f} m, como na envoltória anterior. O estudo com faixa entre os lances e ampliação dos fundos foi descartado e preservado em `historico/rascunhos/revisao08/lances-separados/` após a correção do usuário. A projeção retangular é {d['width']*(d['upper_back_y']-d['upper_front_y']):.2f} m² incluindo varanda e vãos, antes de qualquer conciliação registral. A análise secundária de 51,03 m² exclusivos não foi usada como prova do perímetro.

A porta do lavabo permanece na marca preta confirmada e a implantação anterior de cozinha e garagem foi preservada. A laje do hall cobre a parte baixa inicial do primeiro lance (três degraus na hipótese atual), reproduzindo a sobreposição desenhada no croqui; não há piso ou separação entre os lances. O vazio é contínuo. A guarda de vidro está na borda do hall, perpendicular ao primeiro lance.

Na hipótese de altura entre pisos de {d['floor_height']:.2f} m, o desnível de cada degrau fica em cerca de {d['floor_height']/s['risers']:.3f} m e o avanço reto em {s['first_run']/s['first_steps']:.3f} m. **O avanço de cerca de 0,14 m está comprimido pelo espaço estimado anterior e não deve ser tomado como dimensão real ou solução executiva.** O usuário foi consultado sobre o comprimento do primeiro lance para corrigir a escala. Não foi alargada a casa ou mudada a porta por suposição. Os valores não foram medidos ou aprovados para execução. O leque da curva é uma aproximação visual editável.

## Conferência visual e execução

`comparacao-superior.png` coloca o croqui ao lado da planta. `comparacao-escada.png` relaciona a foto da chegada com a nova perspectiva. `comparacao-quartos.png` reúne as referências dos três quartos; a associação branco/frente e azul/fundos é inferida. As comparações do térreo e fachada também foram regeneradas. `proporcoes-croqui.json` registra uma leitura visual manual das linhas do croqui e sua comparação normalizada com os limites dos cômodos; essa comparação é proporcional, sem atribuir medidas reais ao desenho. Nenhuma imagem de origem foi alterada.

Passaram 17 verificações de integridade, 40 de relações do térreo e 14 de escada/superior. Comandos: `validate_house.py`, `house_atlas.py`, `python3 -m py_compile scripts/*.py` e `git diff --check`. A geometria compartilhada foi conferida entre planta e perspectivas. A checagem das câmeras usa os limites locais dos objetos para evitar falsos positivos na porta diagonal. As câmeras foram conferidas em suas cenas com as transformações dos objetos avaliadas. O arquivo atual foi reconstruído pelo gerador depois da correção dos lances encostados. `camera-quarto-frente.json` registra o ajuste posterior de enquadramento para afastar a vista da porta aberta, sem alterar a geometria. O gerador usa a mesma posição de câmera na configuração.

O editável atual é `projeto/casa-reconstruida.blend`. A revisão 07 está em `historico/revisao07/`, com {archive_counts['revisao07']} registros de cópias e movimentos recuperáveis. Estudos desta etapa ficam em `historico/rascunhos/revisao08/`. Não houve commit, push ou publicação.

## O que continua sem confirmação

'''+'\n'.join('- '+item for item in unknowns)+'\n'
(reports/'RELATORIO.md').write_text(text)
inputs=[root/'config/planta-casa.json',root/cfg['upper_layout_source']['path'],root/cfg['user_layout_source']['path'],*sorted((root/'referencias-originais').glob('*.webp')),*[root/'historico'/name/'ARQUIVAMENTO.json' for name in archive_counts]]
outputs=[blend,root/'README.md',root/'historico/README.md',root/'relatorios/progresso.json',*sorted((root/'scripts').glob('*.py')),*images,*sorted(reports.glob('*.json')),*sorted(reports.glob('*.log')),reports/'RELATORIO.md']
outputs=list(dict.fromkeys(p for p in outputs if p.name!='manifesto.json'))
def metadata(paths):return {str(p.relative_to(root)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in paths}
manifest={'timestamp_utc':stamp,'revision':8,'scope':review['scope'],'inputs':metadata(inputs),'outputs':metadata(outputs),'unknowns':unknowns,'deletions':[],'external_publication':False}
(reports/'manifesto.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('CURRENT_DELIVERY_VERIFIED',17,40,14,23,9)
