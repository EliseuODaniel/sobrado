# Casa — reconstrução e proposta industrial

## Versão atual: industrial v04 — mais próxima da inspiração

A v04 troca o sofá clássico por um conjunto contemporâneo em couro caramelo, usa quatro cadeiras leves com cabeceiras livres, aquece a madeira, acrescenta plantas com mapas PBR, manta e juta e refaz a iluminação do conjunto. A arquitetura e os pavimentos permanecem na posição anterior. São seis câmeras com iluminação comum e imagens em 3342 × 1882, mesma proporção da referência principal.

- [Galeria atual](renders/industrial-v04/painel-ambientes.jpg)
- [Referências e proposta](renders/industrial-v04/referencias-e-proposta.jpg)
- [Comparação v03 / v04, com enquadramentos diferentes](renders/industrial-v04/evolucao-v03-v04.jpg)
- [Sala integrada](renders/industrial-v04/sala-integrada.png), [sofá](renders/industrial-v04/sala.png) e [parede da TV](renders/industrial-v04/sala-tv.png)
- [Cozinha](renders/industrial-v04/cozinha.png), [lazer](renders/industrial-v04/lazer-fundos.png) e [quarto dos fundos](renders/industrial-v04/quarto-fundos.png)
- [Blender completo editável](projeto/industrial-v04/casa-industrial-refinada.blend)
- [Validação e diferenças restantes](relatorios/industrial-v04/RELATORIO.md) e [fontes dos recursos](assets/industrial-v04/README.md)

Abra o `.blend` no Blender 5.2.4 e escolha uma cena `DESIGN_…`. A inicial é `DESIGN_Sala_Integrada`; `Num 0` mostra a câmera e `F12` renderiza. Use **Salvar como** para suas alterações. Os modelos grandes e os novos recursos binários usam Git LFS: num clone novo, execute `git lfs install` e `git lfs pull`.

Os pais `DESIGN Sofá contemporâneo`, `DESIGN Mesa de centro` e `DESIGN Cadeira jantar …` permitem mover cada móvel. Assentos e encostos são malhas nativas, com dados compartilhados entre peças iguais; use Single User se quiser uma almofada independente. A mesa de jantar conserva o pai original `MESA_JANTAR…` da reconstrução. Selecione mesa, cadeiras e arranjo juntos para mover o conjunto.

As novas peças ficam em `DESIGN04`, com subcoleções por ambiente. Os mapas usados estão empacotados; os materiais `DESIGN …` expõem os ajustes no Shader Editor. A cena `EDITAR_Ativos_V04` contém as fontes importadas. As almofadas adaptadas do sofá e das cadeiras são editadas nas próprias cenas de apresentação. A iluminação está em `DESIGN_Iluminacao`: spots e painéis emissivos de preenchimento editáveis, ocultos da câmera e dos reflexos diretos para evitar discos flutuantes. Eles são recursos de fotografia 3D da proposta, não luminárias confirmadas no imóvel.

```bash
# Renderizar os seis enquadramentos a partir do arquivo salvo:
python3 scripts/run_blender.py --wsl-gpu --background projeto/industrial-v04/casa-industrial-refinada.blend \
  --python scripts/refine_industrial.py -- --render-only
# Auditar o arquivo reaberto:
python3 scripts/run_blender.py --background projeto/industrial-v04/casa-industrial-refinada.blend \
  --python scripts/audit_refined.py
python3 scripts/refined_delivery.py
```

Configuração: `config/estilo-industrial-v04.json`. Para regenerar, escolha um **novo destino** nessa configuração e execute `scripts/refine_industrial.py` sobre o arquivo base v03. O gerador recusa sobrescrever o destino. `--preview` gera imagens reduzidas; `--only sala-integrada` limita a câmera. Na interface, você pode escolher CPU se CUDA não estiver disponível. O launcher WSL seleciona o driver apenas no processo filho, sem alterar configurações globais.

A v03 permanece preservada como fonte e comparação. Os rascunhos v04 ficam em `historico/rascunhos/industrial-v04/`, localmente e fora do Git. Esta proposta é adaptada à planta: a profundidade da casa, a posição da escada e as aberturas impedem reproduzir exatamente a perspectiva da inspiração. O jardim do HDRI é ilustrativo. As cotas e os banheiros continuam com as incertezas da reconstrução.

## Versão anterior: industrial v03, inteiramente editável

Cinco renderizações nativas refinam sala, sala/jantar, cozinha, lazer nos fundos e quarto dos fundos. O ganho vem de móveis detalhados, materiais fotográficos, tecidos com volume, luz e câmeras revistas. A arquitetura da revisão 10 continua preservada. Foi mantido o Blender/Cycles e habilitado render real na RTX 4070 Laptop com CUDA.

