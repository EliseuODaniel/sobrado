# Sobrado — versões ativas e infraestrutura

As versões arquitetônicas estão organizadas em **original**, **atual**, **industrial** e **atico**. A pasta **infraestrutura** reúne elétrica e hidráulica, com a caixa na posição original e sem construção do ático. As revisões anteriores foram movidas para [arquivos](arquivos/LEIA-ME.md), sem exclusões.

| Versão | Blender para visualizar | Modelo completo da versão |
| --- | --- | --- |
| Original documental 07 | [Térreo e dois pavimentos](projeto/original/visualizacao-pavimentos.blend) | [Casa original](projeto/original/casa-07.blend) |
| Atual fiel às fotos v02 | [Térreo e dois pavimentos](projeto/atual/visualizacao-pavimentos.blend) | [Casa atual](projeto/atual/casa-07-atual-fiel.blend) |
| Industrial v06 | [Térreo e dois pavimentos](projeto/industrial/visualizacao-pavimentos.blend) | [Casa industrial](projeto/industrial/casa-industrial-fotorrealista.blend) |
| Ático aprovado | [Caixa no canto junto à escada](projeto/atico/atico-caixa-canto-escada.blend) | Telhado transparente; janela livre |

Os três arquivos de pavimentos abrem na cena `VISUALIZACAO_<versao>_COMPARACAO`: à esquerda o térreo isolado; à direita o térreo com o segundo pavimento, sem telhado. As duas casas aparecem lado a lado no mesmo arquivo. Para ver cada uma separadamente, selecione as cenas `VISUALIZACAO_<versao>_terreo` ou `VISUALIZACAO_<versao>_dois-pavimentos`. O térreo aparece sem o segundo pavimento; a outra cena conserva os dois pisos e a laje intermediária, sem telhado. As paredes laterais permanecem completas e opacas. Enquadramento, escala e iluminação de apresentação são iguais entre versões.

**Blender primeiro; novas imagens adiadas por solicitação do usuário.** Imagens já existentes foram preservadas. [Índice das imagens e versões](renders/galeria.html).

## Visualizador 3D local

O navegador reúne as maquetes **Atual**, **Com ático**, **Estrutural** e **Industrial**, com navegação livre, recortes por pavimento e controle das paredes externas. A maquete Estrutural inclui as redes elétricas e hidráulicas, a caixa-d’água e os forros. [Como abrir e atualizar o visualizador](visualizador/README.md).

## Infraestrutura

[Blender de elétrica, hidráulica e forros](projeto/infraestrutura/instalacoes-pavimentos-forro.blend): sete cenas, com os pavimentos lado a lado, vistas por disciplina e detalhe da caixa. Abre na comparação geral. Caixa na posição original; casa sem construção do ático. Paredes e forros translúcidos permitem ler as redes. [Cenas, cores e limites](projeto/infraestrutura/LEIA-ME.md) · [Validação](relatorios/infraestrutura/validacao.json).

## Organização

- `projeto/{original,atual,industrial,atico}`: apenas as entregas vigentes de cada tipo.
- `renders/{original,atual,industrial,atico}`: imagens e galerias da versão correspondente; as novas vistas de pavimentos ficam em `vistas-pavimentos` quando disponíveis.
- `relatorios`: evidências das versões vigentes, manifesto dos movimentos e validação dos Blenders.
- `arquivos`: versões anteriores, histórico e trabalhos intermediários preservados.
- `plantas`, `referencias-*`, `assets`, `config` e `scripts`: fontes e ferramentas necessárias à edição/reprodução, preservadas independentemente da organização das entregas.

[Manifesto dos caminhos](relatorios/organizacao-movimentos.json) · [Recibo dos movimentos](relatorios/organizacao-recibo.json) · [Validação Blender](relatorios/validacao-blender-final.json).

## Renderizar depois

Abra o Blender desejado, escolha a cena e use F12. Para salvar a comparação e as duas vistas individuais por script, execute no Blender `scripts/render_floor_views.py`; as saídas ficam em `renders/<versao>/vistas-pavimentos`. O script não renderiza automaticamente ao abrir o arquivo.

Os modelos conservam as aproximações e limites de suas fontes. O ático com caixa no canto é estudo visual: o acesso de manutenção é apertado e hidráulica, caixa real e apoio estrutural exigem verificação antes de executar. [Detalhes do ático](projeto/atico/LEIA-ME.md).
