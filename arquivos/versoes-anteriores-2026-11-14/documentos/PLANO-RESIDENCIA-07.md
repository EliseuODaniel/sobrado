# Residência 07 — plano consolidado

A base documental, o estado atual pelas fotos e a proposta de ático têm modelos separados. O plano inclui desenhos 2D, geometria 3D editável, imagens, instalações e organização dos arquivos.

A evolução para imagens fotorrealistas e possível apresentação no Unreal está no [plano de fotorrealismo](PLANO-FOTORREALISMO.md), pesquisado em 12/11/2026. Inclui materiais, detalhes, mobiliário, iluminação, hardware e um piloto comparando Cycles com Unreal antes da expansão aos modelos. Essa etapa está planejada; os modelos atuais ainda não receberam essa conversão.

| Etapa | Escopo e fonte | Entrega |
| --- | --- | --- |
| Base da unidade 07 | ARQ03, tipologia esquerda; níveis e cobertura de ARQ04 | `projeto/residencia-07/casa-07.blend`; plantas em `renders/residencia-07` |
| Planta apenas estrutural | Paredes, vãos, lajes, escada e elementos representados na arquitetura; cotas documentais | `02-estrutura/2d` e quatro vistas em `02-estrutura/3d` |
| Cores suaves | Paredes sálvia, lajes creme, escada areia; geometria preservada | `casa-07-instalacoes.blend` e quatro imagens estruturais atualizadas |
| Instalações 2D | Elétrica, água fria/quente, esgoto/ventilação, TV/telefone; legendas e detalhes dos complementares | Plantas vetoriais e caderno técnico em `03-instalacoes` e `00-cadernos` |
| Instalações 3D | Objetos tridimensionais por disciplina e pavimento; paredes parcialmente transparentes e vistas conjuntas | 16 vistas novas em `03-instalacoes/3d`, modelo editável e legenda de cores |
| Ático independente v05 | Dois lances novos exatamente sobre os existentes; caixa e área técnica transferidas à esquerda; forro de 15 cm e mansardas preservados | `projeto/residencia-07-atico-v05` e `renders/residencia-07-atico-v05`; 18 vistas gerais, seis isoladas, giro e cinco desenhos cotados |
| Estado atual | Base 07 com alterações informadas e móveis de `referencias-originais`; fundo aberto, cobertura e separação lazer/lavanderia | `projeto/residencia-07-atual`; 20 vistas e duas plantas cotadas |
| Industrial na planta atual | Quatro referências de estilo; arquitetura atual preservada e alternativa de escritório | `projeto/industrial-v05`, `renders/industrial-v05`; 25 vistas e plantas cotadas |
| Refatoração de `renders/atual` | Arquivar 34 imagens anteriores com hashes; reorganizar por plantas, ambientes, exteriores, comparações e cadernos | Índice, galeria navegável, seis pares foto/modelo e caderno PDF |
| Conferência | Reabrir cada Blender, verificar geometria, destinos, transparência e origem das imagens; conferir PDFs, plantas e links | `relatorios/residencia-07/estudo-instalacoes-atico` |

As medidas da base original são registradas a partir dos PDFs, com divergências internas preservadas no relatório. Isso não confirma as medidas da construção hoje. Os anexos posteriores e móveis vistos nas fotos têm dimensões aproximadas; essas cotas são marcadas com ≈ nas plantas atuais.

As fundações, armaduras e seções resistentes não estão documentadas nas fontes analisadas. A representação estrutural mostra a base arquitetônica disponível. Os percursos embutidos das redes são de estudo: pontos e alturas documentados são identificados, e as rotas 3D não são apresentadas como levantamento da reforma.

Na v05, a última decisão do usuário permite mover a caixa para posicionar os dois lances novos exatamente sobre os existentes. Os 16 pisos mantêm o mesmo XY e são deslocados apenas +2,70 m. A caixa passa de X=5,35 para X=1,80 m, mantendo Y=3,175 m e base +5,45 m. A área técnica é transferida à esquerda e a escada se liga diretamente ao hall. Os dois quartos ficam preservados; a ligação pelo quarto frontal da v04 deixa de existir. O hall nominal de 0,65 m permanece como restrição da base. Abertura da laje em L, nova escada, apoios e cargas do reservatório precisam de dimensionamento específico.

O forro mantém 14 sólidos próprios e reserva vertical proposta de 0,15 m abaixo dos 0,08 m de cobertura, incluindo placa de 0,0125 m e fixação. A altura livre máxima fica em 3,77 m; a menor folga amostrada nas escadas é 2,21 m sob o patamar retido. A faixa de 2,10 m usa a face acabada do forro como referência geométrica, sem aprovação legal ou executiva. [Entrega v05](renders/residencia-07-atico-v05/LEIA-ME.md) e [relatório](relatorios/residencia-07-atico-v05/RELATORIO.md). As propostas anteriores de acesso foram excluídas a pedido do usuário; a base original, o estado atual e a v05 permanecem.

A situação de cada entrega e as evidências observadas ficam no [relatório consolidado](relatorios/residencia-07/estudo-instalacoes-atico/RELATORIO.md).
