# Revisão 09 — proporções dos dois pavimentos

UTC: 2026-11-10T20:14:10.854859+00:00

O novo recorte do usuário foi interpretado pelas linhas das paredes: banheiros e quarto dos fundos mais profundos; quartos da frente mais curtos. Móveis, camas e louças preservam dimensões aproximadas próprias, sem reproduzir as distorções dos pixels. A escada, o lavabo e a divisão da garagem foram deslocados 0,89 m para a frente, e a cozinha começa 0,90 m antes. O limite posterior do superior foi ajustado de y=6,95 para y=6,75 m. Todos esses valores pertencem à escala estimada do estudo.

| Obrigação | Evidência | Estado e limite |
| --- | --- | --- |
| Proporções mais próximas do novo croqui | `proporcoes.json`, linhas manuais preservadas e comparação visual | VERIFIED como aproximação relativa ao desenho |
| Escada alinhada nos dois pisos e com lavabo/garagem | Vértices dos degraus, paredes e vãos, auditados no Blender | VERIFIED geometricamente |
| 7 degraus iniciais, curva e 4 finais, lances colados | Contagem e limites laterais dos meshes | VERIFIED na representação; curva ainda estimada |
| Camas cabem sem serem deformadas | Bounding boxes reais versus limites dos quartos e dimensões da revisão 08 | VERIFIED nas amostras auditadas |
| Portas e circulação do hall | Ray casts aos três quartos e aos dois WCs | VERIFIED nos percursos amostrados |
| Arquivo editável e imagens sincronizados | SHA-256 único, 23 renders e dez comparações | VERIFIED |
| Projeção dos pisos na mesma escala | Registro das duas câmeras ortográficas em `pavimentos-alinhados.png` | VERIFIED para revisão visual geométrica |
| Fontes e versões anteriores preservadas | Hashes de fotos, croqui e quatro históricos | VERIFIED |
| Medidas reais, escada executável e estrutura | Sem levantamento e sem cálculo estrutural | UNKNOWN |

## Dimensões de estudo

| Ambiente superior | Dimensões internas aproximadas | Profundidade anterior → atual |
| --- | --- | --- |
| Suíte · posição conforme croqui | ≈ 2.65 × 3.55 m | 4.45 → 3.55 m |
| WC suíte · hipótese | ≈ 1.25 × 3.70 m | 3.00 → 3.70 m |
| WC social · hipótese | ≈ 1.25 × 3.70 m | 3.00 → 3.70 m |
| Quarto dos fundos | ≈ 2.65 × 2.85 m | 2.15 → 2.85 m |
| Quarto da frente | ≈ 2.65 × 3.40 m | 4.29 → 3.40 m |

As dimensões descontam uma espessura de parede do retângulo nominal. A largura externa continua estimada em 5.60 m. A projeção retangular superior é de 47.04 m² incluindo varanda e vãos. Isso não comprova nem substitui os 51,03 m² exclusivos citados na análise secundária da matrícula.

Os limites lidos manualmente no recorte foram normalizados pelo contorno externo. A maior diferença de borda caiu aproximadamente de 8.9% para 1.3% desse contorno. Esse indicador mostra aproximação ao croqui; não mede o imóvel ou avalia o programa arquitetônico. Os banheiros ficaram longos e estreitos (aproximadamente 1,25 × 3,70 m), conforme a proporção proposta, e precisam ser conferidos no local.

## Efeito no térreo

A nova posição mantém o lavabo sob a faixa do último lance, com porta horizontal e acesso pela lateral da sala. A continuação direita da garagem termina em y=1,90 m (antes 2,79 m); a cozinha começa em y=4,00 m (antes 4,90 m). Sala/jantar, mesa, geladeira e marcenaria foram reposicionados para esse encaixe. O tamanho das camas e dos móveis soltos foi preservado. A fachada, a janela pequena, a vegetação e a cobertura posterior acompanham os novos limites.

A escada tem sete degraus iniciais, seis de curva provisórios e quatro finais. A laje cobre o trecho baixo junto ao hall. O avanço reto continua comprimido em aproximadamente 0.14 m por degrau na escala herdada; ele depende de uma medida real do comprimento do lance. O alinhamento e os testes não aprovam esse valor para execução.

## Arquivos e validação

Editável: `projeto/casa-reconstruida.blend`. Plantas e perspectivas: `renders/atual/`. `pavimentos-alinhados.png` coloca os dois pisos na mesma escala; `comparacao-superior.png` mantém o novo recorte ao lado do modelo; `antes-depois.png` mostra a mudança no térreo. Os 23 enquadramentos foram inspecionados em prévia antes da renderização final.

Passaram 17 verificações de integridade, 40 de relações do térreo e 16 de escada/superior. Comandos: `compare_proportions.py --landmarks referencias-ajustes/proporcoes-r09-linhas.json`, `validate_house.py`, `house_atlas.py`, `python3 -m py_compile scripts/*.py` e `git diff --check`. O novo modelo foi reaberto e renderizado em CPU no Blender 5.2.4 LTS. A revisão 08 foi preservada em `historico/revisao08/`, com 68 registros. Nada foi publicado no GitHub nesta etapa.

## Limites

- Dimensões reais sem âncora medida
- Quantidade e forma da curva ainda estimadas
- Comprimento horizontal do primeiro lance comprimido na estimativa anterior
- Banheiros ainda são proposta, não localização levantada
- Compatibilidade estrutural, cargas e dimensionamento construtivo não estudados
- Projeção retangular não equivale à área exclusiva da análise registral secundária
