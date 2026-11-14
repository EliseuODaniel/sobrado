# Residência 07 — índice da entrega

Comece pelo [caderno completo](00-cadernos/caderno-residencia-07.pdf) ou pelo [painel de imagens](06-galerias/painel-geral.jpg).
As plantas e os renders desta revisão usam a tipologia da esquerda de ARQ03, que inclui a unidade 07.

Atualizações: [instalações 3D e paredes transparentes](03-instalacoes/3d/LEIA-ME.md), [estado atual pelas fotos](../atual/LEIA-ME.md), [industrial sobre a planta atual](../industrial-v05/LEIA-ME.md) e [ático com escadas sobrepostas e caixa lateral](../residencia-07-atico-v05/LEIA-ME.md).
As quatro estruturas receberam paredes em sálvia suave, lajes creme e escada areia. Suas imagens vêm do modelo editável `projeto/original/casa-07-instalacoes.blend`; a geometria da base foi preservada.

| Pasta | Conteúdo |
| --- | --- |
| `00-cadernos` | PDFs completos de apresentação e de instalações |
| `01-plantas-arquitetonicas` | Térreo, superior, sobreposição, corte e cotas originais; PNG, SVG e PDF |
| `02-estrutura/2d` | Base sem mobiliário, com paredes, lajes, vãos, escada e cotas |
| `02-estrutura/3d` | Térreo, superior, conjunto e vista explodida, sem móveis |
| `03-instalacoes` | Elétrica, hidráulica, esgoto, TV/telefone e sobreposições, por disciplina |
| `04-plantas-3d` | Plantas humanizadas e perspectivas de cada pavimento |
| `05-imagens` | Ambientes separados em térreo, superior, exteriores e proposta dos fundos |
| `06-galerias` | Painéis para conferir as vistas em conjunto |
| `_trabalho/previas` | Testes de render e enquadramento; não usar como entrega final |

## Estrutura em 3D, sem mobiliário

- [Térreo](02-estrutura/3d/estrutura-terreo-3d.png) e [superior](02-estrutura/3d/estrutura-superior-3d.png).
- [Conjunto](02-estrutura/3d/estrutura-conjunto-3d.png) e [vista explodida](02-estrutura/3d/estrutura-explodida-3d.png).
- [Base 2D do térreo](02-estrutura/2d/estrutura-terreo.pdf) e [base 2D do superior](02-estrutura/2d/estrutura-superior.pdf).

As paredes são cortadas a 1,15 m nas plantas 3D para mostrar a distribuição. Na vista explodida, somente a cópia ilustrativa do superior é afastada 4 m; o modelo de uso conserva o piso em +2,70 m. O conjunto mantém paredes em altura completa e omite a cobertura para leitura.

## Instalações e medidas

- [Caderno técnico com fontes, detalhes e legendas](00-cadernos/plantas-tecnicas-residencia-07.pdf).
- [Instalações juntas no térreo](03-instalacoes/coordenadas/instalacoes-coordenadas-terreo.pdf) e [no superior](03-instalacoes/coordenadas/instalacoes-coordenadas-superior.pdf).
- [Todas as cotas originais do térreo](01-plantas-arquitetonicas/cotas-originais-terreo.pdf) e [do superior](01-plantas-arquitetonicas/cotas-originais-superior.pdf).

Os traçados das instalações preservam os símbolos, circuitos, bitolas, diâmetros e alturas dos PDFs fornecidos. As folhas originais completas acompanham o caderno técnico. Há divergências entre algumas cotas, traços e áreas do projeto de 2011; elas estão descritas no [relatório](../../relatorios/original/RELATORIO.md).

## Modelo editável

Abra [casa-07.blend](../../projeto/original/casa-07.blend). As cenas `R07_estrutura-…` mostram a base 3D sem móveis. As demais cenas apresentam os ambientes, as plantas e as fachadas. `Num 0` mostra a câmera e `F12` renderiza; os caminhos já apontam para estas pastas.

A base estrutural representa os elementos indicados na arquitetura. Fundações, armaduras e dimensionamento resistente não foram fornecidos. A reconstrução não confirma as alterações executadas no imóvel após 2011. A decoração industrial e os anexos dos fundos são proposta, identificada separadamente.
