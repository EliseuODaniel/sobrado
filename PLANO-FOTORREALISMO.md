# Plano de fotorrealismo — residência 07

Pesquisa e auditoria em **12/11/2026**. Escopo do plano: base original, estado atual, industrial v05, ático v05 e visualizações de estrutura/instalações. **As revisões industrial v06 e atual v02 em Cycles foram executadas após esta pesquisa. A expansão do fotorrealismo para a base original, o ático e a comparação no Unreal continuam como etapas futuras.**

## Execução industrial concluída em 13/11/2026

A industrial v06 entrega **31 PNGs em 3840 × 2880 e 16 bits**, incluindo três pares de dia e noite, uma galeria interativa e um caderno de 41 páginas. Materiais 4K, iluminação, ferragens, rodapés, rack, cadeira, telas, cuba e esquadria foram refinados sobre a planta atual. As 795 impressões geométricas da arquitetura protegida foram preservadas.

A industrial v04 foi descartada; os móveis e recursos úteis ficaram em biblioteca independente. A geladeira do bar foi retirada dos modelos e imagens industriais, incluindo 11 rascunhos e 37 prévias arquivadas. A geladeira da cozinha permanece. A recuperação da apresentação de um rascunho v05 e suas conferências estão documentadas nos recibos de manutenção.

Foram aprovadas 398 verificações nativas, 98 da entrega e 11 do navegador, além da revisão visual dos ângulos. Isso verifica integridade e comportamento; não certifica aparência fotográfica por uma métrica automática. Alguns móveis e equipamentos conservam formas e dimensões de estudo. A base original e o ático continuam como etapas da expansão. O estado atual recebeu uma reconstrução própria orientada às fotos, descrita abaixo.

O usuário informou não ter Unreal instalado. A produção foi feita em **Cycles/GPU**, sem comparação entre motores, passeio Lumen ou medição de FPS no Unreal. O intercâmbio de geometria/UVs passou no teste do cubo de 1 m e de três paredes; os GLBs possuem materiais de identificação, e os acabamentos completos estão no Blender.

[Galeria industrial v06](renders/industrial-v06/galeria.html) · [caderno PDF](renders/industrial-v06/00-cadernos/caderno-industrial-v06.pdf) · [modelo editável](projeto/industrial-v06/casa-industrial-fotorrealista.blend) · [relatório](relatorios/industrial-v06/RELATORIO.md).

## Estado atual — revisão fiel v02 concluída

O modelo atual foi reconstruído com os elementos reconhecíveis nas fotos: sofá e cadeiras cinza, cortinas, painel branco/LEDs, rack mel, mesa de vidro, orquídeas, cozinha, bar, lavanderia, dormitórios e banheiros. As superfícies do sofá, cadeiras e colchas receberam capturas têxteis com rugosidade, normais, refletância e anisotropia, mantendo as cores observadas. A fachada recebeu acabamento bege, cobertura cinza e pavimento intertravado; os vizinhos na vista frontal são contexto ilustrativo.

Foram preservadas 674 impressões de geometria e restauradas 121 posições de esquadria pela fonte oficial. As sete folhas de porta da apresentação têm centro, altura e orientação conferidos. São 274 verificações nativas aprovadas; os recortes de detalhe têm densidade de pixels do render final. Isso verifica integridade e detalhes observáveis, sem atribuir uma pontuação automática de semelhança fotográfica.

As 26 imagens nativas em 3840 × 2880 e 16 bits estão concluídas, com 16 comparações foto/modelo, galeria e caderno de 45 páginas. Foram aprovadas 188 verificações da entrega e 12 do navegador, além da revisão visual das 26 vistas. A fonte antiga da casa atual e as propostas industriais foram preservadas. A geladeira do bar permanece nesta reconstrução da casa fotografada. As medidas de móveis e anexos continuam aproximadas.

