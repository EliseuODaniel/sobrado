"""Conferir contorno comum e coplanaridade dos fundos pela geometria salva."""
import bpy
from mathutils import Vector


def audit(cfg):
    checks={};scene=bpy.data.scenes['FOTO_Chegada_Escada'];d=cfg['estimated_dimensions_m']
    expected=cfg.get('main_volume',{}).get('bounds',[0,d['width'],cfg['facade']['front_y'],cfg['layout']['kitchen']['window_y']])
    def check(name,ok,detail):checks[name]={'passed':bool(ok),'detail':detail}
    with bpy.context.temp_override(scene=scene,view_layer=scene.view_layers[0]):
        scene.view_layers[0].update();deps=bpy.context.evaluated_depsgraph_get()
        def points(obj):
            evaluated=obj.evaluated_get(deps)
            return [evaluated.matrix_world@vertex.co for vertex in obj.data.vertices]
        def rectangle(obj):
            p=points(obj);return [min(v.x for v in p),max(v.x for v in p),min(v.y for v in p),max(v.y for v in p)]
        upper=[rectangle(o) for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Laje superior')]
        lower_names={'Laje sala — dimensões estimadas','Laje faixa lateral','Garagem sob volume superior','Garagem continuação direita'}
        lower=[rectangle(bpy.data.objects[name]) for name in lower_names]
        def extent(rects):return [min(r[0] for r in rects),max(r[1] for r in rects),min(r[2] for r in rects),max(r[3] for r in rects)]
        a,b=extent(lower),extent(upper)
        check('mesmo_contorno_do_corpo_principal',all(abs(x-y)<1e-4 and abs(y-z)<1e-4 for x,y,z in zip(a,b,expected)),{'terreo':a,'superior':b,'expected':expected})
        holes=cfg['layout']['stair_holes'];xs=sorted({round(v,5) for r in lower+upper+holes+[expected] for v in r[:2] if expected[0]-1e-5<=v<=expected[1]+1e-5});ys=sorted({round(v,5) for r in lower+upper+holes+[expected] for v in r[2:] if expected[2]-1e-5<=v<=expected[3]+1e-5})
        def inside(x,y,rects):return any(r[0]-1e-5<x<r[1]+1e-5 and r[2]-1e-5<y<r[3]+1e-5 for r in rects)
        differences=[];count=0
        for xa,xb in zip(xs,xs[1:]):
            for ya,yb in zip(ys,ys[1:]):
                if xb-xa<1e-4 or yb-ya<1e-4:continue
                x,y=(xa+xb)/2,(ya+yb)/2;count+=1
                if not inside(x,y,lower):differences.append(['ground_missing',x,y])
                wanted=not inside(x,y,holes)
                if inside(x,y,upper)!=wanted:differences.append(['upper_coverage',x,y,wanted])
        check('cobertura_das_lajes_sem_faixas_ausentes',not differences,{'cells_tested':count,'differences':differences,'upper_stair_voids':holes})
        rear_upper=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('S1 limite posterior')]
        rear_lower=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Parede janela cozinha') and o.get('parede')]
        def faces(objects):return {o.name:max(v.y for v in points(o)) for o in objects}
        au,al=faces(rear_upper),faces(rear_lower);plane=expected[3]+d['wall_thickness']/2
        check('fundos_wcs_quarto_coplanares_com_cozinha',bool(au and al) and all(abs(v-plane)<1e-4 for v in list(au.values())+list(al.values())),{'exterior_face_upper':au,'exterior_face_kitchen':al,'expected_exterior_face_y':plane,'axis_y':expected[3]})
    return {'checks':checks,'all_passed':all(c['passed'] for c in checks.values()),'scope':'Contorno das lajes e face posterior do corpo principal. Não inclui pátio, anexos térreos, acabamentos salientes ou aprovação estrutural.'}
