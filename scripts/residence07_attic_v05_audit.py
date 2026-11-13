"""Auditoria da v05 reaberta: alinhamento, alturas, caixa deslocada e cômodos."""
import datetime as dt
import json
from pathlib import Path
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
import residence07_geometry as geo
import residence07_attic_v05_data as data
import residence07_attic_v05 as model
from residence07_attic_primitives import bvh,independent_compare
from residence07_industrial import geometry_fingerprint,world


def sample_clearance(obstacles,steps):
    tree=bvh(obstacles);rows=[]
    for step in steps:
        gaps=[];missing=0
        for x,y in data.walking_samples(step):
            hit=tree.ray_cast(Vector((x,y,step['top']+.001)),Vector((0,0,1)),20)
            if hit[0] is None:missing+=1
            else:gaps.append(hit[3]+.001)
        rows.append({'step':step['index'],'minimum_m':min(gaps) if gaps else None,'missing':missing,'rays':len(gaps)})
    return rows


def main(require_renders=False):
    root=data.ROOT;cfg=data.CFG;report=root/cfg['report_directory'];receipt=json.loads((report/'modelo.json').read_text());checks=[]
    def check(name,value,details=None):
        row={'name':name,'passed':bool(value)}
        if details is not None:row['details']=details
        checks.append(row)
    check('modelo salvo reaberto',geo.sha(bpy.data.filepath)==receipt['blend_sha256'])
    check('biblioteca sem acesso descartado íntegra',geo.sha(root/cfg['base_blend'])==receipt['base_sha256'])
    check('modelo atual preservado',geo.sha(root/cfg['current_blend'])==receipt['current_sha256'])
    check('config e geradores',geo.sha(data.CONFIG)==receipt['config_sha256'] and all(geo.sha(root/p)==h for p,h in receipt['generators'].items()))
    check('cobertura forro e fundos preservados',model.states(model.PRESERVE)==receipt['preserved_geometry'])
    check('origem independente da cobertura e forro',not independent_compare(root/cfg['base_blend'],receipt['preserved_geometry']))
    body=bpy.data.collections['ATUAL_Arquitetura'];current={o.name:geometry_fingerprint(o) for o in body.objects}
    delta=independent_compare(root/cfg['current_blend'],current)
    check('arquitetura igual à casa atual, com quartos restaurados',not delta and current==receipt['body_geometry'],{'objects':len(current),'differences':delta})
    check('somente os quatro objetos do guarda anterior retirados',len(receipt['removed_guard'])==4 and all('guarda-corpo' in n or 'Corrimao hall' in n for n in receipt['removed_guard']))
    for wall in ['S-quarto-frente-circulacao','S-quarto-fundos-circulacao']:
        check('divisória preservada '+wall,any(o.get('wall_id')==wall for o in body.objects))
    oldsteps=sorted([o for o in bpy.data.collections['ATC5_Escada_Existente'].objects if o.get('stair_index')],key=lambda o:o['stair_index'])
    newsteps=sorted(bpy.data.collections['ATC5_Escada'].objects,key=lambda o:o['stair_index'])
    check('duas sequências de dezesseis pisos',len(oldsteps)==len(newsteps)==16)
    for old,new in zip(oldsteps,newsteps):
        av=[world(old)@v.co for v in old.data.vertices];bv=[world(new)@v.co for v in new.data.vertices]
        ax={(round(v.x,5),round(v.y,5)) for v in av};bx={(round(v.x,5),round(v.y,5)) for v in bv}
        dz=max(v.z for v in bv)-max(v.z for v in av)
        check('XY idêntico piso '+str(new['stair_index']),ax==bx,{'old_xy':sorted(ax),'new_xy':sorted(bx)})
        check('deslocamento exclusivamente vertical piso '+str(new['stair_index']),abs(dz-2.7)<1e-5,{'dz_m':dz})
    slabs=bpy.data.collections['ATC5_Laje'];forro=bpy.data.collections['ATC4_Forro'];tech=bpy.data.collections['ATC5_Tecnica']
    walls=[o for o in body.objects if o.get('wall_id')]
    gaps=sample_clearance([*slabs.objects,*forro.objects,*tech.objects,*walls],data.steps())
    check('altura livre na escada nova',all(r['minimum_m'] is not None and r['minimum_m']>=2.1 and r['missing']==0 for r in gaps),gaps)
    lower=[{**s,'top':s['top']-2.7} for s in data.steps()]
    existing_slabs=[o for o in body.objects if o.get('slab')]
    lowergaps=sample_clearance([*slabs.objects,*newsteps,*bpy.data.collections['ATC5_Espelhos'].objects,*existing_slabs,*walls],lower)
    check('altura da escada existente sob a nova',all(r['minimum_m'] is not None and r['minimum_m']>=2.1 and r['missing']==0 for r in lowergaps),lowergaps)
    floortree=bvh(slabs.objects)
    for x,y,present in [(5,.5,True),(4.3,3.7,True),(4.7,3.7,False),(4.3,2.6,False),(1.8,3.175,True),(3.7,2.6,True)]:
        hit=floortree.ray_cast(Vector((x,y,6)),Vector((0,0,-1)),1)
        check(f'vão e laje {x},{y}',(hit[0] is not None)==present)
    tank=bpy.data.collections['ATC_Reservatorio'];names=list(receipt['tank_before'])
    with bpy.data.libraries.load(str(root/cfg['base_blend']),link=False) as (src,dst):dst.objects=list(names)
    delta=Vector((-3.55,0,0));errors=[]
    for name,old in zip(names,dst.objects):
        actual=tank.objects[name]
        if old.type!=actual.type:errors.append(name);continue
        if old.type=='MESH':
            if len(old.data.vertices)!=len(actual.data.vertices) or any((a.co-b.co).length>1e-6 for a,b in zip(old.data.vertices,actual.data.vertices)):errors.append(name)
        a=world(actual);b=world(old);b.translation+=delta
        if max(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(4))>1e-5:errors.append(name)
    check('caixa e conexões transladadas somente 3,55 m em X',not errors,errors)
    box=next(o for o in tank.objects if o.get('capacity_liters')==1000)
    bbox=[world(box)@Vector(p) for p in box.bound_box];lo=[min(v[i] for v in bbox) for i in range(3)];hi=[max(v[i] for v in bbox) for i in range(3)]
    check('nova posição e capacidade da caixa',abs((lo[0]+hi[0])/2-1.8)<1e-5 and abs((lo[1]+hi[1])/2-3.175)<1e-5 and abs(lo[2]-5.45)<1e-5 and box['capacity_liters']==1000)
    check('caixa fora dos dois lances',hi[0]<4.1,{'tank_max_x':hi[0],'stair_min_x':4.1})
    tree=bvh(forro.objects);tankgaps=[]
    for i in range(9):
        for j in range(9):
            x=lo[0]+(hi[0]-lo[0])*i/8;y=lo[1]+(hi[1]-lo[1])*j/8
            hit=tree.ray_cast(Vector((x,y,hi[2])),Vector((0,0,1)),10)
            if hit[0] is not None:tankgaps.append(hit[3])
    check('folga da caixa até o forro',len(tankgaps)==81 and min(tankgaps)>.5,{'rays':len(tankgaps),'minimum_m':min(tankgaps) if tankgaps else None})
    # Mobiliário do estudo fora da nova sala técnica e abaixo do forro.
    furniture=[];bad=[]
    for o in bpy.data.collections['ATC_Mobiliario'].objects:
        bb=[world(o)@Vector(p) for p in o.bound_box]
        a=[min(v[i] for v in bb) for i in range(3)];b=[max(v[i] for v in bb) for i in range(3)]
        if a[0]<3.3 and b[0]>.15 and a[1]<4.35 and b[1]>2.1:bad.append(o.name)
        free=min(data.ceiling_z(x,y)-b[2] for x in [a[0],b[0]] for y in [a[1],b[1]])
        furniture.append({'object':o.name,'minimum_ceiling_gap_m':free})
    check('móveis fora da área técnica',not bad,bad)
    check('móveis e armários sob o forro',all(r['minimum_ceiling_gap_m']>=-.01 for r in furniture),furniture)
    check('conjunto exato de 48 cenas',set(bpy.data.scenes.keys())=={j['scene'] for j in receipt['jobs']} and len(receipt['jobs'])==48)
    for j in receipt['jobs']:
        scene=bpy.data.scenes[j['scene']]
        check('câmera '+j['id'],(scene.camera.location-Vector(j['pos'])).length<1e-4)
        check('destino '+j['id'],scene.render.filepath==str(root/j['file']))
        check('sem acesso antigo '+j['id'],not any(o.name.startswith('ATC3 U Piso') or 'helicoidal' in o.name for o in scene.objects))
    if require_renders:
        records=json.loads((report/'renders.json').read_text());check('48 renders finais',{r['id'] for r in records}=={j['id'] for j in receipt['jobs']})
        for r in records:check('imagem '+r['id'],not r['preview'] and r['blend_sha256']==receipt['blend_sha256'] and geo.sha(root/r['file'])==r['sha256'])
    scene=bpy.data.scenes['ATC5_01-referencia'];bpy.context.window.scene=scene;bpy.context.view_layer.update()
    anchors={'inicio':[3.8,3.7,.045],'hall':[3.8,2.6,2.745],'nova':[5.0,3.7,3.5],'saida':[3.65,2.6,5.445],'caixa':[1.8,3.175,6.2]}
    projected={n:list(world_to_camera_view(scene,scene.camera,Vector(p))) for n,p in anchors.items()}
    result={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'checks':checks,'all_passed':all(c['passed'] for c in checks),'blend_sha256':receipt['blend_sha256'],'renders_required':require_renders,'stair_clearance':gaps,'existing_stair_clearance':lowergaps,'tank_ceiling_clearance_m':min(tankgaps) if tankgaps else None,'hero_anchors':projected,'scope':'Geometria da proposta. Hall nominal 65 cm e estrutura/apoios/redes definitivas ainda dependem de projeto.'}
    (report/('validacao-completa.json' if require_renders else 'validacao-modelo.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('ATC5_AUDIT',len(checks),'PASSED' if result['all_passed'] else 'FAILED')
    for c in checks:
        if not c['passed']:print('FAIL',c)
    if not result['all_passed']:raise RuntimeError('Conferência v05 reprovada.')


if __name__=='__main__':main('--require-renders' in sys.argv)
