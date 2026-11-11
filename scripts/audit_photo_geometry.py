"""Testes de contradições fotográficas: implantação, eixo dos lances e visibilidade."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))

import bpy
import stairs_geometry
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
    spec=cfg['layout']['lavabo_door'];annotation=[cfg['user_layout_source']['path'],cfg['upper_layout_source']['path']]
    expected=Vector((*spec['start'],0))
    check('porta_lavabo_na_parede_confirmada_apos_reproporcao',door is not None and (door.matrix_world.translation-expected).length<.001,{'door':list(door.matrix_world.translation) if door else None,'expected':list(expected)},annotation)
    check('porta_lavabo_fechada_para_leitura',door is not None and abs(door.rotation_euler.z)<.001,{'rotation_z':door.rotation_euler.z if door else None,'opening_direction':'não informado'},annotation)
    first=bpy.data.objects.get('Degrau 01 granito');last=bpy.data.objects.get(f"Degrau {cfg['layout']['stairs']['first_steps']:02} granito")
    delta=last.matrix_world.translation-first.matrix_world.translation if first and last else Vector((0,1,0))
    check('primeiro_lance_transversal',abs(delta.y)<.02 and delta.x>.8,{'delta_first_to_seventh':list(delta)},['sala1.webp','sala4.webp'])
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
    for i in range(1,cfg['layout']['stairs']['first_steps']+1):
        obj=bpy.data.objects.get(f'Degrau {i:02} granito')
        if obj:
            point=obj.matrix_world.translation.copy();point.z+=.019;points.append(point)
    v=visibility('FOTO_Sala_Fundos',points,('Degrau ','Espelho fechado degrau','Espelho do degrau'))
    check('primeiro_lance_nao_exposto_na_vista_sala7',v['visible']==0,v,['sala7.webp'])
    v=visibility('FOTO_Detalhe_Escada',points,('Degrau ','Espelho fechado degrau','Espelho do degrau'))
    check('primeiro_lance_visivel_no_angulo_sala1',v['visible']>=3,v,['sala1.webp'])
    v=visibility('FOTO_Acesso_Lavabo',points,('Degrau ','Espelho fechado degrau','Espelho do degrau'))
    check('primeiro_lance_visivel_na_vista_do_acesso',v['visible']>=1,v,annotation)
    pane=bpy.data.objects.get('Janela cozinha vidro')
    if pane:
        center=pane.matrix_world.translation;wx=pane.dimensions.x
        points=[(center.x-wx*.40+wx*.80*i/12,center.y-.009,z) for i in range(13) for z in [1.40,1.72,2.05]]
    else:points=[]
    v=visibility('FOTO_Sala_Fundos',points,('Janela cozinha','Persiana cozinha'))
    check('janela_cozinha_visivel_pela_passagem',v['visible']>=2,v,['sala7.webp','cozinha2.webp'])
    door_point=((spec['start'][0]+spec['end'][0])/2,spec['start'][1],1.15)
    v=visibility('FOTO_Acesso_Lavabo',[door_point],('Porta lavabo folha',))
    check('porta_lavabo_visivel_pela_nova_passagem',v['visible']==1,v,annotation)
    room_parents=[o.name for o in bpy.data.objects if o.name.startswith(('AMBIENTE_quarto','AMBIENTE_suite','AMBIENTE_banho'))]
    check('quartos_implantados_conforme_croqui',set(room_parents)=={'AMBIENTE_suite','AMBIENTE_quarto_branco','AMBIENTE_quarto_azul','AMBIENTE_banho_suite','AMBIENTE_banho_social'},room_parents,[cfg['upper_layout_source']['path']])
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
            check('garagem_aberta_ate_divisao_lavabo',bool(name and name.startswith(('Lavabo divisão com garagem','Garagem parede posterior'))),{'hit':name,'hit_y':hit[1].y if hit[0] else None},source)
        grill=bpy.data.objects.get('CHURRASQUEIRA conforme croqui')
        check('churrasqueira_canto_fundos_esquerdo',grill is not None and grill.location.x<1 and grill.location.y>layout['bar']['counter_y'],list(grill.location) if grill else None,source)
        stools=[o for o in bpy.data.objects if o.name.startswith('BANQUETA_BAR_')]
        check('tres_banquetas_conforme_croqui',len(stools)==3,len(stools),source)
        if cfg.get('revision_number',2)>=4:
            correction=['config/planta-casa.json#user_correction'];stairs=layout['stairs'];ymin=stairs['return_y']-stairs['flight_width']/2;ymax=stairs['return_y']+stairs['flight_width']/2
            check('lavabo_sob_segundo_lance_e_patamar',abs(lavabo[2]-ymin)<1e-5 and abs(lavabo[3]-ymax)<1e-5 and lavabo[1]<=stairs['x_min']+stairs['run']+stairs['landing_depth']+1e-5,{'lavabo':lavabo,'second_flight_y':[ymin,ymax]},annotation)
            previous=json.loads((root/cfg['previous_delivery']['config']).read_text())['layout']['garage_extension_bounds']
            check('garagem_alinhada_ao_lavabo_reposicionado',garage[:3]==previous[:3] and abs(garage[3]-ymin)<1e-5,{'before':previous,'after':garage},annotation)
            violations=[]
            detail=bpy.data.scenes['CORTE_Lavabo_Escada']
            with bpy.context.temp_override(scene=detail,view_layer=detail.view_layers[0]):
                detail.view_layers[0].update();deps=bpy.context.evaluated_depsgraph_get()
                for obj in bpy.data.collections['AMB_lavabo'].objects:
                    if obj.type!='MESH':continue
                    evaluated=obj.evaluated_get(deps)
                    for v in evaluated.bound_box:
                        p=evaluated.matrix_world@Vector(v)
                        ceiling=stairs_geometry.return_ceiling(stairs,cfg['estimated_dimensions_m']['floor_height'],p.x)-.09
                        if p.x<lavabo[0]-.001 or p.x>lavabo[1]+.001 or p.y<lavabo[2]-.001 or p.y>lavabo[3]+.001 or p.z>ceiling+.001:violations.append(obj.name);break
            check('loucas_e_espelho_dentro_lavabo_abaixo_forro',not violations,violations,correction)
    if cfg.get('revision_number',2)>=5:
        ext=['exterior1.webp','exterior2.webp'];front=cfg['facade']['front_y']
        columns=[o for o in bpy.data.objects if o.name.startswith('Coluna frontal integrada')]
        check('fachada_sem_marquise_e_pilares_avancados',len(columns)==2 and all(o.location.y>=front-.10 for o in columns) and bpy.data.objects.get('Cobertura garagem — projeção estimada') is None,{'columns':[list(o.location) for o in columns]},ext)
        sides=[o for o in bpy.data.objects if o.name.startswith('Parede lateral contínua garagem') and o.type=='MESH']
        check('garagem_com_paredes_laterais_continuas',len(sides)==2 and all(o.dimensions.y>=abs(front)-.01 and o.dimensions.z>=2.69 for o in sides),[o.name for o in sides],ext)
        recessed=bpy.data.objects.get('Janela varanda vidro');flush=bpy.data.objects.get('Janela frontal superior vidro');net=bpy.data.objects.get('Rede de proteção varanda')
        check('varanda_recuada_com_rede',recessed is not None and flush is not None and net is not None and recessed.matrix_world.translation.y-flush.matrix_world.translation.y>.70,{'recessed_y':recessed.matrix_world.translation.y if recessed else None,'flush_y':flush.matrix_world.translation.y if flush else None},ext)
        check('janela_sala_com_grade',bpy.data.objects.get('Janela sala grade quadriculada') is not None,{},ext)
        wx0,wx1=cfg['facade']['small_window_x'];z0,z1=cfg['facade']['small_window_z'];rear=cfg['layout']['lavabo_bounds'][2]-.075
        v=visibility('FOTO_Fachada',[((wx0+wx1)/2,rear-.01,(z0+z1)/2)],('Janela posterior garagem','Janela pequena garagem'))
        check('janela_pequena_visivel_no_fundo_garagem',v['visible']>=1,v,['exterior2.webp'])
        tread_points=[]
        for i in range(1,cfg['layout']['stairs']['risers']+1):
            obj=bpy.data.objects.get(f'Degrau {i:02} granito')
            if obj:
                point=obj.matrix_world.translation.copy();point.z+=.019;tread_points.append(point)
        v=visibility('FOTO_Fachada',tread_points,('Degrau ','Espelho fechado degrau'))
        check('escada_oculta_na_vista_externa',bpy.data.scenes.get('FOTO_Fachada') is not None and v['visible']==0,v,ext)
        cooking=bpy.data.scenes.get('FOTO_Cozinha');hits=[]
        if cooking:
            with bpy.context.temp_override(scene=cooking,view_layer=cooking.view_layers[0]):
                cooking.view_layers[0].update();deps=bpy.context.evaluated_depsgraph_get()
                for obj in bpy.data.objects:
                    if not obj.name.startswith('Boca fogão'):continue
                    origin=obj.matrix_world.translation.copy();origin.z=1.2
                    hit=cooking.ray_cast(deps,origin,Vector((0,0,-1)),distance=.5);hits.append(hit[4].name if hit[0] else 'none')
        check('bancada_nao_atravessa_fogao',len(hits)==4 and all(name.startswith('Boca fogão') for name in hits),hits,['cozinha1.webp'])
        washing=bpy.data.scenes.get('FOTO_Lavanderia');washer_hit=None
        if washing:
            with bpy.context.temp_override(scene=washing,view_layer=washing.view_layers[0]):
                washing.view_layers[0].update();deps=bpy.context.evaluated_depsgraph_get();yy=cfg['layout']['laundry_bounds'][3]-.34
                hit=washing.ray_cast(deps,Vector((5.21,yy,1.3)),Vector((0,0,-1)),distance=.6);washer_hit=hit[4].name if hit[0] else None
        check('lavadora_superior_livre_de_granito',washer_hit is not None and washer_hit.startswith('Tampa lavadora superior'),washer_hit,['lavanderia1.webp'])
        left=bpy.data.objects.get('Bancada lavanderia lateral esquerda')
        check('retorno_lavanderia_no_lado_esquerdo',left is not None and left.matrix_world.translation.x<3.6,list(left.matrix_world.translation) if left else None,['lavanderia1.webp'])
        approved=json.loads((root/cfg['previous_delivery']['config']).read_text())
        keys=['spine_x','entry_diagonal','laundry_bounds','bar']
        check('partes_fora_do_ajuste_preservadas',all(cfg['layout'][key]==approved['layout'][key] for key in keys) and cfg['room_studies']==approved['room_studies'],keys,annotation)
        view=bpy.data.scenes['PLANTA_Terreo_Portas']
        with bpy.context.temp_override(scene=view,view_layer=view.view_layers[0]):
            view.view_layers[0].update();deps=bpy.context.evaluated_depsgraph_get()
            leaf=bpy.data.objects.get('Porta lavabo folha')
            check('folha_da_porta_na_parede_horizontal',leaf is not None and leaf.dimensions.x>.65 and leaf.dimensions.y<.06,{'dimensions':list(leaf.dimensions) if leaf else None},annotation)
            hit=view.ray_cast(deps,Vector((s+.25,(lavabo[2]+lavabo[3])/2-.035,1)),Vector((-1,0,0)),distance=.5)
            check('antigo_vao_lateral_fechado',hit[0] and hit[4].name.startswith('ESPINHA_'),{'hit':hit[4].name if hit[0] else None},annotation)
            for name,start,direction,distance,allow in [
                ('passagem_da_sala_livre',(s-.2,spec['start'][1]+.4,.20),(1,0,0),.8,None),
                ('aproximacao_da_nova_porta_livre',(door_point[0],spec['start'][1]+.7,1),(0,-1,0),.8,'Porta lavabo folha')]:
                hit=view.ray_cast(deps,Vector(start),Vector(direction),distance=distance)
                ok=not hit[0] if allow is None else hit[0] and hit[4].name.startswith(allow)
                check(name,ok,{'hit':hit[4].name if hit[0] else None},annotation)
        # Conferir também com os degraus presentes, não só com a escada oculta.
        view=bpy.data.scenes['PLANTA_Terreo_Cotas']
        with bpy.context.temp_override(scene=view,view_layer=view.view_layers[0]):
            view.view_layers[0].update();deps=bpy.context.evaluated_depsgraph_get()
            hit=view.ray_cast(deps,Vector((door_point[0],spec['start'][1]+.7,1)),Vector((0,-1,0)),distance=.8)
            check('acesso_nao_bloqueado_por_degraus',hit[0] and hit[4].name.startswith('Porta lavabo folha'),{'hit':hit[4].name if hit[0] else None},annotation)
    if cfg['revision_number']>=7:
        view=bpy.data.scenes['FOTO_Acesso_Lavabo']
        with bpy.context.temp_override(scene=view,view_layer=view.view_layers[0]):
            view.view_layers[0].update();deps=bpy.context.evaluated_depsgraph_get()
            approach_y=spec['start'][1]+.4;kitchen_y=cfg['layout']['kitchen']['bounds'][2]+1.0
            route=[(door_point[0],kitchen_y,1),(2.9,kitchen_y,1),(2.9,approach_y,1),(door_point[0],approach_y,1)]
            hits=[]
            for a,b in zip(route,route[1:]):
                ray=Vector(b)-Vector(a);hit=view.ray_cast(deps,Vector(a),ray.normalized(),distance=ray.length)
                if hit[0]:hits.append(hit[4].name)
            hit=view.ray_cast(deps,Vector(route[-1]),Vector((0,-1,0)),distance=.6)
            check('cozinha_conectada_a_porta_do_lavabo_pela_sala',not hits and hit[0] and hit[4].name.startswith('Porta lavabo folha'),{'obstructions':hits,'door_hit':hit[4].name if hit[0] else None,'route':route},annotation)
            hit=view.ray_cast(deps,Vector((door_point[0],spec['start'][1]+.45,2.2)),Vector((0,0,1)),distance=1)
            check('passagem_com_laje_sobre_a_area_liberada',hit[0] and hit[4].name.startswith('Laje superior') and abs(hit[1].z-(cfg['estimated_dimensions_m']['floor_height']-.20))<.02,{'hit':hit[4].name if hit[0] else None,'location':list(hit[1]) if hit[0] else None},annotation)
    report={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'blend':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'baseline':args.baseline,'checks':results,'all_passed':all(r['passed'] for r in results.values()),'scope':'Detecção de contradições discretas e visibilidade. Não prova equivalência métrica, fotográfica ou a implantação real do superior.'}
    folder=root/'relatorios/atual';folder.mkdir(exist_ok=True)
    out=folder/('auditoria-antes.json' if args.baseline else 'auditoria-depois.json');out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    for name,result in results.items():print(('PASS' if result['passed'] else 'FAIL'),name,flush=True)
    if not report['all_passed'] and not args.baseline:raise SystemExit(1)


if __name__=='__main__':main()
