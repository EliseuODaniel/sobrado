import json
from pathlib import Path
ROOT=Path.cwd();archive='arquivos/versoes-anteriores-2026-11-14';moves=[]
def add(src,dst):
 if (ROOT/src).exists():moves.append({'source':src,'destination':dst})
# Entregas aprovadas e suas duas cenas de pavimento.
for key,folder in [('original','residencia-07'),('atual','residencia-07-atual-v02'),('industrial','industrial-v06')]:
 add('projeto/'+folder,'projeto/'+key)
 add('projeto/visualizacoes-pavimentos/'+key+'-sem-telhado.blend','projeto/'+key+'/visualizacao-pavimentos.blend')
add('projeto/residencia-07-atico-v05/atico-caixa-canto-escada.blend','projeto/atico/atico-caixa-canto-escada.blend')
add('projeto/residencia-07-atico-v05/LEIA-ME-caixa-canto.md','projeto/atico/LEIA-ME.md')
for p in (ROOT/'projeto').iterdir():
 if p.name not in {'residencia-07','residencia-07-atual-v02','industrial-v06'}:
  add(p.relative_to(ROOT).as_posix(),archive+'/'+p.relative_to(ROOT).as_posix())
add('renders/residencia-07/_trabalho',archive+'/renders/original-trabalho')
add('renders/residencia-07','renders/original')
add('renders/industrial-v06','renders/industrial')
add('renders/atico-caixa-canto','renders/atico')
for key in ['original','atual','industrial']:
 add('renders/visualizacoes-pavimentos/'+key,'renders/'+key+'/vistas-pavimentos')
for p in (ROOT/'renders').iterdir():
 if p.name not in {'residencia-07','atual','industrial-v06','atico-caixa-canto'}:
  add(p.relative_to(ROOT).as_posix(),archive+'/'+p.relative_to(ROOT).as_posix())
# Antigo relatório atual deve sair antes de receber o relatório vigente.
add('relatorios/atual',archive+'/relatorios/atual-anterior')
for old,key in [('residencia-07','original'),('atual-fiel-v02','atual'),('industrial-v06','industrial')]:add('relatorios/'+old,'relatorios/'+key)
for key in ['original','atual','industrial']:
 add('relatorios/visualizacoes-pavimentos/'+key+'-verificacao.json','relatorios/'+key+'/verificacao-pavimentos.json')
for p in (ROOT/'relatorios').iterdir():
 if p.name not in {'residencia-07','atual','atual-fiel-v02','industrial-v06','organizacao-movimentos.json','organizar.ps1','preparar_organizacao.py'}:
  add(p.relative_to(ROOT).as_posix(),archive+'/'+p.relative_to(ROOT).as_posix())
add('exports/fotorrealismo-industrial-v06','exports/industrial')
add('historico','arquivos/historico')
for p in ROOT.glob('PLANO-*.md'):add(p.name,archive+'/documentos/'+p.name)
# Detecta entradas em diretórios que serão movidos; itens internos vêm primeiro.
# As entradas específicas acima já precedem o movimento de seus diretórios pais.
manifest={'date':'2026-11-14','archive':archive,'moves':moves,'preserve':'Sem exclusões; somente Move-Item dentro do projeto.'}
(ROOT/'relatorios/organizacao-movimentos.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Movimentos planejados:',len(moves))
for m in moves:print(m['source'],'->',m['destination'])
