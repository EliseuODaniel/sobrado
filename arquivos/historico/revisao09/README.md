# Casa — estudo atual, revisão 09

As proporções dos dois pavimentos foram revistas a partir da nova imagem: banheiros e quarto dos fundos mais profundos, quartos da frente mais curtos. Escada, lavabo, garagem e cozinha acompanham a mudança no térreo. Os lances continuam encostados, com 7 degraus iniciais, curva provisória de 6 degraus e 4 finais.

- [Planta térrea atual](renders/atual/planta-terreo.png)
- [Planta superior atual](renders/atual/planta-superior.png)
- [Dois pisos na mesma escala e origem](renders/atual/pavimentos-alinhados.png)
- [Nova imagem × proposta superior](renders/atual/comparacao-superior.png)
- [Térreo antes e depois](renders/atual/antes-depois.png)
- [Superior em 3D](renders/atual/superior-3d.png)
- [Blender editável](projeto/casa-reconstruida.blend)
- [Relatório de validação e limites](relatorios/atual/RELATORIO.md)

## Proporções e escala

A [imagem recebida](referencias-ajustes/superior-proporcoes-r09-594cf449.png) controla as proporções relativas das paredes. Ela foi preservada antes de trabalhar no modelo. Camas, sofá e louças mantêm suas dimensões aproximadas; as distorções dos pixels e das letras não foram reproduzidas como geometria.

Na escala estimada do estudo, o quarto dos fundos passa de aproximadamente 2,65 × 2,15 m para 2,65 × 2,85 m. A suíte fica com aproximadamente 2,65 × 3,55 m; o quarto da frente, 2,65 × 3,40 m. Os banheiros ficam compridos e estreitos, com aproximadamente 1,25 × 3,70 m cada, conforme a nova proporção proposta. É necessário conferir essas medidas no imóvel.

A escada e o lavabo foram deslocados 0,89 m para a frente nos dois pisos; a cozinha começa 0,90 m antes. A porta do lavabo preserva sua posição relativa na parede horizontal, junto ao acesso lateral. A continuação da garagem à direita fica mais curta. Mesa, geladeira, marcenaria e elementos da fachada foram ajustados ao novo encaixe.

O comprimento do primeiro lance ainda não foi medido: o espaço herdado resulta em aproximadamente 0,14 m por degrau reto, um avanço comprimido que precisa de calibração. A curva de seis degraus também é provisória. Este modelo serve para visualizar e corrigir a planta; não é um projeto construtivo dimensionado ou um estudo estrutural.

A projeção retangular do superior, incluindo varanda e vãos, não equivale à área exclusiva de 51,03 m² citada na análise secundária da matrícula. Nenhuma medida linear foi tratada como confirmada.

## Conferência dos dois pisos

`pavimentos-alinhados.png` registra as plantas na mesma escala e origem usando as câmeras ortográficas do Blender. Assim, a posição compartilhada da escada e dos limites externos pode ser comparada diretamente.

O hall fica sobre o trecho inicial baixo do primeiro lance. O vão permanece na parte alta, e não há faixa, parede ou laje separando os lances. O vidro fica na borda do hall, perpendicular aos lances. A relação entre escada, limite do quarto frontal, lavabo e garagem foi conferida nos vértices e paredes reais do modelo.

As fotos originais continuam como referência de elementos, materiais e relações. A [comparação do térreo](renders/atual/comparacao-fotos.png), a [dos quartos](renders/atual/comparacao-quartos.png) e a [da fachada](renders/atual/comparacao-fachada.png) foram atualizadas. A associação branco/frente e azul/fundos continua inferida. Os dois WCs seguem a proposta do usuário, sem confirmação por levantamento.

## Abrir, editar e marcar correções

Abra `projeto/casa-reconstruida.blend` no Blender 5.2 LTS. Use `PLANTA_Terreo_Cotas` e `PLANTA_Superior_Cotas` para as plantas. As cenas `FOTO_…` contêm as perspectivas; `CORTE_Lavabo_Escada` mostra o corte. Em `PLANTA_Terreo_Portas`, os degraus estão ocultos apenas para ler a porta.

No Outliner, selecione um conjunto como `Cama suíte` ou `MESA_JANTAR_original seis lugares` e pressione `G` para mover o conjunto. As portas possuem pivô `abrir/girar`. Material Properties permite alterar materiais; Light Properties, a potência das luzes em `Iluminacao`. `Num 0` volta à câmera e `F12` renderiza.

Para marcar no Paint, use as plantas atuais e salve uma cópia com outro nome. O modelo tem 23 cenas editáveis. As 31 fotos originais permanecem intactas, e 26 imagens únicas estão empacotadas. Os módulos em `ESTUDOS_Superior` são referências separadas de mobiliário.

## Regenerar e verificar

Os renders finais usam Cycles em CPU, 64 amostras, AgX e denoise. O Blender local é `.tools/blender-5.2.4-linux-x64/blender`; o launcher também aceita `BLENDER_EXECUTABLE`.

```bash
# Gerar estudo separado sem substituir a entrega:
python3 scripts/run_blender.py --background --factory-startup \
  --python scripts/build_house.py -- --project-root . --device cpu \
  --output historico/rascunhos/casa-nova-geracao.blend

# Comparar proporções com as linhas manuais do recorte:
python3 scripts/compare_proportions.py \
  --landmarks referencias-ajustes/proporcoes-r09-linhas.json

# Reabrir, verificar e renderizar o modelo atual:
python3 scripts/run_blender.py --background projeto/casa-reconstruida.blend \
  --python scripts/validate_house.py -- --project-root . --device cpu
python3 scripts/house_atlas.py
# Após conferir visualmente:
python3 scripts/finalize_ground_revision.py
```

`--no-render` limita a validação às verificações. `--preview` gera todas as vistas reduzidas antes do lote final. São 17 verificações de integridade, 40 de relações do térreo e 16 específicas de escada/superior, incluindo encaixe das camas sem deformação e alinhamento entre pisos. Os testes geométricos não confirmam medidas reais ou condições estruturais.

## Histórico

A revisão anterior foi preservada em [historico/revisao08/](historico/revisao08/INDICE.md), com hashes e registros de cópias/movimentos. Consulte o [índice histórico](historico/README.md). Prévias desta etapa ficam em `historico/rascunhos/revisao09/`.

Não houve commit, push ou publicação nesta etapa.
