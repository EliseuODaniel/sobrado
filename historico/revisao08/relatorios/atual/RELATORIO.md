# Estudo atual — revisão 08

UTC: 2026-11-10T19:41:09.632790+00:00

A escada passou a ter sete degraus no primeiro lance, seis degraus provisórios na curva e quatro no lance final. A chegada final termina antes do início do primeiro lance em planta. Os dois lances são colados lateralmente, sem faixa, laje ou parede entre eles; o vidro fica somente na borda do hall, perpendicular aos lances. Os quartos foram implantados conforme o croqui `referencias-ajustes/superior-croqui-26a026a1.png`: suíte à frente esquerda, quarto à frente direita e quarto nos fundos. Os dois banheiros seguem a proposta mais recente, lado a lado à esquerda até os fundos, sem a faixa de uso desconhecido do estudo anterior. O WC suíte é acessado pela suíte e o WC social, pela lateral do hall. A suíte foi alongada e sua porta de entrada deslocada para a parede lateral junto do hall.

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
| Suíte · posição conforme croqui | ≈ 2.65 × 4.45 m | ≈ 11.79 m² |
| WC suíte · hipótese | ≈ 1.25 × 3.00 m | ≈ 3.75 m² |
| WC social · hipótese | ≈ 1.25 × 3.00 m | ≈ 3.75 m² |
| Quarto dos fundos | ≈ 2.65 × 2.15 m | ≈ 5.70 m² |
| Quarto da frente | ≈ 2.65 × 4.29 m | ≈ 11.37 m² |

Essas dimensões descontam uma espessura de parede do retângulo de cada ambiente. Não são levantamento nem áreas registrais. Portas, shafts e medidas finais dos banheiros ainda podem alterar a distribuição.

A largura externa estimada permanece 5.60 m e o limite posterior superior está em y=6.95 m, como na envoltória anterior. O estudo com faixa entre os lances e ampliação dos fundos foi descartado e preservado em `historico/rascunhos/revisao08/lances-separados/` após a correção do usuário. A projeção retangular é 48.16 m² incluindo varanda e vãos, antes de qualquer conciliação registral. A análise secundária de 51,03 m² exclusivos não foi usada como prova do perímetro.

A porta do lavabo permanece na marca preta confirmada e a implantação anterior de cozinha e garagem foi preservada. A laje do hall cobre a parte baixa inicial do primeiro lance (três degraus na hipótese atual), reproduzindo a sobreposição desenhada no croqui; não há piso ou separação entre os lances. O vazio é contínuo. A guarda de vidro está na borda do hall, perpendicular ao primeiro lance.

Na hipótese de altura entre pisos de 2.90 m, o desnível de cada degrau fica em cerca de 0.171 m e o avanço reto em 0.140 m. **O avanço de cerca de 0,14 m está comprimido pelo espaço estimado anterior e não deve ser tomado como dimensão real ou solução executiva.** O usuário foi consultado sobre o comprimento do primeiro lance para corrigir a escala. Não foi alargada a casa ou mudada a porta por suposição. Os valores não foram medidos ou aprovados para execução. O leque da curva é uma aproximação visual editável.

## Conferência visual e execução

`comparacao-superior.png` coloca o croqui ao lado da planta. `comparacao-escada.png` relaciona a foto da chegada com a nova perspectiva. `comparacao-quartos.png` reúne as referências dos três quartos; a associação branco/frente e azul/fundos é inferida. As comparações do térreo e fachada também foram regeneradas. `proporcoes-croqui.json` registra uma leitura visual manual das linhas do croqui e sua comparação normalizada com os limites dos cômodos; essa comparação é proporcional, sem atribuir medidas reais ao desenho. Nenhuma imagem de origem foi alterada.

Passaram 17 verificações de integridade, 40 de relações do térreo e 14 de escada/superior. Comandos: `validate_house.py`, `house_atlas.py`, `python3 -m py_compile scripts/*.py` e `git diff --check`. A geometria compartilhada foi conferida entre planta e perspectivas. A checagem das câmeras usa os limites locais dos objetos para evitar falsos positivos na porta diagonal. As câmeras foram conferidas em suas cenas com as transformações dos objetos avaliadas. O arquivo atual foi reconstruído pelo gerador depois da correção dos lances encostados. `camera-quarto-frente.json` registra o ajuste posterior de enquadramento para afastar a vista da porta aberta, sem alterar a geometria. O gerador usa a mesma posição de câmera na configuração.

O editável atual é `projeto/casa-reconstruida.blend`. A revisão 07 está em `historico/revisao07/`, com 103 registros de cópias e movimentos recuperáveis. Estudos desta etapa ficam em `historico/rascunhos/revisao08/`. Não houve commit, push ou publicação.

## O que continua sem confirmação

- Contagem e forma reais dos degraus na curva; seis adotados provisoriamente
- Comprimento real do primeiro lance e escala linear: avanço reto comprimido de aproximadamente 0,14 m na escala anterior; demais medidas também estimadas
- Posições e dimensões reais dos banheiros; agora seguem a proposta do último croqui
- Associação do quarto branco à frente e azul aos fundos; posições dos três quartos confirmadas, identidade fotográfica inferida
- Portas superiores, janelas posteriores e sentido definitivo da porta do lavabo
