# Residência 07 — conferência da reconstrução

Data de conferência: 2026-11-12T13:36:02.746575+00:00. Entrega **VERIFICADA para o escopo documental e visual abaixo**.

O projeto foi reconstruído pela tipologia da esquerda de ARQ03. As revisões baseadas em fotos e croquis permanecem preservadas; não controlam as medidas desta revisão. A entrega contém plantas redesenhadas, plantas humanizadas, quatro vistas 3D sem mobiliário, fachadas, ambientes e instalações vetoriais provenientes dos complementares.

Foram consideradas a adaptação da base estimada e uma reconstrução métrica independente. Foi adotada a segunda opção: configuração geométrica única para plantas e Blender, preservando apenas móveis reaproveitáveis. É uma escolha pragmática para este repositório, com validação determinística; não se apresenta como um modelo BIM de engenharia dimensionado.

## Evidências e limites do resultado

| Obrigação | Recibo | Situação |
| --- | --- | --- |
| Identificar a unidade 07 | ARQ03, lista de unidades da tipologia; `fontes.json` e recortes em `fontes/` | VERIFICADO |
| Reconstruir paredes, vãos, lajes, escada e cobertura | `modelo.json` e `validacao-modelo.json` | 287 verificações; passaram |
| Compartilhar a geometria das plantas e do Blender | `config/residencia-07.json`, hash nas 29 cenas | VERIFICADO pela auditoria do arquivo reaberto |
| Preservar as fontes fornecidas | SHA-256 de cada arquivo em `fontes.json` | VERIFICADO pela auditoria |
| Instalações alinhadas à unidade correta | `instalacoes.json` | 24 verificações; passaram |
| Renderizar todas as câmeras do modelo salvo | `renders.json`, hashes das imagens e do `.blend` | 29 de 29 imagens verificadas |
| Organizar sem perder conteúdo | `organizacao.json` | Arquivos movidos com hashes preservados |
| Conferência final de cadernos e imagens | `validacao-completa.json` | VERIFICADO |
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
| sala | 18.01 | 18.1303 | +0.1203 |
| cozinha | 7.84 | 7.7000 | -0.1400 |
| garagem | 5.80 | 5.7000 | -0.1000 |
| lavabo | 1.90 | 2.3275 | +0.4275 |
| suite | 11.16 | 11.3400 | +0.1800 |
| quarto-frente | 8.69 | 8.5400 | -0.1500 |
| quarto-fundos | 7.84 | 7.7000 | -0.1400 |
| banheiro-suite | 4.50 | 4.5000 | -0.0000 |
| banheiro-social | 4.35 | 4.5000 | +0.1500 |
| sacada | 2.02 | 1.5750 | -0.4450 |
| circulacao | 2.30 | 1.3000 | -1.0000 |

As áreas declaradas de 40,77 m² no térreo, 48,92 m² computáveis e 2,11 m² não computáveis no superior, total de 91,80 m² e lote de 81,60 m² são transcrições dos documentos. Não equivalem a uma medição nova. A tabela compara polígonos de leitura dos ambientes, sem substituir o quadro legal de áreas.

Os contornos gerais oferecem uma conferência independente: o polígono da laje térrea, incluindo garagem, resulta em 40,77 m², e o contorno bruto superior resulta em 51,03 m². Esses dois valores fecham com ARQ03, embora persistam as diferenças internas da tabela. O vão da escada é subtraído na malha da laje; a área bruta de contorno não é a área líquida da laje.

A escada foi reconstituída com cinco pisos retos, seis compensados e cinco de retorno: 16 espelhos de 0,16875 m vencem 2,70 m. O trecho reto tem avanço de 0,25 m. A contagem completa, as folgas e o dimensionamento executivo precisam ser conferidos; os PDFs não oferecem uma seção estrutural da escada. Os apoios e a viga frontal são representações gráficas da arquitetura, sem seções resistentes confirmadas.

## O que está nas plantas estruturais 3D

As cenas `R07_estrutura-terreo-3d` e `R07_estrutura-superior-3d` mostram lajes, paredes, escada e vãos, sem qualquer coleção de móveis. As paredes são cortadas a 1,15 m para leitura. `R07_estrutura-conjunto-3d` mantém a altura completa das paredes e omite a cobertura. `R07_estrutura-explodida-3d` mostra uma cópia do superior afastada 4 m, exclusivamente para explicar a sobreposição; as cenas de uso conservam Z=0,00 e +2,70 m.

As quatro imagens atuais usam paredes sálvia suave, lajes creme e escada areia, vindas de `casa-07-instalacoes.blend`. As cenas originais permanecem na base com material neutro; a revisão de materiais tem recibo próprio em `estudo-instalacoes-atico/instalacoes-modelo.json`. A auditoria confere cada imagem contra o seu arquivo nativo. A orientação das faces dos prismas fechados foi conferida; a correção não moveu vértices. Não há fundações, ferragens ou vigas dimensionadas inventadas para preencher dados ausentes.

## Instalações

O caderno técnico tem 14 folhas organizadas e 22 páginas com os anexos completos. Usa ELE04/05/06, HID04/05/08 e TV-TEL04/05. Foram preservados os símbolos e os textos gráficos de circuitos, bitolas, diâmetros, materiais e alturas. Os traçados foram recortados para a tipologia da unidade 07; pontos compartilhados na divisa continuam completos nas pranchas originais anexas.

As folhas elétricas e de TV/telefone originais dizem “sem escala”. O registro pela arquitetura não torna seus arcos e linhas comprimentos executivos de eletrodutos ou cabos. As sobreposições permitem leitura conjunta; não constituem verificação de interferências tridimensionais. O quadro de esquadrias de ARQ03 conserva um cabeçalho “residência 01”; seus códigos foram cruzados com os vãos efetivamente desenhados da tipologia interna.

## Interiores, contexto e reprodução

A linguagem industrial da versão anterior foi mantida como proposta: sofá e cadeiras nativos reaproveitados, novos armários e mobiliário adaptados à planta, concreto, madeira, aço preto e tecidos verdes. Jardim e implantação externa do cenário são ilustrativos. Churrasqueira e lavanderia posteriores, baseadas nas fotos anteriores, ficam somente em `R07_Proposta_Fundos` e nas respectivas cenas; não foram incorporadas à arquitetura original dos PDFs.

O modelo tem 2276 objetos e 29 cenas. As imagens são renderizações Cycles do arquivo salvo, em 1920 × 1440 e até 192 amostras adaptativas, com CUDA. Não houve retoque generativo. As texturas usadas estão empacotadas e não há bibliotecas vinculadas; os recursos reaproveitados mantêm suas fontes em `assets/industrial-v03` e `assets/industrial-v04`.

Abra o [índice organizado](../../renders/residencia-07/LEIA-ME.md), o [modelo Blender](../../projeto/residencia-07/casa-07.blend) ou os comandos de reprodução no [README](../../README.md). Testes locais: `testes.log`. O arquivo final do modelo tem SHA-256 `cc82299b375aeb74635724a8e21972851bac1c4fe806819f20697a4fb374c0c8`.
