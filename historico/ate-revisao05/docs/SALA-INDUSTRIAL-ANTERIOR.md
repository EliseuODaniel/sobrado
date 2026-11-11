# Casa — Sala industrial no Blender

Reconstrução 3D editável do estar, jantar, bar e trecho visível da cozinha, usando as três imagens em `referencias/`. O projeto usa **Blender 5.2.4 LTS, Cycles, AgX e denoise**. A unidade é o metro.

**A escala é estimada.** Não foram fornecidas fotos reais, planta ou medidas. Esta é uma hipótese visual para desenvolver o projeto; as dimensões precisam ser conferidas no imóvel antes de comprar móveis ou executar marcenaria.

## Abrir e editar

Abra [projeto/sala-industrial.blend](../projeto/sala-industrial.blend) no Blender 5.2 LTS. Geometria, materiais, iluminação e câmeras ficam no próprio arquivo. Não é necessário executar o gerador para editar ou renderizar pela interface.

No WSL com interface gráfica disponível, também é possível iniciar o Blender portátil:

```bash
./.tools/blender-5.2.4-linux-x64/blender projeto/sala-industrial.blend
```

- **Mover a mesa:** no Outliner, abra `Jantar` e selecione o objeto pai `MESA_Jantar — mover conjunto`. Use `G`, seguido de `X` ou `Y`, para mover o conjunto no piso. Digite a distância em metros. `R`, depois `Z`, gira o móvel.
- **Mover uma cadeira:** selecione um dos pais `CADEIRA_Esquerda_1`, `CADEIRA_Esquerda_2`, `CADEIRA_Direita_1` ou `CADEIRA_Direita_2`. Cada cadeira é independente. O mesmo vale para os pais `BANQUETA_01` a `BANQUETA_04`, em `Bar`.
- **Trocar um material:** selecione uma peça de malha dentro do móvel, abra Material Properties e escolha outro material. No Shader Editor, os nós `Cores ajustáveis`, `Escala e direção da textura` e `Relevo ajustável — metros` controlam o acabamento. A rugosidade fica no Principled BSDF.
- **Ajustar uma luz:** em `Iluminacao`, selecione, por exemplo, `Luz Pendente principal jantar`. Em Light Properties, altere Power, Color e tamanho da fonte. Os difusores visíveis têm materiais emissivos separados.
- **Voltar à câmera principal:** selecione `CAM_Referencia` em `Cameras` e use `Ctrl + Num 0` para torná-la ativa; `Num 0` entra na vista da câmera. Use `F12` para renderizar.
- **Ver a planta:** ative `CAM_Superior`. Para reproduzir a planta entregue, o script de validação oculta temporariamente teto, cobertura e luminárias. Essa ocultação não é salva sobre o arquivo principal.
- **Liberar a arquitetura:** no filtro do Outliner, habilite a coluna de seleção, com ícone de seta. Reative a seleção da coleção `Arquitetura` e dos objetos que pretende editar. O bloqueio evita mover paredes acidentalmente.
- **Preservar ajustes manuais:** use Save As para salvar, por exemplo, `projeto/sala-industrial-editada.blend`. A geração cria outro arquivo quando o destino já existe.

## Arquivos

| Arquivo | Uso |
| --- | --- |
| `projeto/sala-industrial.blend` | Cena de entrega, com `CAM_Referencia` ativa e recursos empacotados. |
| `config/cena.json` | Medidas estimadas, origem da escala, câmera, posições, cores, iluminação e qualidade. |
| `scripts/build_scene.py` | Gerador executado pelo Python do Blender. |
| `scripts/run_blender.py` | Localiza o Blender portátil e permite indicar outro executável. |
| `scripts/validate_scene.py` | Reabre o arquivo, valida o layout, testa o espelho e renderiza. |
| `scripts/compare_renders.py` | Monta comparação lado a lado e sobreposição. Usa Pillow no Python local. |
| `renders/principal.png` | Render de entrega em 1671 × 941, obtido do `.blend` reaberto. |
| `renders/vista-superior.png` | Vista superior da distribuição e circulação. |
| `renders/comparacao.png` | Referência à esquerda e render à direita, na mesma proporção. |
| `renders/comparacao-sobreposicao.png` | Sobreposição para conferir enquadramento e volumes. |
| `renders/teste-espelho-comparacao.png` | Antes, depois e diferença do teste de reflexão. |
| `projeto/versoes/` | Versões anteriores preservadas, inclusive a anterior ao ajuste da manta. |
| `relatorios/` | Logs de execução, validação, entradas, comparação e manifesto de arquivos. |

