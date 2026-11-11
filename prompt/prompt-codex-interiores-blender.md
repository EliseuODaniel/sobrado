# Reconstrua esta sala como projeto 3D editável no Blender

Trabalhe nesta pasta e entregue um projeto real do **Blender 5.2 LTS**, com geometria editável, materiais, luzes e câmeras. Use a API Python do Blender (`bpy`) para gerar a primeira versão, rode o Blender em modo background, inspecione os renders e refine a cena. Quero abrir o `.blend`, mudar móveis, revestimentos e iluminação e renderizar de novo pela interface, sem precisar rodar o script para cada ajuste. O estilo é industrial aconchegante, para uso diário e para receber amigos e familiares.

## 1. Leia as referências e decida o que cada uma controla

| Arquivo esperado | Use para |
| --- | --- |
| `referencias/01-cena-final.png` | Imagem final “Warm Industrial Living Space with Reflective Kitchen Mirror.png”, de 1671 × 941 px. É a referência principal de enquadramento, distribuição de móveis, proporções aparentes, luz e acabamento. |
| `referencias/02-bar-fundo.png` | Imagem “image(20261110-091901).png”. É a referência de detalhe do bar, incluindo a paginação da pedra, bancada, marcenaria, cobertura, banquetas e porta lateral. |
| `referencias/03-mesa-jantar.png` | Imagem “image(20261110-091412).png”. É a referência do desenho da mesa, das três tábuas, da moldura, da saia e dos pés. |
| `referencias/fotos-reais/` e planta ou medidas, se fornecidas | São a fonte de verdade da arquitetura e da escala. Use-as para piso, paredes, teto, escada, portas, janelas, pilares, cobertura e demais elementos fixos. |

Localize também arquivos anexados com os nomes originais. Abra a imagem final e os detalhes antes de modelar. Se a imagem final estiver ausente ou ilegível, peça esse arquivo. Se só faltarem referências secundárias ou medidas, avance com a evidência disponível e registre as lacunas.

Em caso de divergência, preserve primeiro a arquitetura documentada nas fotos e medidas reais. Em seguida, aplique as instruções explícitas deste prompt. Use a imagem final para a composição e as imagens de detalhe para os móveis e acabamentos correspondentes. Mantenha a localização e as proporções das aberturas documentadas. A cobertura envidraçada só entra como elemento existente se estiver confirmada nas fotos reais. Se só houver os renders, represente o que aparece como hipótese visual e deixe essa parte separada e identificada no modelo.

Use metros e separe no arquivo de configuração as medidas confirmadas das estimadas. Use uma dimensão real conhecida para ancorar a escala, quando disponível. Sem ela, faça uma reconstrução proporcional aproximada. Mantenha áreas fora de quadro ou ocluídas tão simples quanto a evidência permitir e documente os trechos que ficaram sem modelagem.

## 2. Reproduza a composição e os detalhes

- **Estar, à esquerda.** Parede com acabamento contínuo de concreto ou cimento, fosco e discretamente texturizado. Sofá de couro caramelo envelhecido, almofadas neutras, manta, prateleira preta com plantas, quadro e arandela preta de braço. No primeiro plano, tapete de trama natural e mesa de centro de madeira sobre estrutura metálica preta, com vaso, livros e tigela.
- **Jantar, no centro.** Mesa retangular compacta de madeira de demolição. Modele três tábuas longitudinais contínuas no tampo, moldura perimetral, saia e quatro pés de madeira levemente afunilados, com pequenos ressaltos no alto e na base. Faça exatamente quatro cadeiras de couro caramelo com base preta, duas de cada lado comprido, com as cabeceiras livres. Inclua o pendente principal preto em cúpula e o arranjo central da imagem.
- **Bar, ao fundo.** Use o detalhe para reproduzir as peças quadradas de pedra escura, com variação de marrom e ferrugem, relevo moderado e juntas regulares. Preserve a leitura de pedra quadrada em vez de paginação de tijolos. Modele bancada escura polida com frente amadeirada, cuba e torneira, armários superiores envidraçados com louças e taças, luz sob o armário e quatro banquetas de assento redondo de madeira, pernas pretas e sem encosto. Represente a vegetação acima da cobertura apenas onde a arquitetura comportar esse enquadramento. Use a imagem geral para o que fica visível no render principal.
- **Direita.** Modele a parede da TV com acabamento texturizado e painel de cantos superiores arredondados, TV independente, duas barras verticais âmbar e rack baixo com tampo de madeira e frentes de tela metálica preta. Inclua a iluminação superior, a luminária e os objetos sobre o rack. Preserve o enquadramento da divisória ripada escura e da cozinha visível ao fundo, com janela, persiana, cuba e armários. Mantenha a composição livre de geladeira.
- **Espelho, à esquerda do jantar.** Modele a faixa vertical do espelho no plano, posição e orientação coerentes com a parede. A indicação em **x = 19,2%, y = 41,6%**, medida do canto superior esquerdo, aponta para uma região dentro do espelho na imagem principal. Use um material especular com rugosidade muito baixa e reflexo calculado pelo Cycles. Use apenas os objetos reais da cena como origem do reflexo. Ajuste câmera, plano do espelho e alinhamento com o bar dentro do que a geometria documentada permite. O reflexo precisa responder à posição da câmera e às mudanças no bar. Se a geometria real tornar algum detalhe do reflexo de referência impossível, preserve o resultado físico e mostre a diferença na comparação.

