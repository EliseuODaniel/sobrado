# Casa — revisão 02 por confronto com as fotos

O térreo foi revisto para corrigir contradições da versão anterior: posição da parede da TV, acessos laterais do lavabo e da escada, direção do primeiro lance, relação com a cozinha e superfícies embutidas nas paredes.

- [Arquivo Blender revisado](projeto/casa-reconstruida.blend)
- [Comparação: foto, versão rejeitada e revisão](renders/planta-casa/comparacao-antes-depois.png)
- [Seis ângulos comparados com as fotos](renders/planta-casa/comparacao-originais.png)
- [Térreo em 3D e estudos separados do superior](renders/planta-casa/planta-3d.png)
- [Vistas superiores](renders/planta-casa/plantas-superiores.png)
- [Configuração e origem das hipóteses](config/planta-casa.json)
- [Auditoria fotográfica](relatorios/revisao-02/auditoria-depois.json)

**A planta completa do superior continua não estabelecida.** As ligações que haviam sido inventadas entre quartos e banheiros foram retiradas. Os cômodos permanecem editáveis em `ESTUDOS_Superior`, separados da casa e identificados como módulos sem posição confirmada. A envoltória superior não representa um andar vazio real.

## O que foi corrigido

| Contradição anterior | Revisão | Fotos de controle |
| --- | --- | --- |
| TV na parede externa, alargando artificialmente a sala | TV na espinha lateral interna, na sequência dos demais acessos | `sala4`, `sala7` |
| Porta do lavabo em outra face e aberta, expondo a louça | Porta fechada na lateral entre TV e escada | `sala2`, `sala4` |
| Dois lances longitudinais expostos ao estar | Primeiro lance transversal e recuado, com parede separando a faixa lateral | `sala1`, `sala4`, `sala7` |
| Cozinha vista por uma circulação inadequada | Entrada lateral junto ao ripado e janela voltada ao pátio | `sala1`, `sala7`, `cozinha1`, `cozinha2` |
| Espelho e pedra do bar ocultos dentro da espessura das paredes | Superfícies trazidas para as faces internas visíveis | `sala7`, `area3` |
| Superior com distribuição sem comprovação | Envoltória e módulos de cômodos separados, sem adjacências presumidas | Fotos isoladas não demonstram a circulação |

A versão rejeitada está preservada em `projeto/versoes/revisao-02-antes/`, incluindo gerador, configuração e README. O `.blend` anterior também foi mantido em `projeto/versoes/casa-reconstruida-rejeitada-antes-revisao02.blend`.

## Abrir e editar

Abra `projeto/casa-reconstruida.blend` no Blender 5.2 LTS. A cena inicial é `PLANTA_Terreo`. `Num 0` entra na câmera e `F12` renderiza.

As cenas disponíveis são:

- `PLANTA_Terreo` e `PLANTA_Terreo_Cotas`: implantação revisada do térreo.
- `PLANTA_Superior` e `PLANTA_Superior_Cotas`: envoltória sem distribuição interna confirmada.
- `ESTUDOS_Superior`: beliche, quarto branco, suíte e dois banheiros como módulos independentes, fora das coordenadas da casa.
- `FOTO_Sala_Fundos`, `FOTO_Sala_Frente`, `FOTO_Detalhe_Escada`, `FOTO_Cozinha`, `FOTO_Cozinha_Reversa` e `FOTO_Bar`: ângulos de comparação.
- `CASA_Completa`: volumes e coberturas, com o superior ainda sem implantação interna.

No Outliner, mova os pais `SOFA_…`, `TV_E_RACK_original`, `MESA_JANTAR_…`, `CADEIRA_…` e `BANQUETA_…` usando `G` e o eixo desejado. Os pais `ESTUDO_…` movem os módulos independentes do superior. Não use a posição desses módulos para deduzir onde ficam na casa.

Selecione uma peça para trocar seu material em Material Properties. As luzes estão em `Iluminacao`; Power, Color e Size permanecem editáveis. Os pais das portas têm pivô no batente e podem ser girados em Z. As fotografias estão empacotadas em `Referencias`, fora dos renders. Não são usadas como fundo ou como imagem do espelho.

