# Conferência visual da casa atual v02

A comparação é feita pelas fotografias em `referencias-originais`, preservadas. A inspeção de cada vista deve distinguir: correspondência do móvel/revestimento, posição coerente, iluminação legível e defeitos geométricos. Aumento da resolução isoladamente não atende ao pedido.

## Limites de reconstrução

As fotografias não fornecem calibração da lente, plantas dos móveis, medições das alterações posteriores, identificação exata dos tecidos nem fotos de todas as faces. Os detalhes são modelados por observação, mantendo a arquitetura oficial e evitando apresentar medidas inferidas como medidas verificadas.

## Revisão das vistas

As 26 prévias do modelo congelado foram revistas antes do lote 4K. A cobertura da revisão dos arquivos finais, vinculada ao SHA de cada PNG, fica em [revisao-visual-final.json](revisao-visual-final.json). Os JPEGs de conferência estão em `revisao-final`; são cópias reduzidas ou recortes dos PNGs nativos, sem retoque de conteúdo.

As 26 vistas finais foram revisadas. A entrega reúne os PNGs 3840 × 2880, 16 pares de comparação, galeria e PDF de 45 páginas. Passaram 188 conferências dos arquivos e 12 do navegador. A capa, páginas de imagem, comparação e plantas vetoriais do caderno também foram inspecionadas em `revisao-final/pdf-contato.jpg`.

As imagens anteriores foram reunidas em `antes.jpg`; as referências estão nos quatro painéis `originais-*.jpg`. Fotografias completas continuam sendo a autoridade para detalhes.

## Revisão do piloto de 26 vistas

As vistas foram examinadas nos painéis `piloto-02-quartos.jpg`, `piloto-02-demais.jpg` e `piloto-02-reversas.jpg`, e nos arquivos individuais da sala, cozinha e bar. Foram encontrados enquadramentos bloqueados nos banheiros e na bancada azul, tecidos claros demais e frestas superiores no anexo. A revisão seguinte corrige esses pontos. As imagens desse piloto não são a entrega final.

A fachada recebe o acabamento bege, telhas cinza e pavimento intertravado observados. Unidades vizinhas na vista frontal são cópias ilustrativas da volumetria 07, sem levantamento das casas vizinhas. As vistas de planta e cortes 3D são diagramáticas.

## Composição dos banheiros

A inspeção das prévias revelou excesso da parede direita na composição. As duas câmeras foram orientadas diagonalmente a partir da entrada, para mostrar bancada à esquerda, louça ao centro e box ao fundo. Esse ajuste é um estágio explícito de acabamento e não muda a arquitetura. O lote final usa o arquivo corrigido, reaberto e conferido.

### Causa verificada da obstrução

O rastreamento de raios em `diagnostico-vistas-antes.json` identificou a folha `ATUAL BASE R07 Porta P2-quarto-fundos` no espaço do banheiro social. O volume parecia uma parede na imagem. A pose genérica de abertura de 170 graus foi substituída, somente na apresentação, por folhas fechadas dentro dos vãos. Os objetos originais de esquadria e os vãos oficiais foram preservados para conferência.

A primeira correção ainda lia uma matriz global desatualizada de objetos fora da cena ativa. A correção final recompõe a transformação pela cadeia dos pais. Além das 121 peças originais, o centro, a altura e a orientação das sete folhas copiadas são verificados independentemente na reabertura. A validação nativa final tem 274 verificações.

## Mobiliário e materiais

Sala e jantar receberam sofá cinza com chaise e costuras, cortina restrita à parede frontal reta, painel branco com LEDs, rack mel/branco, mesa preta refletiva, seis cadeiras de madeira com estofado cinza, pendente e orquídeas remodeladas. Cozinha e lavanderia receberam marcenaria e eletrodomésticos detalhados, cubas com profundidade e aberturas nas bancadas, ferragens, revestimentos e plantas nas posições observadas. No bar há quatro banquetas, mosaico, armário envidraçado e a cobertura de madeira/vidro; a geladeira permanece conforme as fotos da casa atual.

Os quartos receberam os padrões de corações, triângulos e listras observados, móveis brancos ou de madeira, cortinas e roupa de cama com textura. O pavimento superior usa laminado claro, com cerâmica nos banheiros. As louças têm cavidades, assentos e caixas acopladas; a cerâmica dos boxes é branca.

As superfícies têxteis usam capturas CC0 da Poly Haven (`scuba_suede`, `bi_stretch`, `waffle_pique_cotton`), com escala física e canais conferidos no shader oficial. Foram verificadas 18 imagens de textura. Isso oferece microdetalhe plausível; não identifica a marca ou o tecido exato dos móveis fotografados. Manifesto em `assets/atual-fiel-v02/tecidos/manifesto.json` e conferência de densidade nativa em [revisao-refinamento/recorte-recibo.json](revisao-refinamento/recorte-recibo.json).

## Interpretação dos resultados

As verificações nativas e de integridade não medem semelhança fotográfica. A revisão visual confere elementos reconhecíveis, materiais, continuidade espacial, exposição e defeitos aparentes. Posições de câmera, dimensões dos móveis, trechos não fotografados e acabamentos sem identificação continuam aproximações. Não foi executado teste no Unreal.
