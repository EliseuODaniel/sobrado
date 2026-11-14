# Térreo atual — revisão 07

UTC: 2026-11-10T18:14:06.968016+00:00

O modelo aproximado foi corrigido para conectar a cozinha ao acesso da porta horizontal do lavabo. A antiga divisória atravessava essa passagem. O trecho foi encurtado, o retorno da cozinha foi alinhado à escada e a laje preenchida acima da faixa liberada. A porta continua na marca preta confirmada pelo usuário. O lavabo permanece sob o segundo lance e o patamar.

| Obrigação | Recibo observado | Estado e limite |
| --- | --- | --- |
| Porta na posição confirmada | Fonte anotada preservada; orientação e posição da folha verificadas | VERIFIED no modelo aproximado |
| Ligação da cozinha até a porta | Diagnóstico anterior atingia a divisória; ray cast atual atinge a folha | VERIFIED na linha amostrada; não certifica dimensões reais |
| Cobertura da passagem liberada | Ray cast vertical atinge a laje | VERIFIED no ponto amostrado |
| Perspectivas e planta usam a mesma arquitetura | Identidade dos objetos, transformações e visibilidade nas cenas FOTO verificadas | VERIFIED para o conjunto arquitetônico auditado |
| Vistas atualizadas | 19 cenas renderizadas do mesmo SHA-256 do Blender editável; seis comparações | VERIFIED |
| Hipótese de imagem antiga fora de sincronia | 45 arquivos da revisão 06 conferidos, sem divergências | REFUTED nesse conjunto; o defeito estava na geometria e no enquadramento |
| Preservação das versões anteriores | 48 hashes da revisão 06 e 333 do histórico anterior conferidos | VERIFIED; nenhuma exclusão |
| Dimensões reais e fidelidade métrica às fotos | Levantamento não fornecido | UNKNOWN |

## Revisão visual

`sala-frente.png` usa um novo enquadramento para reduzir a obstrução da cadeira de jantar. A nova `acesso-lavabo.png` mostra porta e primeiro lance a partir da circulação da sala. As montagens `sala-frente-planta.png` e `acesso-lavabo-planta.png` relacionam a posição e direção dessas câmeras à planta: vermelho marca a câmera; laranja marca a porta.

A escada fica oculta somente na planta de leitura dos vãos (`porta-lavabo.png`) e nas vistas de corte indicadas. Está presente nas perspectivas internas. A fotografia `sala4.webp` continua sendo referência dos elementos e relações do ambiente; a câmera atual tem outra posição. Não se declara reprodução métrica das fotos.

`comparacao-planta.png` mantém a planta anotada ao lado da vista dos vãos. `antes-depois.png` compara as plantas 06 e 07. `comparacao-fotos.png` reúne oito referências internas e `comparacao-fachada.png`, duas externas. A anotação do usuário prevalece nas correções da porta, lavabo e passagem. Fachada e demais ambientes foram novamente renderizados da geometria compartilhada.

## Preservação e validação

Modelo ativo: `projeto/casa-reconstruida.blend`. Renders: `renders/atual/`. Fontes, configuração e scripts ficam nas pastas correspondentes da raiz. A revisão 06 completa está em `historico/revisao06/`; versões anteriores, em `historico/ate-revisao05/`. Prévias e enquadramentos preliminares estão em `historico/rascunhos/revisao07/`. As 31 imagens originais permanecem intactas. As 16 funções compartilhadas preservam seus hashes anteriores.

Passaram 16 verificações de integridade e 40 relações geométricas. Comandos: `validate_house.py`, `house_atlas.py`, `python3 -m py_compile scripts/*.py` e `git diff --check`. O manifesto liga configuração, scripts, Blender e imagens pelos hashes; os recibos dos comandos registram a execução sobre o arquivo de trabalho antes de sua promoção para o caminho ativo.

A checagem de cenas considera a laje superior intencionalmente oculta no corte da planta: identidade e geometria são compartilhadas, e a transformação mundial é comparada nas cenas em que o objeto está incluído. O primeiro teste desse corte foi ajustado, conforme `integridade-ajuste-corte.log`; a verificação final passou em `integridade-final.log`. O launcher também foi verificado para retornar erro quando um script Python falha (`launcher.json`).

## Limites

- Medidas reais, profundidade dos degraus e inclinação da escada; implantação visual aproximada
- Lado da dobradiça e sentido definitivo da porta; folha mostrada fechada
- Planta interna do segundo pavimento, detalhes da área de serviço e telhado sem levantamento

A escada representa o croqui aproximado; os degraus não foram dimensionados ou certificados para execução. A distribuição do segundo pavimento continua pendente. Não houve commit, push ou publicação.
