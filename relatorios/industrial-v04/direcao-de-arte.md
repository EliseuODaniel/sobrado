# Direção de arte e decisão de implementação

O pedido é deixar o projeto mais bonito e semelhante à referência principal, mantendo o `.blend` editável e a arquitetura construída nas revisões anteriores. A inspeção da v03 apontou diferenças de desenho e composição: sofá clássico, seis cadeiras volumosas, madeira escura, vegetação pequena e preenchimentos diferentes por câmera.

Foram comparadas duas abordagens: migrar o projeto para outro motor, ou conservar o Cycles e corrigir formas, materiais, composição e iluminação. Foi escolhida a segunda como solução pragmática: o render real em CUDA já estava validado e o arquivo nativo reúne toda a geometria. Uma migração, por si só, não corrigiria os desenhos divergentes. Não houve benchmark comparativo com Unreal.

Os recursos de sofá prontos avaliados no Poly Haven e na biblioteca Khronos tinham desenho clássico ou proporções diferentes. A solução usa almofadas detalhadas do ativo CC0 Modern Arm Chair 01, com estrutura contemporânea própria e quatro cadeiras adaptadas. Plantas e folhas usam geometria e UV de ativos CC0; não são fotografias planas colocadas no lugar dos móveis.

A iluminação usa uma coleção comum nas seis vistas. Os preenchimentos são painéis emissivos nativos que não aparecem diretamente em câmera, espelho ou vidro; emitem apenas pelo lado apontado para o ambiente. Spots e emissores das luminárias decorativas dão a luz quente. O espelho permanece material reflexivo calculado sobre a cena. O gerenciamento de cor continua AgX, com amostragem adaptativa e Light Tree. Estes são recursos de produção disponíveis no Blender, não certificação de equivalência visual a uma produção Unreal.

Fontes primárias consultadas:

- [Blender: amostragem e Light Tree](https://docs.staging.blender.org/manual/en/latest/render/cycles/render_settings/sampling.html)
- [Blender: configurações de luz](https://docs.blender.org/manual/en/5.0/render/cycles/light_settings.html)
- [Khronos: opções de sofá e materiais](https://github.com/KhronosGroup/glTF-Sample-Assets/blob/main/Models/GlamVelvetSofa/README.md) — avaliado, não incorporado
- [Poly Haven: licença CC0](https://polyhaven.com/license)
- Origem, licença, tamanho e hashes de cada recurso incorporado: `assets/industrial-v04/manifesto.json`.

As diferenças restantes são a profundidade real estimada da casa, o posicionamento dos elementos fixos, os aparelhos e partes simplificadas da marcenaria. Não foram encurtadas paredes ou movidas aberturas para imitar uma imagem de inspiração.
