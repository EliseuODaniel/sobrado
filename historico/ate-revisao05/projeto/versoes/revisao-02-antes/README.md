# Casa — planta 3D pelas referências originais

Modelo preliminar editável dos dois pavimentos, construído a partir das fotos em `referencias-originais/`. A base representa garagem, sala, jantar, escada, lavabo, cozinha, bar coberto, lavanderia, três quartos e dois banheiros.

**As dimensões são estimadas e a distribuição do andar superior é hipotética.** O texto com áreas foi identificado pelo usuário como análise do ChatGPT. A matrícula original não foi recebida nem conferida. Esses números estão registrados como informação secundária não verificada, sem transformar as sugestões de largura e comprimento em medidas oficiais.

## Abrir o projeto

- [Arquivo Blender editável](projeto/casa-reconstruida.blend)
- [Plantas 3D dos dois pavimentos](renders/planta-casa/planta-3d.png)
- [Vistas superiores](renders/planta-casa/plantas-superiores.png)
- [Comparação com as fotos originais](renders/planta-casa/comparacao-originais.png)
- [Configuração e origem das hipóteses](config/planta-casa.json)
- [Relatório de validação](relatorios/planta-casa/validacao.json)

O `.blend` abre na cena `PLANTA_Terreo`. No seletor de cenas, na parte superior do Blender, escolha:

| Cena | Conteúdo |
| --- | --- |
| `PLANTA_Terreo` | Corte 3D do térreo, com móveis e circulação visíveis. |
| `PLANTA_Superior` | Corte 3D do superior, com a implantação estimada dos quartos e banheiros. |
| `PLANTA_Terreo_Cotas` | Vista superior do térreo com nomes e cotas aproximadas. |
| `PLANTA_Superior_Cotas` | Vista superior do superior com os ambientes incertos identificados. |
| `CASA_Completa` | Volumetria dos dois pavimentos, coberturas e garagem. |
| `FOTO_Sala_Fundos` | Vista da sala em direção ao jantar, bar e cozinha. |
| `FOTO_Sala_Frente` | Vista em direção à entrada e à escada. |
| `FOTO_Cozinha` | Vista interna da cozinha. |

Use `Num 0` para entrar na câmera da cena e `F12` para renderizar. As cenas compartilham os mesmos objetos: editar um móvel atualiza as vistas correspondentes. As exclusões de coleções de cada cena permitem conferir os pavimentos sem deslocá-los de sua posição real no modelo.

No WSL com interface gráfica disponível, o Blender portátil pode ser iniciado assim:

```bash
./.tools/blender-5.2.4-linux-x64/blender projeto/casa-reconstruida.blend
```

## Como editar

As coleções `Terreo`, `Superior`, `Escada` e `Cobertura` organizam a arquitetura. As coleções `AMB_sala`, `AMB_cozinha`, `AMB_suite` e equivalentes organizam os ambientes. Os objetos pais `AMBIENTE_…` registram as fotos usadas e o grau de confiança da implantação nas propriedades personalizadas.

- Para mover um móvel inteiro, selecione seu objeto pai no Outliner, como `SOFA_original cinza — mover conjunto`, `MESA_JANTAR_original seis lugares`, uma `CADEIRA_…`, `BANQUETA_BAR_…` ou `CAMA_…`. Use `G`, depois `X` ou `Y`. `R`, depois `Z`, gira o conjunto.
- Para trocar acabamento, selecione uma peça de malha e escolha o material em Material Properties. Cor, rugosidade e relevo continuam editáveis nos nós.
- Para ajustar iluminação, selecione uma luz em `Iluminacao` e altere Power, Color e Size em Light Properties.
- As portas têm um pai com o nome `… — abrir/girar`, com pivô no batente. Use rotação em Z para abrir ou fechar a folha.
- Algumas paredes estão com seleção bloqueada. Habilite a coluna de seleção no filtro do Outliner e reative a seta do objeto desejado.
- As fotos ficam na coleção `Referencias`, empacotadas no arquivo e fora do render. Não são usadas como fundo das câmeras.
- Para preservar alterações manuais, salve como `projeto/casa-minha-versao.blend`. O gerador preserva destinos existentes e acrescenta um timestamp à nova saída.

## O que as fotos sustentam

A organização relativa da sala, jantar, bar, cozinha e escada foi inferida por fotos em sentidos opostos. Foram preservados os elementos visíveis: sofá cinza, espelho, painel de TV, rack amarelo, mesa de vidro, seis cadeiras, quatro banquetas com encosto, divisória ripada, bancada da cozinha em L, janelas, degraus de granito e guarda-corpo de vidro.

A cobertura de vidro do bar agora tem evidência nas referências originais. O bar, a cozinha e a lavanderia têm os equipamentos fotografados. A localização exata do lavabo sob a escada, o percurso completo dos degraus e a ligação entre pátio e lavanderia continuam estimados.

Os quartos foram reproduzidos pelos elementos visíveis: beliche e bancada no quarto azul, cama individual e armários no quarto branco, cama de casal, armário e TV na suíte. **A posição desses ambientes no superior e suas ligações são hipóteses**, pois as fotos não mostram uma circulação contínua entre eles. O mesmo vale para a posição dos dois banheiros. Áreas sem foto permanecem sem definição de uso.

