# Sobrado — residência 07, reconstrução e interiores

[Plano de fotorrealismo e comparação Blender/Unreal](PLANO-FOTORREALISMO.md) — pesquisa de 12/11/2026, auditoria dos cinco modelos vigentes e evolução por etapas. A execução industrial em Cycles está descrita abaixo; o teste no Unreal permanece pendente.

## Estado atual da residência 07 — revisão fiel v02

O novo modelo aproxima móveis, tecidos, cortinas, marcenaria, eletrodomésticos, revestimentos e luminárias das fotos em `referencias-originais`. Esquadrias e peças de banheiro foram reposicionadas pela base oficial; as folhas das portas são apresentadas fechadas dentro dos vãos. O sofá, as cadeiras e as colchas usam capturas de tecido recoloridas; o arranjo de orquídeas foi remodelado.

- [Modelo atual editável v02](projeto/residencia-07-atual-v02/casa-07-atual-fiel.blend) · [26 imagens finais 4K](renders/atual/galeria.html)
- [Entrega organizada](renders/atual/LEIA-ME.md) · [16 comparações foto/modelo](renders/atual/galeria.html#comparacoes) · [caderno de 45 páginas](renders/atual/00-cadernos/caderno-atual.pdf)
- [Planta cotada do térreo](renders/atual/01-plantas/planta-atual-terreo.pdf) · [superior](renders/atual/01-plantas/planta-atual-superior.pdf)
- [Relatório e verificações](relatorios/atual-fiel-v02/RELATORIO.md) · [critérios de fidelidade](relatorios/atual-fiel-v02/FIDELIDADE.md) · [pesquisa e materiais](relatorios/atual-fiel-v02/PESQUISA-E-CRITERIOS.md)

**Os 26 PNGs finais da revisão estão concluídos, em 3840 × 2880 e 16 bits.** Galeria, comparações e caderno foram atualizados; passaram 188 verificações da entrega e 12 do navegador, além da revisão visual de todas as vistas. Os arquivos da versão anterior foram preservados em `historico/estudos/atual-v01`. O modelo anterior permanece como fonte das propostas industriais.

As 674 impressões de geometria preservada e 121 posições de esquadria foram conferidas, junto a 274 verificações nativas. Móveis e anexos continuam com dimensões aproximadas pelas fotos, sem levantamento presencial. A geladeira do bar atual permanece conforme as fotos; sua remoção foi solicitada somente para as propostas industriais. As plantas vetoriais conservam a base documental anterior.

## Industrial v06 — 31 imagens 4K e pares de dia/noite

A revisão v06 aplica materiais 4K, iluminação diurna/noturna, detalhamento de móveis, esquadrias, cuba e vegetação sobre a planta atual. A v04 foi descartada e as versões industriais passam a ficar sem geladeira no bar, preservando a geladeira da cozinha.

- [Galeria v06](renders/industrial-v06/galeria.html) · [caderno de 41 páginas](renders/industrial-v06/00-cadernos/caderno-industrial-v06.pdf) · [bar sem geladeira em 4K](renders/industrial-v06/02-ambientes/bar.png)
- [Modelo editável](projeto/industrial-v06/casa-industrial-fotorrealista.blend) · [conferência da entrega](relatorios/industrial-v06/RELATORIO.md)
- [Intercâmbio geométrico GLB e teste de unidade](exports/fotorrealismo-industrial-v06/LEIA-ME.md)

São 31 PNGs em 3840 × 2880 e 16 bits, incluindo três pares de dia e noite. A galeria possui filtros e comparadores de iluminação. As conferências do modelo, dos arquivos e da galeria no navegador passaram. A comparação no Unreal permanece pendente da instalação; esta implementação usa Cycles/GPU. Móveis e equipamentos com dimensões de estudo continuam identificados no relatório.

## Industrial atualizado — v05 sobre a planta atual da residência 07

O bar industrial não possui geladeira; a geladeira da cozinha permanece. A proposta industrial foi refeita com as quatro referências de `referencias-estilo-industrial`, usando a arquitetura atual da unidade 07. As medidas documentais, paredes, vãos, escada, abertura dos fundos, cobertura posterior e divisão lazer/lavanderia foram preservados. A arquitetura estimada da antiga v04 não foi reutilizada.

- [Entrega industrial organizada](renders/industrial-v05/LEIA-ME.md), [galeria](renders/industrial-v05/galeria.html) e [caderno de 35 páginas](renders/industrial-v05/00-cadernos/caderno-industrial-v05.pdf)
- [Blender editável](projeto/industrial-v05/casa-industrial-residencia07-atual.blend), [comparações com a casa atual](renders/industrial-v05/04-comparacoes) e [referências × proposta](renders/industrial-v05/05-referencias/referencias-e-proposta.jpg)
- [Relatório de conferência](relatorios/industrial-v05/RELATORIO.md)

São 25 imagens, plantas vetoriais e uma alternativa de escritório em duas cenas próprias. Cimento suave, madeira quente, couro caramelo, aço preto e luz âmbar seguem as referências. As dimensões dos anexos e móveis permanecem aproximadas; a proposta não altera as instalações existentes.

## Ático atualizado — v05 com lances alinhados e caixa à esquerda

Os dois lances novos ficam exatamente sobre os inferiores: os 16 pisos repetem as coordenadas em planta, deslocados apenas 2,70 m para cima. A caixa de 1.000 L foi transferida 3,55 m para a esquerda, mantendo sua cota de base. A subida fica junto ao hall; os quartos permanecem livres da nova escada.

- [Entrega v05](renders/residencia-07-atico-v05/LEIA-ME.md), [galeria do ático](renders/residencia-07-atico-v05/galeria.html) e [caderno PDF](renders/residencia-07-atico-v05/00-cadernos/caderno-atico-v05.pdf).
- [Desenho completo das escadas e caixa](renders/residencia-07-atico-v05/07-escadas/escada-completa-caixa.png), [lateral atualizada](renders/residencia-07-atico-v05/07-escadas/01-vistas/05-lateral-patamares.png), [giro 360°](renders/residencia-07-atico-v05/07-escadas/galeria.html) e [GIF](renders/residencia-07-atico-v05/07-escadas/giro-360.gif).
- [Planta do alinhamento](renders/residencia-07-atico-v05/04-plantas/escadas-alinhadas.pdf), [planta do ático](renders/residencia-07-atico-v05/04-plantas/planta-atico-cotada.pdf) e [nova posição da caixa](renders/residencia-07-atico-v05/04-plantas/reposicionamento-caixa.pdf).
- [Blender editável](projeto/residencia-07-atico-v05/atico-escadas-sobrepostas-caixa-lateral.blend) e [relatório](relatorios/residencia-07-atico-v05/RELATORIO.md).

O vão da laje foi refeito em L, com altura livre mínima amostrada de 2,21 m sob o pequeno patamar. O forro mantém reserva vertical de 15 cm e altura livre máxima de 3,77 m. Mansardas, fundos e arquitetura atual são preservados; a área técnica, o estar, o escritório e os armários baixos foram compatibilizados no ático.

A ligação pelo quarto frontal de 60 cm da v04 foi eliminada. O hall nominal de 65 cm permanece como restrição da base; apoios e cargas da caixa, estrutura e redes definitivas precisam de projeto específico. A forma externa do reservatório continua ilustrativa. A posição nova é proposta, autorizada pelo usuário.

```bash
python3 scripts/run_blender.py --wsl-gpu --background projeto/residencia-07-atico-v05/atico-escadas-sobrepostas-caixa-lateral.blend --python scripts/residence07_attic_v05.py -- --render --group main
python3 scripts/run_blender.py --wsl-gpu --background projeto/residencia-07-atico-v05/atico-escadas-sobrepostas-caixa-lateral.blend --python scripts/residence07_attic_v05.py -- --render --group detail
python3 scripts/run_blender.py --wsl-gpu --background projeto/residencia-07-atico-v05/atico-escadas-sobrepostas-caixa-lateral.blend --python scripts/residence07_attic_v05.py -- --render --group orbit
python3 scripts/run_blender.py --background projeto/residencia-07-atico-v05/atico-escadas-sobrepostas-caixa-lateral.blend --python scripts/residence07_attic_v05_audit.py -- --require-renders
.tools/planta-venv/bin/python scripts/residence07_attic_v05_delivery.py
```

## Estrutura colorida, instalações 3D e ático

- [Instalações 3D, legendas e paredes transparentes](renders/residencia-07/03-instalacoes/3d/LEIA-ME.md) · [modelo nativo](projeto/residencia-07/casa-07-instalacoes.blend)
- [Estrutura sem móveis, em cores suaves](renders/residencia-07/06-galerias/painel-estrutura.jpg)
- [Ático com lances sobrepostos, forro e caixa lateral](renders/residencia-07-atico-v05/LEIA-ME.md) · [modelo nativo](projeto/residencia-07-atico-v05/atico-escadas-sobrepostas-caixa-lateral.blend)
- [Conferência das três versões](relatorios/residencia-07/estudo-instalacoes-atico/RELATORIO.md)

O modelo de instalações contém quatro estruturas com paredes em sálvia suave e 16 vistas de redes, por pavimento e em conjunto. Elétrica, água fria/quente, esgoto/ventilação e TV/telefone aparecem através de paredes parcialmente transparentes. Os caminhos embutidos em 3D são de estudo, com as alturas documentadas transcritas onde disponíveis.

O ático v05 propõe escritório e estar sob a cobertura, com mansardas centralizadas e prolongadas até a cumeeira principal. A nova escada repete os dois lances inferiores e a caixa de 1.000 L foi transferida à esquerda. Os quartos ficam preservados; o forro real é descontado das alturas livres. A cumeeira permanece em +9,40 m. O hall nominal de 65 cm, o vão em L, a escada, a laje e os apoios/cargas da caixa precisam de projeto específico para execução. As versões usam arquivos independentes, preservando a base documental.

Para reproduzir as imagens destas versões salvas:

```bash
python3 scripts/render_current_photoreal.py --resume
python3 scripts/run_blender.py --wsl-gpu --background projeto/residencia-07/casa-07-instalacoes.blend --python scripts/residence07_services.py -- --render-only
python3 scripts/run_blender.py --wsl-gpu --background projeto/residencia-07-atico-v05/atico-escadas-sobrepostas-caixa-lateral.blend --python scripts/residence07_attic_v05.py -- --render --group main
.tools/planta-venv/bin/python scripts/residence07_studies_delivery.py
python3 -m unittest discover -s scripts -p 'test_residence07*.py'
```

Os geradores recusam sobrescrever modelos existentes. Antes de regenerar um modelo, preserve a revisão anterior ou escolha outro destino em `config/residencia-07-estudos.json`. Os geradores antigos `house_…` e `rebuild_…` pertencem às revisões históricas; não controlam `renders/atual`.

## Base documental: residência 07 a partir das pranchas fornecidas

A nova revisão usa a tipologia da esquerda de `plantas/arq03.pdf`, que inclui explicitamente a residência 07. `arq04.pdf` controla os níveis e a cobertura; `arq01.pdf` identifica a implantação. A largura é 6,35 m até o eixo da geminação, o superior está em +2,70 m e os contornos respeitam o avanço frontal e os recuos posteriores do projeto. Esta base substitui as dimensões estimadas das revisões anteriores.

- [Índice da pasta organizada](renders/residencia-07/LEIA-ME.md)
- [Caderno completo](renders/residencia-07/00-cadernos/caderno-residencia-07.pdf) e [caderno técnico](renders/residencia-07/00-cadernos/plantas-tecnicas-residencia-07.pdf)
- [Galeria geral](renders/residencia-07/06-galerias/painel-geral.jpg) e [estrutura em 3D sem móveis](renders/residencia-07/06-galerias/painel-estrutura.jpg)
- [Planta térrea](renders/residencia-07/01-plantas-arquitetonicas/planta-terreo.pdf) e [superior](renders/residencia-07/01-plantas-arquitetonicas/planta-superior.pdf)
- [Estrutura 3D do térreo](renders/residencia-07/02-estrutura/3d/estrutura-terreo-3d.png), [superior](renders/residencia-07/02-estrutura/3d/estrutura-superior-3d.png), [conjunto](renders/residencia-07/02-estrutura/3d/estrutura-conjunto-3d.png) e [vista explodida](renders/residencia-07/02-estrutura/3d/estrutura-explodida-3d.png)
- [Blender editável](projeto/residencia-07/casa-07.blend) e [relatório de conferência e divergências](relatorios/residencia-07/RELATORIO.md)

São 29 câmeras nativas, incluindo quatro vistas da base estrutural sem mobiliário. As plantas técnicas incluem elétrica, água fria/quente, esgoto/ventilação, TV/telefone e leitura conjunta das instalações. Os símbolos, circuitos, bitolas, diâmetros e alturas dos complementares são preservados vetorialmente. O caderno técnico inclui as legendas, os detalhes e os esquemas originais completos. As folhas `cotas-originais-…` conservam as inscrições de ARQ03 para conferência.

Há diferenças entre algumas cotas, traços e áreas declaradas no projeto de 2011. Elas permanecem identificadas; o modelo não representa medição da situação construída. Não foram fornecidas fundações, armaduras ou dimensionamento resistente: a base estrutural 2D/3D mostra os elementos indicados na arquitetura. Móveis industriais, iluminação e os anexos dos fundos são proposta, em camadas separadas.

No Blender, escolha uma cena `R07_…`, pressione `Num 0` para a câmera e `F12` para renderizar. As cenas `R07_estrutura-…` não têm móveis. As plantas 3D cortam as paredes a 1,15 m para leitura; o conjunto mostra a altura completa. A vista explodida afasta uma cópia ilustrativa do superior em 4 m, mantendo os pavimentos de uso em 0,00 e +2,70 m. Os caminhos de saída seguem a organização do índice.

```bash
# Regenerar plantas vetoriais e instalações (ambiente local de leitura PDF):
.tools/planta-venv/bin/python scripts/residence07_plans.py
.tools/planta-venv/bin/python scripts/residence07_technical.py

# Renderizar novamente o modelo salvo, com CUDA no WSL:
python3 scripts/run_blender.py --wsl-gpu --background projeto/residencia-07/casa-07.blend \
  --python scripts/residence07_build.py -- --render-only

# Montar cadernos/galerias e validar a entrega em processo limpo:
.tools/planta-venv/bin/python scripts/residence07_plans.py --delivery-only
python3 scripts/residence07_delivery.py
python3 scripts/run_blender.py --background projeto/residencia-07/casa-07.blend \
  --python scripts/residence07_audit.py -- --require-renders
python3 -m unittest discover -s scripts -p 'test_residence07.py'
```

Para gerar outro modelo a partir da biblioteca independente, altere primeiro o destino em `config/residencia-07.json`; o gerador recusa substituir um `.blend` existente. Execute `residence07_build.py` sobre a base `projeto/fontes/mobiliario-industrial.blend`, reaproveitada somente para seis conjuntos de móveis. As dimensões, os vãos, as lajes, a escada e a cobertura são novos. O ambiente PDF local usa PyMuPDF 1.26.7 e Pillow 12.0.0; as imagens 3D são renderizadas no Blender/Cycles, sem alterações generativas.

## Industrial v04 descartada

A revisão v04, suas imagens e rascunhos foram excluídos a pedido do proprietário. Os móveis reutilizáveis ficam em `projeto/fontes/mobiliario-industrial.blend` e os recursos CC0 em `assets/biblioteca-industrial`, sem a arquitetura antiga.

## Estudos industriais anteriores

Os modelos [industrial v01](projeto/industrial-v01/casa-industrial.blend) e [industrial v03](projeto/industrial-v03/casa-fotografica.blend) permanecem como estudos de geometria anterior à reconstrução documental da unidade 07. Não controlam a planta atual. A geladeira do bar foi removida desses arquivos e da fonte do estudo v02; a da cozinha foi conferida e preservada.

Não há imagens de entrega nas pastas `renders/industrial-v01` e `renders/industrial-v03`. As seis imagens existentes do estudo v02 ficam em `historico/estudos/industrial-v02`, com atualização própria para retirar a geladeira do bar. A versão industrial atual sobre as medidas documentais é a v06, com a v05 mantida como revisão anterior.

[Recibo da manutenção dos modelos](relatorios/industrial-v06/remocao-geladeiras-fontes.json).

## Histórico — revisão 10, substituída pela base documental 07

O corpo principal dos dois pisos agora tem o mesmo contorno. Os fundos dos dois banheiros e do quarto superior coincidem com a parede da cozinha abaixo. O desencontro anterior de 0,85 m foi corrigido na geometria do Blender, e a profundidade interna foi redistribuída entre os ambientes.

- [Sobreposição dos pavimentos com contorno comum](historico/atual-pre-residencia07/renders/pavimentos-sobrepostos.png)
- [Plantas na mesma escala e origem](historico/atual-pre-residencia07/renders/pavimentos-alinhados.png)
- [Planta térrea atual](historico/atual-pre-residencia07/renders/planta-terreo.png)
- [Planta superior atual](historico/atual-pre-residencia07/renders/planta-superior.png)
- [Superior em 3D](historico/atual-pre-residencia07/renders/superior-3d.png)
- [Blender editável](projeto/casa-reconstruida.blend)
- [Relatório de alinhamento, dimensões e limites](historico/atual-pre-residencia07/relatorios/RELATORIO.md)

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

[Antes e depois do térreo](historico/atual-pre-residencia07/renders/antes-depois.png), [referência proporcional do superior](historico/atual-pre-residencia07/renders/comparacao-superior.png), [fotos do térreo](historico/atual-pre-residencia07/renders/comparacao-fotos.png), [fotos dos quartos](historico/atual-pre-residencia07/renders/comparacao-quartos.png) e [fachada](historico/atual-pre-residencia07/renders/comparacao-fachada.png) acompanham a revisão.

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