Salve suas alterações com outro nome, por exemplo `projeto/casa-minha-edicao.blend`. A geração usa um destino novo com timestamp quando o arquivo escolhido já existe.

## Medidas e pontos ainda desconhecidos

Todas as dimensões lineares continuam estimadas. A largura da sala é distinta da largura total da faixa lateral. Os retângulos de 5 × 8,50 m e 5 × 10,20 m da análise do ChatGPT não foram tratados como restrições: eram exemplos hipotéticos e contribuíram para distorcer a versão anterior.

A análise de áreas enviada pelo usuário está registrada como fonte secundária não verificada. A matrícula original não foi recebida, e nenhum perímetro comum ou privativo foi deduzido desses números.

O primeiro lance foi confrontado com as fotos; o retorno completo em U transversal continua sendo uma hipótese geométrica. O número de degraus, a posição da lavanderia, os alinhamentos externos e o contorno total ainda precisam de confirmação. A pequena janela da fachada foi preservada sem atribuir a ela um ambiente interno não demonstrado.

Para fechar o superior, falta confirmar quais quartos ficam na frente e nos fundos e o percurso completo da escada. As fotografias isoladas dos cômodos não mostram essas ligações.

## Gerar e verificar

Na raiz do projeto:

```bash
python3 scripts/run_blender.py --background --factory-startup --python-exit-code 1 \
  --python scripts/build_house.py -- --project-root . --device cpu \
  --output projeto/versoes/casa-nova-geracao.blend
```

Use o caminho da versão gerada para validá-la. A validação abaixo refere-se à entrega principal:

```bash
python3 scripts/run_blender.py --background projeto/casa-reconstruida.blend \
  --python-exit-code 1 --python scripts/validate_house.py -- --project-root . --device cpu
python3 scripts/house_atlas.py
# Após conferir as comparações visualmente:
python3 scripts/finalize_house.py
```

`validate_house.py --no-render` executa somente as verificações. `--preview` renderiza seis ângulos em resolução reduzida. O gerador depende do Python e de `bpy` do Blender; as montagens usam Pillow. O ajuste opcional de câmeras por pontos aproximados usa NumPy e SciPy já disponíveis neste ambiente e não faz parte da geração normal.

O Blender portátil é `.tools/blender-5.2.4-linux-x64/blender`. Também é possível chamar esse executável diretamente com os mesmos argumentos. Para uma instalação Windows funcional, o equivalente em PowerShell é:

```powershell
$Blender = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
& $Blender --background --factory-startup --python-exit-code 1 `
  --python ".\scripts\build_house.py" -- --project-root "." --device cpu `
  --output ".\projeto\versoes\casa-nova-geracao.blend"
```

Foi usado Blender 5.2.4 LTS, Cycles, AgX e denoise em CPU. Os pacotes portáteis estão ignorados pelo Git. Nenhuma configuração global, driver ou runtime foi alterado nesta revisão.

## O que os testes demonstram

Os testes de integridade conferem reabertura, cenas, recursos, hashes das 31 fotos e preservação do arquivo. A auditoria fotográfica confere relações específicas: mesma face lateral, direção do lance, porta fechada, ausência de escada exposta em `sala7`, visibilidade pelos ângulos de `sala1` e `sala4`, janela da cozinha e revestimentos fora das paredes.

Esses testes agora detectam contradições presentes na versão rejeitada. **Passar neles não comprova equivalência da planta completa com o imóvel.** O ajuste de câmera usa pontos aproximados marcados nas imagens, sem âncora métrica. Permanecem diferenças de proporção, acabamento, enquadramento e detalhamento, registradas nas comparações.

Relatórios: `relatorios/revisao-02/RELATORIO.md`, `auditoria-antes.json`, `auditoria-depois.json`, `renders-finais.json` e `manifesto.json`. Não foi feito commit, push ou publicação nesta revisão.