## 3. Construa para editar e renderizar

1. **Enquadre antes de detalhar.** Monte a arquitetura e volumes principais simples. Use as arestas do piso, do teto, da bancada e das aberturas para alinhar a câmera `CAM_Referencia`. Preserve a proporção de 1671 × 941 da imagem final. Se as linhas convergirem de forma coerente, use ajuste por pontos de fuga manual ou fSpy como ponto de partida opcional. Refine posição, rotação, lente e deslocamento de lente pelo render. Acrescente uma câmera ortográfica superior para conferir a disposição e a circulação.
2. **Modele os objetos separadamente.** Use coleções chamadas `Arquitetura`, `Estar`, `Jantar`, `Bar`, `Cozinha`, `Iluminacao`, `Cameras` e `Referencias`. Dê nomes claros, use pivôs que facilitem mover cada móvel, mantenha as quatro cadeiras e as quatro banquetas com transformações independentes e agrupe as peças de cada móvel sob um objeto pai quando isso facilitar a edição. Deixe as referências apenas no viewport ou na comparação, fora do render final. Desative a seleção acidental da arquitetura pelo Outliner, com instrução de como reativá-la.
3. **Use materiais ajustáveis.** Separe concreto, pedra, madeira, couro, metal, vidro e piso. Exponha cor, escala de textura, rugosidade e relevo nos materiais. Alinhe os veios às tábuas e preserve a escala das juntas da pedra. Use materiais procedurais quando derem boa leitura. Se usar arquivos de terceiros, documente a licença e empacote os recursos elegíveis no `.blend`.
4. **Faça a iluminação no Cycles.** Combine a luz natural documentada com pendentes, arandelas, spots e luz indireta quente. Use fontes de luz para iluminar as superfícies e materiais emissivos onde as luminárias aparecem. Comece com AgX e denoise. Rode prévias em resolução reduzida e ajuste exposição, intensidade e cor pelo render. Use OptiX na RTX 4070 se o Blender a detectar e o render de teste passar. Use CPU como fallback e registre qual dispositivo foi realmente usado.
5. **Permita regenerar sem perder edições.** Centralize medidas, posições e parâmetros principais em `config/cena.json`. Use caminhos relativos à raiz do projeto e salve as saídas em pasta própria. Proteja arquivos de trabalho existentes e permita escolher outro destino de geração. Preserve as edições manuais como uma versão separada do arquivo gerado.

## 4. Execute, compare e valide

- Detecte o executável e verifique `blender --version`. Use o Python do próprio Blender para executar `bpy`. No Windows, rode pelo PowerShell ou, se estiver no WSL local, chame o `blender.exe` do Windows e converta caminhos com `wslpath -w`. Em ambiente remoto, use o Blender e o dispositivo de renderização disponíveis nesse ambiente. Se a execução estiver bloqueada, entregue o código e o comando reproduzível, identifique o bloqueio e indique quais saídas dependem da execução.
- Implemente os argumentos do script para que o seguinte exemplo funcione da raiz do projeto, onde `blender` é o executável detectado ou seu caminho completo.

  ```bash
  blender --background --factory-startup --python-exit-code 1 --python scripts/build_scene.py -- --project-root . --quality preview --device auto
  ```

  Aceite também `--quality final` e `--device cpu` e documente o equivalente no PowerShell com caminho entre aspas quando houver espaços.
- Compare a prévia e a referência na mesma proporção. Faça uma comparação lado a lado ou com sobreposição e confira as linhas do piso e do teto, cantos de aberturas, silhueta da bancada, tamanho da TV e posição da mesa, sofá e espelho. Corrija câmera e volumes antes de refinar materiais. Inspecione as imagens geradas e faça ao menos uma rodada de ajustes guiada pela comparação.
- Confira na vista superior quatro cadeiras em 2 + 2, quatro banquetas e a circulação entre estar, jantar, bar e cozinha. Verifique móveis apoiados no piso e interseções indevidas. Para testar o espelho, mova temporariamente um objeto identificável do bar que esteja no campo refletido, renderize um recorte e confirme visualmente que o reflexo se move. Restaure a posição antes de salvar a versão final.
- Reabra o `.blend` salvo em um processo limpo. Confirme que a câmera principal está ativa, que texturas e recursos estão disponíveis e que o render sai do arquivo final. Faça uma conferência visual dos renders antes de declarar a entrega pronta.

## 5. Entregue

| Arquivo | Conteúdo |
| --- | --- |
| `projeto/sala-industrial.blend` | Cena editável com câmeras, objetos, luzes e materiais nomeados e recursos empacotados quando elegíveis. |
| `scripts/build_scene.py` e `config/cena.json` | Gerador reproduzível e parâmetros ajustáveis, com indicação da origem das medidas. |
| `renders/principal.png` | Render na câmera de referência a 1671 × 941, gerado a partir do arquivo final. |
| `renders/vista-superior.png` e `renders/comparacao.png` | Vista de layout e comparação com a referência principal. |
| `README.md` | Comandos executados, versão do Blender, dispositivo de renderização, como abrir e editar, medidas que faltam, aproximações visuais e resultado das verificações. |

No README, explique como selecionar e mover a mesa ou uma cadeira pelo Outliner, trocar um material, ajustar uma luz e voltar à câmera principal. Na resposta final, aponte o caminho do `.blend`, do render e do README e identifique as diferenças que ainda são visíveis em relação à referência.
