import json,sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from residence07_industrial import geometry_fingerprint
from industrial_bar_policy import bar_fridges
REPORT=ROOT/'relatorios/industrial-v06'
layout=json.loads((REPORT/'rascunhos-v05-vinculos.json').read_text())['previa02']
rows=json.loads((REPORT/'rascunhos-industriais-sem-geladeira.json').read_text())
removed=set(next(r for r in rows if r['file'].endswith('/previa02.blend'))['removed'])

def members(name):
 c=layout['collections'][name]
 return set(c['objects']).union(*(members(child) for child in c['children']))

checks=[]
for name in ['previa01','previa02']:
 path=ROOT/'historico/rascunhos/industrial-v05'/(name+'.blend')
 bpy.ops.wm.open_mainfile(filepath=str(path))
 original=json.loads((REPORT/('inspecao-'+name+'.json')).read_text())['all_geometry']
 expected={n:h for n,h in original.items() if n not in removed}
 actual={o.name:geometry_fingerprint(o) for o in bpy.data.objects}
 checks.append({'name':name+' retained geometry','passed':all(actual.get(n)==h for n,h in expected.items())})
 checks.append({'name':name+' 25 scenes and no bar fridge','passed':len(bpy.data.scenes)==25 and not bar_fridges()})
 meta=json.loads(path.with_suffix('.json').read_text())
 for job in meta['jobs']:
  s=bpy.data.scenes[job['scene']];record=layout['scenes'][s.name]
  visible=set(record['objects']).union(*(members(child) for child in record['children']))-removed
  checks.append({'name':name+' visible objects '+job['id'],'passed':set(s.objects.keys())==visible})
  checks.append({'name':name+' camera '+job['id'],'passed':s.camera.name==record['camera'] and (s.camera.location-Vector(job['pos'])).length<1e-5})
assert all(c['passed'] for c in checks),[c for c in checks if not c['passed']]
(REPORT/'validacao-recuperacao-rascunhos-v05.json').write_text(json.dumps({'all_passed':True,'checks':checks,'scope':'Reabertura independente: objetos visíveis e câmeras das 25 cenas, geometria retida de cada rascunho e ausência da geladeira do bar.'},ensure_ascii=False,indent=2)+'\n')
print('DRAFT_V05_PRESENTATION_CHECKS',len(checks),'PASSED',flush=True)
