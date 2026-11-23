# Visualizador 3D do Sobrado

O navegador abre a casa **Atual fiel às fotos v02** com as paredes externas em vidro. Use **Maquete** no cabeçalho para alternar entre as versões disponíveis.

| Maquete | Cena no Blender |
| --- | --- |
| Casa atual | `FIEL2_volumetria` em [casa-07-atual-fiel.blend](../projeto/atual/casa-07-atual-fiel.blend) |
| Casa com ático | `ATC5_atico-cobertura` em [atico-caixa-canto-escada.blend](../projeto/atico/atico-caixa-canto-escada.blend) |
| Estrutural | `INFRA_04_CONJUNTO_FORRO_CAIXA` e os recortes de pavimento em [instalacoes-pavimentos-forro.blend](../projeto/infraestrutura/instalacoes-pavimentos-forro.blend) |
| Industrial | `PHOTO6_volumetria` em [casa-industrial-fotorrealista.blend](../projeto/industrial/casa-industrial-fotorrealista.blend) |

A exportação da **Casa atual** aplica os ajustes do mobiliário observados nas fotos. [Comparação por ambiente e limites da revisão](../relatorios/atual/REVISAO-POSICOES-VISUALIZADOR.md).

## Abrir

Use Node.js com npm para instalar o Three.js, Python 3 para servir os arquivos e um navegador com WebGL 2. Se o Git tiver baixado apenas os ponteiros dos GLBs, materialize os arquivos com `git lfs pull --include="visualizador/modelo/*.glb"` na raiz do repositório.

No PowerShell, a partir da raiz do projeto:

```powershell
cd visualizador
npm.cmd ci
python -m http.server 8765 --bind 127.0.0.1
```

Abra [http://127.0.0.1:8765](http://127.0.0.1:8765). Depois da instalação do Three.js, a página funciona localmente sem internet e sem abrir o Blender. Use `Ctrl+C` no terminal para parar o servidor que iniciou.

- **Prancha** abre em **Girar**, com projeção axonométrica, traços finos e cobertura hachurada. **Drone** e as **Vistas prontas** usam perspectiva com o mesmo acabamento. O endereço [com `vista=prancha`](http://127.0.0.1:8765/?vista=prancha) abre direto nesse modo.
- Use **Planta** para ver o desenho em escala gerado por cortes na geometria exportada. **Planta + 3D** mantém os dois painéis abertos e acompanha o pavimento selecionado. O desenho usa um plano de corte a 1,07 m acima do piso e traços auxiliares a 0,34 m. A barra de escala acompanha o zoom.
- No painel 3D, ative **Corte horizontal** e ajuste a cota em metros acima do nível do térreo para ver abaixo dela. Os botões **Diagonal**, **Frente**, **Lado** e **Topo** mudam a orientação da câmera.
- Para testar a disposição de móveis, escolha uma peça e clique em **Posicionar**, depois marque o ponto na planta ou no 3D em painel duplo. Selecione um móvel de estudo para mover, girar ou remover. Os estudos ficam no armazenamento local do navegador, por maquete. As peças são referências de volume para experimentar posições.
- Tanto em **Drone** quanto em **Girar**, arraste com o botão esquerdo ou com um dedo para orbitar. A roda aproxima ou afasta sob o cursor. Arraste com o botão direito para deslocar a vista. Com dois dedos, faça pinça para dar zoom ou arraste para deslocar.
- Clique na cena para usar o teclado. No **Drone**, **W/S** avançam e recuam na direção do olhar, inclusive em altura quando a câmera está inclinada. Em **Girar**, **W/S** movem no plano horizontal. Nos dois modos, **A/D** deslocam para os lados e **Q/E** seguem a vertical da tela.
- Nos dois modos, as setas giram o olhar no lugar. **F** enquadra a superfície no centro da tela. No painel 3D individual, um duplo clique enquadra a superfície escolhida.
- **Casa inteira** mantém os dois pavimentos e permite alternar a cobertura principal e a dos fundos juntas. **Térreo** retira o pavimento superior e as coberturas. **Superior** isola o segundo pavimento com a laje e sem o telhado.
- Em **Paredes externas**, selecione **Sólidas**, **Vidro** ou **Ocultas**. O controle atua também nos muros anexos e preserva divisórias internas, pilares, portas e janelas. Ele funciona junto aos recortes dos pavimentos e ao controle do telhado.
- A maquete **Estrutural** abre com telhado oculto e todas as redes visíveis. Use os filtros de **Instalações** para isolar elétrica, água fria, água quente, extravasor ou limpeza da caixa. Os recortes usam os trechos de cada pavimento já preparados no Blender. A vista geral inclui a caixa-d’água na posição original. [Escopo e origem dos traçados](../projeto/infraestrutura/LEIA-ME.md).
- As **Vistas prontas** voltam à casa inteira e posicionam a câmera no ambiente escolhido. **Recentrar câmera** repõe o enquadramento ativo. **Vista geral** restaura a abertura com as paredes em vidro. A casa com ático abre com o telhado oculto e tem um recorte exclusivo para o ático.

## Atualizar o GLB

Após salvar a cena de origem, execute este comando na raiz do repositório, com o Blender 5.2 instalado. Ajuste o caminho de `BLENDER_EXECUTABLE` se a instalação estiver em outra pasta.

```powershell
$env:BLENDER_EXECUTABLE = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
python scripts/run_blender.py --background --factory-startup --disable-autoexec projeto/atual/casa-07-atual-fiel.blend --python scripts/export_web_viewer.py
python scripts/run_blender.py --background --factory-startup --disable-autoexec projeto/atico/atico-caixa-canto-escada.blend --python scripts/export_web_viewer.py -- atico
python scripts/run_blender.py --background --factory-startup --disable-autoexec projeto/infraestrutura/instalacoes-pavimentos-forro.blend --python scripts/export_web_viewer.py -- estrutural
python scripts/run_blender.py --background --factory-startup --disable-autoexec projeto/industrial/casa-industrial-fotorrealista.blend --python scripts/export_web_viewer.py -- industrial
```

Cada comando substitui o GLB correspondente em `visualizador/modelo/` após finalizar a conversão e conferir a integridade do Blender de origem. Recarregue a página para ver a revisão exportada. O GLB contém a identificação da cena, o SHA-256 do arquivo de origem e as câmeras disponíveis. O Blender e o glTF usam a mesma escala em metros.

O Three.js ilumina a cena em tempo real. A exportação limita as texturas a 1.536 pixels no maior lado, aplica a correção de cor aos tecidos e conserva o relevo do piso externo como mapa de normais. Granitos e porcelanato usam a cor-base do modelo. A iluminação, as reflexões e os materiais com nós procedurais podem aparecer diferentes dos [renders do Blender](../renders/atual/galeria.html).

Os vidros usam transparência com reflexos simplificados no navegador para manter a leitura das esquadrias ao mover a câmera.
