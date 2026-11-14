# Manutenção dos modelos Blender

Os modelos e renders são gerados pelos scripts de cada revisão. Confira o índice principal para escolher a fonte e o gerador vigentes.

Ao manter um arquivo existente:

- Confira o hash esperado antes de editar. Preserve alterações externas em vez de substituí-las silenciosamente.
- Salve em um caminho temporário, reabra esse temporário e compare a geometria preservada, as cenas, câmeras e coleções. Promova o temporário ao destino somente depois dessas conferências.
- Ao salvar arquivos carregados em sequência no modo de fundo, retenha explicitamente as cenas/coleções necessárias (`use_fake_user`) e defina uma cena válida em `bpy.context.window.scene`. O rascunho industrial v05 exigiu essa correção; [recibo da recuperação](../relatorios/industrial/rascunhos-industriais-sem-geladeira.json) e [conferência independente](../relatorios/industrial/validacao-recuperacao-rascunhos-v05.json).
- Em `bpy.data.libraries.load`, mantenha a lista de nomes separada da lista atribuída ao destino: use `target.objects = list(names)`. Ao concluir a carga, o Blender substitui os nomes da lista de destino por IDs. A lista de nomes deve continuar contendo textos para criar os mapas de correspondência.

Os recibos históricos de geração conservam seus hashes originais. Manutenções posteriores têm recibos próprios com os hashes atuais e as alterações autorizadas; não devem reescrever a história como se o modelo tivesse sido gerado novamente.

## Reconstrução fotográfica da casa atual

A receita da revisão atual está em `config/atual-fiel-v02.json`. O arquivo anterior `arquivos/versoes-anteriores-2026-11-14/projeto/residencia-07-atual/casa-07-atual.blend` permanece como fonte preservada.

```bash
python3 scripts/rebuild_current_photoreal.py
python3 scripts/render_current_photoreal.py --preview
python3 scripts/render_current_photoreal.py --resume
.tools/planta-venv/bin/python scripts/deliver_current_photoreal.py
.tools/planta-venv/bin/python scripts/validate_current_delivery.py
```

A reconstrução executa a geometria, o laminado claro, a calibração dos banheiros, as poses de portas/cortina, a conferência de superfícies e os tecidos/orquídeas refinados. Cada gravação é reaberta e validada antes da promoção. A revisão existente só pode ser substituída se corresponder ao recibo; uma cópia com hash fica no histórico. Os estágios foram executados individualmente e validados durante a revisão v02. O encadeamento pelo novo comando completo não foi reexecutado.

A fila de render usa a instalação Windows do Blender 5.2 com OptiX, copia o arquivo nativo para staging e confere os hashes antes e depois da cópia. `--resume` reaproveita somente PNGs íntegros do mesmo modelo/configuração. As prévias ficam em `relatorios/atual`, fora da entrega final. O staging pode ser removido após conferir a entrega.

Objetos preservados fora da cena ativa podem ter `matrix_world` desatualizada. Para ler transformações durante cópias/manutenção, use a função recursiva `world_matrix` de `residence07_current.py`, calculada por `matrix_basis` e pais. Confira independentemente posição, orientação e altura de cada cópia reaberta; apenas conferir os objetos fonte não detecta erro nas cópias de apresentação.
