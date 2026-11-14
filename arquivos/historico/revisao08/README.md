# Casa — estudo atual, revisão 08

O segundo pavimento agora tem os três quartos nas posições indicadas pelo usuário: suíte à frente esquerda, quarto à frente direita e quarto nos fundos. A escada tem **7 degraus iniciais, curva provisória com 6 degraus e 4 degraus finais**. O lance final termina antes do início do primeiro, na chegada à laje. **Os lances são encostados: não há faixa de piso, parede ou separação entre eles.**

- [Planta superior atual](renders/atual/planta-superior.png)
- [Croqui recebido × proposta superior](renders/atual/comparacao-superior.png)
- [Superior em 3D](renders/atual/superior-3d.png)
- [Chegada da escada × foto original](renders/atual/comparacao-escada.png)
- [Quartos × fotos originais](renders/atual/comparacao-quartos.png)
- [Planta térrea atualizada](renders/atual/planta-terreo.png)
- [Porta do lavabo e posição da câmera](renders/atual/acesso-lavabo-planta.png)
- [Blender editável](projeto/casa-reconstruida.blend)
- [Relatório de hipóteses e validação](relatorios/atual/RELATORIO.md)

## O que está confirmado e o que é proposta

As posições relativas dos três quartos vêm do [último croqui superior preservado](referencias-ajustes/superior-croqui-26a026a1.png). A associação do quarto branco à frente e do azul aos fundos é uma interpretação das fotos. Os dois banheiros seguem agora a última proposta: ficam lado a lado à esquerda, até a parede dos fundos. O WC da suíte é acessado pela suíte; o WC social tem porta lateral para o hall. Essa distribuição ainda é uma sugestão do usuário, sem levantamento. Portas e janela posterior também permanecem propostas.

O usuário informou sete degraus antes da curva e quatro depois. A quantidade na curva não foi confirmada; seis foram usados para este estudo. Todas as dimensões lineares, pé-direito e espessuras continuam estimados. Este arquivo serve para visualizar e corrigir a distribuição; não é um projeto construtivo dimensionado.

O perímetro aproximado anterior do superior foi mantido, sem a ampliação de fundos usada no estudo descartado. A referência secundária de 51,03 m² não comprova largura ou comprimento. **A escala do primeiro lance ainda está comprimida:** o espaço anterior resulta em aproximadamente 0,14 m por degrau reto. Esse valor não é dimensão real nem proposta de execução. É necessária uma medida do comprimento do lance para recalibrar a planta sem deslocar a porta confirmada do lavabo.

## Escada e impacto no térreo

O primeiro lance é mais longo que o último e ambos se encostam pela lateral. O hall ocupa a área sobre o trecho inicial baixo do primeiro lance, conforme a sobreposição indicada no último desenho; o vão permanece na parte alta. A porta horizontal do lavabo permanece na marca preta confirmada. A cozinha e a garagem preservam a implantação anterior. O guarda-corpo de vidro fica na borda do hall, perpendicular aos lances, sem dividi-los.

A laje superior cobre os três primeiros degraus baixos; o restante do lance fica no vão. Por isso a planta superior não mostra todos os sete degraus inteiros. A legenda indica a contagem total e os três sob a laje. A vista `escada-superior.png` mostra a chegada com quatro degraus e o vidro inspirado em `escada1.webp`.

As cenas fotográficas compartilham a mesma arquitetura. Em `porta-lavabo.png`, a escada está oculta apenas para ler os vãos. As [comparações do térreo](renders/atual/comparacao-fotos.png) e da [fachada](renders/atual/comparacao-fachada.png) foram regeneradas do arquivo atual.

## Arquivos e edição

| Finalidade | Arquivo |
| --- | --- |
| Marcar o superior no Paint | `renders/atual/planta-superior.png` |
| Marcar o térreo no Paint | `renders/atual/planta-terreo.png` |
| Editar paredes, portas, degraus e móveis | `projeto/casa-reconstruida.blend` |
| Rever parâmetros e hipóteses | `config/planta-casa.json` |
| Conferir execução e hashes | `relatorios/atual/` |
| Consultar versões anteriores | `historico/` |

Salve marcações novas com outro nome para preservar os renders. As 31 imagens originais continuam em `referencias-originais/`; 26 fotos únicas estão empacotadas no Blender.

Abra o editável no Blender 5.2 LTS. As cenas `PLANTA_Superior_Cotas` e `PLANTA_Superior` mostram o novo andar; `FOTO_Chegada_Escada`, `FOTO_Suite`, `FOTO_Quarto_Frente` e `FOTO_Quarto_Fundos` são as novas perspectivas. `PLANTA_Terreo_Portas` e `CORTE_Lavabo_Escada` são cortes identificados. Os módulos `ESTUDOS_Superior` continuam separados, como referências de mobiliário. Há 23 cenas editáveis.

No Outliner, expanda `AMB_suite`, `AMB_quarto_branco` ou `AMB_quarto_azul` e selecione o conjunto da cama; `G` move o móvel inteiro. As portas superiores têm um pivô `abrir/girar`. Selecione uma peça e abra Material Properties para trocar cor ou rugosidade; as luzes ficam em `Iluminacao`, com potência em Light Properties. `Num 0` volta à câmera da cena e `F12` renderiza.

Os renders desta revisão usam Cycles em CPU, 64 amostras, AgX e denoise.

## Gerar e conferir

O Blender portátil local fica em `.tools/blender-5.2.4-linux-x64/blender`. O launcher aceita `BLENDER_EXECUTABLE` e propaga falhas dos scripts Python.

```bash
# Nova versão de estudo, sem substituir o editável atual:
python3 scripts/run_blender.py --background --factory-startup \
  --python scripts/build_house.py -- --project-root . --device cpu \
  --output historico/rascunhos/casa-nova-geracao.blend

# Validar e renderizar o arquivo atual:
python3 scripts/run_blender.py --background projeto/casa-reconstruida.blend \
  --python scripts/validate_house.py -- --project-root . --device cpu
python3 scripts/house_atlas.py
# Depois da inspeção visual:
python3 scripts/finalize_ground_revision.py
```

`--no-render` em `validate_house.py` limita a execução às verificações. `render_revision.py --preview --upper-only`, no Python do Blender, gera prévias dos quartos, da escada e do superior. Há 17 verificações de integridade, 40 relações do térreo e 14 verificações específicas de escada/superior; nenhuma delas confirma medidas reais ou os banheiros propostos.

## Histórico

A revisão 07 foi preservada em [historico/revisao07/](historico/revisao07/INDICE.md). Revisões 06 e anteriores continuam nos respectivos arquivos. Os modelos e prévias de trabalho desta etapa ficam em `historico/rascunhos/revisao08/`, com hashes registrados no início da revisão. Consulte o [índice histórico](historico/README.md).

As referências e os prompts foram preservados. Nenhum commit, push ou publicação foi realizado.
