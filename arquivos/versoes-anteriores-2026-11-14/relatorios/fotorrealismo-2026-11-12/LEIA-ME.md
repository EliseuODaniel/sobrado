# Pesquisa e auditoria de fotorrealismo — 12/11/2026

**Resultado:** diagnóstico e plano concluídos para os cinco modelos vigentes. A migração de motor e a geração das novas imagens são etapas futuras. [Plano completo](../../PLANO-FOTORREALISMO.md).

| Obrigação | Evidência observada | Situação |
| --- | --- | --- |
| Conhecer os arquivos vigentes | Cinco arquivos abertos em Blender 5.2.4 LTS; hashes antes/depois iguais; cena representativa de cada arquivo inventariada | VERIFICADO |
| Examinar a aparência existente | Sala atual, sala industrial e interior frontal do ático examinados nos PNGs nativos | VERIFICADO para três imagens; demais ângulos pendentes |
| Conhecer a máquina | Consultas locais `nvidia-smi`, PowerShell, `lscpu`, `free` e espaço livre | VERIFICADO; não é benchmark de render |
| Pesquisar opções atuais | Fontes primárias Epic, Blender e artigo de pesquisa; links e limites no plano | VERIFICADO; falhas de acesso ao manual Blender explicitadas |
| Comparar e planejar | Cycles, Unreal e Twinmotion; piloto, etapas, critérios de qualidade e regressão | CONCLUÍDO como planejamento |
| Demonstrar realismo/desempenho novo | Exige executar piloto e examinar resultados novos | NÃO EXECUTADO; fora desta etapa |

## Recibos

- [Inventário nativo](auditoria-modelos.json): contagens globais e de uma cena por arquivo, materiais, imagens, UVs, luzes, câmeras, amostragem e hashes.
- [Hardware](hardware.json): comandos, resultados e distinção entre memória física do Windows e orçamento do WSL.
- [Auditor somente leitura](auditar_blends.py): não contém operação para salvar `.blend`.
- [Checkpoint](checkpoint.json): objetivo, obrigações e pendências.
- [Validação](validacao.json): 20 verificações aprovadas sobre arquivos, hashes, referências de imagem, links locais, sintaxe e comandos de hardware; não avalia a qualidade de renders futuros.

Para repetir o inventário, executando na raiz do projeto:

```bash
python3 scripts/run_blender.py --background --factory-startup --python relatorios/fotorrealismo-2026-11-12/auditar_blends.py
```

O comando reescreve somente o relatório JSON. As contagens de polígonos são de malhas fonte únicas, antes de modificadores e instâncias avaliados; não representam triângulos finais de renderização. A existência de UVs, imagens ou chanfros não mede automaticamente sua qualidade. O inventário de imagens considera nós, inclusive nós potencialmente desconectados.

**Conclusão delimitada:** há base reaproveitável e um plano verificável para testar a evolução. A superioridade visual de Unreal sobre Cycles neste projeto e o desempenho no notebook continuam desconhecidos até o piloto. A revisão física da construção, o levantamento dos móveis e a licença de cada asset também não foram concluídos por esta auditoria.
