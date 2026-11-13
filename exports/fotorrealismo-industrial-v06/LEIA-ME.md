# Intercâmbio industrial v06

Os GLBs contêm geometria, UVs e nomes dos materiais, em metros. A casa principal e o escritório alternativo são arquivos separados. O cubo de referência mede 1 m em cada eixo e foi reimportado no Blender para conferir a unidade; três paredes da casa também tiveram seus limites comparados, com tolerância de 1 mm.

**Os materiais são placeholders.** Para reproduzir as imagens desta revisão, use o Blender editável, que contém os shaders completos. Materiais procedurais, correções de cor, relevo, vidros, luz e exposição precisam ser convertidos/reconstruídos no Unreal. As texturas licenciadas estão em `assets/fotorrealismo-industrial`; os grafos completos permanecem no `.blend`.

Não houve importação ou benchmark no Unreal. Ao importar, conferir que o cubo de 1 m chega como 100 cm na unidade padrão do motor; este teste ainda está pendente. Recibo em `relatorios/industrial-v06/intercambio.json`.
