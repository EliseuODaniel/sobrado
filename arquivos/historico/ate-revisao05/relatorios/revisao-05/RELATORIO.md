# Revisão 05 — conferência fotográfica do térreo e da fachada

UTC: 2026-11-10T16:29:44.510521+00:00

O térreo e a fachada foram confrontados com as referências originais. Foram removidas contradições específicas e preservadas as correções explícitas do usuário: entrada diagonal, garagem ampliada, lavabo sob o segundo lance e posição relativa da lavanderia. As divisões do segundo pavimento não foram iniciadas.

## Resultado por parte

| Parte | Evidência e ajuste | Estado da conclusão |
| --- | --- | --- |
| Fachada | `exterior1.webp` e `exterior2.webp`: garagem sob a laje superior, laterais contínuas, varanda recuada, rede, molduras e grades, janela posterior, revestimento claro e pavimento externo | VERIFIED para essas relações no modelo; proporções INFERRED |
| Garagem e lavabo | Parede externa vertical oculta a escada, mantendo janela pequena e lavabo sob o segundo lance | VERIFIED no modelo e nos ângulos de controle; folgas reais UNKNOWN |
| Sala e jantar | Painel com fundo cinza, rack amarelo, mesa escura, pendente inclinado e detalhes dos encostos | VERIFIED como ajustes visuais aproximados; marcenaria não medida |
| Cozinha | `cozinha1/2.webp`: bancada separada no vão do fogão, micro-ondas, aéreo lateral, puxadores, azulejos e lava-louças | VERIFIED para presença e relações; proporções INFERRED |
| Churrasqueira | `area2/4.webp`: revestimento em madeira e boca lateral substituem a coifa de alvenaria exposta | VERIFIED como correção da contradição visual; construção interna UNKNOWN |
| Lavanderia | `lavanderia1.webp`: retorno à esquerda, tanque, aéreos, puxadores e tampo livre sobre máquina superior | VERIFIED para relações; extensão do retorno e ligação ao pátio INFERRED/UNKNOWN |
| Integridade e preservação | Arquivo reaberto, hashes das 31 referências e do backup conferidos; 15 verificações de integridade e 33 relações geométricas | VERIFIED para o arquivo entregue |
| Segundo pavimento | Estudos separados e parâmetros de distribuição mantidos | VERIFIED: nenhuma distribuição nova; planta interna UNKNOWN |

## Comparação e testes

O mesmo arquivo salvo gerou 17 renders. Oito ângulos internos e dois externos foram comparados com as fotos; as montagens são `renders/planta-casa/comparacao-originais.png` e `fachada-comparacao.png`. A comparação de volumetria externa antes/depois está em `fachada-antes-depois.png`.

A versão anterior preservada foi submetida à mesma auditoria. 9 falhas específicas deixaram de ocorrer. As verificações abrangem vãos, posições, oclusão da escada na fachada, fogão livre da bancada e máquina superior livre do tampo. Elas não constituem prova de identidade métrica da planta. A ausência de uma câmera de controle na versão anterior também é registrada como falha de evidência; a contagem não corresponde a uma nota de semelhança ou a nove erros construtivos comprovados.

