# Revisão 10 — contorno comum dos pavimentos

UTC: 2026-11-10T20:46:16.640592+00:00

Foi corrigido um desencontro real de 0,85 m no modelo anterior: o superior terminava em y=6,75 m e a cozinha em y=7,60 m. Agora o fundo dos dois WCs e do quarto superior é uma parede contínua no mesmo plano da cozinha. A laje dos dois pisos tem o mesmo contorno no corpo principal: x=0 a 5,60 m e y=−1,65 a 7,60 m, ou aproximadamente 5,60 × 9,25 m na escala estimada.

Esse contorno inclui a garagem sob o volume superior no térreo e a varanda no superior. O pátio frontal e a churrasqueira/lavanderia posteriores são anexos térreos, fora do corpo principal. O vão da escada é retirado da laje superior; igualdade de contorno não significa igualdade de área líquida ou área registral.

| Obrigação | Evidência | Estado e limite |
| --- | --- | --- |
| Contorno externo comum | Extensões dos vértices das lajes dos dois pisos, reabertas do Blender | VERIFIED no corpo principal |
| Fundos dos WCs/quarto no plano da cozinha | Faces externas nativas em y=7,675 m, nas duas alturas | VERIFIED; eixos coincidem em y=7,60 m |
| Ausência de faixas de laje faltantes | Comparação célula a célula da cobertura real, com exceção explícita do vão da escada | VERIFIED |
| Escada, lavabo, garagem e quarto frontal alinhados | Vértices e paredes reais, percursos do hall e acesso ao lavabo | VERIFIED nas amostras auditadas |
| Distribuição proporcional e camas preservadas | Limites internos redistribuídos e dimensões das camas comparadas à revisão anterior | VERIFIED no estudo |
| Geometria, renders e editável sincronizados | Mesmo SHA-256, 23 renders e 11 comparações | VERIFIED |
| Dimensões reais e solução estrutural | Sem levantamento ou cálculo de estrutura | UNKNOWN |

## Antes e depois

`encaixe-antes.json` registra os três testes novos aplicados à revisão 09. O contorno e as faces posteriores não coincidiam. `encaixe-pavimentos.json` registra os mesmos testes no arquivo novo, todos aprovados. Esses recibos avaliam vértices e faces reais do modelo, não apenas valores escritos na configuração ou o zoom das imagens.

`pavimentos-alinhados.png` apresenta as plantas na mesma escala e origem. `pavimentos-sobrepostos.png` combina os dois pisos e marca o contorno comum em branco. A linha dos fundos mostra o alinhamento da cozinha com os dois banheiros e o quarto do superior.

## Redistribuição interna

| Ambiente superior | Dimensões internas aproximadas | Profundidade anterior → atual |
| --- | --- | --- |
| Suíte · posição conforme croqui | ≈ 2.65 × 3.95 m | 3.55 → 3.95 m |
| WC suíte · hipótese | ≈ 1.25 × 4.15 m | 3.70 → 4.15 m |
| WC social · hipótese | ≈ 1.25 × 4.15 m | 3.70 → 4.15 m |
| Quarto dos fundos | ≈ 2.65 × 3.25 m | 2.85 → 3.25 m |
| Quarto da frente | ≈ 2.65 × 3.70 m | 3.40 → 3.70 m |

A profundidade adicional foi distribuída entre os quartos e banheiros. A escada foi deslocada 0,30 m junto com o lavabo e a divisão da garagem, mantendo largura, contato entre os lances e degraus. A cozinha passa a começar em y=4,30 m; seu fundo permanece em y=7,60 m. A porta horizontal do lavabo e o acesso lateral acompanham esse encaixe.

As posições relativas do croqui foram preservadas. O critério explícito mais recente do usuário — fundos no plano da cozinha — controla o contorno. A comparação com o desenho manual continua sendo uma referência proporcional, sem escala levantada. Os banheiros permanecem compridos e estreitos, com aproximadamente 1,25 × 4,15 m, e requerem medição.

O corpo principal tem projeção retangular de 51.80 m² na hipótese atual. Isso não comprova os 51,03 m² de área exclusiva citados na análise secundária da matrícula: varanda, vãos, paredes e critérios de área não foram conciliados com o documento original.

## Validação e arquivos

Passaram 18 verificações de integridade, 40 de relações do térreo, 16 de escada/superior e os três testes específicos de contorno e coplanaridade. Comandos: `validate_house.py`, `house_atlas.py`, `compare_proportions.py --landmarks referencias-ajustes/proporcoes-r09-linhas.json`, `python3 -m py_compile scripts/*.py` e `git diff --check`.

O arquivo atual é `projeto/casa-reconstruida.blend`. As 23 prévias foram inspecionadas antes dos renders finais em CPU no Blender 5.2.4 LTS. A revisão 09 está preservada em `historico/revisao09/`, com 71 registros. Fotos originais e referências foram preservadas. Não houve commit, push ou publicação.

## Limites

O avanço do primeiro lance ainda está comprimido em cerca de 0.14 m por degrau na escala herdada; exige uma medida real do comprimento do lance. A curva de seis degraus também permanece estimada. O alinhamento corrigido é geométrico e não aprova a escada para execução.

- Dimensões reais sem medida de referência
- Curva estimada em seis degraus e comprimento do primeiro lance ainda comprimido
- Não é validação estrutural ou de execução
- Banheiros ainda são proposta, não localização levantada
- Compatibilidade estrutural, cargas e dimensionamento construtivo não estudados
- Projeção retangular não equivale à área exclusiva da análise registral secundária
