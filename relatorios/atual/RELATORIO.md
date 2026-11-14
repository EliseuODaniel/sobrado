# Casa atual — reconstrução pelas fotos, v02

A revisão foi concluída em 13/11/2026. A entrega em [renders/atual](../../renders/atual/galeria.html) foi substituída pelos renders do novo modelo: **26 PNGs nativos de 3840 × 2880, RGB de 16 bits, 16 comparações foto/modelo e caderno de 45 páginas**. As imagens foram renderizadas em Cycles com OptiX, até 512 amostras e limiar adaptativo de 0,008.

[Galeria](../../renders/atual/galeria.html) · [PDF](../../renders/atual/00-cadernos/caderno-atual.pdf) · [Blender editável](../../projeto/residencia-07-atual-v02/casa-07-atual-fiel.blend) · [comparações](../../renders/atual/galeria.html#comparacoes).

## O que mudou

O mobiliário e os acabamentos foram refeitos por observação das fotografias: sofá cinza com chaise, cadeiras estofadas de madeira, cortinas, painel de TV iluminado, rack mel/branco, mesa refletiva, pendente e orquídeas. Cozinha, bar e lavanderia receberam marcenaria, cubas com profundidade, ferragens, eletrodomésticos e revestimentos detalhados. Nos quartos foram reconstruídos os padrões de parede, móveis, cortinas e tecidos; o piso superior recebeu laminado claro. Banheiros, escada, fachada e cobertura também receberam acabamento próprio.

Os tecidos usam capturas CC0 verificadas, com escala física e canais de relevo, rugosidade, refletância e anisotropia. O piloto 4K foi inspecionado e substituído após o refinamento dos tecidos e das orquídeas. Não houve retoque generativo sobre as imagens finais: os PNGs vieram do modelo nativo.

As 674 impressões de geometria protegida foram preservadas. Foram restauradas 121 posições de peças de esquadria pela fonte oficial e relações de parentesco de peças dos banheiros. As sete folhas de porta da apresentação têm centro, altura e orientação conferidos na reabertura. A abertura dos fundos, a cobertura posterior e a divisão lazer/lavanderia permanecem na arquitetura atual.

A **geladeira do bar atual permanece** porque aparece nas fotografias; a remoção solicitada era das propostas industriais. O modelo atual anterior permanece preservado como fonte dessas propostas. A entrega anterior está em `historico/estudos/atual-v01`, com recibo de arquivamento.

## Verificações e evidências

| Conferência | Resultado | Recibo |
| --- | --- | --- |
| Reabertura do Blender, geometria, esquadrias e materiais | 274 verificações aprovadas | [validacao-nativa.json](validacao-nativa.json) |
| PNGs, configuração, hashes, referências e arquivos da entrega | 188 verificações aprovadas | [entrega-validacao.json](entrega-validacao.json) |
| Galeria em 1440 e 390 px, imagens, links e largura da página | 12 verificações aprovadas | [navegador-validacao.json](navegador-validacao.json) |
| Revisão visual dos arquivos finais | 26 de 26 vistas, vinculadas ao SHA de cada PNG | [revisao-visual-final.json](revisao-visual-final.json) |
| Compilação Python | 21 módulos sem erro | [python-validacao.json](python-validacao.json) |

As revisões incluíram recortes com densidade de pixels do render final, os dois ângulos das escadas e os interiores/exteriores, além de capa, imagens, comparação e plantas do PDF. Os JPEGs de revisão e capturas do navegador ficam neste diretório. As verificações de integridade não atribuem uma pontuação de realismo.

Modelo entregue: `projeto/residencia-07-atual-v02/casa-07-atual-fiel.blend`.

SHA-256: `3e453a03d1e50cb63967d8a3ff2540594b953bc9f57c9cbbb52acfc85b9518c0`.

Fonte anterior preservada: `projeto/residencia-07-atual/casa-07-atual.blend`, SHA-256 `585b9c6a2844053ebf29da25cd80367f79d21039dfc476940f55435649c68ea5`. [Conferência dos modelos](preservacao-modelos.json).

## Limites e continuidade

As fotografias não são um levantamento calibrado. Medidas de móveis, anexos e detalhes posteriores continuam aproximadas; partes não fotografadas foram interpretadas. As unidades vizinhas na fachada são contexto volumétrico ilustrativo. As plantas vetoriais cotadas mantêm a base documental anterior; as novas plantas em imagem mostram a reconstrução visual. Não se trata de projeto executivo nem de certificação de identidade fotográfica.

Unreal não está instalado; a entrega usa Cycles/GPU e não inclui medição de FPS ou comparação executada com Lumen. A expansão do fotorrealismo para o ático e a base original continua no [plano geral](../../PLANO-FOTORREALISMO.md).

A reconstrução está organizada em estágios no `scripts/rebuild_current_photoreal.py`. Nesta produção, os estágios foram executados individualmente com reabertura e validação antes da promoção; o agregador completo não foi executado de ponta a ponta. Preserve a revisão entregue antes de reconstruir. [Critérios de fidelidade](FIDELIDADE.md) e [pesquisa e materiais](PESQUISA-E-CRITERIOS.md).