| Relação testada | Revisão anterior | Revisão 05 | Fontes |
| --- | --- | --- | --- |
| tv_na_parede_interna_lateral | PASS | PASS | sala4.webp, sala7.webp |
| porta_lavabo_na_mesma_face | PASS | PASS | sala2.webp, sala4.webp |
| porta_lavabo_fechada_como_na_foto | PASS | PASS | sala4.webp |
| primeiro_lance_transversal | PASS | PASS | sala1.webp, sala4.webp |
| espelho_fora_do_volume_da_parede | PASS | PASS | sala7.webp |
| pedra_exposta_na_frente_da_parede | PASS | PASS | area3.webp |
| primeiro_lance_nao_exposto_na_vista_sala7 | PASS | PASS | sala7.webp |
| primeiro_lance_visivel_no_angulo_sala1 | PASS | PASS | sala1.webp |
| primeiro_lance_visivel_na_vista_sala4 | PASS | PASS | sala4.webp |
| janela_cozinha_visivel_pela_passagem | PASS | PASS | sala7.webp, cozinha2.webp |
| porta_lavabo_visivel_entre_tv_e_escada | PASS | PASS | sala4.webp |
| superior_sem_adjacencias_inventadas | PASS | PASS | quartosuite1.webp, quartoazul1.webp, quartobranco1.webp |
| entrada_em_diagonal | PASS | PASS | referencias-ajustes/planta-terreo-anotada.png |
| lavabo_atras_da_continuacao_garagem | PASS | PASS | referencias-ajustes/planta-terreo-anotada.png |
| lavanderia_imediatamente_atras_cozinha | PASS | PASS | referencias-ajustes/planta-terreo-anotada.png |
| fundos_churrasqueira_lavanderia_alinhados | PASS | PASS | referencias-ajustes/planta-terreo-anotada.png |
| passagem_lateral_lavanderia_livre | PASS | PASS | referencias-ajustes/planta-terreo-anotada.png |
| garagem_aberta_ate_divisao_lavabo | PASS | PASS | referencias-ajustes/planta-terreo-anotada.png |
| churrasqueira_canto_fundos_esquerdo | PASS | PASS | referencias-ajustes/planta-terreo-anotada.png |
| tres_banquetas_conforme_croqui | PASS | PASS | referencias-ajustes/planta-terreo-anotada.png |
| lavabo_na_projecao_segundo_lance | PASS | PASS | config/planta-casa.json#user_correction |
| garagem_ocupa_antiga_area_lavabo | PASS | PASS | config/planta-casa.json#user_correction |
| loucas_e_espelho_dentro_lavabo_abaixo_forro | PASS | PASS | config/planta-casa.json#user_correction |
| fachada_sem_marquise_e_pilares_avancados | FAIL | PASS | exterior1.webp, exterior2.webp |
| garagem_com_paredes_laterais_continuas | FAIL | PASS | exterior1.webp, exterior2.webp |
| varanda_recuada_com_rede | FAIL | PASS | exterior1.webp, exterior2.webp |
| janela_sala_com_grade | FAIL | PASS | exterior1.webp, exterior2.webp |
| janela_pequena_visivel_no_fundo_garagem | FAIL | PASS | exterior2.webp |
| escada_oculta_na_vista_externa | FAIL | PASS | exterior1.webp, exterior2.webp |
| bancada_nao_atravessa_fogao | FAIL | PASS | cozinha1.webp |
| lavadora_superior_livre_de_granito | FAIL | PASS | lavanderia1.webp |
| retorno_lavanderia_no_lado_esquerdo | FAIL | PASS | lavanderia1.webp |
| implantacao_aprovada_pelo_usuario_preservada | PASS | PASS | config/planta-casa.json#user_correction |

## Limites conhecidos

- Enquadramentos aproximados; nenhuma calibração métrica ou nota de similaridade
- Três bancos do croqui mantidos apesar de as fotos mostrarem quatro
- Retorno esquerdo da bancada da lavanderia encurtado para preservar o acesso lateral do croqui; profundidade real não demonstrada
- Forro do lavabo usa envelope inclinado e ressaltos aproximados; não é uma reprodução estrutural medida
- Vizinhas são contexto volumétrico aproximado apenas nas câmeras externas, sem interiores

## Desconhecidos e evidência que falta

- Dimensões reais, espessuras, inclinação e folgas da escada
- Ligação exata entre janela da cozinha, eventual pátio aberto e lavanderia; esclarecimento solicitado ao usuário, sem resposta registrada
- Forma completa do telhado da unidade, aproximada pela tipologia vista nas vizinhas
- Implantação dos cômodos do segundo pavimento, reservada para a próxima etapa

A matrícula original continua não conferida; a análise do ChatGPT recebida não foi promovida a dado oficial. Para concluir dimensões reais, são necessárias medidas ou planta cotada. A pergunta sobre eventual pátio entre cozinha e lavanderia ficou pendente; foi preservada a organização geral do croqui em vez de acrescentar uma divisória sem evidência.

Validação executada: `validate_house.py`, `audit_photo_geometry.py --baseline`, `house_atlas.py`, `python3 -m py_compile scripts/*.py` e `git diff --check`. Os recibos são `validacao.json`, `auditoria-antes.json`, `auditoria-depois.json`, `renders-finais.json` e os logs do Blender. Não houve commit, push ou publicação.
