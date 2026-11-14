$ErrorActionPreference = 'Stop'
$items = @(
 @('original','projeto/residencia-07/casa-07.blend'),
 @('atual','projeto/residencia-07-atual-v02/casa-07-atual-fiel.blend'),
 @('industrial','projeto/industrial-v06/casa-industrial-fotorrealista.blend')
)
foreach ($item in $items) {
 & '.tools/blender-5.2.4-windows-x64/blender.exe' --background $item[1] --python-exit-code 1 --python scripts/floor_comparison_views.py -- $item[0] *> ('relatorios/visualizacoes-pavimentos/render-'+$item[0]+'.log')
 if ($LASTEXITCODE -ne 0) { throw ('Falha: '+$item[0]) }
}
