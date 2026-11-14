# Industrial v05 — residência 07 na planta atual

Conferência: 2026-11-13T00:44:52.927182+00:00. 224 verificações nativas e 56 verificações de entrega passaram. O escopo é documental e visual, sem levantamento presencial ou projeto executivo.

Foram comparadas duas opções: adaptar a arquitetura estimada da v04 ou usar diretamente a casa atual. Foi adotada a segunda, preservando paredes, vãos, lajes, escada, cobertura e divisão dos fundos. A v04 fornece apenas componentes de móveis e materiais. É uma solução pragmática com um contrato explícito de geometria, em vez de recalibrar uma planta estimada.

| Obrigação | Evidência | Estado |
| --- | --- | --- |
| Base oficial da unidade 07 | `config/residencia-07.json`, ARQ03/04 e seus hashes | VERIFICADO para a geometria documental |
| Considerar a planta atual alterada | Hash de `casa-07-atual.blend`, 795 elementos arquitetônicos e comparação independente com a fonte | VERIFICADO |
| Preservar a casa atual e a v04 | Hashes dos arquivos antes e depois | VERIFICADO |
| Seguir as quatro referências de estilo | Referências com hashes, prévias e painel `referencias-e-proposta.jpg` | INTERPRETAÇÃO VISUAL |
| Gerar todas as vistas | 25 cenas e PNGs com hash do modelo nativo | VERIFICADO |
| Plantas coerentes | Polígonos e linhas dos SVG iguais à arquitetura atual; quatro vistas nativas humanizadas/3D | VERIFICADO |
| Escritório como alternativa | Duas cenas exclusivas, sem a coleção do beliche | VERIFICADO |
| Medidas executadas dos anexos | Fotos e instruções; sem medição no local | APROXIMADAS |

O acabamento usa cimento suave, couro caramelo, madeira quente, aço preto, pedra oxidada e luz âmbar. A mesa e as banquetas são modelos novos; sofá e cadeiras são componentes nativos reaproveitados da biblioteca v04, sem a sua arquitetura. As imagens PBR usadas estão empacotadas no Blender.

As medidas documentais incluem largura 6,35 m até o eixo da geminação, superior em +2,70 m, pé-direito 2,55 m e laje 0,15 m. As divergências internas dos PDFs permanecem no relatório da base. A abertura dos fundos e seus anexos vêm do modelo atual; não são apresentados como partes confirmadas do desenho aprovado de 2011.

São 25 renders em 1920 × 1440, Cycles/CUDA, 128 amostras; duas plantas vetoriais em SVG/PDF/PNG, duas folhas de cotas originais, quatro comparações atual/industrial, um painel de referências e caderno de 35 páginas. A galeria HTML teve seus links conferidos estaticamente; não foi exercitada em navegador.

As cenas de escritório propõem outro uso de mobiliário no quarto dos fundos. As outras cenas e a planta superior usam a opção com dormitório; não se somam as duas opções no mesmo ambiente. A proposta não altera ou certifica instalações elétricas/hidráulicas existentes.

Referência técnica consultada: [atribuição e reutilização de materiais no Blender](https://docs.blender.org/manual/en/latest/render/materials/assignment.html). Os geradores e recibos mantêm a separação entre geometria, materiais, fontes e renderizações.
