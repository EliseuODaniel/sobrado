# Casa — térreo atual, revisão 06

Esta é a entrega atual baseada na nova planta anotada e na confirmação do usuário: **a porta do lavabo fica no traço preto, na parede horizontal superior do lavabo**. O vão anterior na lateral da sala foi fechado. O limite do lavabo segue o retângulo vermelho e a área branca permanece como acesso, com o início da escada recuado.

- [Planta completa atual](renders/atual/planta-terreo.png)
- [Porta do lavabo legível, com escada oculta](renders/atual/porta-lavabo.png)
- [Nova planta anotada × modelo](renders/atual/comparacao-planta.png)
- [Térreo em 3D](renders/atual/terreo-3d.png)
- [Blender editável atual](projeto/casa-reconstruida.blend)
- [Fonte confirmada pelo usuário](referencias-ajustes/terreo-revisao06-porta-lavabo.png)
- [Relatório de validação](relatorios/atual/RELATORIO.md)

## Qual arquivo usar

| Finalidade | Arquivo ou pasta atual |
| --- | --- |
| Marcar outra correção no Paint | `renders/atual/planta-terreo.png` |
| Conferir a porta sem os degraus encobrindo | `renders/atual/porta-lavabo.png` |
| Editar objetos, paredes, portas e materiais em 3D | `projeto/casa-reconstruida.blend` |
| Parâmetros e hipóteses geométricas | `config/planta-casa.json` |
| Renders e comparações desta entrega | `renders/atual/` |
| Validação, hashes e relatório desta entrega | `relatorios/atual/` |
| Versões anteriores e arquivos legados | `historico/` |

Para futuras marcações, salve uma cópia com outro nome antes de enviar. A imagem original desta correção já está preservada em `referencias-ajustes/`.

## Porta, passagem e escada

A porta está na parede horizontal acima do lavabo, acessada pela passagem marcada em branco. A indicação gráfica escura nas plantas identifica a posição da folha; não é outro elemento construtivo. A vista `porta-lavabo.png` oculta a escada apenas para mostrar paredes, porta e louças. Os degraus continuam presentes na planta completa e no arquivo 3D.

O lado da dobradiça e o sentido definitivo de abertura não foram informados. A folha está fechada, sem arco de abertura presumido. O conjunto `Porta lavabo — abrir/girar` permite ajustar a abertura depois.

O lavabo ocupa a faixa indicada em vermelho, sob o segundo lance e o patamar. O recuo do primeiro lance acompanha a área branca da nova planta. **Profundidade dos degraus, inclinação, pé-direito e demais dimensões continuam hipóteses visuais, sem levantamento métrico.** Este arquivo é um estudo de visualização, não um projeto construtivo dimensionado.

Sala, cozinha, churrasqueira, lavanderia, entrada diagonal, garagem e fachada foram preservadas nas demais relações da revisão anterior. As [comparações com as fotos](renders/atual/comparacao-fotos.png) usam a nova planta como referência prioritária para a porta e a passagem. A [comparação da fachada](renders/atual/comparacao-fachada.png) continua disponível.

O segundo pavimento permanece sem distribuição interna confirmada. Seus cinco cômodos continuam como estudos separados em `ESTUDOS_Superior`; nenhuma nova planta superior foi criada nesta etapa.

## Abrir no Blender

Abra `projeto/casa-reconstruida.blend` no Blender 5.2 LTS. A cena inicial é `PLANTA_Terreo`; `Num 0` entra na câmera e `F12` renderiza.

- `PLANTA_Terreo_Cotas`: planta completa.
- `PLANTA_Terreo_Portas`: mesma implantação com escada oculta para ler os vãos.
- `CORTE_Lavabo_Escada`: encaixe do lavabo sob a escada, com duas paredes ocultas no corte.
- `FOTO_…`: dez ângulos de comparação, incluindo fachada, sala, cozinha, churrasqueira, lavanderia e lavabo.
- `CASA_Completa`, envoltória superior e estudos separados: vistas complementares.

Há 18 cenas editáveis. As 26 fotos únicas estão empacotadas; os 31 arquivos originais continuam preservados em `referencias-originais/`. As fotografias não são fundos dos renders.

## Gerar e conferir

O Blender portátil local é `.tools/blender-5.2.4-linux-x64/blender`. O launcher também aceita `BLENDER_EXECUTABLE`. Os scripts atuais usam `blender_primitives.py`; o antigo gerador decorativo foi arquivado, preservando suas funções compartilhadas sem alteração.

Para gerar outra versão de estudo sem substituir a entrega atual:

```bash
python3 scripts/run_blender.py --background --factory-startup --python-exit-code 1 \
  --python scripts/build_house.py -- --project-root . --device cpu \
  --output historico/rascunhos/casa-nova-geracao.blend
```

Para reabrir, verificar e renderizar o modelo atual:

```bash
python3 scripts/run_blender.py --background projeto/casa-reconstruida.blend \
  --python-exit-code 1 --python scripts/validate_house.py -- --project-root . --device cpu
python3 scripts/house_atlas.py
# Depois de conferir visualmente as comparações:
python3 scripts/finalize_ground_revision.py
```

`--no-render` limita a validação às verificações. `render_revision.py --preview --ground-only`, no Python do Blender, gera prévias da planta, da porta e do corte 3D. As montagens usam Pillow já disponível; nenhum pacote ou configuração global foi adicionado.

## Histórico preservado

Os arquivos anteriores foram retirados das pastas ativas e reunidos em [historico/](historico/README.md). O [manifesto do arquivamento](historico/ate-revisao05/ARQUIVAMENTO.json) registra origens, destinos e hashes das versões até a revisão 05. O README daquela entrega foi preservado como `historico/ate-revisao05/ENTREGA-05.md`.

As fotos originais, demais referências fornecidas pelo usuário e prompts foram mantidos como fontes. Nenhum conteúdo anterior foi descartado. Não houve commit, push ou publicação.
