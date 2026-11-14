# Proposta industrial v01

UTC: 2026-11-11T01:44:00.750947+00:00

Sala/jantar, cozinha, lazer nos fundos e quarto dos fundos receberam uma proposta de acabamento inspirada nas quatro imagens de `referencias-estilo-industrial/`. O Blender industrial é uma variante separada da reconstrução da revisão 10. As dimensões permanecem estimadas.

| Obrigação | Recibo observado | Estado |
| --- | --- | --- |
| Arquitetura, aberturas e escada preservadas | 2575 hashes de malhas/curvas, transformações locais, pais e modificadores herdados iguais antes/depois; zero diferenças ao reabrir | VERIFIED |
| Encaixe dos pavimentos | Três verificações dos vértices das lajes e faces posteriores, no arquivo salvo | VERIFIED |
| Quatro ambientes renderizados | Sete PNGs, com reconciliação exata dos nomes, dimensões e SHA-256 | VERIFIED |
| Editável sincronizado aos renders | Reabertura em outro processo; SHA-256 do `.blend` antes/depois da renderização igual | VERIFIED |
| Recursos e cenas editáveis | Nove verificações independentes ao reabrir o Blender em `validacao.json` | VERIFIED |
| Reconstrução e imagens inspiradoras intactas | SHA-256 do modelo base e das quatro referências preservados | VERIFIED |
| Câmeras fora de sólidos | Nenhuma interseção detectada com caixas locais das malhas visíveis | VERIFIED |
| Conferência visual final | revisao-visual.json vinculado aos hashes finais | VERIFIED |
| Medidas do imóvel e dimensionamento construtivo | Sem levantamento novo | UNKNOWN |

## Decisões de estilo

- **Sala/jantar:** cimento cinza, couro caramelo, rack escuro com tampo de madeira, mesa de centro e tapete. A mesa de jantar recebe três tábuas e quatro pés de madeira; pendentes e trilhos complementam a luz ambiente. O espelho existente fica livre de prateleiras.
- **Cozinha:** marcenaria grafite, revestimento escuro, metais pretos, detalhes de madeira e luz de bancada. Bancadas, pia, fogão, geladeira, janelas e acessos mantêm suas posições.
- **Lazer:** bar em nogueira e metal, revestimento de pedra oxidada, prateleiras iluminadas, taças, cerâmica e arandelas. A cobertura acompanha a geometria existente; as travessas adicionais são elementos da proposta.
- **Quarto dos fundos:** beliche com estrutura escura e estrados de madeira, linho neutro, azul petróleo na parede da bancada, prateleiras, monitores, cadeira e iluminação de trabalho. A inspiração de escritório não transforma o ambiente em outro cômodo.

## Organização e reprodução

Editável: `projeto/industrial-v01/casa-industrial.blend`. Cenas: `IND_…`. Novas peças: coleções `IND_Decor_…`. Materiais: `IND …`. As quatro referências acompanham o repositório, sem serem necessárias para renderizar; os revestimentos são procedurais e ajustáveis. As 26 fotos originais únicas herdadas continuam empacotadas. A configuração `config/estilo-industrial-v01.json` define câmeras, versão e saídas; cores e texturas ficam nos materiais do Blender e na função `materials()` do gerador.

O arquivo base e a geometria herdada ficam preservados. Na variante, o pendente de anéis, o pé central da mesa e a TV antiga do quarto ficam ocultos no render para receber as peças da proposta, sem excluir os objetos. A apresentação não é uma reprodução literal das imagens: proporções, mobiliário simplificado e incidência de luz obedecem ao modelo da casa.

Os renders foram produzidos pelo Blender em Cycles/CPU, 96 amostras, AgX e denoise, em 1600 × 1000. O log da execução está em `renderizacao.log`. Houve uma rodada de prévias e refinamento de câmera, cimento, madeira, iluminação e posição das prateleiras; as prévias iniciais estão preservadas localmente em `historico/rascunhos/industrial-v01/rodada01/`.

Os binários antigos e rascunhos continuam no disco, ignorados pelo Git. Apenas modelos/renders atuais, referências, código, configuração e documentos/recibos históricos são publicados. A comprovação do push fica no SHA retornado por `git ls-remote origin refs/heads/main`, conferido após publicar; este relatório não antecipa esse resultado.

## Limites

O modelo é um estudo visual com móveis simplificados, não um projeto executivo. Persistem as incertezas de escala, banheiros superiores e degraus já registradas na revisão 10. As referências inspiram materiais e iluminação; não comprovam a arquitetura nem o mobiliário real da casa. A conferência geométrica não substitui levantamento nem cálculo estrutural.