- [Galeria atual](renders/industrial-v03/painel-ambientes.jpg)
- [Comparação com as inspirações](renders/industrial-v03/referencias-e-proposta.jpg)
- [Sala](renders/industrial-v03/sala.png), [sala integrada](renders/industrial-v03/sala-integrada.png), [cozinha](renders/industrial-v03/cozinha.png), [lazer](renders/industrial-v03/lazer-fundos.png) e [quarto](renders/industrial-v03/quarto-fundos.png)
- [Modelo Blender editável](projeto/industrial-v03/casa-fotografica.blend)
- [Relatório de validação e limites](relatorios/industrial-v03/RELATORIO.md)
- [Licenças e fontes](assets/industrial-v03/README.md)

As imagens são renderizações do arquivo 3D salvo, sem retoque generativo. Materiais, móveis, câmeras e luzes são editáveis. O jardim visto nas janelas é contexto de iluminação ilustrativo. O sofá Chesterfield e os eletrodomésticos vintage são escolhas desta proposta, com diferenças em relação às inspirações. O resultado visual pode ser avaliado nas comparações; não há equivalência certificada a Unreal Engine.

### Abrir e editar

O arquivo grande usa Git LFS. Ao clonar, execute `git lfs install` e `git lfs pull`; baixar apenas o ponteiro de texto não baixa o modelo.

Abra `projeto/industrial-v03/casa-fotografica.blend` no Blender 5.2.4. Escolha uma cena `PHOTO_…`, `Num 0` para a câmera e `F12` para renderizar. A cena inicial é `PHOTO_Sala`. Guarde suas alterações com **Salvar como**, em outro arquivo; o gerador não substitui um destino existente.

- Mova móveis importados pelos objetos pais `PHOTO …` no Outliner, usando `G` e `R`. Cadeiras herdadas ficam sob `HQ …`; bancada e beliche mantêm seus pais originais. Todos os elementos continuam em escala de metros.
- Para editar vértices de um ativo importado, abra a cena `EDITAR_Ativos` e habilite no View Layer apenas a coleção `PHOTO_Ativo_…` desejada. Por padrão o sofá está visível. Alterações na malha fonte afetam suas instâncias. Para uma cópia independente, use Make Instances Real numa cópia do objeto.
- Ajuste materiais no Shader Editor, incluindo mapas de cor, rugosidade e normal. As imagens usadas estão empacotadas. A biblioteca externa permite reimportar os originais.
- A iluminação comum está em `PHOTO_Mobiliario`; cada cena também tem uma coleção `RIG_PHOTO_…` com painel emissivo fotográfico. São elementos de iluminação 3D editáveis. Coleções antigas e peças substituídas ficam preservadas e ocultas no render; use as cenas `PHOTO_…` para esta proposta.
- Na interface, selecione CUDA nas preferências Cycles e a GPU nas propriedades de renderização. Se CUDA não estiver disponível na sua instalação, escolha CPU. No WSL desta máquina, o comando abaixo usa o driver correto só no processo do Blender; não muda drivers ou configurações globais.

```bash
# Renderizar novamente a partir do .blend salvo:
python3 scripts/run_blender.py --wsl-gpu --background projeto/industrial-v03/casa-fotografica.blend \
  --python scripts/photographic_interiors.py -- --render-only
# Conferir o arquivo nativo em processo limpo:
python3 scripts/run_blender.py --wsl-gpu --background projeto/industrial-v03/casa-fotografica.blend \
  --python scripts/photographic_interiors.py -- --validate-only
python3 scripts/run_blender.py --background projeto/industrial-v03/casa-fotografica.blend \
  --python scripts/audit_photographic.py
python3 scripts/photographic_delivery.py
```

`config/estilo-industrial-v03.json` define as vistas e saídas. A geração usa `projeto/fontes/casa-base-detalhada.blend`; para regenerar, escolha antes um **novo destino** no arquivo de configuração e execute o gerador a partir dessa base. `--preview` produz testes locais; `--cpu` permite renderizar sem CUDA, omitindo também `--wsl-gpu`. Os finais usam 2880 × 1800, até 768 amostras adaptativas, AgX e denoise.

A base técnica intermediária e a v01 foram preservadas. O estudo v02 teve renderização interrompida por qualidade insuficiente e foi movido para [histórico de estudos](historico/estudos/industrial-v02/README.md), com manifesto dos movimentos. Rascunhos e binários históricos ficam apenas localmente. Os renders arquitetônicos em `renders/atual/` continuam sendo a referência das plantas; a v03 muda decoração e enquadramento.

## Proposta industrial v01

