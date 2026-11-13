# Casa atual — reconstrução pelas fotos

A versão anterior é visualmente simplificada: faltam cortinas, as janelas perderam a posição de seus pais, os estofados têm volumes rígidos e os eletrodomésticos carecem de peças e relevos. A arquitetura documental, o fundo aberto e a divisão posterior continuam como base. Fotografias sem escala não estabelecem medidas exatas dos móveis.

Foram comparadas duas abordagens: trocar por móveis escaneados genéricos, ou reconstruir os móveis observados com detalhes e materiais físicos. A primeira produz rapidamente superfícies convincentes, mas troca o desenho da casa. Foi escolhida a segunda, uma aproximação prática da reconstrução de referência. Fotogrametria rigorosa exigiria fotos calibradas, maior sobreposição e medidas de campo, ausentes no conjunto fornecido.

O Cycles continua adequado aos renders estáticos; trocar apenas o motor não corrige móveis, aberturas e cores diferentes. Unreal não está instalado. Não foi realizado teste comparativo com Unreal.

Fontes oficiais consultadas em 13/11/2026:

- [Principled BSDF / OpenPBR](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html): rugosidade, metal, transmissão, camada de tecido e índice de refração. Cópia de consulta do texto oficial em `fontes/principled.rst`, obtida do repositório Blender Projects.
- [Cycles: redução de ruído](https://docs.blender.org/manual/en/latest/render/cycles/optimizations/reducing_noise.html): amostragem, iluminação e ruído em interiores. Texto oficial em `fontes/reducing_noise.rst`.
- [Cycles — renderização](https://www.blender.org/features/rendering/): rastreamento de raios para produção e suporte OptiX.

Critérios visuais por ambiente:

| Ambiente | Elementos identificáveis nas fotos |
|---|---|
| Sala/jantar | sofá cinza com chaise junto à janela, cortina inteira, painel branco com LEDs verticais, rack mel/branco, seis cadeiras cinza com madeira escura e costura diagonal, mesa preta reflexiva, orquídeas, pendente duplo dourado |
| Cozinha | armários cinza azulado, puxadores inox, granito preto pontilhado, azulejo branco com rejunte claro, cuba rebaixada, fogão com grelhas e forno, coifa de vidro curvo, micro-ondas e lava-louças |
| Bar | quatro cadeiras altas estofadas, louceiro branco com vidro/prateleiras/copos, mosaico oxidado pequeno, tampo preto e cuba, madeira e vidro na cobertura, geladeira observada preservada |
| Lavanderia | lavadora frontal com tambor/vidro, lavadora superior com painel elevado, tanque fundo, filetes de travertino, armários claros, plantas pequenas no peitoril |
| Suíte | cabeceira bege modular, parede taupe com frisos verticais, colcha caída, cortinas, roupeiro amadeirado com trilhos, TV/lareira e split |
| Quarto branco | cama branca com grades, papel de corações, portas e puxadores dos armários, persiana, estante e TV |
| Quarto azul | papel triangular azul, bancada e prateleiras brancas, teclado/mouse/PC, beliche com colchas e grade superior |
| Banheiros/escada | peças reposicionadas corretamente, granito cinza, louças claras, perfis claros, papel elíptico no lavabo |

A conferência visual é separada das verificações automáticas. Contagem de amostras e resolução não provam semelhança fotográfica. Cada enquadramento precisa ser visto antes da entrega final. Cotas estruturais são preservadas por impressão digital da geometria; esquadrias defeituosas são comparadas separadamente com suas matrizes no modelo oficial 07.

## Refinamento após inspecionar o primeiro PNG 4K

O primeiro recorte em densidade nativa mostrou que o ruído procedural dos tecidos era fino demais para produzir a aparência observada nas fotos. Foram selecionadas capturas multicanal de [camurça sintética](https://polyhaven.com/a/scuba_suede), [tecido fino](https://polyhaven.com/a/bi_stretch) e [algodão em relevo](https://polyhaven.com/a/waffle_pique_cotton), todas com [licença CC0](https://polyhaven.com/license). São equivalentes visuais recoloridos: não identificam a composição ou o fabricante dos móveis reais.

As capturas têm escala física aproximada de 26–28 cm, registrada em metros no manifesto. Albedo, rugosidade e normais usam 4K; anisotropia e nível especular usam 2K. Normais e dados EXR preservam a precisão sem a sobrecarga dos PNGs de 16 bits; os arquivos são validados com tamanho/MD5 da API oficial e SHA local. Os canais de dados ficam em Non-Color.

O shader Blender oficial da captura foi inspecionado em `fontes/scuba-nodes.json`: `spec_ior` alimenta **Specular IOR Level**, e a rugosidade alimenta **Roughness** e **Diffuse Roughness**. Essa ligação foi mantida, com ajuste visual da cor ao cinza/branco das referências. A variação de refletância e relevo vem das capturas.

A orquídea foi reconstruída com duas pétalas largas, três sépalas e labelo curvo por flor, folhas finas curvas e hastes com alturas variadas. O arranjo ficou mais compacto e com distribuição central. Continua sendo uma interpretação geométrica das fotos, sem escaneamento do exemplar.

A pose das folhas das portas passou a usar a matriz local recursiva das fontes preservadas fora da cena ativa. A conferência independente verifica centro, nível e alinhamento das sete folhas; isso evita que cópias recebam transformações antigas da avaliação do Blender.
