# Validação da água quente — 14/11/2026

## Resultado

Havia um defeito na representação 3D: o gerador reaproveitado construía uma coluna por ponto quente, sobrepondo subidas e distribuidores nos fundos. A revisão vigente usa uma coluna compartilhada entre os pavimentos e uma distribuição comum com derivações. A caixa continua na posição original, sem construção do ático.

| Obrigação | Evidência observada | Estado |
| --- | --- | --- |
| Verificar se as linhas representavam ramais distintos | Antes: 18 trechos quentes não nulos; cinco extras com coordenadas idênticas, quatro subidas geométricas coincidentes cruzando o piso | VERIFICADO: havia duplicação, não apenas cinco ramais legítimos |
| Conferir o princípio de distribuição | HID04, planta superior: AQ-1, CPVC 22 mm, indicação de uma distribuição comum sob a laje; recorte `hid04-superior.png` | VERIFICADO no desenho fornecido |
| Conferir os pontos de consumo | HID05, elevação 02 cozinha e elevações 06/07 dos banheiros: lavatório e chuveiro em cada banho | VERIFICADO no desenho; cinco pontos preservados no estudo |
| Eliminar trechos coincidentes | Auditoria geométrica procura sobreposição exata e parcial de segmentos colineares, não apenas igualdade de nomes | VERIFICADO: zero sobreposições na rede quente corrigida |
| Preservar alimentação e alcance dos aparelhos | Teste percorre a rede desde a entrada, passando por reservatório/aquecedor, até os pontos frios e quentes | VERIFICADO no grafo de estudo |
| Conferir o arquivo final | Blender reaberto, coordenadas dos trechos e pontos conferidas contra o grafo; sete cenas, forros e caixa original | VERIFICADO em `../validacao.json` |
| Confirmar a tubulação construída e as cotas completas | Não há levantamento de todos os caminhos embutidos | DESCONHECIDO |

## O que foi corrigido

A antiga função criava repetidamente o percurso aquecedor → coluna → distribuição para cada lavatório e chuveiro. Quatro nomes diferentes apontavam para a mesma subida. Os distribuidores para cada banheiro também se repetiam e se sobrepunham parcialmente entre si.

O modelo corrigido tem uma subida comum, um distribuidor compartilhado com derivações e um ramal separado para a cozinha. Permanecem exatamente cozinha, lavatório e chuveiro da suíte e lavatório e chuveiro do banheiro social. Não foram criadas linhas quentes para vasos ou lavanderia. As conexões preservam o diâmetro nominal de 22 mm do estudo; a espessura visual continua ampliada.

O número de segmentos de desenho não equivale ao número de canos independentes. A distribuição foi dividida em trechos nos pontos de derivação, para expressar a conexão corretamente, sem desenhar o mesmo tubo várias vezes.

## Fontes, inferências e desconhecidos

HID04 e HID05 pertencem à pasta `plantas/PDF - COMPLEMENTARES ZANON 131`; os hashes das duas pranchas estão em `auditoria.json`. Foram usados os recortes de leitura e a prancha completa da HID05 anexados nesta pasta. A indicação "sob a laje" sustenta o princípio do distribuidor comum, mas não fornece todas as alturas e trajetórias do volume construído.

A altura Z=5,15 m do distribuidor e a compatibilização tridimensional são escolhas de apresentação. O registro XY é aproximado pela planta. As posições do aquecedor e dos caminhos embutidos não foram medidas no local. A revisão não valida execução, pressão, isolamento térmico, perda de carga ou interferências com a estrutura. Para confirmar esses itens, faltam levantamento presencial e projeto hidráulico compatibilizado.

Veredito limitado ao modelo em 14/11/2026: duplicações identificadas e corrigidas, com topologia compartilhada e cinco pontos mantidos. A instalação real permanece não validada. Não foram renderizadas novas imagens 3D; os PNGs desta pasta são somente recortes das pranchas de referência.

[Blender vigente](../../../projeto/infraestrutura/instalacoes-pavimentos-forro.blend) · [Auditoria antes/depois](auditoria.json) · [Validação do Blender](../validacao.json).
