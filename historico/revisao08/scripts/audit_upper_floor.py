"""Verificação geométrica independente da escada e do superior proposto."""
import json
from pathlib import Path
import bpy
from mathutils import Vector


def audit(cfg):
    result={}
    def check(name,passed,detail):result[name]={'passed':bool(passed),'detail':detail}
    scene=bpy.data.scenes['FOTO_Chegada_Escada']
    with bpy.context.temp_override(scene=scene,view_layer=scene.view_layers[0]):
        scene.view_layers[0].update();deps=bpy.context.evaluated_depsgraph_get()
        steps=sorted([o for o in bpy.data.objects if o.get('step_index')],key=lambda o:o['step_index'])
        phases={phase:[o for o in steps if o.get('lance')==phase] for phase in [1,'curva',2]}
        check('contagens_7_curva_4',len(phases[1])==7 and len(phases[2])==4 and len(phases['curva'])==cfg['layout']['stairs']['turn_steps'],{str(p):len(v) for p,v in phases.items()})
        def vertices(o):return [o.evaluated_get(deps).matrix_world@v.co for v in o.data.vertices]
        verts=[vertices(o) for o in steps]
        tops=[max(v.z for v in points) for points in verts]
        rise=cfg['estimated_dimensions_m']['floor_height']/len(steps)
        check('alturas_continuas_ate_piso_superior',all(abs(z-(i+1)*rise)<1e-4 for i,z in enumerate(tops)),tops)
        def ext(objects):
            points=[v for o in objects for v in vertices(o)]
            return [min(v.x for v in points),max(v.x for v in points)]
        lower,upper=ext(phases[1]),ext(phases[2])
        y_first=min(v.y for o in phases[1] for v in vertices(o));y_final=max(v.y for o in phases[2] for v in vertices(o))
        check('lances_encostados_sem_faixa_intermediaria',abs(y_first-y_final)<1e-4,{'first_south_y':y_first,'final_north_y':y_final,'gap_m':y_first-y_final})
        check('lance_final_mais_curto_e_chega_antes_do_inicial',upper[1]-upper[0]<lower[1]-lower[0] and upper[0]>lower[0]+.3,{'first_x':lower,'final_x':upper})
        def top_edges(points):
            z=max(v.z for v in points);p=[(v.x,v.y) for v in points if abs(v.z-z)<1e-5]
            return list(zip(p,p[1:]+p[:1]))
        def shared(a,b,c,d):
            u=Vector((b[0]-a[0],b[1]-a[1]));v=Vector((c[0]-a[0],c[1]-a[1]));w=Vector((d[0]-a[0],d[1]-a[1]))
            if u.length<1e-5:return 0
            if abs(u.x*v.y-u.y*v.x)>1e-4 or abs(u.x*w.y-u.y*w.x)>1e-4:return 0
            axis=u.normalized();t0=v.dot(axis);t1=w.dot(axis)
            return max(0,min(u.length,max(t0,t1))-max(0,min(t0,t1)))
        gaps=[]
        for i,(a,b) in enumerate(zip(verts,verts[1:])):
            overlap=max(shared(*e,*f) for e in top_edges(a) for f in top_edges(b))
            if overlap<.15:gaps.append(i+1)
        check('degraus_consecutivos_sem_lacunas_no_plano',not gaps,gaps)
        clearances=[]
        for points in verts[:7]:
            center=sum(points,Vector())/len(points);center.z=max(v.z for v in points)+.01
            hit=scene.ray_cast(deps,center,Vector((0,0,1)),distance=2.7)
            if hit[0] and hit[4].name.startswith('Laje superior'):clearances.append(hit[1].z-center.z)
        check('laje_sobre_degraus_baixos_sem_colisao_de_altura',len(clearances)==3 and min(clearances)>2.0,{'clearances_m':clearances,'scope':'folga no estudo, não verificação normativa'})
        x=upper[0]-.03;y=cfg['layout']['stairs']['return_y'];z=cfg['estimated_dimensions_m']['floor_height']
        hit=scene.ray_cast(deps,Vector((x,y,z+.1)),Vector((0,0,-1)),distance=.5)
        check('chegada_ligada_a_laje',hit[0] and hit[4].name.startswith('Laje superior') and abs(hit[1].z-z)<.02,{'hit':hit[4].name if hit[0] else None,'position':list(hit[1]) if hit[0] else None})
        hall_hit=scene.ray_cast(deps,Vector((4.2,4.08,z+.1)),Vector((0,0,-1)),distance=.4)
        check('hall_ampliado_tem_laje_sobre_primeiro_lance',hall_hit[0] and hall_hit[4].name.startswith('Laje superior') and abs(hall_hit[1].z-z)<.02,{'point':[4.2,4.08],'hit':hall_hit[4].name if hall_hit[0] else None,'height':hall_hit[1].z if hall_hit[0] else None})
        routes={'suite':[(4.11,3.22),(3.3,3.3),(2.45,3.25)],'frente':[(4.11,3.22),(3.4,2.5)],'fundos':[(4.11,3.22),(2.95,4.05),(3.38,4.05),(3.38,4.95)]}
        failures=[]
        for key,route in routes.items():
            for a,b in zip(route,route[1:]):
                origin=Vector((*a,z+1.05));ray=Vector((*b,z+1.05))-origin
                hit=scene.ray_cast(deps,origin,ray.normalized(),distance=ray.length)
                if hit[0]:failures.append([key,hit[4].name])
            for p in route:
                hit=scene.ray_cast(deps,Vector((*p,z+.08)),Vector((0,0,-1)),distance=.25)
                if not hit[0]:failures.append([key,'sem laje',p])
        check('circulacao_conecta_tres_quartos_sem_parede_ou_vao',not failures,{'routes':routes,'failures':failures})
        positions={key:list(bpy.data.objects[name].matrix_world.translation) for key,name in [('suite','Cama suíte'),('frente','Cama quarto frente'),('fundos','Beliche quarto fundos')]}
        check('camas_nas_posicoes_relativas_confirmadas',positions['suite'][0]<2.8 and positions['suite'][1]<2.85 and positions['frente'][0]>2.8 and positions['frente'][1]<2.79 and positions['fundos'][0]>2.55 and positions['fundos'][1]>5.5,positions)
        bounds_errors=[]
        for r in cfg['rooms']:
            if r['level']!=1:continue
            x0,x1,y0,y1=r['bounds']
            if x0<0 or x1>5.6 or y0<cfg['estimated_dimensions_m']['upper_front_y'] or y1>cfg['estimated_dimensions_m']['upper_back_y']:bounds_errors.append(r['id'])
            for hole in cfg['layout']['stair_holes']:
                area=max(0,min(x1,hole[1])-max(x0,hole[0]))*max(0,min(y1,hole[3])-max(y0,hole[2]))
                if area>1e-5:bounds_errors.append([r['id'],'intersecta vão',area])
        check('quartos_e_banheiros_dentro_envoltoria_fora_vao',not bounds_errors,bounds_errors)
        bathroom_routes={'suite':[(.85,3.55),(.85,4.15)],'social':[(3.35,4.25),(2.45,4.25)]}
        bathroom_failures=[]
        for key,route in bathroom_routes.items():
            a,b=route;origin=Vector((*a,z+1.05));ray=Vector((*b,z+1.05))-origin
            hit=scene.ray_cast(deps,origin,ray.normalized(),distance=ray.length)
            if hit[0]:bathroom_failures.append([key,hit[4].name])
        check('acessos_wcs_pelos_lados_do_novo_croqui',not bathroom_failures,{'routes':bathroom_routes,'failures':bathroom_failures})
        suite_wc=next(r for r in cfg['rooms'] if r['id']=='banho_suite')['bounds'];social_wc=next(r for r in cfg['rooms'] if r['id']=='banho_social')['bounds']
        check('wcs_paralelos_na_faixa_esquerda_sem_area_inventada',suite_wc[2:]==social_wc[2:] and abs(suite_wc[1]-social_wc[0])<1e-5 and social_wc[1]<=2.8 and cfg['upper_layout']['unresolved_bounds'] is None,{'wc_suite':suite_wc,'wc_social':social_wc})
        check('banheiros_marcados_como_hipotese',not cfg['upper_layout']['bathrooms_confirmed'] and all('HIPÓTESE' in bpy.data.objects['Rótulo superior '+k].data.body for k in ['banho_suite','banho_social']),['banho_suite','banho_social'])
    return {'checks':result,'all_passed':all(v['passed'] for v in result.values()),'scope':'Conectividade e coerência do estudo aproximado; não certifica medidas ou execução.'}
