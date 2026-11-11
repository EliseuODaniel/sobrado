"""Testes de contradições fotográficas: implantação, eixo dos lances e visibilidade."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view


def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=Path('.'));p.add_argument('--baseline',action='store_true');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    root=args.project_root.resolve();cfg=json.loads((root/'config/planta-casa.json').read_text());s=cfg['layout']['spine_x']
    results={}
    def check(name,ok,detail,photos):results[name]={'passed':bool(ok),'detail':detail,'references':photos}
    tv=bpy.data.objects.get('TV_E_RACK_original')
    check('tv_na_parede_interna_lateral',tv is not None and abs(tv.matrix_world.translation.x-s)<.12,{'tv_x':tv.matrix_world.translation.x if tv else None,'spine_x':s},['sala4.webp','sala7.webp'])
    door=bpy.data.objects.get('Porta lavabo — abrir/girar')
    check('porta_lavabo_na_mesma_face',door is not None and abs(door.matrix_world.translation.x-s)<.025,{'door':list(door.matrix_world.translation) if door else None},['sala2.webp','sala4.webp'])
    check('porta_lavabo_fechada_como_na_foto',door is not None and abs(door.rotation_euler.z)<.001,{'rotation_z':door.rotation_euler.z if door else None},['sala4.webp'])
    first=bpy.data.objects.get('Degrau 01 granito');last=bpy.data.objects.get('Degrau 09 granito')
    delta=last.matrix_world.translation-first.matrix_world.translation if first and last else Vector((0,1,0))
    check('primeiro_lance_transversal',abs(delta.y)<.02 and delta.x>.8,{'delta_first_to_ninth':list(delta)},['sala1.webp','sala4.webp'])
    mirror=bpy.data.objects.get('Espelho original sala');inner=cfg['estimated_dimensions_m']['wall_thickness']/2
    # O corte axonométrico exclui o espelho junto com sua parede. Avaliar na
    # cena fotográfica evita ler a matriz ainda não atualizada desse objeto.
    mirror_scene=bpy.data.scenes.get('FOTO_Sala_Fundos',bpy.context.scene)
    with bpy.context.temp_override(scene=mirror_scene,view_layer=mirror_scene.view_layers[0]):
        mirror_scene.view_layers[0].update()
        deps=bpy.context.evaluated_depsgraph_get()
        evaluated_mirror=mirror.evaluated_get(deps) if mirror else None
        mirror_front=evaluated_mirror.matrix_world.translation.x+evaluated_mirror.dimensions.x/2 if evaluated_mirror else -1
    check('espelho_fora_do_volume_da_parede',mirror_front>inner+.002,{'mirror_front_x':mirror_front,'wall_inside_x':inner},['sala7.webp'])
    stone=next((o for o in bpy.data.objects if o.name.startswith('Pedra bar original')),None)
    stone_front=stone.matrix_world.translation.y-stone.dimensions.y/2 if stone else 100
    back_wall=next((o for o in bpy.data.objects if o.type=='MESH' and o.get('parede') and 'fundo bar' in o.name.lower()),None)
    wall_front=back_wall.matrix_world.translation.y-back_wall.dimensions.y/2 if back_wall else -1
    check('pedra_exposta_na_frente_da_parede',stone_front<wall_front-.002,{'stone_front_y':stone_front,'wall_front_y':wall_front},['area3.webp'])
    def visibility(scene_name,points,allowed):
        scene=bpy.data.scenes.get(scene_name)
        if not scene:return {'visible':0,'total':len(points),'hits':['scene missing']}
        vis=0;hits=[];ndcs=[]
        with bpy.context.temp_override(scene=scene,view_layer=scene.view_layers[0]):
            deps=bpy.context.evaluated_depsgraph_get();scene.view_layers[0].update()
            origin=scene.camera.matrix_world.translation
            for point in points:
                point=Vector(point);ndc=world_to_camera_view(scene,scene.camera,point);ndcs.append(list(ndc))
                if not(0<=ndc.x<=1 and 0<=ndc.y<=1 and ndc.z>0):hits.append('out_of_frame');continue
                ray=point-origin;result=scene.ray_cast(deps,origin,ray.normalized(),distance=ray.length+.15)
                name=result[4].name if result[0] else 'no_hit';hits.append(name)
                if any(name.startswith(prefix) for prefix in allowed):vis+=1
        return {'visible':vis,'total':len(points),'hits':hits,'ndc':ndcs}
    points=[]
    for i in range(1,10):
        obj=bpy.data.objects.get(f'Degrau {i:02} granito')
        if obj:
            point=obj.matrix_world.translation.copy();point.z+=.019;points.append(point)
    v=visibility('FOTO_Sala_Fundos',points,('Degrau ','Espelho fechado degrau','Espelho do degrau'))
    check('primeiro_lance_nao_exposto_na_vista_sala7',v['visible']==0,v,['sala7.webp'])
    v=visibility('FOTO_Detalhe_Escada',points,('Degrau ','Espelho fechado degrau','Espelho do degrau'))
    check('primeiro_lance_visivel_no_angulo_sala1',v['visible']>=3,v,['sala1.webp'])
    v=visibility('FOTO_Sala_Frente',points,('Degrau ','Espelho fechado degrau','Espelho do degrau'))
    check('primeiro_lance_visivel_na_vista_sala4',v['visible']>=1,v,['sala4.webp'])
    pane=bpy.data.objects.get('Janela cozinha vidro')
    if pane:
        center=pane.matrix_world.translation;wx=pane.dimensions.x
        points=[(center.x-wx*.40+wx*.80*i/12,center.y-.009,z) for i in range(13) for z in [1.40,1.72,2.05]]
    else:points=[]
    v=visibility('FOTO_Sala_Fundos',points,('Janela cozinha','Persiana cozinha'))
    check('janela_cozinha_visivel_pela_passagem',v['visible']>=2,v,['sala7.webp','cozinha2.webp'])
    point=(s,3.185,1.15)
    v=visibility('FOTO_Sala_Frente',[point],('Porta lavabo folha',))
    check('porta_lavabo_visivel_entre_tv_e_escada',v['visible']==1,v,['sala4.webp'])
    room_parents=[o.name for o in bpy.data.objects if o.name.startswith(('AMBIENTE_quarto','AMBIENTE_suite','AMBIENTE_banho'))]
    check('superior_sem_adjacencias_inventadas',not room_parents,room_parents,['quartosuite1.webp','quartoazul1.webp','quartobranco1.webp'])
    if cfg.get('revision_number',2)>=3:
        source=[cfg['user_layout_source']['path']];layout=cfg['layout']
        diagonal=bpy.data.objects.get('ENTRADA_DIAGONAL conforme croqui')
        check('entrada_em_diagonal',diagonal is not None and .15<abs(diagonal.rotation_euler.z)<1.4,
              {'angle_radians':diagonal.rotation_euler.z if diagonal else None},source)
        garage=layout['garage_extension_bounds'];lavabo=layout['lavabo_bounds'];laundry=layout['laundry_bounds'];kitchen=layout['kitchen']['bounds']
        check('lavabo_atras_da_continuacao_garagem',abs(lavabo[2]-garage[3])<1e-5 and lavabo[0]>=garage[0] and lavabo[1]<=garage[1],{'garage':garage,'lavabo':lavabo},source)
        check('lavanderia_imediatamente_atras_cozinha',laundry[:2]==kitchen[:2] and laundry[2]==kitchen[3],{'laundry':laundry,'kitchen':kitchen},source)
        check('fundos_churrasqueira_lavanderia_alinhados',abs(layout['bar']['back_y']-laundry[3])<.001,{'bar_back':layout['bar']['back_y'],'laundry_back':laundry[3]},source)
        scene=bpy.data.scenes['PLANTA_Terreo_Cotas']
        with bpy.context.temp_override(scene=scene,view_layer=scene.view_layers[0]):
            scene.view_layers[0].update();deps=bpy.context.evaluated_depsgraph_get()
            ay0,ay1=layout['laundry_access_y'];y=(ay0+ay1)/2
            hit=scene.ray_cast(deps,Vector((s-.3,y,1)),Vector((1,0,0)),distance=.6)
            check('passagem_lateral_lavanderia_livre',not hit[0],{'hit':hit[4].name if hit[0] else None},source)
            hit=scene.ray_cast(deps,Vector(((garage[0]+garage[1])/2,-1,1)),Vector((0,1,0)),distance=4)
            name=hit[4].name if hit[0] else None
            check('garagem_aberta_ate_divisao_lavabo',bool(name and name.startswith('Lavabo divisão com garagem')),{'hit':name,'hit_y':hit[1].y if hit[0] else None},source)
        grill=bpy.data.objects.get('CHURRASQUEIRA conforme croqui')
        check('churrasqueira_canto_fundos_esquerdo',grill is not None and grill.location.x<1 and grill.location.y>layout['bar']['counter_y'],list(grill.location) if grill else None,source)
        stools=[o for o in bpy.data.objects if o.name.startswith('BANQUETA_BAR_')]
        check('tres_banquetas_conforme_croqui',len(stools)==3,len(stools),source)
        if cfg.get('revision_number',2)>=4:
            correction=['config/planta-casa.json#user_correction'];stairs=layout['stairs'];ymin=stairs['return_y']-stairs['flight_width']/2;ymax=stairs['return_y']+stairs['flight_width']/2
            check('lavabo_na_projecao_segundo_lance',abs(lavabo[2]-ymin)<1e-5 and abs(lavabo[3]-ymax)<1e-5 and lavabo[1]<=stairs['x_min']+stairs['run']+1e-5,{'lavabo':lavabo,'second_flight_y':[ymin,ymax]},correction)
            previous=json.loads((root/'projeto/versoes/revisao-04-antes/config/planta-casa.json').read_text())['layout']['garage_extension_bounds']
            check('garagem_ocupa_antiga_area_lavabo',garage[3]>previous[3]+1 and abs(garage[3]-ymin)<1e-5,{'before':previous,'after':garage},correction)
            violations=[]
            detail=bpy.data.scenes['CORTE_Lavabo_Escada']
            with bpy.context.temp_override(scene=detail,view_layer=detail.view_layers[0]):
                detail.view_layers[0].update();deps=bpy.context.evaluated_depsgraph_get()
                for obj in bpy.data.collections['AMB_lavabo'].objects:
                    if obj.type!='MESH':continue
                    evaluated=obj.evaluated_get(deps)
                    for v in evaluated.bound_box:
                        p=evaluated.matrix_world@Vector(v)
                        ratio=max(0,min(1,(p.x-stairs['x_min'])/stairs['run']))
                        ceiling=cfg['estimated_dimensions_m']['floor_height']*(1-ratio/2)-.25
                        if p.x<lavabo[0]-.001 or p.x>lavabo[1]+.001 or p.y<lavabo[2]-.001 or p.y>lavabo[3]+.001 or p.z>ceiling+.001:violations.append(obj.name);break
            check('loucas_e_espelho_dentro_lavabo_abaixo_forro',not violations,violations,correction)
    report={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'blend':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'baseline':args.baseline,'checks':results,'all_passed':all(r['passed'] for r in results.values()),'scope':'Detecção de contradições discretas e visibilidade. Não prova equivalência métrica, fotográfica ou a implantação real do superior.'}
    folder=root/'relatorios'/f"revisao-{cfg.get('revision_number',2):02d}";folder.mkdir(exist_ok=True)
    out=folder/('auditoria-antes.json' if args.baseline else 'auditoria-depois.json');out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    for name,result in results.items():print(('PASS' if result['passed'] else 'FAIL'),name,flush=True)
    if not report['all_passed'] and not args.baseline:raise SystemExit(1)


if __name__=='__main__':main()
