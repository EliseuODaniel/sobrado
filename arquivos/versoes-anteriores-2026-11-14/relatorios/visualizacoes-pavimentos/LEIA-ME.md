# Visualizações dos pavimentos — 14/11/2026

Seis imagens com câmera ortográfica e escala iguais, paredes completas e opacas, sem telhado nem fechamento superior que encubra o recorte.

Fontes:
- Original: projeto/residencia-07/casa-07.blend, cena R07_volumetria. É o projeto documental da residência 07, não as antigas reconstruções estimadas.
- Atual: projeto/residencia-07-atual-v02/casa-07-atual-fiel.blend, cena FIEL2_volumetria.
- Industrial: projeto/industrial-v06/casa-industrial-fotorrealista.blend, cena PHOTO6_volumetria.

Para cada versão:
1. Somente térreo: segundo pavimento e laje superior ausentes. Paredes completas, escada existente e mobiliário preservados no recorte.
2. Dois pavimentos: térreo e superior empilhados em suas posições reais, com a laje intermediária. Telhado e forro superior ausentes. A laje naturalmente encobre parte do térreo.

Não são usadas as coleções de paredes baixas/cortadas das plantas existentes. As paredes laterais, internas e de fachada do recorte conservam a geometria e os materiais originais. Os fechamentos laterais dos anexos atuais também são preservados. A cobertura dos anexos é retirada para permitir leitura do térreo.

Entorno genérico e vizinhos são omitidos para não obstruir a casa. O original documental tem geometria diferente nos fundos; não recebe anexos novos para artificialmente igualar as versões. A luz de apresentação e o enquadramento são comuns às três versões.

Cada modelo de entrega contém duas cenas VISUALIZACAO_<versao>_<modo>. Arquivos em projeto/visualizacoes-pavimentos; imagens e galeria em renders/visualizacoes-pavimentos. As fontes não são sobrescritas, e seus SHA-256 são conferidos antes/depois de cada execução.

Verificações por versão: *-verificacao.json registra objetos incluídos, paredes completas e elementos superiores retirados. Os testes do gerador exigem todas as paredes documentais do nível escolhido e recusam o uso de paredes de corte. As imagens são revistas visualmente após o render. Limites: medidas e mobiliário conservam os limites documentais/aproximados de cada fonte; esta entrega é de apresentação e não de projeto executivo.

Gerador: scripts/floor_comparison_views.py. Fila: relatorios/visualizacoes-pavimentos/renderizar.ps1, executar com PowerShell 7. O gerador recusa sobrescrever os modelos de entrega existentes.
