# Revisão 03 — térreo conforme o desenho do usuário

UTC: 2026-11-10T13:35:24.168878+00:00

O croqui foi aplicado como orientação de distribuição aproximada, sem convertê-lo em medidas reais. A imagem recebida está preservada em `referencias-ajustes/planta-terreo-anotada.png`.

| Obrigação | Evidência | Estado e limite |
| --- | --- | --- |
| Churrasqueira no canto posterior esquerdo e bancada com três bancos | Render superior, croqui e teste de posição | VERIFIED no modelo aproximado |
| Lavanderia ao lado da churrasqueira, imediatamente atrás da cozinha, com fundos alinhados | Render superior e testes de alinhamento e passagem | VERIFIED no modelo aproximado |
| Lavabo à frente da escada e acima da continuação da garagem | Render superior, louças reposicionadas e teste de divisão | VERIFIED no modelo; acesso sob a escada permanece INFERRED |
| Continuação direita da garagem aberta para a frente | Ray cast do acesso até a parede do lavabo e render | VERIFIED no modelo |
| Entrada em diagonal | Ângulo do conjunto editável e render da folha fechada | VERIFIED no modelo; ângulo métrico INFERRED |
| Arquivo editável e renders correspondentes | Reabertura do arquivo, 15 testes de integridade e hashes iguais | VERIFIED para o arquivo entregue |
| Preservação das referências e da revisão anterior | Hashes das 31 fotos, do croqui e do backup | VERIFIED |
| Dimensões reais e planta do superior | Nenhum levantamento novo fornecido | UNKNOWN |

O arquivo salvo gerou 12 renders. Os 20 testes de geometria incluem 12 relações da revisão fotográfica anterior e oito verificações do croqui; não são uma pontuação de fidelidade visual.

## Interpretações adotadas

- A área marcada como “metade da garagem” é a continuação da garagem à direita da entrada, aberta para a parte frontal.
- O lavabo ocupa a faixa marcada pelo usuário e mantém acesso pela porta fotografada junto à escada. O pequeno trecho de ligação sob o retorno é uma interpretação, porque o croqui não desenha sua porta.
- A janela da cozinha foi mantida na posição fotografada, agora voltada ao volume identificado como lavanderia. Não foi presumida cobertura para toda essa área.
- A bancada e os três bancos seguem o desenho. Materiais e marcenaria continuam simplificados.
- Sala, jantar, cozinha, primeiro lance e estudos do superior foram preservados em suas posições, com ajuste curto do rack para acomodar a entrada diagonal.

## Validação e limites

Comandos: `scripts/validate_house.py`, `scripts/house_atlas.py`, `python3 -m py_compile scripts/*.py` e `git diff --check`. A execução do Blender foi registrada em `geracao.log` e `validacao.log`; testes e renders estão em `validacao.json`, `auditoria-depois.json` e `renders-finais.json`.

O croqui e a planta foram comparados lado a lado em `renders/planta-casa/croqui-e-planta.png`. Foram revistos também o corte em 3D e seis ângulos das fotos. A maior distância até a bancada nos enquadramentos da sala acompanha a extensão posterior indicada no desenho; não foi escondida por uma falsa escala das fotografias.

Permanecem desconhecidos: Medidas lineares reais e ângulo exato da entrada; Ligação interna do lavabo mantida sob o retorno da escada; não desenhada no croqui; Cobertura e detalhes construtivos da lavanderia; Retorno completo da escada e implantação dos cômodos superiores. A conclusão desta data se restringe à aplicação aproximada do croqui ao térreo. Não houve commit, push ou publicação.
