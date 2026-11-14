# Industrial v03 — renderização nativa editável

Verificação UTC: 2026-11-11T12:07:02.737455+00:00

Cinco imagens finais saíram do `.blend` salvo e reaberto em outro processo. A nova proposta usa ativos detalhados, materiais fotográficos, tecido com volume e iluminação fotográfica 3D. Nenhuma imagem final foi substituída por geração ou retoque de IA.

| Obrigação | Recibo observado | Estado |
| --- | --- | --- |
| Modelo nativo editável | Arquivo final e SHA-256 conciliados entre modelo, auditoria e render | VERIFIED |
| Preservar arquitetura e encaixe | 3446 geometrias herdadas sem diferenças; três verificações do contorno e faces posteriores | VERIFIED |
| Renderizar todos os ambientes | Cinco PNGs 2880 × 1800; nomes, bytes e hashes conciliados | VERIFIED |
| Dispositivo de render efetivo | Registro do processo: CUDA / NVIDIA GeForce RTX 4070 Laptop GPU | VERIFIED |
| Texturas disponíveis | 126 imagens empacotadas, nenhuma biblioteca externa vinculada ao reabrir | VERIFIED |
| Preservar reconstrução, v01 e referências | SHA-256 dos dois modelos e das quatro referências de estilo inalterados | VERIFIED |
| Conferir visualmente o resultado final | revisao-visual.json vinculado aos hashes finais | VERIFIED |
| Atingir equivalência certificada a Unreal Engine | Sem benchmark ou cena Unreal equivalente para medir | UNKNOWN |

## Modelo e alterações

Arquivo: `projeto/industrial-v03/casa-fotografica.blend`. Cenas `PHOTO_Sala`, `PHOTO_Sala_Integrada`, `PHOTO_Cozinha`, `PHOTO_Lazer` e `PHOTO_Quarto`. A cena `EDITAR_Ativos` permite editar as malhas fontes das instâncias. Os pais `PHOTO …` permitem mover os móveis. Luzes comuns e painéis emissivos de cada cena também são objetos 3D editáveis.

Auditoria independente: 3376 objetos de malha, 431222 vértices em datablocks e 24 instâncias de ativos editáveis. Esses números descrevem o arquivo; não medem realismo visual.

Sofá Chesterfield em couro, mesa de centro em aço e madeira, almofadas, livros e plantas detalhados substituem volumes simplificados. A cozinha recebe fogão e acessórios vintage. O quarto conserva o beliche e acrescenta edredons com caída, proteções metálicas, cadeira com tela curva, rodízios e luminária articulada. Pisos, cortinas, materiais e câmeras foram revistos. A circulação e as paredes não foram deslocadas para imitar o enquadramento da inspiração.

## Execução e reprodução

Blender 5.2.4 / Cycles; CUDA na RTX 4070 Laptop, AgX, denoise, até 768 amostras adaptativas, limiar 0,008, mínimo 64. São parâmetros máximos, não contagem fixa de amostras por pixel. Logs `geracao-previa.log` e `renderizacao.log`; recibos `modelo.json`, `validacao.json`, `previas.json` e `renders.json`.

O driver CUDA antigo instalado no Linux impedia detectar a GPU. `scripts/run_blender.py --wsl-gpu` seleciona `/usr/lib/wsl/lib/libcuda.so.1` somente para o processo filho. A execução de render foi validada com CUDA; OptiX não foi usado. Nenhum driver ou configuração global foi alterado. Na interface, configure CUDA ou selecione CPU conforme a sua instalação.

Configuração ativa: `config/estilo-industrial-v03.json`. A base técnica está em `projeto/fontes/casa-base-detalhada.blend`; o estudo parcial v02 está arquivado com manifesto em `historico/estudos/industrial-v02/`. O gerador recusa sobrescrever um modelo existente. Consulte o README para renderizar ou escolher um destino novo antes de regenerar.

## Comparação e limites

Veja `renders/industrial-v03/referencias-e-proposta.jpg`: referência à esquerda, proposta à direita, com enquadramentos diferentes. Não é comparação pixel a pixel. Preservam-se cimento, madeira escura, metal preto, couro, espelho e luz quente. O sofá vintage, os eletrodomésticos, a distribuição real e a luz diferem das inspirações. A planta herdada mantém seis cadeiras de jantar e três banquetas, em vez das quantidades mostradas nos renders inspiradores. A marcenaria e alguns elementos herdados ainda são simplificados. A equivalência ao realismo de uma produção específica em Unreal continua sem comprovação objetiva.

O jardim do HDRI é contexto ilustrativo, não levantamento do imóvel. As medidas lineares, posições dos banheiros e detalhes da escada continuam com as incertezas da reconstrução. A área de matrícula não comprova todas as cotas do modelo. Este é um estudo de interiores, não projeto executivo.

Verificações adicionais: `python3 -m unittest scripts/test_blender_launcher.py -v` (três testes do ambiente e argumentos), `python3 -m py_compile` nos scripts alterados e `git diff --check`.

Os ativos externos são [CC0 do Poly Haven](https://polyhaven.com/license); URLs oficiais, bytes e SHA-256 constam nos manifestos de `assets/`. Os recursos usados estão empacotados. Fontes alternativas não utilizadas ficam identificadas na biblioteca. Imagens decorativas e telas são materiais de superfícies, não substituem paredes, móveis ou o render por uma fotografia plana.