[Galeria atual v02](renders/atual/galeria.html) · [caderno PDF](renders/atual/00-cadernos/caderno-atual.pdf) · [modelo atual v02](projeto/residencia-07-atual-v02/casa-07-atual-fiel.blend) · [relatório](relatorios/atual-fiel-v02/RELATORIO.md) · [critérios e pesquisa](relatorios/atual-fiel-v02/PESQUISA-E-CRITERIOS.md).

## 1. Direção recomendada

Para alcançar aparência de fotografia de arquitetura e permitir visitar a casa, recomendo **manter a modelagem métrica no Blender e acrescentar Unreal Engine como ambiente de apresentação**, com dois modos:

- **Passeio interativo:** Lumen com ray tracing por hardware, medindo qualidade e desempenho nesta máquina.
- **Imagens finais e sequências selecionadas:** Path Tracer, que calcula a iluminação por trajetórias de luz e está integrado ao Sequencer/Movie Render Queue. Esse modo prioriza qualidade e pode levar tempo para produzir cada quadro; não pressupõe navegação instantânea nessa mesma qualidade. [Documentação do Path Tracer](https://dev.epicgames.com/documentation/en-us/unreal-engine/path-tracer-in-unreal-engine).

Primeiro, produzir um **piloto comparável em Cycles e Unreal**, com os mesmos detalhes, materiais e enquadramentos. A decisão de migrar o restante depende desse resultado. Cycles já é um renderizador físico adequado a imagens finais; sua presença nos cinco arquivos foi confirmada. Mudar de motor não acrescenta, sozinho, tecido, juntas, esquadrias detalhadas ou um entorno convincente. [Manual oficial do Cycles](https://docs.blender.org/manual/en/5.0/render/cycles/introduction.html).

**Versão proposta:** família **UE 5.8**, fixando o hotfix e os plugins depois do teste de compatibilidade. A Epic publicou a 5.8 em 23/06/2026. A **5.9 MegaJam Preview**, de 09/11/2026, é uma prévia explicitamente instável, com validação mais curta; reservar para testes em cópia. Não há motivo para condicionar o realismo deste projeto à adoção dessa prévia. [Lançamento 5.8](https://www.unrealengine.com/news/unreal-engine-5-8-is-now-available), [anúncio oficial da 5.9 Preview](https://forums.unrealengine.com/t/unreal-engine-5-9-megajam-preview/2852840).

## 2. O que existe e o que limita o resultado

Abri os cinco `.blend` vigentes em Blender 5.2.4 LTS e examinei uma cena representativa de cada arquivo. Os hashes antes/depois são iguais: nenhum modelo foi salvo ou modificado pela auditoria. Também examinei os PNGs da sala atual, sala industrial e interior frontal do ático. Dados reproduzíveis em [auditoria-modelos.json](relatorios/fotorrealismo-2026-11-12/auditoria-modelos.json).

| Modelo / cena examinada | Materiais com nós de imagem / materiais usados | Objetos de malha sem UV / objetos de malha habilitados | Configuração atual |
| --- | ---: | ---: | --- |
| Original / `R07_sala-integrada` | 4 / 27 | 856 / 1.084 | Cycles, 192 amostras, 1920 × 1440 |
| Atual / `ATUAL_sala-fundos` | 1 / 55 | 1.222 / 1.913 | Cycles, 96 amostras, 1920 × 1440 |
| Estrutura / `COLOR_estrutura-terreo-3d` | 0 / 3 | 38 / 44 | Cycles, 96 amostras, 1920 × 1440 |
| Industrial / `IND07_sala-fundos` | 5 / 56 | 1.180 / 1.927 | Cycles, 128 amostras, 1920 × 1440 |
| Ático / `ATC5_atico-interior-frente` | 1 / 41 | 490 / 781 | Cycles, 96 amostras, 1920 × 1440 |

Os números são do primeiro view layer, respeitando exclusões e `hide_render`, sem eliminar objetos fora da câmera. “Ter UV” significa possuir coordenadas de textura; não comprova ausência de distorção. Nós de imagem podem estar desconectados. Materiais procedurais e projeção tridimensional podem funcionar sem UV: esses totais indicam o trabalho de preparação, não uma taxa automática de defeitos. A cena estrutural foi feita para leitura técnica, portanto sua simplicidade é intencional.

**Fatos adicionais:** as imagens de textura referenciadas nas cenas examinadas têm 2048 × 2048; não foram encontrados arquivos ausentes entre essas referências. Todas as cenas usam AgX, amostragem adaptativa e denoising. Seus mundos têm céu procedural e não têm nós de textura de ambiente HDRI. A sala industrial tem 29 luzes de área, três spots e um sol; essa contagem não demonstra erro, mas recomenda revisar a contribuição de cada fonte.

**Diagnóstico visual, com interpretação:**

- [Sala atual](renders/atual/02-ambientes/sala-fundos.png): cadeiras, sofá e marcenaria representam a disposição, mas ainda faltam detalhes de construção, costuras, variação de superfície e encontros com o piso. A luz é bastante uniforme.
- [Sala industrial](renders/industrial-v05/02-ambientes/sala-fundos.png): já há texturas, vegetação e móveis aproveitáveis. A madeira, o cimento e os tecidos precisam de escala e resposta à luz mais convincentes; revisar acabamentos, repetição e detalhes em primeiro plano. Não cabe descartar toda a biblioteca existente.
- [Ático](renders/residencia-07-atico-v05/02-interiores/atico-interior-frente.png): a câmera mostra o sofá muito de perto e omite boa parte do espaço; a vista externa é genérica. Materiais e móveis são mais esquemáticos. Novos enquadramentos e entorno têm prioridade junto ao acabamento.

Essas observações cobrem três imagens, não uma inspeção visual de todos os ângulos. O inventário cobre os cinco arquivos; a revisão artística completa fica no início da execução.

## 3. Comparação de caminhos

| Caminho | Melhor aplicação neste projeto | Trabalho e limitações | Decisão |
| --- | --- | --- | --- |
| **Blender + Cycles** | Fotografias virtuais, detalhes, cortes e automação já existente | Preserva os geradores; exige melhorar conteúdo e iluminação. Imagens finais têm tempo de cálculo | Referência de comparação e alternativa de produção se só forem necessárias imagens |
| **Blender + Unreal 5.8** | Passeio pela casa, variações de projeto e imagens finais com Path Tracer | Exige preparar exportação, materiais próprios do Unreal, iluminação, colisões e orçamento de memória | **Caminho principal proposto**, condicionado ao piloto |
| **Blender + Twinmotion** | Montagem arquitetônica e apresentação com menor personalização | Menos adequado ao controle específico de variantes e instalações deste repositório; shaders ainda precisam de adaptação. Seu Path Tracer exige Windows, DX12 e pelo menos 8 GB de VRAM | Alternativa se o piloto indicar que a manutenção do Unreal completo não compensa |

O Twinmotion também pode produzir imagens fotorrealistas; a escolha aqui é de controle e fluxo de trabalho. [Requisitos oficiais do Path Tracer do Twinmotion](https://dev.epicgames.com/documentation/en-us/twinmotion/path-tracer-requirements-for-twinmotion).

Nanite administra geometria detalhada de forma eficiente; não cria detalhes ausentes. Usar em malhas compatíveis e medir memória/desempenho. Na documentação da família 5.8, materiais opacos e mascarados são suportados; tratar vidro e transparências técnicas por um caminho próprio. Conferir também a geometria de fallback usada pelo ray tracing, para que silhuetas e reflexos mantenham os detalhes no Path Tracer. [Nanite — documentação oficial](https://dev.epicgames.com/documentation/it-it/unreal-engine/nanite-virtualized-geometry-in-unreal-engine).

## 4. Melhorias necessárias, em ordem de impacto

### A. Referência e fidelidade ao que existe

Organizar as 31 fotos atuais e as quatro referências industriais por ambiente, com correspondência entre objeto, material e medida conhecida. Separar o que é observado, medido, documental e apenas estimado. Registrar acabamentos reais de piso, parede, teto, esquadrias e bancada; fotografias próximas com uma referência de tamanho ajudam a reproduzir sua escala.

Para móveis atuais, preservar o desenho e as proporções reconhecíveis nas fotos. Um sofá de biblioteca sofisticado que não corresponde ao sofá existente prejudica a representação do estado atual. Para a proposta industrial, selecionar peças coerentes com as referências e com a circulação disponível.

As fotos disponíveis não comprovam cobertura suficiente para fotogrametria. Caso seja necessário reconstruir um móvel específico, levantar dimensões e imagens de vários lados antes de decidir entre modelagem, modelo de fabricante ou captura.

### B. Geometria de acabamento

Adicionar o que aparece em uma fotografia próxima: rodapés, guarnições, rebaixos, folgas de portas/gavetas, trilhos, peitoris, ferragens, tomadas, interruptores, juntas e espessuras reais do vidro. Refinar telhas, rufos, calhas e encontros das mansardas nas imagens externas.

Rever os chanfros conforme material e escala: arredondamentos pequenos capturam a luz, mas o mesmo raio em todos os objetos produz aparência artificial. Modelar detalhes que alteram silhueta; usar mapas de relevo para detalhes menores. Corrigir interseções, objetos flutuando, faces sobrepostas e sombreamento inadequado.

A geometria documental continua sendo a referência. Esses detalhes ficam em camadas de acabamento, sem alterar vãos, níveis e alinhamentos para favorecer uma imagem.

### C. Materiais físicos e coordenadas de textura

Criar uma biblioteca compartilhada de materiais **PBR**, isto é, com propriedades que aproximam a resposta física à luz: cor de base, rugosidade, metalicidade e relevo/normal; transmissão e índice de refração quando aplicáveis. Ajustar rugosidade e variações discretas a cada superfície. [Guia oficial de materiais físicos](https://dev.epicgames.com/documentation/en-us/unreal-engine/physically-based-materials-in-unreal-engine).

Prioridades: piso, cimento, madeira, tecido/couro, pedra, metal pintado e vidro. A madeira deve ter direção e tamanho de veio corretos; piso e rejunte precisam repetir o módulo real. Evitar sombras já pintadas na textura de cor e desgaste exagerado em uma casa conservada.

Preparar UVs quando necessários; testar distorção e densidade de textura com padrão quadriculado. Projeção tridimensional pode servir à arquitetura; converter/bakear quando o intercâmbio exigir. Adotar inicialmente 2K–4K e reservar 8K a detalhes próximos que demonstrem necessidade, em vez de multiplicar tudo por resolução.

Para migração, **bakear** materiais procedurais relevantes — convertê-los em mapas de imagem — ou reconstruí-los em materiais do Unreal. Verificar espaços de cor: mapas de dados não recebem a mesma interpretação da cor de base. Testar a orientação dos mapas de normal entre exportador e importador.

### D. Móveis, objetos e vegetação

Refinar ou substituir seletivamente sofá, cadeiras, tecidos, eletrodomésticos e luminárias. Buscar costuras, dobras, pequenas assimetrias e ferragens coerentes com o produto, preservando dimensões e passagem. Aproveitar os assets que já resistem ao enquadramento próximo; priorizar os objetos em primeiro plano.

Usar instâncias para peças repetidas. Vegetação precisa de silhueta, espessura/transmissão de folha e distribuição plausíveis. Aumentar a quantidade de objetos só quando eles ajudarem a composição ou a fidelidade ao ambiente real.

### E. Iluminação e entorno

Conferir orientação solar e aberturas; criar uma configuração diurna e uma noturna. Comparar céu físico e HDRI adequado, uma imagem de ambiente com grande faixa de luminosidade. HDRI não é obrigatório e não corrige, sozinho, a falta de entorno.

Representar vizinhos, pátio, vegetação e horizonte realmente visíveis pelas janelas, com geometria suficiente para reflexos, sombras e paralaxe. Rever especialmente as vistas do ático e a área posterior.

Revisar as luzes auxiliares existentes, mantendo contribuição e propósito registrados. Configurar luminárias com fluxo, temperatura de cor e, quando houver catálogo, perfil fotométrico IES, que descreve a distribuição de luz da peça. Evitar depender apenas de superfícies emissivas muito pequenas para iluminar o ambiente.

No Unreal, testar reflexos, vidro e iluminação indireta em interiores. Manter paredes, teto, piso e móveis em peças adequadas à representação do Lumen; importar tudo como uma malha única dificulta seu cálculo. Procurar vazamentos de luz, regiões sem cobertura e ruído em reflexos. [Detalhes técnicos do Lumen](https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-technical-details-in-unreal-engine).

### F. Fotografia e renderização

Criar câmeras específicas para apresentação, além das técnicas. Testar alturas de observação próximas às de uma pessoa e lentes inicialmente entre 24–35 mm equivalentes, usando grande angular quando o espaço realmente exigir. As salas auditadas usam 18–19 mm; o ático usa 21 mm. A mudança depende da composição, sem deformar a casa para caber no quadro.

Fixar exposição e balanço de branco por condição de luz, controlar verticais e conferir que a câmera não atravessa paredes, teto ou móveis. Usar profundidade de campo com discrição. No ático, incluir vista geral do estar, escritório, duas mansardas e relação com a escada; complementar com detalhes próximos.

Manter 1920 × 1440 para revisão. Para finais, propor **3840 × 2880** preservando o formato 4:3; para vídeo 16:9, reenquadrar em **3840 × 2160**, sem esticar imagens. Amostras e denoising serão definidos por comparação de ruído e detalhe: 256–1024 amostras podem ser pontos de teste no Cycles, sem tratá-las como receita universal.

Comparar a resposta de cor AgX/Cycles e a transformação de exibição do Unreal usando referências comuns; os mesmos números de exposição não garantem aparência idêntica. Guardar EXR de trabalho quando útil e exportar PNG para entrega. Processamento final não deve inventar geometria nem esconder mudanças de projeto.

## 5. Migração sem perder medidas ou manutenção

O projeto usa geradores Python e configurações JSON. Preservar essa fonte e exportar cópias de apresentação, com um manifesto que relacione cada objeto exportado à sua origem, variante e material. Uma nova geração não deve apagar o acabamento feito no Unreal.

**Não pressupor exportação Datasmith oficial direta do Blender:** ele não aparece na tabela de aplicativos suportados consultada. Começar o piloto comparando **GLB/glTF 2.0** e **FBX**, escolhendo um fluxo após medir o que sobrevive: transformações, instâncias, materiais, UVs e atualização. FBX é uma opção para malhas, mas sua importação automática de materiais é limitada; glTF também não representa qualquer shader arbitrário. [Tabela Datasmith](https://dev.epicgames.com/documentation/en-us/unreal-engine/datasmith-supported-software-and-file-types), [FBX](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-static-mesh-pipeline-in-unreal-engine), [glTF](https://dev.epicgames.com/documentation/en-us/unreal-engine/gltf-file-format-support-in-unreal-engine).

Contrato mínimo do piloto:

1. Testar um objeto de 1 m e uma distância conhecida da casa: **1 m deve chegar como 100 cm** na unidade padrão do Unreal. Conferir eixos, origem, escala e orientação.
2. Manter IDs estáveis, hierarquia por pavimento/disciplina e pivôs coerentes. Não unir a casa inteira para facilitar uma exportação.
3. Avaliar modificadores na cópia exportada; conferir normais, triangulação, vidro, curvas convertidas e faces posteriores. Não modificar o mestre por conveniência do exportador.
4. Mapear os materiais a famílias reutilizáveis no Unreal e registrar texturas, escala e parâmetros. Não depender de conversão visual perfeita dos nós do Blender.
5. Criar colisões simples para passeio; testar portas e circulação nas escadas. Preservar separadamente a geometria visual detalhada.
6. Reimportar uma pequena alteração de acabamento e verificar que materiais, câmeras e organização permanecem. Só depois expandir para a casa.

**Invariantes do ático v05:** lances novos com o mesmo XY dos existentes e deslocamento vertical de +2,70 m; caixa centrada em `[1,80; 3,175]` m com base +5,45 m; reserva vertical do forro de 0,15 m; mansardas centralizadas e ligadas à cumeeira principal. Conferir contra `config/residencia-07-atico-v05.json` e os relatórios vigentes. Manter as limitações conhecidas do estudo, inclusive o hall nominal de 0,65 m. Não recuperar as propostas de escada excluídas.

## 6. Hardware e orçamento

**Verificado neste host:** Windows 11, Core i9-14900HX identificado pelo WSL, RTX 4070 Laptop com 8.188 MiB de VRAM e aproximadamente 32 GB de RAM física no Windows. O WSL enxerga cerca de 15 GiB, um limite distinto da RAM física. [Recibo de hardware](relatorios/fotorrealismo-2026-11-12/hardware.json).

A recomendação geral publicada pela Epic inclui 32 GB de RAM e 8 GB ou mais de VRAM. Isso não garante casa inteira em 4K, qualidade máxima e navegação fluida. Este equipamento permite propor o piloto, com controle de texturas, carregamento por ambiente e instâncias; desempenho real continua pendente. Preferir Unreal nativo no Windows/DX12 para esse teste. O funcionamento do Blender no WSL não comprova a viabilidade do editor Unreal nessa mesma configuração. [Especificações oficiais](https://dev.epicgames.com/documentation/en-us/unreal-engine/hardware-and-software-specifications-for-unreal-engine).

Para trabalho mais confortável com toda a casa detalhada, **64 GB de RAM e GPU com 16–24 GB ou mais de VRAM são uma faixa de planejamento**, não requisito oficial nem compra já recomendada. Só avaliar nova máquina, render remoto ou serviço de renderização depois de medir o piloto. Verificar antes a possibilidade de upgrade do notebook; não presumir substituição de sua GPU.

Reservar armazenamento para motor, projeto, assets e cache, acompanhando crescimento. No momento da coleta havia aproximadamente 255 GB livres em C: e 839 GB no volume WSL; são disponibilidades observadas, não capacidade reservada. Instâncias, texturas proporcionais ao uso e carregamento seletivo vêm antes de elevar indiscriminadamente a qualidade.

No Cycles 5.2, incluir no benchmark o **Texture Cache**, recurso que carrega blocos e resoluções de textura conforme a necessidade. A documentação de lançamento registra redução de memória dependente da cena, com custo de disco e possível impacto de desempenho; medir quando a biblioteca de imagens crescer. [Lançamento Blender 5.2 LTS](https://www.blender.org/download/releases/5-2/).

O orçamento deve separar: acabamento/modelagem, texturas e móveis, configuração do motor, tempo de render, armazenamento e eventual hardware. Custos e prazo total serão estimados após o piloto, com quantidade de ambientes e peças a refazer.

Conferir o enquadramento da licença do Unreal e a licença de cada asset antes da aquisição. Não presumir que todo Megascans/Fab seja gratuito ou tenha a mesma licença. A Standard License do Fab permite uso em ferramentas compatíveis, mas o histórico de aquisição e o contrato aplicável a cada item precisam ser registrados. [Licenciamento Unreal](https://www.unrealengine.com/license), [Fab](https://www.fab.com/eula).

## 7. Plano de execução e entregas

| Etapa | Trabalho | Entrega e condição para avançar |
| --- | --- | --- |
| **0 — diagnóstico: concluído neste turno** | Pesquisa oficial, leitura de cinco arquivos, inspeção de três PNGs e hardware | Este plano, inventário e recibos; sem alteração dos modelos |
| **1 — preparar referências** | Revisar todos os ângulos vigentes; catalogar materiais/móveis, medidas conhecidas e estimativas; escolher referências de fotografia para a qualidade desejada | Lista por ambiente do que reaproveitar, detalhar ou substituir; escopo do piloto fechado |
| **2 — piloto sala/cozinha industrial** | Detalhar piso/parede/esquadria, mesa/cadeira/sofá e luminária; montar entorno; melhorar Cycles; preparar importação e materiais no Unreal | Três câmeras × dia/noite × Cycles/UE Path Tracer = 12 imagens comparáveis; percurso Lumen de 30 s; métricas de memória, tempo e atualização |
| **3 — decidir o fluxo** | Comparar qualidade, custo de edição, tempo de render, compatibilidade e estabilidade no host | Escolher Unreal híbrido, Cycles ou Twinmotion; fixar versões e procedimento de reimportação. Se só o passeio exigir compromissos, manter finais com Path Tracer/Cycles |
| **4 — biblioteca compartilhada** | Consolidar materiais físicos, acabamentos e assets aprovados; instâncias, nomes, proveniência e exportação | Biblioteca reutilizável e manifesto; uma mudança pode ser reproduzida sem perder acabamento |
| **5 — estado atual** | Aplicar biblioteca à casa atual; refinar móveis reais, fundo aberto, cobertura posterior e divisão lazer/lavanderia | Interiores/exteriores diurnos e noturnos; comparações foto/modelo e medidas estimadas identificadas |
| **6 — industrial completo** | Expandir piloto aos demais ambientes e à alternativa de escritório, mantendo a arquitetura atual | Nova série de ambientes e imagens externas; nenhum móvel ocupa passagem por mudança de escala |
| **7 — ático v05** | Aplicar acabamento ao forro, mansardas, escadas, guarda-corpo e área técnica; rever móveis, entorno e câmeras | Interiores, fachada frontal/posterior, escadas/caixa por vários ângulos e percurso; regressão geométrica do encaixe |
| **8 — original e modos técnicos** | Reaproveitar acabamento compatível na base original; melhorar luz e apresentação de estrutura/redes | Série original e duas apresentações técnicas: opaca e transparente/cortada; cotas e legendas legíveis |
| **9 — entrega e revisão** | Revisar cada imagem, vídeo, link e variante; registrar configurações e consumo | Arquivos editáveis, exportações, imagens, galeria/cadernos atualizados e relatório de validação |

As etapas 5–8 reutilizam a mesma biblioteca; não significam reconstruir quatro casas do zero. O número final de imagens será mapeado aos ângulos existentes, mais os novos enquadramentos necessários. Plantas 2D continuam vetoriais e cotadas; sua legibilidade não depende do motor das imagens fotográficas.

**Estrutura planejada para a expansão aos demais modelos:** a execução industrial usa `projeto/industrial-v06`, `renders/industrial-v06`, `assets/fotorrealismo-industrial` e `relatorios/industrial-v06`; o desenho abaixo permanece como organização proposta para a expansão.

```text
projeto/fotorrealismo/blender/       # cópias de apresentação e biblioteca
projeto/fotorrealismo/unreal/        # projeto UE, caso aprovado no piloto
assets/fotorrealismo/               # materiais, móveis e registro de licenças
exports/fotorrealismo/              # intercâmbio gerado e manifestos
renders/fotorrealismo/
  00-piloto/
  01-original/
  02-atual/
  03-industrial/
  04-atico-v05/
  05-estrutura-instalacoes/
relatorios/fotorrealismo/            # benchmarks, validações e entregas
```

As entregas atuais permanecem como referência até existir uma substituição validada. Não duplicar caches gerados do Unreal no controle de versão; definir armazenamento de arquivos grandes segundo a política do projeto.

## 8. Critérios de qualidade e validação

**Geometria e fidelidade:** conferir pontos de controle importados com diferença máxima proposta de 1 mm em relação ao modelo fonte — tolerância de transferência, não precisão do levantamento real. Preservar dimensões documentais e marcação das estimativas. Validar separadamente a escada, caixa, forro, mansardas e abertura posterior.

**Materiais e detalhe:** avaliar imagem inteira e recortes a 100% de tecido, madeira, piso, metal e vidro. Procurar distorção de textura, repetição evidente, reflexos incoerentes, contornos facetados e ausência de encontros construtivos. Nenhum arquivo de textura necessário pode estar ausente. Denoising não deve apagar costuras ou criar manchas.

**Luz e câmera:** testar dia/noite, reflexos, áreas sob escadas, janelas e transição interior/exterior. Não aceitar câmera dentro de objetos, vazamento de luz ou exposição automática alterando o resultado durante a comparação. Aprovar referências e imagens piloto visualmente; não existe um número de amostras que comprove, sozinho, fotorrealismo.

**Passeio:** meta inicial de **30 FPS ou mais em 1920 × 1080**, após aquecimento/compilação, no percurso definido da máquina atual. Registrar resolução interna/TSR, configuração, tempo de quadro p50/p95, pico de VRAM/RAM e falhas. A meta é proposta e ainda não foi medida. Repetir com câmera em movimento para procurar cintilação, rastros e instabilidade; uma captura parada não valida o passeio.

**Finais:** renders no formato/resolução combinados, sem ruído ou defeitos perceptíveis nas regiões críticas a 100%; registrar amostras, tempo, memória e configurações. Aprovar uma comparação entre motores sem exigir igualdade pixel a pixel, pois seus materiais e transformações de cor diferem.

**Manutenção:** testar reimportação de uma mudança pequena sem perda de materiais, IDs ou câmeras; manter relatório de diferenças. Executar os validadores geométricos existentes sobre as versões correspondentes ao fim da conversão.

**Estrutura/instalações:** preservar as cores por disciplina, paredes transparentes, cortes e legendas em um modo técnico próprio. A apresentação fotográfica usa acabamentos opacos e pode ter cortes localizados. O maior realismo visual não transforma rotas de estudo ou elementos arquitetônicos em levantamento verificado ou dimensionamento estrutural.

## 9. Tecnologias de pesquisa e limites ainda abertos

Também pesquisei reconstrução neural: **LuxRemix, CVPR 2026**, apresenta edição de iluminação de interiores capturados com várias vistas usando Gaussian Splatting. É uma linha relevante para representar espaços existentes. Para este projeto, minha avaliação é que continua sendo complementar: alterações de paredes, escada, caixa, materiais e desenhos cotados favorecem uma base de malhas editáveis com medidas explícitas. Não incluir esse fluxo no caminho obrigatório antes de testar cobertura de captura e edição. [Artigo dos autores](https://arxiv.org/abs/2601.15283).

**Pendências antes de prometer qualidade/prazo para toda a casa:** benchmark real no Unreal, inspeção artística dos demais ângulos, levantamento dos detalhes não medidos, auditoria de licença dos assets escolhidos, teste de intercâmbio e estimativa por ambiente. A documentação Epic sem versão explícita já abre na prévia 5.9; durante a execução, confirmar recursos e interfaces na versão 5.8 fixada, sem copiar configurações experimentais automaticamente. As páginas do manual Blender tiveram falha de acesso direto nesta pesquisa; a definição do Cycles foi consultada no resultado indexado oficial e sua utilização foi verificada nos arquivos nativos.

**Decisão planejada:** começar pela sala/cozinha industrial como prova de qualidade; melhorar o conteúdo compartilhado; usar Unreal para a apresentação se o piloto comprovar a vantagem. A prioridade é tornar superfícies, objetos, luz e enquadramentos convincentes, mantendo a casa fiel ao projeto e às alterações já registradas.