O arquivo `config/planta-casa.json` relaciona cada ambiente às fotos, registra as conexões observadas ou estimadas e separa os dados secundários das hipóteses geométricas.

## Escala e áreas

Nenhuma dimensão linear foi confirmada. Como ponto de partida, foram adotados os retângulos sugeridos na análise enviada:

| Volume-base | Hipótese geométrica | Área do retângulo |
| --- | --- | --- |
| Térreo | 5,00 × 8,50 m | 42,50 m² |
| Superior | 5,00 × 10,20 m | 51,00 m² |
| Pé-direito | 2,70 m | — |
| Espessura inicial de parede | 0,15 m | — |
| Distância entre pisos | 2,90 m | — |

O superior tem projeção maior que o térreo e um recorte na laje para a escada. A diferença dos retângulos é 8,50 m². Isso não corresponde automaticamente aos 10,26 m² de diferença entre áreas exclusivas mencionadas na análise: os retângulos usam outra base de comparação, e não houve conciliação de critérios de área.

O texto secundário menciona 42,51 m² de implantação, 40,77 m² exclusivos no térreo, 51,03 m² exclusivos no superior e 1,74 m² de construção comum. **Nenhuma região da casa foi arbitrariamente identificada como esses 1,74 m² comuns.** A quota de terreno informada também não foi tratada como perímetro privativo.

O recorte da escada, paredes, varanda, garagem, bar e lavanderia impedem usar a área de um retângulo como comprovação de área construída. A extensão e a inclusão dos anexos nas áreas mencionadas não foram confirmadas. O relatório registra essas diferenças sem alegar validação da matrícula.

Para substituir as hipóteses, os dados mais úteis são planta cotada, largura e profundidade externas, posição e medidas da escada, dimensões dos cômodos e aberturas. O modelo está preparado para receber esses ajustes.

## Gerar e verificar

Execute na raiz do projeto:

```bash
python3 scripts/run_blender.py --background --factory-startup --python-exit-code 1 \
  --python scripts/build_house.py -- --project-root . --device auto

python3 scripts/run_blender.py --background projeto/casa-reconstruida.blend \
  --python-exit-code 1 --python scripts/validate_house.py -- --project-root . --device auto

python3 scripts/house_atlas.py
# Depois de inspecionar visualmente as imagens:
python3 scripts/finalize_house.py
```

Se o destino já existir, o novo arquivo recebe um timestamp. Para validar a versão recém-gerada, use o caminho indicado na linha `HOUSE_BUILT` no lugar de `projeto/casa-reconstruida.blend`.

Para gerar outro destino e forçar CPU:

```bash
python3 scripts/run_blender.py --background --factory-startup --python-exit-code 1 \
  --python scripts/build_house.py -- --project-root . --device cpu \
  --output projeto/versoes/casa-regenerada.blend
```

`build_house.py --preview` também renderiza uma prévia do térreo. O validador aceita `--preview` para renderizar em resolução reduzida e `--only plans`, `--only photos` ou `--only exterior` para limitar as saídas.

Equivalente com o executável diretamente:

```bash
./.tools/blender-5.2.4-linux-x64/blender --background --factory-startup \
  --python-exit-code 1 --python scripts/build_house.py -- --project-root . --device auto
```

Exemplo de PowerShell para uma instalação Windows funcional, ajustando o caminho do executável:

```powershell
Set-Location "\\wsl.localhost\Ubuntu\home\edann\projects\sobrado"
$Blender = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
& $Blender --background --factory-startup --python-exit-code 1 `
  --python ".\scripts\build_house.py" -- --project-root "." --device auto
```

Neste host foi usado **Blender 5.2.4 LTS, Cycles, CPU Intel Core i9-14900HX, AgX e denoise**. O OptiX falhou com erro 7804 e não enumerou a RTX 4070 neste WSL. A versão portátil Windows falhou por dependência de execução; nenhum driver, runtime ou configuração global foi alterado. Os pacotes portáteis em `.tools/` foram conferidos pelo checksum oficial e estão ignorados pelo Git.

## Validação e limites

O validador reabre o `.blend` em um processo limpo, confere a preservação das oito cenas, os dois níveis, o recorte da escada, os ambientes, os recursos empacotados e os hashes das 31 referências originais. Há 26 imagens únicas; as duplicatas foram identificadas sem alterar os arquivos. Os renders são obtidos do arquivo salvo, e seu hash é conferido novamente ao fim dos testes.

A inspeção compara a organização dos elementos com as fotografias. Não há calibração por medida real nem reconstrução fotogramétrica. Permanecem diferenças nas proporções, posição de aberturas, forma completa da escada, cobertura da garagem, distribuição superior e detalhamento dos móveis. A planta é uma base visual para revisão, não um levantamento fiel já confirmado.

Os comandos e resultados estão em `relatorios/planta-casa/geracao.log`, `validacao.log`, `validacao.json` e `manifesto.json`. Não foram feitos commit ou envio ao GitHub nesta etapa.

A proposta industrial anterior foi preservada em [projeto/sala-industrial.blend](projeto/sala-industrial.blend), com sua documentação em [docs/SALA-INDUSTRIAL-ANTERIOR.md](docs/SALA-INDUSTRIAL-ANTERIOR.md). As versões intermediárias estão em `projeto/versoes/`.
