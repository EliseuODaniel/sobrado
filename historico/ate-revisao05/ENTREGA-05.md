# Casa — revisão 05: térreo e fachada conferidos com as fotos

O térreo e a fachada foram revistos com as referências originais, mantendo as correções do usuário: entrada diagonal, garagem ampliada, lavabo sob o segundo lance e posição geral da lavanderia. As medidas continuam aproximadas. A distribuição interna do segundo pavimento fica para a próxima etapa.

- [Blender editável atual](projeto/casa-reconstruida.blend)
- [Versão 05 identificada](projeto/casa-terreo-revisao05.blend)
- [Fachada frontal](renders/revisao-05/final/fachada-frontal.png)
- [Fachada × fotos originais](renders/planta-casa/fachada-comparacao.png)
- [Exterior antes × depois](renders/planta-casa/fachada-antes-depois.png)
- [Oito ângulos do térreo × fotos originais](renders/planta-casa/comparacao-originais.png)
- [Planta inferior vista de cima](renders/revisao-05/final/planta-terreo.png)
- [Térreo em 3D](renders/revisao-05/final/terreo-3d.png)
- [Corte: lavabo sob o segundo lance](renders/revisao-05/final/lavabo-sob-escada.png)
- [Relatório de evidências e limites](relatorios/revisao-05/RELATORIO.md)
- [Configuração](config/planta-casa.json)

## Ajustes principais

A garagem agora fica sob o próprio volume superior, com paredes laterais contínuas. Foram retirados os pilares avançados e a cobertura avulsa que contradiziam a fachada. A varanda recuada, rede de proteção, molduras brancas, grade da janela da sala, pequena janela posterior da garagem, jardineiras e piso externo seguem as relações observadas em `exterior1.webp` e `exterior2.webp`.

Uma parede externa vertical fecha o fundo da garagem antes do volume da escada. A pequena janela permanece aberta nessa parede e no fechamento do lavabo. A escada deixa de aparecer na vista externa; o lavabo continua sob o segundo lance e a entrada continua diagonal.

No interior, a revisão inclui fundo cinza do painel da TV, rack amarelo, tampo de jantar escuro e detalhes dos encostos e pendente. A churrasqueira recebeu revestimento em madeira e boca lateral, substituindo a coifa exposta que não aparecia nas fotos. Foram mantidos os três bancos do croqui, embora as fotos mostrem quatro.

Na cozinha, o tampo e os gabinetes agora deixam o vão do fogão livre. Foram acrescentados micro-ondas, aéreo junto ao ripado, puxadores, azulejos e frente da lava-louças. Na lavanderia, o retorno da bancada passou para a esquerda; o tampo não cobre mais a lavadora de abertura superior, e foram acrescentados tanque e aéreos. O lavabo recebeu gabinete, torneira, porta-toalhas e padrão de parede aproximado.

## Limites que continuam abertos

As fotos não estabelecem dimensões lineares exatas. Enquadramentos, móveis, equipamentos e marcenaria continuam aproximados. O forro do lavabo usa um envelope inclinado com ressaltos aproximados; a geometria estrutural e as folgas reais sob a escada não foram medidas.

A ligação entre a janela da cozinha, eventual pátio aberto e lavanderia não foi confirmada. Foi solicitado esclarecimento ao usuário; enquanto isso, a posição geral do croqui foi preservada. O retorno esquerdo da bancada da lavanderia é curto para manter livre a passagem lateral, cuja posição exata também não foi medida.

A cobertura completa da própria unidade não aparece nas fotos. O telhado foi aproximado pela tipologia vista nas unidades vizinhas e está identificado como hipótese. As fachadas vizinhas são apenas contexto volumétrico para as duas câmeras externas; não têm plantas internas modeladas.

A matrícula original não foi recebida. O texto do ChatGPT sobre as áreas continua como fonte secundária não verificada, sem ser convertido em medidas oficiais.

## Abrir e editar

Abra `projeto/casa-reconstruida.blend` no Blender 5.2 LTS. A cena inicial é `PLANTA_Terreo`; `Num 0` entra na câmera e `F12` renderiza. `PLANTA_Terreo_Cotas` mostra a distribuição vista de cima. `FOTO_Fachada` e `FOTO_Fachada_Obliqua` mostram a frente em ângulos de controle. `CASA_Completa` mostra a unidade isolada, sem as vizinhas de contexto.

Há 17 cenas, incluindo as comparações da sala, escada, cozinha, churrasqueira, lavanderia e lavabo; plantas e envoltória superior; estudos dos cômodos; corte do lavabo e exterior. `CORTE_Lavabo_Escada` omite duas paredes para mostrar o encaixe por baixo do lance. As paredes continuam presentes nas outras cenas.

**O segundo pavimento ainda não tem distribuição interna confirmada.** Seus cinco módulos permanecem separados em `ESTUDOS_Superior`, fora das coordenadas da casa. Os ajustes da fachada superior representam apenas a parte externa vista nas fotos.

No Outliner, os pais `SOFA_…`, `TV_E_RACK_original`, `MESA_JANTAR_…`, `CHURRASQUEIRA conforme croqui` e `ENTRADA_DIAGONAL conforme croqui` movem conjuntos. O filho `Porta entrada diagonal — abrir/girar` abre a folha sem alterar a diagonal do vão. As coleções `Terreo`, `Superior`, `Fachada`, `Escada`, `Cobertura`, `Referencias` e `Contexto_Condominio` separam os elementos. As fotos estão empacotadas e não são usadas como fundos dos renders.

Salve suas alterações com outro nome para preservar a entrega atual.

## Reproduzir e verificar

O Blender portátil é `.tools/blender-5.2.4-linux-x64/blender`. O launcher usa essa instalação ou `BLENDER_EXECUTABLE`. Não foram instaladas dependências nem alteradas configurações globais. A geração usa Cycles em CPU, AgX e denoise; as montagens usam Pillow já disponível.

```bash
python3 scripts/run_blender.py --background --factory-startup --python-exit-code 1 \
  --python scripts/build_house.py -- --project-root . --device cpu \
  --output projeto/versoes/casa-nova-geracao.blend
```

O gerador cria outro nome com timestamp se o destino existir. Para verificar e renderizar a entrega principal:

```bash
python3 scripts/run_blender.py --background projeto/casa-reconstruida.blend \
  --python-exit-code 1 --python scripts/validate_house.py -- --project-root . --device cpu
python3 scripts/house_atlas.py
# Após conferir visualmente as comparações:
python3 scripts/finalize_ground_revision.py
```

`validate_house.py --no-render` executa somente verificações. No Python do Blender, `render_revision.py --preview` gera as dez comparações em resolução reduzida; `--preview --facade-only` limita a prévia às duas fachadas. O script `facade_details.py` contém os elementos externos e `build_house.py` define a implantação e os detalhes do térreo.

Os testes verificam integridade, relações e contradições específicas, incluindo visibilidade da janela posterior, oclusão da escada na fachada, fogão sem tampo atravessado e lavadora superior livre. A versão anterior foi submetida à mesma auditoria. Os testes não comprovam equivalência métrica ou fidelidade integral da planta.

## Histórico

A revisão 04, seus scripts, configuração e README estão em `projeto/versoes/revisao-05-antes/`; seus renders continuam em `renders/revisao-04/`. As revisões anteriores, o croqui do usuário e a proposta decorativa `projeto/sala-industrial.blend` foram preservados.

Os recibos atuais estão em `relatorios/revisao-05/`: auditorias antes/depois, validação, renders, relatório e manifesto de hashes. Não houve commit, push ou publicação.
