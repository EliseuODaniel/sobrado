$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Get-Location).Path)
$manifest = Get-Content -LiteralPath 'relatorios/organizacao-movimentos.json' -Raw | ConvertFrom-Json
$receipt = @()
foreach ($item in $manifest.moves) {
 $source = [IO.Path]::GetFullPath((Join-Path $root $item.source))
 $target = [IO.Path]::GetFullPath((Join-Path $root $item.destination))
 if (-not $source.StartsWith($root + [IO.Path]::DirectorySeparatorChar) -or -not $target.StartsWith($root + [IO.Path]::DirectorySeparatorChar)) { throw 'Movimento fora do projeto' }
 if (-not (Test-Path -LiteralPath $source)) { throw ('Origem ausente: '+$item.source) }
 if (Test-Path -LiteralPath $target) { throw ('Destino já existe: '+$item.destination) }
 $sourceItem = Get-Item -LiteralPath $source
 $files = if ($sourceItem.PSIsContainer) { @(Get-ChildItem -LiteralPath $source -File -Recurse -Force) } else { @($sourceItem) }
 $count = $files.Count
 $bytes = ($files | Measure-Object -Property Length -Sum).Sum
 $null = New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target)
 Move-Item -LiteralPath $source -Destination $target
 $targetItem = Get-Item -LiteralPath $target
 $after = if ($targetItem.PSIsContainer) { @(Get-ChildItem -LiteralPath $target -File -Recurse -Force) } else { @($targetItem) }
 if ($after.Count -ne $count -or ($after | Measure-Object -Property Length -Sum).Sum -ne $bytes) { throw ('Contagem/tamanho divergente: '+$item.destination) }
 $receipt += [pscustomobject]@{source=$item.source;destination=$item.destination;files=$count;bytes=$bytes;verified=$true}
 $receipt | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $root 'relatorios/organizacao-recibo.json') -Encoding utf8
}
Write-Output ('ORGANIZACAO_OK: '+$receipt.Count+' movimentos sem exclusões')
