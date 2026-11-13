"""Estrutura colorida e instalações em 3D com paredes transparentes."""
import argparse
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
import residence07_geometry as geo
import residence07_studies_data as data
import residence07_studies_scene as s
import blender_primitives as g


def build():
    s.initialize();data.validate();graph=data.pipe_points();nodes={n['id']:n for n in graph['nodes']}
    networks={key:s.collection('INST_'+key) for key in s.COLORS}
    for i,edge in enumerate(graph['edges']):
        if edge['geometry']=='junction':continue
        a,b=nodes[edge['a']],nodes[edge['b']];system=edge['system'];nominal=edge['nominal_diameter_m'];display=max(nominal,.035)
        s.polyline('INST '+system+f' {i:03}',[a['xyz'],b['xyz']],display,s.M['EST Rede '+system],networks[system],
                   network_system=system,node_a=a['id'],node_b=b['id'],nominal_diameter_m=nominal,display_diameter_m=display,source=edge['source'])
    for node in graph['nodes']:
        if node['kind']=='junction':continue
        key=node['system'];col=networks[key];xyz=node['xyz'];mat=s.M['EST Rede '+key]
        if node['kind'] in ['panel','distribution']:s.box('INST '+node['id'],xyz,(.08,.28,.38),mat,col)
        elif node['kind']=='light':g.cylinder('INST '+node['id'],xyz,.11,.035,mat,col.name)
        elif node['kind'] in ['socket','switch','tv_phone']:s.box('INST '+node['id'],xyz,(.055,.10,.12),mat,col,.012)
        else:g.sphere('INST '+node['id'],xyz,(.055,)*3,mat,col.name)
    tankcol=s.collection('INST_Reservatorio');s.tank(tankcol)
    ghost=s.architectural_variant('ghost')
    # Vistas de pavimento usam subconjuntos da arquitetura e das redes em sua cota real.
    levels={}
    for level in [0,1]:
        col=s.collection('INST_Arquitetura_Piso_'+str(level));z0=level*2.7
        suffix='Terreo' if level==0 else 'Superior'
        originals={o.name for key in ['Paredes_','Piso_'] for o in bpy.data.collections['R07_'+key+suffix].objects}
        for obj in ghost.objects:
            if obj.get('study_source_object') in originals:col.objects.link(obj)
        levels[level]=col
    layer_levels={}
    for key,col in networks.items():
        for level in [0,1]:
            target=s.collection(f'INST_{key}_Piso_{level}')
            for obj in col.objects:
                if obj.type=='CURVE':
                    points=[Vector(p.co[:3]) for p in obj.data.splines[0].points]
                    low,high=level*2.7-.35,(level+1)*2.7-.05
                    a,b=points;delta=b-a;t0,t1=0.0,1.0
                    if abs(delta.z)<1e-8:
                        if not low<=a.z<=high:continue
                    else:
                        t0=max(0,min((low-a.z)/delta.z,(high-a.z)/delta.z));t1=min(1,max((low-a.z)/delta.z,(high-a.z)/delta.z))
                        if t1<=t0:continue
                    new=s.polyline(obj.name+' piso '+str(level),[tuple(a+delta*t0),tuple(a+delta*t1)],obj.data.bevel_depth*2,obj.data.materials[0],target,
                                   network_system=key,study_clipped_to_level=level,study_source_segment=obj.name)
                    continue
                else:zs=[obj.location.z]
                lo,hi=min(zs),max(zs)
                if hi>=level*2.7-.2 and lo<=(level+1)*2.7:target.objects.link(obj)
            layer_levels[key,level]=target
    structures={}
    for view in data.views():
        if view['kind']=='structure':
            # Mesmas posições, formas e cotas; apenas materiais próprios dessas cenas.
            import residence07_build as old
            group=s.collection('EST_'+view['id'])
            for key in old.scene_collections(view['mode']):
                if key in ['R07_Iluminacao','R07_Cameras']:continue
                wall='Paredes' in key or 'Corte_' in key;slab='Piso_' in key
                if key=='R07_Superior_Explodido':
                    for obj in bpy.data.collections[key].objects:
                        mat=s.M['EST Parede sálvia suave'] if 'Corte' in obj.name else s.M['EST Laje creme']
                        temp=s.collection('EST_TEMP_'+str(len(s.C)));temp.objects.link(obj)
                        s.copy_objects(temp,group,mat,prefix='COLOR ');temp.objects.unlink(obj)
                    continue
                s.copy_objects(bpy.data.collections[key],group,s.M['EST Parede sálvia suave' if wall else 'EST Laje creme' if slab else 'EST Escada areia'],prefix='COLOR ')
            structures[view['id']]=group;s.camera_scene(view,[group],data.output_path(view),prefix='COLOR_')
        else:
            level=view['level'];collections=[ghost if level is None else levels[level]]
            collections += [networks[k] if level is None else layer_levels[k,level] for k in view['systems']]
            if view['kind']=='tank' or (level is None and 'cold' in view['systems']):collections.append(tankcol)
            s.camera_scene(view,collections,data.output_path(view),prefix='INST_')
    s.finish_build('instalacoes',geo.ROOT/data.CFG['services_blend'],{'network_graph':graph,'palette':data.CFG['palette'],'tank':data.CFG['tank'],'source_notes':data.CFG['source_notes']})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--render-only',action='store_true');p.add_argument('--preview',action='store_true');p.add_argument('--only')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if args.render_only:s.render('instalacoes',args.preview,args.only)
    else:build()
