# Residência 07 — atual, instalações 3D e ático

Conferência em 2026-11-12T18:07:47.788432+00:00. Entrega verificada para reconstrução documental e visual: 108 verificações de arquivos, além das conferências nativas abaixo. Não houve levantamento presencial nem cálculo estrutural.

| Modelo | Imagens/quadros finais | Verificações nativas | Arquivo editável |
| --- | ---: | ---: | --- |
| atual | 20 | 183 | `projeto/residencia-07-atual/casa-07-atual.blend` |
| instalacoes | 20 | 210 | `projeto/residencia-07/casa-07-instalacoes.blend` |
| atico | 48 | 251 | `projeto/residencia-07-atico-v05/atico-escadas-sobrepostas-caixa-lateral.blend` |

## Estado atual e refatoração

`renders/atual` foi inteiramente substituída pela reconstrução sobre a unidade 07. As 34 imagens da raiz foram preservadas em `historico/atual-pre-residencia07/renders`, com hashes em `atual-arquivos-anteriores.json`. A pasta vigente contém 20 vistas, duas plantas vetoriais em SVG/PDF/PNG, seis comparações foto/modelo, galeria navegável e caderno de 29 páginas.

A arquitetura deriva de ARQ03/04. A abertura do fundo da sala vem da instrução do usuário e das fotos; cobertura de vidro, vigas de madeira e divisão lazer/lavanderia aparecem na reconstrução posterior. A cozinha cinza, sofá cinza, mesa escura de vidro, bar com quatro banquetas e dormitórios seguem as referências disponíveis. A cama da suíte foi orientada para a parede da TV, com roupeiro ao fundo. As 31 fotos de entrada continuam com seus hashes originais.

## Estrutura e instalações tridimensionais

As quatro estruturas têm paredes em sálvia suave e materiais próprios para laje e escada. O arquivo original `casa-07.blend` continua intacto; as imagens coloridas são produzidas por `casa-07-instalacoes.blend`. A auditoria compara os vértices das cópias com os objetos do arquivo aprovado.

São 16 novas vistas das redes: elétrica, hidráulica, esgoto/ventilação e TV/telefone por pavimento e em conjunto; três sobreposições coordenadas e uma vista do reservatório. Paredes usam 12% de opacidade; lajes, 5,5%. As tubulações são curvas 3D editáveis. Diâmetros de exibição são ampliados onde necessário, mantendo o diâmetro nominal registrado nos objetos. Os recortes por pavimento são conferidos em Z.

## Proposta de ático

O ático vigente é a v05: dois lances exatamente sobre os inferiores e caixa de 1.000 L transferida para a esquerda, preservando sua cota de base. São 18 vistas gerais, seis isoladas e 24 quadros do giro. O forro tem reserva de 15 cm e as alturas são medidas sobre a geometria salva. As propostas antigas foram excluídas por solicitação do usuário. [Entrega vigente](../../../renders/residencia-07-atico-v05/LEIA-ME.md).

## Obrigações e limites

| Obrigação | Recibo observado | Situação |
| --- | --- | --- |
| Estrutura colorida sem alterar a base | `instalacoes-modelo.json`, `instalacoes-validacao.json` | VERIFICADO |
| Redes editáveis e paredes transparentes | Objetos e materiais do Blender reaberto; auditoria nativa | VERIFICADO |
| Imagens produzidas dos modelos salvos | `*-renders.json`, hashes nativos e PNG | VERIFICADO |
| Ático em projeto independente | V05 distinta, 48 cenas e auditoria de alinhamento/caixa/alturas | VERIFICADO |
| Atual com alterações e móveis | `atual-modelo.json`, imagens e comparações com as fotos | RECONSTRUÇÃO VISUAL |
| Organização e preservação do conteúdo anterior | Manifesto de 34 arquivos e hashes de arquivo | VERIFICADO |
| Medidas executadas de anexos e móveis | Fotos e inferências; sem medição local | APROXIMADAS |
| Trajetos reais das redes após a reforma | Não fornecidos em levantamento | DESCONHECIDOS |
| Fundações, armaduras, reforços e resistência da laje | Ausentes nas fontes analisadas | DESCONHECIDOS |

Os trajetos 3D de instalações são de estudo, com alturas documentadas transcritas quando disponíveis. A lavanderia posterior tem pontos inferidos das fotos, com altura de 1,00 m de estudo; a referência genérica a HID05 no grafo não confirma essa altura. Esta modelagem não atualiza os projetos de execução da reforma. As cotas da arquitetura original permanecem documentais; divergências internas dos PDFs estão no relatório principal. O vão, a laje, o suporte da caixa e a nova escada do ático precisam de dimensionamento específico.

## Reprodução e conferência

Os geradores são `residence07_current.py`, `residence07_services.py` com contrato em `config/residencia-07-estudos.json`; o ático usa `residence07_attic_v05.py` e sua configuração própria. `residence07_studies_audit.py` reabre os modelos; `residence07_studies_delivery.py` monta cadernos/galerias/plantas; `residence07_studies_verify.py` confere a entrega. Os recibos registram os hashes dos scripts que geraram cada modelo.

Os PNGs finais têm 1920 × 1440 pixels, Cycles/CUDA, 96 amostras e redução de ruído. As imagens são renders de geometria nativa, sem alterações generativas. A base documental mantém 29 imagens verificáveis, incluindo as quatro estruturas atualizadas pelo modelo complementar.

Os links e imagens das galerias HTML foram conferidos estaticamente. O conector de navegador estava sem Chrome, e a alternativa com Chromium local excedeu 35 segundos; o filtro da galeria não foi exercitado em navegador. Essa limitação não impede abrir os PNGs e os cadernos PDF diretamente.
