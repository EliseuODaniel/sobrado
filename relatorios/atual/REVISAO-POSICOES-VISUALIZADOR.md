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
