# Térreo atual — revisão 06

UTC: 2026-11-10T17:19:19.589607+00:00

A nova planta anotada e a confirmação textual do usuário substituem a interpretação anterior da porta. A abertura fica na parede horizontal superior do lavabo, no traço preto. O antigo vão na lateral da sala foi fechado. O limite do lavabo segue o retângulo vermelho até a lateral direita da casa, sob o segundo lance e o patamar. O início do primeiro lance foi recuado para representar a área branca de acesso.

| Obrigação | Evidência | Estado e limite |
| --- | --- | --- |
| Porta na marcação preta | Planta recebida, confirmação do usuário e posição/orientação da folha no modelo | VERIFIED no modelo aproximado |
| Vão lateral anterior fechado | Ray cast na posição antiga | VERIFIED |
| Passagem até a porta | Ray casts com a escada presente e oculta | VERIFIED nos pontos amostrados; não é validação dimensional de circulação |
| Limite vermelho do lavabo | Configuração e planta atual com escada oculta | VERIFIED na implantação aproximada |
| Modelos, renders, scripts e documentação atuais | 18 cenas reabertas, 18 renders do mesmo arquivo, hashes e links conferidos | VERIFIED |
| Arquivos antigos arquivados | 333 registros e 68 movimentos conferidos em `historico/ate-revisao05/ARQUIVAMENTO.json` | VERIFIED; nada apagado |
| Helpers compartilhados preservados | SHA-256 de 16 funções extraídas do antigo gerador | VERIFIED; gerador decorativo arquivado |
| Dimensões reais e sentido da porta | Não informados pelo usuário | UNKNOWN |

## Comparações

A imagem original recebida está preservada em `referencias-ajustes/terreo-revisao06-porta-lavabo.png`. `renders/atual/comparacao-planta.png` coloca essa imagem ao lado da vista da porta. Em `porta-lavabo.png`, a escada foi ocultada apenas para mostrar paredes, folha e louças; ela continua presente no modelo e na planta completa. Uma chamada gráfica marca a porta nas vistas de planta, sem representar um novo elemento construtivo.

A comparação anterior/atual é `antes-depois.png`. `comparacao-fotos.png` contém oito ângulos internos e `comparacao-fachada.png` contém dois externos. A nova planta confirmada prevalece onde corrige a interpretação anterior das fotografias. Não se declara equivalência métrica com as fotos.

## Arquivamento e arquivos ativos

A entrega ativa tem um único modelo em `projeto/casa-reconstruida.blend`, renders em `renders/atual/`, configuração em `config/planta-casa.json` e recibos em `relatorios/atual/`. As versões 02 a 05, renders rejeitados, testes e scripts legados de decoração foram retirados das pastas ativas e preservados em `historico/ate-revisao05/`.

O script antigo `build_scene.py` era também uma dependência de primitivas. Suas funções compartilhadas foram extraídas sem alteração para `blender_primitives.py` antes de arquivar o fluxo decorativo. As fotos originais, as referências do usuário e os prompts foram preservados.

## Validação e limites

Passaram 15 verificações de integridade e 38 relações geométricas. Comandos: `validate_house.py`, `house_atlas.py`, `python3 -m py_compile scripts/*.py` e `git diff --check`. O manifesto concilia o arquivo editável, a configuração, os renders e os relatórios; os hashes do histórico foram verificados separadamente.

- Medidas reais, profundidade dos degraus e inclinação da escada; implantação visual aproximada
- Lado da dobradiça e sentido definitivo de abertura da porta; folha mostrada fechada
- Planta interna do segundo pavimento e detalhes ainda não medidos da área de serviço e telhado

O recuo e os degraus da escada seguem a representação visual do desenho; profundidade e inclinação não foram levantadas ou certificadas. O lado da dobradiça não foi confirmado; não foi desenhado arco de abertura presumido. O segundo pavimento continua como envoltória e estudos separados. Não houve commit, push ou publicação.
