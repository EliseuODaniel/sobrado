# Casa — revisão 04: lavabo sob a escada e garagem ampliada

O lavabo foi movido para baixo do segundo lance da escada, conforme a correção do usuário. A continuação direita da garagem ocupa agora a área liberada à frente da escada. As medidas continuam aproximadas.

- [Blender editável atual](projeto/casa-reconstruida.blend)
- [Versão 04 identificada](projeto/casa-terreo-revisao04.blend)
- [Seu croqui × planta revisada](renders/planta-casa/croqui-e-planta.png)
- [Planta inferior vista de cima](renders/revisao-04/final/planta-terreo.png)
- [Corte: lavabo sob a escada](renders/revisao-04/final/lavabo-sob-escada.png)
- [Térreo em 3D](renders/revisao-04/final/terreo-3d.png)
- [Planta anterior × revisão 04](renders/planta-casa/comparacao-antes-depois.png)
- [Comparação com seis fotos originais](renders/planta-casa/comparacao-originais.png)
- [Configuração e hipóteses](config/planta-casa.json)
- [Relatório e limites](relatorios/revisao-04/RELATORIO.md)

## O que mudou

A lavanderia deixou de ser um anexo prolongado nos fundos. Ela ocupa a faixa imediatamente atrás da cozinha e compartilha o alinhamento posterior com a churrasqueira. O acesso fica na divisória lateral, conforme o croqui.

A churrasqueira foi modelada no canto posterior esquerdo, atrás da bancada com três banquetas. O lavabo passou da faixa à frente da escada para a projeção do segundo lance, liberando essa faixa para ampliar a garagem. A entrada tem um conjunto próprio em diagonal; a folha fica fechada na planta para mostrar o alinhamento.

A correção por mensagem substitui a posição do lavabo desenhada no croqui anterior. Sua porta continua junto à escada, entre TV e primeiro lance, como nas fotos. Paredes inclinadas e louças foram encaixadas sob o forro do segundo lance; o formato e as folgas reais ainda precisam de medidas. A janela da cozinha foi mantida, agora voltada para a área marcada como lavanderia. A cobertura completa desse trecho não foi presumida.

As dimensões e o ângulo da entrada continuam aproximados. O desenho recebido está preservado em [referencias-ajustes/planta-terreo-anotada.png](referencias-ajustes/planta-terreo-anotada.png). A análise de áreas do ChatGPT continua registrada como fonte secundária não verificada; não foi convertida em medidas oficiais.

## Abrir e editar

Abra `projeto/casa-reconstruida.blend` no Blender 5.2 LTS. A cena inicial é `PLANTA_Terreo`; `Num 0` entra na câmera e `F12` renderiza. Para conferir a distribuição, selecione a cena `PLANTA_Terreo_Cotas`.

O conjunto `ENTRADA_DIAGONAL conforme croqui` controla a orientação da entrada. Seu filho `Porta entrada diagonal — abrir/girar` permite abrir a folha sem alterar a diagonal do vão. Os móveis, louças e equipamentos permanecem como objetos editáveis. Os pais `SOFA_…`, `TV_E_RACK_original`, `MESA_JANTAR_…` e `CHURRASQUEIRA conforme croqui` movem seus conjuntos.

As coleções `Terreo`, `Superior`, `Escada`, `Cobertura`, `Cotas_Terreo` e `Referencias` separam a geometria. As 26 imagens únicas estão empacotadas no arquivo; os 31 arquivos originais foram preservados.

Há 13 cenas: duas vistas do térreo, duas da envoltória superior, `CASA_Completa`, seis ângulos `FOTO_…`, `ESTUDOS_Superior` e `CORTE_Lavabo_Escada`. Esta última remove duas paredes apenas no corte para mostrar o encaixe sob o lance. **A distribuição interna do superior permanece não estabelecida.** Seus cinco módulos são estudos separados fora da casa, sem ligações presumidas entre quartos e banheiros. A forma completa do retorno da escada também continua inferida.

Salve suas edições com outro nome para conservar a entrega atual.

## Reproduzir e verificar

O Blender portátil local é `.tools/blender-5.2.4-linux-x64/blender`. O launcher usa essa instalação Linux ou a variável `BLENDER_EXECUTABLE`. Os pacotes portáteis e caches estão ignorados pelo Git; nenhuma configuração global é necessária.

Para gerar outra versão:

```bash
python3 scripts/run_blender.py --background --factory-startup --python-exit-code 1 \
  --python scripts/build_house.py -- --project-root . --device cpu \
  --output projeto/versoes/casa-nova-geracao.blend
```

O gerador usa outro nome com timestamp quando o destino já existe. Para verificar a entrega principal e refazer as montagens:

```bash
python3 scripts/run_blender.py --background projeto/casa-reconstruida.blend \
  --python-exit-code 1 --python scripts/validate_house.py -- --project-root . --device cpu
python3 scripts/house_atlas.py
# Após conferir visualmente croqui, planta e fotos:
python3 scripts/finalize_ground_revision.py
```

`validate_house.py --no-render` executa somente verificações. Para uma prévia rápida da planta e do corte em 3D, use `render_revision.py --preview --ground-only` no Python do Blender. As montagens usam Pillow já disponível. A entrega foi renderizada com Cycles em CPU, AgX e denoise.

Os testes verificam integridade, relações geométricas, passagem livre para a lavanderia, continuidade da garagem e as relações fotográficas anteriores. Eles não comprovam medidas reais ou fidelidade integral do imóvel.

## Histórico preservado

A revisão 03, sua configuração, scripts e README estão em `projeto/versoes/revisao-04-antes/`; seus renders continuam em `renders/revisao-03/`. A revisão 02 também foi preservada. A versão anterior rejeitada e a proposta decorativa `projeto/sala-industrial.blend` também foram mantidas. A imagem anotada pelo usuário dentro da pasta da revisão 02 foi preservada.

Os recibos atuais estão em `relatorios/revisao-04/`, incluindo testes, renders e manifesto de hashes. `finalize_house.py` corresponde ao fechamento histórico da revisão 02; para esta revisão, use `finalize_ground_revision.py`. Não houve commit, push ou publicação.
