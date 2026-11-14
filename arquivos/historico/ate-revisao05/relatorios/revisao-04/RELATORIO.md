# Revisão 04 — lavabo sob o segundo lance e garagem ampliada

UTC: 2026-11-10T15:53:40.361712+00:00

A mensagem posterior do usuário corrige a posição do lavabo do croqui: ele fica sob a segunda metade da escada. A área que o lavabo ocupava à frente da escada foi incorporada à garagem. O croqui anterior está preservado em `referencias-ajustes/planta-terreo-anotada.png`; sua indicação do lavabo foi substituída explicitamente pela correção em `config/planta-casa.json:user_correction`.

| Obrigação | Evidência | Estado e limite |
| --- | --- | --- |
| Churrasqueira no canto posterior esquerdo e bancada com três bancos | Render superior, croqui e teste de posição | VERIFIED no modelo aproximado |
| Lavanderia ao lado da churrasqueira, imediatamente atrás da cozinha, com fundos alinhados | Render superior e testes de alinhamento e passagem | VERIFIED no modelo aproximado |
| Lavabo na projeção do segundo lance | Teste de projeção e corte específico com paredes frontal/lateral removidas | VERIFIED no modelo aproximado |
| Louças e espelho sob o forro inclinado e dentro do lavabo | Teste de todos os vértices das caixas de contorno das peças | VERIFIED no modelo; não valida folgas reais de uso |
| Garagem ampliada até o início do segundo lance | Comparação com revisão 03 e ray cast do acesso até a nova parede do lavabo | VERIFIED no modelo |
| Entrada em diagonal | Ângulo do conjunto editável e render da folha fechada | VERIFIED no modelo; ângulo métrico INFERRED |
| Arquivo editável e renders correspondentes | Reabertura do arquivo, 15 testes de integridade e hashes iguais | VERIFIED para o arquivo entregue |
| Preservação das referências e da revisão anterior | Hashes das 31 fotos, do croqui e do backup | VERIFIED |
| Dimensões reais e planta do superior | Nenhum levantamento novo fornecido | UNKNOWN |

O arquivo salvo gerou 13 renders. Os 23 testes de geometria incluem as relações fotográficas anteriores, as relações do croqui ainda válidas e três verificações da correção: projeção sob o lance, ampliação da garagem e encaixe das peças abaixo do forro. Não são uma pontuação de fidelidade visual ou certificação de uso do espaço.

## Interpretações adotadas

- A continuação direita da garagem avança até a face dianteira do volume sob o segundo lance. A antiga divisão à frente da escada foi retirada.
- O lavabo agora fica inteiramente na faixa longitudinal do segundo lance, com a porta fotografada mantida entre a TV e o primeiro lance. As louças foram deslocadas para esse volume.
- As paredes do lavabo acompanham o forro inclinado em vez de atravessar os degraus. A cena `CORTE_Lavabo_Escada` omite duas dessas paredes para mostrar o interior; elas continuam presentes nas demais cenas.
- A janela da cozinha foi mantida na posição fotografada, agora voltada ao volume identificado como lavanderia. Não foi presumida cobertura para toda essa área.
- A bancada e os três bancos seguem o desenho. Materiais e marcenaria continuam simplificados.
- A entrada diagonal e as posições de sala, jantar, cozinha, churrasqueira e lavanderia foram mantidas.

## Validação e limites

Comandos: `scripts/validate_house.py`, `scripts/house_atlas.py`, `python3 -m py_compile scripts/*.py` e `git diff --check`. A execução do Blender foi registrada em `geracao.log` e `validacao.log`; testes e renders estão em `validacao.json`, `auditoria-depois.json` e `renders-finais.json`.

As revisões 03 e 04 foram comparadas em `renders/planta-casa/comparacao-antes-depois.png`. O lavabo fica oculto pelos degraus na vista superior, por isso seu rótulo indica “sob 2º lance”. O encaixe é mostrado diretamente em `renders/revisao-04/final/lavabo-sob-escada.png`. A comparação com o croqui antigo avisa que a posição do lavabo foi corrigida posteriormente por mensagem. Foram revistos também o corte em 3D e os seis ângulos das fotos.

Permanecem desconhecidos: Medidas lineares reais e ângulo exato da entrada; Dimensões e folgas reais sob o segundo lance; o encaixe modelado não é verificação de habitabilidade; Cobertura e detalhes construtivos da lavanderia; Dimensões exatas do retorno da escada e implantação dos cômodos superiores. A conclusão desta data se restringe à aplicação aproximada do croqui ao térreo. Não houve commit, push ou publicação.
