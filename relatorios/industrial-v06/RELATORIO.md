# Industrial v06 — residência 07

Conferência em 2026-11-13T08:14:56.143358+00:00. **398 verificações nativas e 98 de entrega aprovadas.**

| Escopo | Evidência | Situação |
| --- | --- | --- |
| Descarte da v04 | `descarte-v04.json`, inventário e biblioteca extraída | Verificado |
| Arquitetura atual | 795 impressões geométricas e comparação independente ao reabrir a v05 | Preservada |
| Materiais e recursos | 19 recursos 4K CC0 íntegros, telas próprias, recursos empacotados | Verificado |
| Imagens | 31 saídas Cycles/GPU em 3840 × 2880, PNG de 16 bits, hashes do modelo e dos arquivos | Verificado |
| Entrega | Plantas, pares dia/noite, comparações, galeria e caderno de 41 páginas | Verificado estaticamente |
| Unreal/Lumen | Usuário informou não possuir instalação; nenhum teste no Unreal executado | Pendente |

O render é físico e usa recursos 3D editáveis. A qualidade visual deve ser avaliada nas imagens; uma contagem de amostras ou verificações não prova fotorrealismo. O entorno é ilustrativo e as dimensões aproximadas da reforma e dos móveis permanecem identificadas como estudo. Esta revisão não altera a base original, a casa atual ou o ático v05.

Recibos: `modelo.json`, `renders.json`, `gpu-render.json`, `validacao-completa.json`, `validacao-entrega.json`. O consumo em `gpu-render.json` é amostrado para a GPU inteira e inclui outros processos; não equivale ao pico exato do Blender. Os tempos são desta máquina e configuração, sem comparação com Unreal.

[Galeria](../../renders/industrial-v06/galeria.html) · [índice](../../renders/industrial-v06/LEIA-ME.md).

## Fechamento da revisão

A galeria final passou em **11 verificações no Chromium**: 31 cartões, 37 imagens carregadas, cinco filtros, três controles de dia/noite, links locais e apresentações de desktop/celular. Consulte `browser-final.json` e as capturas `galeria-final-desktop.png` e `galeria-final-mobile.png`.

Os 31 enquadramentos finais e páginas representativas do caderno foram revisados visualmente. Couro, madeira, cuba, vidros e cadeira tiveram recortes na densidade original. Os painéis e limites perceptivos estão em `revisao-visual.json`. Alguns móveis e equipamentos continuam como formas de estudo; o entorno é ilustrativo.

A retirada da geladeira também foi aplicada às versões industriais anteriores, incluindo 11 rascunhos e 37 prévias: `rascunhos-industriais-sem-geladeira.json`, `validacao-rascunhos-industriais.json` e `validacao-recuperacao-rascunhos-v05.json`. A geladeira da cozinha foi preservada.

Uma divergência entre os contadores de tempo do Windows e do controlador WSL está documentada em `observacoes-tempos.json`; esse quadro não serve como benchmark. Nenhum teste no Unreal foi executado.
