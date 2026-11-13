# Base técnica de geração

`casa-base-detalhada.blend` é a fonte intermediária que combina a arquitetura R10, a proposta v01 e o primeiro detalhamento de materiais. Ela não é a entrega visual atual. Seu conteúdo foi preservado ao mover o estudo v02 para o histórico.

A manutenção posterior retirou somente a geladeira do bar desta fonte industrial, preservando a da cozinha. Os hashes anteriores e atuais estão no [recibo de manutenção](../../relatorios/industrial-v06/remocao-geladeiras-fontes.json).

SHA-256: `70980ced81d16e89c38d458d3f2c6e021d0c6da3d5c9e42b9d669846a5cff09a`.

A entrega está em `projeto/industrial-v03/casa-fotografica.blend`. Ambos os modelos usam Git LFS. O gerador `scripts/photographic_interiors.py` parte desta base; escolha um novo caminho de saída na configuração para preservar seus ajustes manuais.

## Biblioteca do ático vigente

`atico-cobertura-forro-sem-acesso.blend` contém componentes de cobertura, forro, materiais, reservatório e mobiliário, além da base da casa. Não contém escada de acesso ao ático. É a fonte independente para a v05 após a exclusão das propostas antigas. A solução vigente está em `../residencia-07-atico-v05`.

## Biblioteca de mobiliário industrial

`mobiliario-industrial.blend` contém somente a coleção de componentes reutilizáveis e o material de pedra selecionado. Não contém cenas ou a arquitetura da industrial v04 descartada. Origem e validação em `relatorios/industrial-v06/biblioteca-extraida.json`.
