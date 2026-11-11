# Revisão 02 — contradições fotográficas e limites

UTC: 2026-11-10T12:02:54.983260+00:00

Foram corrigidas contradições concretas da versão rejeitada. O arquivo foi reaberto e gerou 12 renders em Cycles. Passaram 15 verificações de integridade e 12 verificações de implantação/visibilidade. Os recibos são `auditoria-antes.json`, `auditoria-depois.json`, `renders-finais.json` e `relatorios/planta-casa/validacao.json`.

Esses resultados não validam a planta completa. O superior permanece sem implantação demonstrada pelas fotos.

## Evidência dos testes

| Relação ou erro testado | Versão rejeitada | Revisão 02 | Fotos de controle |
| --- | --- | --- | --- |
| tv_na_parede_interna_lateral | FAIL | PASS | sala4.webp, sala7.webp |
| porta_lavabo_na_mesma_face | FAIL | PASS | sala2.webp, sala4.webp |
| porta_lavabo_fechada_como_na_foto | FAIL | PASS | sala4.webp |
| primeiro_lance_transversal | FAIL | PASS | sala1.webp, sala4.webp |
| espelho_fora_do_volume_da_parede | FAIL | PASS | sala7.webp |
| pedra_exposta_na_frente_da_parede | PASS | PASS | area3.webp |
| primeiro_lance_nao_exposto_na_vista_sala7 | FAIL | PASS | sala7.webp |
| primeiro_lance_visivel_no_angulo_sala1 | FAIL | PASS | sala1.webp |
| primeiro_lance_visivel_na_vista_sala4 | PASS | PASS | sala4.webp |
| janela_cozinha_visivel_pela_passagem | PASS | PASS | sala7.webp, cozinha2.webp |
| porta_lavabo_visivel_entre_tv_e_escada | FAIL | PASS | sala4.webp |
| superior_sem_adjacencias_inventadas | FAIL | PASS | quartosuite1.webp, quartoazul1.webp, quartobranco1.webp |

O teste da versão anterior utiliza o arquivo preservado. Ausência de uma vista requerida também aparece como falha e está detalhada no JSON; a tabela não é uma pontuação de semelhança fotográfica.

## Conferência visual

As montagens mostram foto, versão rejeitada e revisão em dois sentidos da sala, além de seis ângulos comparados. As câmeras foram reajustadas por marcos aproximados selecionados pelo agente ao inspecionar as imagens; isso não é avaliação humana nem fotogrametria. Persistem diferenças de proporção, enquadramento, acabamento e detalhes.

No térreo, TV e acessos foram reunidos na espinha lateral; a porta do lavabo fica fechada; o primeiro lance deixa de invadir longitudinalmente o estar. Espelho e pedra estavam embutidos nas paredes e agora estão expostos. A vista superior inclui as paredes externas e oculta as vergas para permitir ler os vãos. O corte 3D usa outro lado de observação para mostrar a face interna da parede da TV.

## Desconhecidos que impedem afirmar a planta inteira

| Afirmação | Estado | Evidência necessária |
| --- | --- | --- |
| Quartos e banheiros na posição correta do superior | UNKNOWN | Confirmar quais ficam na frente/fundos e como se conectam à circulação |
| Retorno completo da escada em U | INFERRED | Fotos contínuas ou planta do percurso completo |
| Dimensões lineares reais | UNKNOWN | Medidas ou planta cotada |
| Áreas da matrícula conciliadas | UNKNOWN | Documento original; o texto recebido foi identificado como análise do ChatGPT |

As divisões internas do superior foram retiradas da envoltória principal. Cômodos editáveis continuam como módulos na cena `ESTUDOS_Superior`, sem conexão presumida com a casa. O perímetro do serviço e a atribuição da pequena janela frontal a um cômodo também não foram confirmados.

## Escopo da conclusão

Nesta data, a revisão remove as contradições específicas testadas e fornece arquivo editável, renders e comparações. Não se declara a planta completa fiel ao imóvel. As 31 fotos originais e a versão rejeitada estão preservadas. Não houve commit, push ou publicação.
