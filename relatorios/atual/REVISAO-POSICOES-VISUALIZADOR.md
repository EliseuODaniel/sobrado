# Posições dos móveis no visualizador da Casa atual

Revisão de 21/11/2026. Comparei as 31 fotos de `referencias-originais` com 12 vistas do visualizador antes da revisão e com os dois recortes de pavimento. Usei portas, janelas e paredes como referências para distinguir a posição dos móveis do efeito da perspectiva.

| Ambiente | Fotos originais | Resultado da comparação |
| --- | --- | --- |
| Sala e jantar | `sala1` a `sala8` | Sofá com chaise junto à janela, TV e rack em frente, mesa e cadeiras entre o estar e o bar. Modelei o banco estofado visível em `sala5`, junto à lateral depois da mesa. |
| Cozinha | `cozinha1` a `cozinha5` | Cuba sob a janela, fogão na bancada perpendicular e lava-louças no retorno junto à passagem. A posição relativa desses elementos coincide com as fotos. |
| Bar e churrasqueira | `area1` a `area4` | Quatro banquetas à frente do balcão, churrasqueira à esquerda e geladeira ao lado da divisão envidraçada. As relações de posição coincidem com as fotos. |
| Lavanderia | `lavanderia1` | Bancada em L, lavadora frontal sob a bancada e lavadora de abertura superior junto à parede direita. A sequência coincide com a foto. |
| Suíte | `quartosuite1` a `quartosuite3` | O guarda-roupa ocupa a lateral externa, a cama e o ar-condicionado ficam na parede oposta e a TV fica na divisória do banheiro. Levei o painel frizado para trás da cabeceira e limitei sua extensão antes da porta. |
| Quarto da frente | `quartobranco1`, `quartobranco2` | Passei o guarda-roupa para junto da entrada, ao lado da cama. Coloquei a TV e a estante na parede oposta. Desloquei o conjunto da cama em direção à janela para liberar a frente do armário. |
| Quarto dos fundos | `quartoazul1`, `quartoazul2` | A bancada e a TV ficam de frente para o beliche. Modelei o armário estreito que aparece entre a bancada e a janela. |
| Lavabo e banheiros | `lavabo1`, `suite1`, `banheiro2` | Bancadas junto à entrada, vaso adiante e boxes ao fundo nos banheiros superiores. As fotos sustentam a posição relativa das peças principais. |
| Escada e fachada | `escada1`, `exterior1`, `exterior2` | A escada serviu de referência ao layout da sala. Na fachada, comparei os vasos junto à janela e no fundo da garagem. |

Os ajustes são reproduzidos pelo exportador do visualizador. O Blender de origem preserva a revisão fotográfica anterior. A conferência geométrica em `scripts/validate_web_furniture.py` usa os limites das malhas avaliadas. Ela verifica que os móveis ficam dentro dos vãos previstos e evita interseções nas relações testadas. A largura exata do banco e do armário estreito, as folgas reais e os detalhes fora dos enquadramentos continuam estimados.

Após a exportação, as 13 vistas e os dois recortes renderizaram no Chrome. A inspeção visual confirmou o guarda-roupa junto à entrada do quarto da frente, o armário ao lado da janela do quarto dos fundos, o banco junto à lateral do jantar e o painel atrás da cabeceira da suíte.

## Segunda conferência em 22/11/2026

A primeira revisão acertou a sequência das máquinas, mas superestimou a fidelidade da bancada. Na geometria anterior, o tampo lateral avançava apenas cerca de 7 cm além da frente do tampo de fundo. Em `lavanderia1.webp`, a bancada e os gabinetes acompanham a parede esquerda, a cuba fica sob a janela e a lavadora frontal aparece imediatamente ao lado da máquina com tampa superior.

O modelo de navegador agora tem retorno de 1,16 m, com módulos inferiores e aéreo à esquerda. O conjunto da cuba e da lavadora frontal foi alinhado ao da máquina de abertura superior, com cerca de 2 cm entre os corpos. O vão da janela foi ajustado ao conjunto e recebeu montantes. A passagem do lazer continua livre. As medidas são estimativas visuais. As fotos `area1` a `area4` mostram a passagem à direita do bar, mas não determinam sozinhas a posição métrica de todo o anexo no lote.

A revisão também identificou a câmera do quarto da frente dentro do roupeiro após a mudança anterior. A vista foi reposicionada para o espaço de circulação. A conferência usa as 31 fotos de referência e as 13 vistas do navegador. Os ângulos disponíveis permitem avaliar posições relativas, com cobertura parcial de cada cômodo.

## Terceira conferência em 23/11/2026

Nova comparação direta de todas as 31 fotos em `referencias-originais` contra as 15 vistas renderizadas no navegador corrigiu mais seis divergências de posicionamento e acabamento:

- **Cozinha (`cozinha1`, `cozinha2`, `sala1`)**: a geladeira inox estava orientada para `+Y` (com as portas abrindo contra o armário lateral do fogão). Foi rotacionada 90° junto à parede leste (`X ≈ 6,24 m`), com portas abrindo para o centro da cozinha (`-X`) e puxadores do lado do fogão.
- **Suíte (`quartosuite1` a `quartosuite3`)**: o split do ar-condicionado foi movido para o canto próximo à cortina da sacada (`Y = -0,23..0,55 m`); o conjunto de TV, painel e console foi deslocado para junto da porta do banheiro (`X = 1,59..2,49 m`), com o painel amadeirado estendido do piso ao teto (`Z = 2,71..5,23 m`) e adição da prateleira branca superior. Também foi incluída a vista pronta `Suíte · cabeceira e ar`.
- **Quarto da frente (`quartobranco1`, `quartobranco2`)**: a estante branca e a TV foram aproximadas da parede da porta (`Y = 0,95..1,65 m`), o armário aéreo foi estendido até encontrar o roupeiro sem vão intermediário, foram acrescentadas as duas prateleiras pequenas junto à janela e a câmera do preset foi ajustada para não cortar o canto do roupeiro.
- **Banheiros superiores (`suite1`, `banheiro2`)**: o chuveiro da suíte foi passado para a parede direita do box (`X ≈ 1,56 m`, oposta à bancada) e o gabinete do banheiro social recebeu acabamento em madeira clara distinto da suíte.
- **Sala de jantar (`sala1`, `sala5`, `sala6`, `sala7`)**: a mesa passou de 6 para 8 cadeiras (3 por lateral + 2 cabeceiras) e o banco estofado foi deslocado para o trecho posterior ao pilar (`Y = 6,33..7,51 m`), entre o jantar e as banquetas do bar.
- **Acabamentos WebGL**: granitos cinza/preto e porcelanato bege passaram a receber texturas tileáveis geradas na exportação em vez de cor chapada. Todas as folgas e posições foram verificadas por `scripts/validate_web_furniture.py`.
