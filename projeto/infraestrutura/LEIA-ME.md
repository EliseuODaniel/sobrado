# Infraestrutura — elétrica, hidráulica e forros

Abra [instalacoes-pavimentos-forro.blend](instalacoes-pavimentos-forro.blend). O arquivo começa na comparação lado a lado: térreo isolado à esquerda; os dois pavimentos com forros e caixa-d'água à direita.

**Caixa na posição original, sem construção do ático.** Centro X=5,35 / Y=3,175 m, base +5,45 m, conforme o estudo documental existente da HID04. Capacidade de 1.000 L; a forma externa permanece ilustrativa. A arquitetura de referência é a casa atual, sem mobiliário nesta apresentação.

| Cena | Conteúdo |
| --- | --- |
| `INFRA_01_COMPARACAO_GERAL` | Elétrica e hidráulica, térreo e conjunto lado a lado; cena inicial |
| `INFRA_02_COMPARACAO_ELETRICA` | Elétrica dos pavimentos, lado a lado |
| `INFRA_03_COMPARACAO_HIDRAULICA` | Água fria/quente, alimentação da caixa, limpeza e extravasor |
| `INFRA_04_CONJUNTO_FORRO_CAIXA` | Casa inteira com forros, cobertura original e caixa |
| `INFRA_05_CAIXA_ENTRADA_SAIDAS` | Aproximação da entrada e saídas da caixa |
| `INFRA_06_TERREO` | Redes do térreo isoladas |
| `INFRA_07_SUPERIOR` | Redes do segundo pavimento isoladas |

As paredes laterais permanecem completas. Paredes, lajes, forros e cobertura são translúcidos para enxergar os caminhos das redes. No Blender, use o seletor de cenas no alto da janela; use Material Preview para ver os materiais e as cores.

Cores: laranja = elétrica/eletrodutos; azul = água fria; vermelho = água quente; verde-água = extravasor; magenta = limpeza. As setas em trechos principais indicam o sentido representado do fluxo. As linhas têm espessura visual ampliada; o diâmetro nominal está nas propriedades de cada objeto. Os caminhos elétricos representam conexões de estudo, sem simular condutores e circuitos executivos.

## Evidências e limites

| Verificação em 14/11/2026 | Resultado |
| --- | --- |
| Arquivo reaberto e cena inicial | 7 cenas; comparação geral como padrão |
| Posição original da caixa | Conferida em X=5,35 / Y=3,175 / Z=5,45 m |
| Ausência de construção do ático | Conferida nas cenas; sem nova escada, mansardas ou caixa deslocada |
| Redes e marcadores | 132 trechos e 58 pontos com coordenadas conferidas |
| Forros e paredes laterais | Geometria presente; materiais translúcidos |
| Situação construída, pressão, circuitos e interferências | Não verificados; dependem de levantamento e projeto executivo |

As redes 3D reaproveitam o estudo interpretativo existente baseado em ELE04/05, HID04/05 e na arquitetura. A posição da caixa é documental; os percursos embutidos não foram levantados. A ligação esquemática ao aquecedor e os percursos de limpeza/extravasor são identificados como propostos; terminam em conexão externa pendente, sem conexão ao esgoto nem definição de descarga sobre área habitável. Não houve cálculo de pressão, vazão, carga, circuitos, queda de tensão ou verificação de interferências. Esta visualização não autoriza execução.

O forro inferior tem uma placa fina de referência para leitura da face inferior da laje; não declara o material nem a espessura real instalada. O forro/fechamento superior e a cobertura usam a geometria existente da base, sem adaptação para ático.

Novas imagens continuam adiadas. O arquivo está preparado para visualização no Blender e futura renderização. [Modelo e topologia](../../relatorios/infraestrutura/modelo.json) · [Validação](../../relatorios/infraestrutura/validacao.json).

## Correção da água quente

A rede quente foi revisada em 14/11/2026: cinco trechos idênticos extras foram eliminados; as quatro subidas sobrepostas deram lugar a uma coluna comum. Permanecem os cinco pontos de consumo: cozinha, dois lavatórios e dois chuveiros. O traçado usa distribuição compartilhada sob a laje, conforme leitura da HID04, e ramais dos banheiros/cozinha conforme HID05. Não foram acrescentados pontos quentes na lavanderia nem nos vasos.

A altura de 5,15 m do distribuidor é de apresentação, não uma cota extraída da prancha. Posições do aquecedor e dos ramais embutidos ainda são aproximadas. [Auditoria e limites](../../relatorios/infraestrutura/validacao-agua-quente/RELATORIO.md). Reabra o Blender para carregar a correção.