Nova decoração para sala/jantar, cozinha, lazer nos fundos e quarto dos fundos, inspirada nas quatro imagens de `referencias-estilo-industrial/`. Cimento, madeira nogueira, aço preto, couro caramelo e iluminação quente formam a proposta. O quarto mantém o beliche e recebe bancada e detalhes de escritório. A arquitetura e os móveis herdados mantêm a geometria da revisão 10.

- [Galeria dos quatro ambientes](renders/industrial-v01/painel-ambientes.jpg)
- [Sala integrada](renders/industrial-v01/sala-integrada.png) e [sala vista da frente](renders/industrial-v01/sala-frente.png)
- [Cozinha](renders/industrial-v01/cozinha.png) e [vista reversa](renders/industrial-v01/cozinha-reversa.png)
- [Lazer nos fundos](renders/industrial-v01/lazer-fundos.png)
- [Quarto dos fundos](renders/industrial-v01/quarto-fundos.png) e [escritório](renders/industrial-v01/quarto-escritorio.png)
- [Comparação com as referências de estilo](renders/industrial-v01/referencias-e-proposta.jpg)
- [Blender industrial editável](projeto/industrial-v01/casa-industrial.blend)
- [Relatório e validação da proposta](relatorios/industrial-v01/RELATORIO.md)

Abra o modelo industrial no Blender e escolha uma cena `IND_…`. As novas peças ficam nas coleções `IND_Decor_…`; os materiais começam com `IND `. As coleções da reconstrução permanecem disponíveis. Selecione a cena desejada, use `Num 0` para a câmera e `F12` para renderizar. As referências de estilo acompanham o repositório; os revestimentos novos são procedurais e funcionam sem imagens externas.

```bash
# Gerar uma variante nova a partir da reconstrução (o destino deve estar livre):
python3 scripts/run_blender.py --background projeto/casa-reconstruida.blend \
  --python scripts/style_industrial.py -- --project-root . --build-only

# Reabrir o arquivo entregue e renderizar as sete câmeras:
python3 scripts/run_blender.py --background projeto/industrial-v01/casa-industrial.blend \
  --python scripts/style_industrial.py -- --project-root . --render-only
python3 scripts/run_blender.py --background projeto/industrial-v01/casa-industrial.blend \
  --python scripts/audit_industrial.py
python3 scripts/industrial_delivery.py
```

A configuração de câmeras, versão e saídas fica em `config/estilo-industrial-v01.json`; as cores e texturas ficam nos materiais do Blender e na função `materials()` do gerador. Use outra versão/destino para regenerar sem substituir edições manuais. `--preview` produz prévias em subpasta local. Os renders finais usam Cycles em CPU, 96 amostras, 1600 × 1000, AgX e denoise. A proposta adapta os acabamentos à planta: não replica a distribuição de móveis nem todas as peças das imagens inspiradoras.

## Reconstrução — revisão 10: contorno comum dos pavimentos

O corpo principal dos dois pisos agora tem o mesmo contorno. Os fundos dos dois banheiros e do quarto superior coincidem com a parede da cozinha abaixo. O desencontro anterior de 0,85 m foi corrigido na geometria do Blender, e a profundidade interna foi redistribuída entre os ambientes.

- [Sobreposição dos pavimentos com contorno comum](renders/atual/pavimentos-sobrepostos.png)
- [Plantas na mesma escala e origem](renders/atual/pavimentos-alinhados.png)
- [Planta térrea atual](renders/atual/planta-terreo.png)
- [Planta superior atual](renders/atual/planta-superior.png)
- [Superior em 3D](renders/atual/superior-3d.png)
- [Blender editável](projeto/casa-reconstruida.blend)
- [Relatório de alinhamento, dimensões e limites](relatorios/atual/RELATORIO.md)

## Qual contorno coincide

Na escala estimada, os dois pisos ocupam o retângulo x=0 a 5,60 m e y=−1,65 a 7,60 m: aproximadamente **5,60 × 9,25 m**. A frente é a fachada do volume sobre a garagem; os fundos são a parede da cozinha. As faces externas posteriores também coincidem, com a mesma espessura de parede nos dois níveis.

Esse corpo principal inclui a garagem sob o superior no térreo e a varanda no superior. O pátio frontal e a churrasqueira/lavanderia posteriores são anexos térreos, fora desse contorno comum. O vão da escada é uma abertura na laje superior; por isso contorno igual não implica área líquida igual.

O arquivo `config/planta-casa.json` registra esse limite em `main_volume`. O gerador verifica a concordância entre a referência da cozinha, o limite superior e o contorno comum. A auditoria testa os vértices das lajes e as faces reais das paredes após reabrir o `.blend`.

## Redistribuição dos ambientes

As posições relativas do último croqui foram mantidas: suíte à frente esquerda, outro quarto à frente direita, dois WCs à esquerda nos fundos e quarto dos fundos à direita. A instrução mais recente sobre o alinhamento com a cozinha controla o limite externo.