As coleções principais são `Arquitetura`, `Estar`, `Jantar`, `Bar`, `Cozinha`, `Iluminacao`, `Cameras` e `Referencias`. As imagens de referência ficam fora do render e disponíveis no viewport. A mesa tem três tábuas longitudinais, moldura, saia e quatro pés afunilados com ressaltos. Há quatro cadeiras em 2 + 2, cabeceiras livres e quatro banquetas sem encosto.

## Gerar de novo

Execute os comandos a partir da raiz do projeto. O gerador inicia uma cena nova; não abre nem reescreve suas versões editadas. Se o nome de saída existir, acrescenta um timestamp ao novo arquivo.

Prévia com detecção automática do dispositivo:

```bash
python3 scripts/run_blender.py --background --factory-startup --python-exit-code 1 \
  --python scripts/build_scene.py -- --project-root . --quality preview --device auto
```

Qualidade final, forçando CPU e escolhendo outro destino:

```bash
python3 scripts/run_blender.py --background --factory-startup --python-exit-code 1 \
  --python scripts/build_scene.py -- --project-root . --quality final --device cpu \
  --output projeto/versoes/sala-industrial-regenerada.blend
```

O equivalente com o executável diretamente também funciona:

```bash
./.tools/blender-5.2.4-linux-x64/blender --background --factory-startup \
  --python-exit-code 1 --python scripts/build_scene.py -- \
  --project-root . --quality preview --device auto
```

`--no-render` salva somente a cena. As prévias e os renders produzidos pelo gerador recebem nomes próprios em `renders/`. O render de entrega é produzido separadamente, a partir do arquivo salvo:

```bash
python3 scripts/run_blender.py --background projeto/sala-industrial.blend \
  --python-exit-code 1 --python scripts/validate_scene.py -- --project-root . --device auto
python3 scripts/compare_renders.py renders/principal.png
```

Para indicar outra instalação funcional:

```bash
BLENDER_EXECUTABLE=/caminho/para/blender python3 scripts/run_blender.py --version
```

### PowerShell

Equivalente para uma instalação Windows funcional; ajuste o caminho do executável. Estes comandos são instruções de uso, não registros de execução neste host:

```powershell
Set-Location "\\wsl.localhost\Ubuntu\home\edann\projects\casa-interiores"
$Blender = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
& $Blender --background --factory-startup --python-exit-code 1 `
  --python ".\scripts\build_scene.py" -- `
  --project-root "." --quality preview --device auto
```

No WSL, `wslpath -w /caminho/linux` converte um caminho para uso com o `blender.exe`. O launcher converte os argumentos de caminho quando um executável Windows é indicado.

## Ambiente e execução

