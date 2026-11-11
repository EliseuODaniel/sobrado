# Casa — revisão 03 do térreo

O térreo segue agora o desenho aproximado enviado pelo usuário: churrasqueira e bancada nos fundos à esquerda, lavanderia à direita atrás da cozinha, lavabo à frente da escada, continuação da garagem abaixo dele e entrada em diagonal.

- [Blender editável atual](projeto/casa-reconstruida.blend)
- [Versão 03 identificada](projeto/casa-terreo-revisao03.blend)
- [Seu croqui × planta revisada](renders/planta-casa/croqui-e-planta.png)
- [Planta inferior vista de cima](renders/revisao-03/final/planta-terreo.png)
- [Térreo em 3D](renders/revisao-03/final/terreo-3d.png)
- [Planta anterior × revisão 03](renders/planta-casa/comparacao-antes-depois.png)
- [Comparação com seis fotos originais](renders/planta-casa/comparacao-originais.png)
- [Configuração e hipóteses](config/planta-casa.json)
- [Relatório e limites](relatorios/revisao-03/RELATORIO.md)

## O que mudou

A lavanderia deixou de ser um anexo prolongado nos fundos. Ela ocupa a faixa imediatamente atrás da cozinha e compartilha o alinhamento posterior com a churrasqueira. O acesso fica na divisória lateral, conforme o croqui.

A churrasqueira foi modelada no canto posterior esquerdo, atrás da bancada com três banquetas. O lavabo foi ampliado para a faixa indicada à direita da sala, com a continuação da garagem à sua frente. A entrada tem um conjunto próprio em diagonal; a folha fica fechada na planta para mostrar o alinhamento.

O acesso do lavabo foi mantido junto à escada, como nas fotos. Sua ligação interna sob o retorno é uma interpretação: o croqui não desenha a porta. A janela da cozinha foi mantida, agora voltada para a área marcada como lavanderia. A cobertura completa desse trecho não foi presumida.

As dimensões e o ângulo da entrada continuam aproximados. O desenho recebido está preservado em [referencias-ajustes/planta-terreo-anotada.png](referencias-ajustes/planta-terreo-anotada.png). A análise de áreas do ChatGPT continua registrada como fonte secundária não verificada; não foi convertida em medidas oficiais.

## Abrir e editar

Abra `projeto/casa-reconstruida.blend` no Blender 5.2 LTS. A cena inicial é `PLANTA_Terreo`; `Num 0` entra na câmera e `F12` renderiza. Para conferir a distribuição, selecione a cena `PLANTA_Terreo_Cotas`.

O conjunto `ENTRADA_DIAGONAL conforme croqui` controla a orientação da entrada. Seu filho `Porta entrada diagonal — abrir/girar` permite abrir a folha sem alterar a diagonal do vão. Os móveis, louças e equipamentos permanecem como objetos editáveis. Os pais `SOFA_…`, `TV_E_RACK_original`, `MESA_JANTAR_…` e `CHURRASQUEIRA conforme croqui` movem seus conjuntos.

As coleções `Terreo`, `Superior`, `Escada`, `Cobertura`, `Cotas_Terreo` e `Referencias` separam a geometria. As 26 imagens únicas estão empacotadas no arquivo; os 31 arquivos originais foram preservados.

Há 12 cenas: duas vistas do térreo, duas da envoltória superior, `CASA_Completa`, seis ângulos `FOTO_…` e `ESTUDOS_Superior`. **A distribuição interna do superior permanece não estabelecida.** Seus cinco módulos são estudos separados fora da casa, sem ligações presumidas entre quartos e banheiros. A forma completa do retorno da escada também continua inferida.

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

A revisão 02, sua configuração, scripts e README estão em `projeto/versoes/revisao-03-antes/`; seus renders continuam em `renders/revisao-02/`. A versão anterior rejeitada e a proposta decorativa `projeto/sala-industrial.blend` também foram mantidas. A imagem anotada pelo usuário dentro da pasta da revisão 02 foi preservada.

Os recibos atuais estão em `relatorios/revisao-03/`, incluindo testes, renders e manifesto de hashes. `finalize_house.py` corresponde ao fechamento histórico da revisão 02; para esta revisão, use `finalize_ground_revision.py`. Não houve commit, push ou publicação.
