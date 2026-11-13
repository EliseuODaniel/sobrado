"""Reabre e confere a reconstrução antes de promover o arquivo .blend."""
import json
from pathlib import Path
import sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
import current_photoreal_data as data
from current_photoreal import protected
from residence07_current import world_matrix

m=json.loads((data.REPORT/'modelo.json').read_text());checks=[]
def check(label,ok):
    checks.append({'check':label,'passed':bool(ok)})
    if not ok:raise AssertionError(label)
check('Arquivo reaberto é exatamente a gravação temporária',data.sha(bpy.data.filepath)==m['temporary_sha256'])
check('Fonte atual preservada',data.sha(data.ROOT/data.CFG['base_blend'])==data.CFG['base_sha256'])
check('Geometria estrutural e alterações aprovadas preservadas',protected()==m['protected_geometry'])
check('Conjunto de cenas sem faltas ou sobras',{s.name for s in bpy.data.scenes}=={j['scene'] for j in m['jobs']})
for name,mat in m['opening_repairs'].items():
    current=world_matrix(bpy.data.objects[name]);check('Esquadria oficial '+name,all(abs(current[i][j]-mat[i][j])<1e-5 for i in range(4) for j in range(4)))
for suffix in ['.001','.002']:
    for part in ['Gabinete banho','Bancada banho','Cuba banho','Espelho banho','Louca base','Louca assento','Louca abertura']:
        o=bpy.data.objects['ATUAL R07 '+part+suffix];check('Peça do banheiro posicionada '+o.name,o.parent is not None and world_matrix(o).translation.z>=2.7-1e-5)
for j in m['jobs']:
    s=bpy.data.scenes[j['scene']];check('Câmera '+j['id'],s.camera is not None and s.camera.name in s.objects)
    check('Posição de câmera '+j['id'],all(abs(s.camera.location[k]-j['pos'][k])<1e-5 for k in range(3)))
    check('Cena preservada '+j['id'],s.use_fake_user and len(s.objects)>300)
    check('Saída 4K '+j['id'],[s.render.resolution_x,s.render.resolution_y]==data.CFG['resolution'])
check('Geladeira do bar atual preservada',bpy.data.objects.get('ATUAL Geladeira bar observada') is not None)
check('Geladeira da cozinha preservada',bpy.data.objects.get('ATUAL Geladeira cozinha') is not None)
for name,count in [('Banqueta bar encosto',4),('Cadeira jantar encosto',4),('Cadeira cabeceira encosto',2)]:
    check('Quantidade '+name,len([o for o in bpy.data.objects if o.name.startswith('FIEL2 '+name)])==count)
for token in ['Sofa almofada encosto','Cortina sala voil','Papel azul junto porta','Quarto branco papel coracoes','Suite cortina voil','Coifa vidro curvo','Cuba cozinha profunda','Lavadora vidro','Lavabo papel elipses']:
    check('Detalhe fotográfico '+token,any(o.name.startswith('FIEL2 '+token) for o in bpy.data.objects))
# A posição de apresentação usa as bases locais explícitas, mesmo para fontes fora da cena.
from mathutils import Vector
leaves=[o for o in bpy.data.objects if o.name.startswith('FIEL2 Porta em posicao fechada ATUAL BASE R07 Porta ')]
if leaves:
    check('Sete folhas fechadas na apresentação',len(leaves)==7)
    for o in leaves:
        id_=o['official_source_object'].removeprefix('ATUAL BASE R07 Porta ')
        root=bpy.data.objects['ATUAL BASE R07 Vao '+id_];hinge=bpy.data.objects['ATUAL BASE R07 Folha '+id_];r=world_matrix(root)
        expected=world_matrix(hinge).translation+r.to_3x3()@Vector((root['width_m']/2,0,root['height_m']/2))
        actual=world_matrix(o)
        check('Folha centralizada e no nível correto '+id_,(actual.translation-expected).length<1e-5)
        check('Folha alinhada ao vão '+id_,all(abs(actual[i][j]-r[i][j])<1e-5 for i in range(3) for j in range(3)))
missing=[i.name for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()]
check('Texturas presentes ou empacotadas',not missing)
check('Fotografias originais preservadas',all(data.sha(data.ROOT/r['file'])==r['sha256'] for r in m['references']))
result={'passed':True,'checks':checks,'total':len(checks),'protected_count':len(m['protected_geometry']),'opening_repairs':len(m['opening_repairs']),'scenes':len(bpy.data.scenes),'objects':len(bpy.data.objects),'scope':'Validação determinística de geometria, recursos e entrega; semelhança fotográfica exige inspeção visual.'}
(data.REPORT/'validacao-nativa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('CURRENT2_REOPEN_OK',len(checks),'checks',flush=True)