- Blender Linux **5.2.4 LTS**, build `cd5dc428cce1`, portátil em `.tools/`. O pacote foi baixado do servidor oficial e o SHA-256 foi conferido com o arquivo oficial.
- Dispositivo efetivamente usado: **CPU Intel Core i9-14900HX**. O Cycles não enumerou a RTX 4070 como dispositivo OptiX neste WSL; a inicialização retornou erro `7804`. O modo `auto` selecionou CPU e concluiu os renders.
- A versão portátil Windows também foi testada. O Windows recusou a inicialização por configuração lado a lado incorreta. Nenhum runtime, driver ou configuração global foi instalado ou alterado.
- Prévia: 50% da resolução, 32 amostras. Principal: 1671 × 941, até 160 amostras com adaptive sampling, denoise e AgX. O arquivo final já guarda a qualidade final.
- O gerador depende apenas do Python, NumPy e `bpy` fornecidos pelo Blender. A comparação usa o Pillow já disponível no Python local. Os pacotes portáteis e caches estão ignorados pelo Git.
- Materiais procedurais, folhagem modelada e artes de TV/quadro geradas por algoritmo. Não foram incorporados modelos ou texturas de terceiros. As três referências fornecidas foram empacotadas para consulta; não são usadas como fundo do render nem como imagem do espelho.
- O espelho usa superfície metálica com rugosidade `0.003`; a reflexão é traçada pelo Cycles. Luzes de preenchimento são aproximações artísticas, e algumas têm visibilidade especular desativada para evitar reflexos de softboxes sobre a cobertura.

Os registros exatos estão em `relatorios/geracao-final.log`, `relatorios/correcao-manta.log` e `relatorios/validacao-final.log`. O comando de geração da entrega usou `--quality final --device auto --no-render`; o arquivo foi então reaberto pelo validador para produzir os renders. A manta foi corrigida também no gerador, mantendo a versão anterior em `projeto/versoes/`.

## Medidas, hipóteses e limites

`confirmed_dimensions_m` está vazio: não há medidas reais confirmadas. As dimensões e posições estimadas ficam em `config/cena.json`. A largura adotada é 6,40 m, o fundo está em Y = 8,70 m, o limite frontal estimado em Y = −1,20 m e o pé-direito em 3,15 m. O tampo do jantar mede aproximadamente 1,35 × 1,65 m e tem 0,78 m de altura.

A cobertura envidraçada, a vegetação externa e o ressalto da parede que sustenta o espelho são **hipóteses visuais**, identificadas com `HIPOTESE_` no Outliner. Sem fotos reais, não representam elementos existentes confirmados. O ressalto permite uma faixa de espelho coerente com a composição, mantendo o reflexo físico. A cozinha e a porta lateral foram aproximadas apenas no trecho visível; ambientes atrás da porta, espaços externos, instalações e áreas ocluídas não foram detalhados. A composição não inclui geladeira.

A comparação deve ser lida como reconstrução proporcional, não como reprodução fotográfica. Permanecem diferenças no enquadramento, largura aparente dos ambientes, reflexo, maciez e envelhecimento do couro, desenho das plantas, textura da pedra, detalhes da marcenaria e distribuição da luz. As artes da TV e dos quadros são próprias e diferem da referência. A cobertura e o reflexo respondem à geometria modelada, por isso também podem divergir do render de referência.

## Verificações

O relatório `relatorios/validacao.json` registra as contagens, apoios no piso, limites e ausência de sobreposição das caixas delimitadoras dos móveis principais. Esse teste é conservador e não substitui levantamento de circulação, projeto executivo ou análise completa de colisões de cada triângulo da cena. A vista superior permite conferir os espaços de passagem. As interseções intencionais entre peças de um mesmo móvel — assento e estrutura, por exemplo — não são tratadas como erro.

O teste do espelho usa o mesmo seed, move temporariamente o vaso claro do bar e gera dois recortes. O vaso é restaurado antes do render principal, e o validador não salva suas alterações de teste sobre o `.blend`. A comparação visual e a diferença de pixels estão em `renders/teste-espelho-comparacao.png` e `relatorios/espelho.json`.

O manifesto `relatorios/manifesto.json` lista os arquivos de entrada e saída com SHA-256. As referências originais são preservadas. Nenhum commit ou envio ao GitHub foi feito nesta etapa.

Referências técnicas: [Blender 5.2 LTS](https://www.blender.org/releases/5-2/), [Cycles](https://www.blender.org/features/rendering/), [manual de GPU](https://docs.blender.org/manual/en/latest/render/cycles/gpu_rendering.html) e [API Python](https://docs.blender.org/api/current/).
