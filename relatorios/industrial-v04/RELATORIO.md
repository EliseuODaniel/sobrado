# Industrial v04 — direção de arte mais próxima da referência

UTC: 2026-11-11T13:17:04.722243+00:00

Foram produzidas seis imagens nativas em 3342 × 1882, duas vezes cada dimensão da referência principal. A proposta aproxima móveis, materiais e iluminação da inspiração sem alterar paredes, aberturas, escada ou encaixe dos pavimentos. Tudo continua no `.blend` editável; não houve retoque generativo das imagens finais.

| Obrigação | Recibo observado | Estado |
| --- | --- | --- |
| Nativo editável e autossuficiente | Modelo salvo/reaberto; 150 imagens empacotadas e zero bibliotecas externas | VERIFIED |
| Preservar planta e fonte v03 | 3576 hashes de geometrias herdadas sem diferenças; SHA da base inalterado | VERIFIED |
| Manter alinhamento dos pavimentos | Três verificações do contorno e faces posteriores | VERIFIED |
| Móveis próximos da composição | Três assentos no sofá, quatro cadeiras em 2 + 2, cabeceiras livres; conferência nativa | VERIFIED |
| Gerar todas as imagens a partir do arquivo salvo | Seis PNGs com nomes, dimensões, bytes e hashes conciliados | VERIFIED |
| Dispositivo efetivo | CUDA: NVIDIA GeForce RTX 4070 Laptop GPU | VERIFIED |
| Preservar reconstrução, v01, v03 e referências | Hashes dos modelos, imagens anteriores e referências conferidos | VERIFIED |
| Inspeção dos finais e comparações | revisao-visual.json vinculado aos seis hashes | VERIFIED |
| Certificar equivalência estética a Unreal | Sem benchmark comparável; o critério é visual | UNKNOWN |

## O que mudou

O sofá clássico foi substituído por estrutura contemporânea própria, com almofadas derivadas do ativo detalhado Modern Arm Chair 01, preservando seus UVs e pregas. O couro foi ajustado para caramelo; a manta tem geometria de caída e UV de tecido. Há três assentos e encostos, braços arredondados, costuras e pés metálicos.

As seis cadeiras antigas foram ocultadas e preservadas. Quatro cadeiras novas usam assento e encosto em couro sobre estrutura de aço, mantendo as cabeceiras livres. A mesa original continua na mesma posição. A mesa de centro tem três tábuas, quadro de metal, livros, tigela e arranjo. Madeira, piso e pedra do bar foram revistos. O painel da TV tem cantos com raio no plano da parede, UV próprio e quatro downlights.

As plantas usam geometrias e mapas PBR CC0. Uma folha com UV foi isolada para as pendentes; a calathea usa apenas uma touceira do conjunto original. A iluminação comum em `DESIGN_Iluminacao` combina spots e painéis emissivos de fotografia 3D. Estes painéis são editáveis, emitem pelo lado voltado ao ambiente e ficam fora da câmera/reflexos diretos. Não são luminárias confirmadas do imóvel. O espelho continua refletindo a cena 3D.

## Arquivo, execução e edição

Modelo: `projeto/industrial-v04/casa-industrial-refinada.blend`. Cenas: DESIGN_Sala_Integrada, DESIGN_Sala, DESIGN_Sala_TV, DESIGN_Cozinha, DESIGN_Lazer, DESIGN_Quarto. Coleção principal: `DESIGN04`. Pais `DESIGN Sofá contemporâneo`, `DESIGN Mesa de centro` e `DESIGN Cadeira jantar …` permitem mover os móveis. Os materiais `DESIGN …` ficam no Shader Editor; as fontes estão em `EDITAR_Ativos_V04`. O README descreve a edição e os comandos.

Blender 5.2.4 LTS; Cycles/CUDA, Light Tree, AgX, denoise e até 512 amostras adaptativas, limiar 0.007. O total registrado para renderizar as seis vistas foi 24.8 minutos, incluindo preparação por vista; não é benchmark entre motores. A configuração está em `config/estilo-industrial-v04.json`; o gerador é `scripts/refine_industrial.py`. Ele recusa sobrescrever o modelo de destino.

Recibos: `modelo.json`, `validacao.json`, `recursos-nativos.json`, `previas.json`, `renders.json`, `testes.log` e os logs de geração/renderização. A auditoria independente reabriu o arquivo e conferiu recursos, móveis, câmeras e resolução. Sete testes verificaram o launcher e o download de ativos, incluindo integridade, retomada e proteção de arquivos existentes. Os recursos são [CC0 do Poly Haven](https://polyhaven.com/license), com MD5 do fornecedor e SHA-256 em `assets/industrial-v04/manifesto.json`.

## Comparação e limites

`referencias-e-proposta.jpg` mostra inspiração à esquerda e proposta à direita. `evolucao-v03-v04.jpg` mostra a evolução com enquadramentos diferentes; não é comparação pixel a pixel. A casa é mais profunda do que a composição sugerida na referência. Escada, entrada diagonal, aberturas e aparelhos condicionam o resultado. Não foram deslocados elementos fixos para falsear essa correspondência.

A marcenaria e alguns aparelhos ainda têm simplificações. O jardim do HDRI é ilustrativo. As medidas, detalhes da escada e posições dos banheiros superiores mantêm as incertezas da reconstrução. A proposta é um estudo de interiores, não projeto executivo ou certificação de equivalência visual a Unreal.

A v03 foi preservada como base e comparação. Os rascunhos v04 foram guardados localmente em `historico/rascunhos/industrial-v04/`, fora do Git. O manifesto desta entrega registra arquivos e hashes; publicação é verificada após o commit para evitar autorreferência do SHA.