Dimensões internas aproximadas do estudo:

| Ambiente superior | Dimensões |
| --- | --- |
| Suíte | 2,65 × 3,95 m |
| Quarto da frente | 2,65 × 3,70 m |
| Quarto dos fundos | 2,65 × 3,25 m |
| Cada banheiro | 1,25 × 4,15 m |

Os banheiros continuam compridos e estreitos, conforme a distribuição proposta, e precisam ser medidos. Os móveis e as camas mantêm suas dimensões aproximadas próprias. No térreo, escada, lavabo e divisão da garagem se deslocaram 0,30 m; a cozinha começa em y=4,30 m e termina na referência comum y=7,60 m.

A escada mantém os lances encostados, sete degraus iniciais, curva provisória de seis e quatro degraus finais. A laje cobre o trecho baixo junto ao hall; não há faixa, parede ou laje entre os lances. O comprimento do primeiro lance ainda precisa ser medido: o avanço herdado de aproximadamente 0,14 m por degrau está comprimido e não é dimensão executiva.

As dimensões gerais são estimadas. O contorno comum corresponde a uma projeção retangular de 51,80 m² incluindo varanda e vãos, que não equivale aos 51,03 m² exclusivos citados na análise secundária da matrícula. Não houve levantamento nem cálculo estrutural.

## Comparações e validação

[Antes e depois do térreo](renders/atual/antes-depois.png), [referência proporcional do superior](renders/atual/comparacao-superior.png), [fotos do térreo](renders/atual/comparacao-fotos.png), [fotos dos quartos](renders/atual/comparacao-quartos.png) e [fachada](renders/atual/comparacao-fachada.png) acompanham a revisão.

`encaixe-antes.json` e `encaixe-pavimentos.json`, em `relatorios/atual/`, registram a diferença entre o modelo anterior e o atual. São três verificações novas: contorno externo, cobertura das lajes e coplanaridade da parede posterior. Passaram também 18 verificações de integridade, 40 de relações do térreo e 16 de escada/superior. Isso confirma geometria do estudo, sem aprovar estrutura ou medidas reais.

## Abrir, editar e marcar correções

Abra `projeto/casa-reconstruida.blend` no Blender 5.2 LTS. `PLANTA_Terreo_Cotas` e `PLANTA_Superior_Cotas` mostram as plantas; as cenas `FOTO_…`, as perspectivas. `CORTE_Lavabo_Escada` é o corte identificado. Em `PLANTA_Terreo_Portas`, os degraus ficam ocultos apenas para ler os vãos.

No Outliner, selecione um conjunto como `Cama suíte` e pressione `G` para movê-lo. Portas têm pivô `abrir/girar`. Materiais ficam em Material Properties; luzes, em `Iluminacao` e Light Properties. `Num 0` volta à câmera e `F12` renderiza.

Para corrigir no Paint, use as plantas atuais e salve uma cópia com outro nome. Há 23 cenas editáveis e 26 fotos únicas empacotadas; os 31 arquivos originais continuam preservados. `ESTUDOS_Superior` contém referências separadas de mobiliário.

## Regenerar

Os renders finais usam Cycles em CPU, 64 amostras, AgX e denoise. O Blender portátil fica em `.tools/blender-5.2.4-linux-x64/blender`; o launcher aceita `BLENDER_EXECUTABLE`.

```bash
# Estudo separado, preservando o arquivo atual:
python3 scripts/run_blender.py --background --factory-startup \
  --python scripts/build_house.py -- --project-root . --device cpu \
  --output historico/rascunhos/casa-nova-geracao.blend

# Reabrir, validar e renderizar:
python3 scripts/run_blender.py --background projeto/casa-reconstruida.blend \
  --python scripts/validate_house.py -- --project-root . --device cpu
python3 scripts/house_atlas.py
# Após a inspeção visual:
python3 scripts/finalize_ground_revision.py
```

`--no-render` executa apenas as verificações; `--preview` gera todas as vistas reduzidas. `compare_proportions.py --landmarks referencias-ajustes/proporcoes-r09-linhas.json` compara a distribuição com o croqui manual, subordinado ao alinhamento externo solicitado nesta revisão.

## Histórico

A [revisão 09](historico/revisao09/INDICE.md) foi arquivada com hashes. As demais versões permanecem no [histórico](historico/README.md). Os modelos e imagens históricos e as prévias ficam preservados localmente, fora do Git; seus documentos e recibos continuam versionados. O repositório remoto contém os modelos e renders atuais, as referências e os geradores. A conferência completa de retenção dos arquivos antigos em `finalize_ground_revision.py` exige esse histórico local.
