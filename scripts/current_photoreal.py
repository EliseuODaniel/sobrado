"""Construção independente da casa atual fiel às fotos; não modifica a fonte."""
import argparse
import datetime as dt
import json
import math
from pathlib import Path
import sys
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import blender_primitives as g
import current_photoreal_data as data
import current_photoreal_materials as materials
import current_photoreal_geometry as geo
import current_photoreal_furniture as furniture
import current_photoreal_details as details
import current_photoreal_exterior as exterior
from residence07_industrial import geometry_fingerprint

ROOT,CFG,REPORT=data.ROOT,data.CFG,data.REPORT

def protected():
    # Esquadrias copiadas sem pais são reparadas contra o modelo oficial, em recibo separado.
    objects={o for key in CFG['protected_collections'] for o in bpy.data.collections[key].all_objects}
    return {o.name:geometry_fingerprint(o) for o in sorted(objects,key=lambda o:o.name)
            if not (o.name.startswith('ATUAL BASE ') and o.name.removeprefix('ATUAL BASE ') in OFFICIAL_NAMES)}

OFFICIAL_NAMES={r['name'] for r in json.loads((REPORT/'esquadrias-originais.json').read_text())} if (REPORT/'esquadrias-originais.json').exists() else set()

def world():
    w=bpy.data.worlds.new('FIEL2 Luz natural');w.use_nodes=True;n,l=w.node_tree.nodes,w.node_tree.links;n.clear()
    bg=n.new('ShaderNodeBackground');bg.inputs['Strength'].default_value=.45
    env=n.new('ShaderNodeTexEnvironment')
    manifest=json.loads((ROOT/'assets/fotorrealismo-industrial/manifesto.json').read_text())
    entry=next(r for r in manifest['records'] if r['asset']=='garden_nook' and r['channel']=='hdri')
    assert data.sha(ROOT/entry['path'])==entry['sha256'];im=bpy.data.images.load(str(ROOT/entry['path']),check_existing=True);im.pack();env.image=im
    coord=n.new('ShaderNodeTexCoord');mp=n.new('ShaderNodeMapping');mp.inputs['Rotation'].default_value.z=1.25
    l.new(coord.outputs['Generated'],mp.inputs['Vector']);l.new(mp.outputs[0],env.inputs[0]);l.new(env.outputs[0],bg.inputs[0]);out=n.new('ShaderNodeOutputWorld');l.new(bg.outputs[0],out.inputs[0]);return w

def lights():
    c=geo.col('Iluminacao');g.C['Iluminacao']=c
    def area(name,pos,target,watts,size,color=(1,.84,.66),kind='AREA'):
        if kind=='SUN':
            ld=bpy.data.lights.new('FIEL2 '+name,'SUN');ld.energy=watts;ld.color=color
            o=bpy.data.objects.new(ld.name,ld);c.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
        else:o=g.light('FIEL2 '+name,pos,watts,color,kind,target,size)
        o['fixture_reference']=name
        if kind=='AREA':
            o.visible_camera=False;o.visible_glossy=False;o.visible_transmission=False
        return o
    area('Janela sala',(1.50,.11,1.70),(1.55,4.0,1.10),110,1.6,(.87,.93,1))
    area('Rebate difuso do ceu no bar',(1.65,8.0,2.70),(1.65,10.1,1.70),85,2.0,(.92,.96,1))
    area('Cobertura vidro',(1.60,8.80,3.06),(1.6,8.9,.5),160,2.4,(.90,.95,1))
    area('Janela cozinha',(4.72,7.11,1.70),(4.65,5.4,1),70,1.5,(.87,.93,1))
    area('Janela lavanderia',(4.9,10.30,1.65),(4.8,8.9,.6),65,1.5,(.87,.93,1))
    area('Janela suite',(1.6,-.47,4.2),(1.5,2.0,3.7),110,1.7,(.90,.95,1))
    area('Janela quarto branco',(4.75,-1.10,4.2),(5.25,1.2,3.5),110,1.5,(.90,.95,1))
    area('Janela quarto azul',(4.75,7.11,4.2),(4.7,5.4,3.6),100,1.5,(.90,.95,1))
    for name,pos,target,w,size in [
        ('Pendente jantar',(1.6,4.50,2.10),(1.6,4.5,.7),35,.45),
        ('Plafon sala',(1.60,1.70,2.51),(1.6,1.70,.3),25,.35),
        ('Plafon cozinha',(4.80,5.75,2.51),(4.80,5.75,.3),40,.6),
        ('Plafon hall',(4.6,3.70,2.51),(4.6,3.7,.3),22,.35),
        ('Plafon superior',(4.6,3.70,5.22),(4.6,3.7,3),25,.35),
        ('Plafon suite',(1.6,1.6,5.22),(1.6,1.6,3),20,.35),
        ('Plafon quarto branco',(4.8,.4,5.22),(4.8,.4,3),22,.35),
        ('Plafon quarto azul',(4.8,5.8,5.22),(4.8,5.8,3),22,.35),
        ('Pendente bar A',(.6,9.15,2.22),(.6,9.15,.7),25,.16),
        ('Pendente bar B',(1.9,9.15,2.22),(1.9,9.15,.7),25,.16),
        ('Plafon lavanderia',(4.8,8.8,2.80),(4.8,8.8,.7),25,.45),
        ('Lavabo',(4.4,2.6,2.2),(4.4,2.8,.5),15,.3),
        ('Banheiro suite',(.9,4.5,5.2),(.9,4.5,3),25,.35),
        ('Banheiro social',(2.55,4.5,5.2),(2.55,4.5,3),25,.35),
    ]:area(name,pos,target,w,size)
    for y in [.17,2.85]:area('LED TV',(3.16,y,1.45),(3.29,y,1.45),6,.6,(1,.72,.39))
    for y in [.6,1.35,2.1,2.85]:
        o=area('Spot TV',(3.03,y,2.50),(3.27,y,1.0),5,.04,(1,.73,.43),'SPOT');o.data.spot_size=math.radians(55);o.data.spot_blend=.65
    sun=area('Sol difuso',(4,-6,12),(2,6,0),1.4,1,(1,.95,.87),'SUN');sun.data.angle=math.radians(8)
    # Iluminação neutra para plantas, separada das fontes fotografadas.
    p=geo.col('Luz_Plantas');g.C['Iluminacao']=p
    for z in [8,12]:g.light('FIEL2 Luz planta',(3,4,z),1300,(1,.97,.93),'AREA',(3,4,0),8)
    return c,p

def fixtures(ground,upper):
    for c,z,positions in [(ground,2.515,[(1.6,1.7),(4.8,5.75),(4.6,3.7)]),(upper,5.235,[(1.6,1.6),(4.8,.4),(4.8,5.8),(4.6,3.7),(.9,4.5),(2.55,4.5)])]:
        for x,y in positions:
            geo.cyl('Plafon base',(x,y,z),.15,.025,'Branco laqueado',c)
            geo.cyl('Plafon difusor',(x,y,z-.016),.137,.015,'LED quente',c)
    for y in [.6,1.35,2.1,2.85]:
        geo.cyl('Spot aro',(3.03,y,2.516),.032,.007,'Branco laqueado',ground)
        geo.cyl('Spot difusor',(3.03,y,2.510),.022,.003,'LED quente',ground)

def trims(ground,upper):
    count=0
    for o in list(bpy.data.collections['ATUAL_Arquitetura'].objects):
        if o.type!='MESH' or 'Parede' not in o.name:continue
        pts=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
        z0=2.70 if lo[2]>2.6 else 0
        if abs(lo[2]-z0)>.01 or hi[2]-lo[2]<1:continue
        c=upper if z0 else ground;dx=hi[0]-lo[0];dy=hi[1]-lo[1]
        if dx<.22:
            for x in [lo[0]-.004,hi[0]+.004]:geo.box('Rodape branco',(x,(lo[1]+hi[1])/2,z0+.045),(.010,dy,.09),'Branco laqueado',c,.003);count+=1
        elif dy<.22:
            for y in [lo[1]-.004,hi[1]+.004]:geo.box('Rodape branco',((lo[0]+hi[0])/2,y,z0+.045),(dx,.010,.09),'Branco laqueado',c,.003);count+=1
    return count

def setup(job,collections,w,light_col,plan_light):
    source=bpy.data.scenes[job['source_scene']];scene=source.copy();scene.name=job['scene'];scene.use_fake_user=True;scene.world=w
    # A proteção de vidro observada substitui só na apresentação a guarda tubular genérica.
    for source_col,proxy in collections['stair_proxies'].items():
        if source_col in scene.collection.children:
            scene.collection.children.unlink(bpy.data.collections[source_col]);scene.collection.children.link(proxy)
    # O jardim genérico anterior atravessava o bar; manter os dados históricos fora da apresentação.
    if 'R07_Contexto' in scene.collection.children:
        scene.collection.children.unlink(bpy.data.collections['R07_Contexto']);scene.collection.children.link(collections['context'])
    cam=bpy.data.objects.new(job['scene']+'_Camera',source.camera.data.copy());scene.collection.objects.link(cam);scene.camera=cam
    cam.location=job['pos'];cam.rotation_euler=(Vector(job['target'])-cam.location).to_track_quat('-Z','Y').to_euler()
    if job.get('top'):cam.rotation_euler=(0,0,0)
    if 'ortho' in job:cam.data.type='ORTHO';cam.data.ortho_scale=job['ortho']
    else:cam.data.type='PERSP';cam.data.lens=job['lens'];cam.data.sensor_width=36
    cam.data.clip_start=.025;cam.data.clip_end=300;cam.data.dof.use_dof=False
    plan=job['mode'].startswith(('plan','iso'));upper=job['mode'] in {'plan1','iso1'} or job['pos'][2]>2.7 and job['mode']=='photo'
    chosen=[collections['upper'] if upper else collections['ground']]
    if not plan:chosen+=[collections['fixtures_upper'] if upper else collections['fixtures_ground'],collections['roof_details'],light_col]
    else:chosen.append(plan_light)
    if job['mode']=='exterior':chosen+=[collections['upper'],collections['roof_details'],collections['exterior']]
    if job['id']=='fachada-frontal':chosen.append(collections['neighbors'])
    if job['mode']=='exterior':
        scene.world=w.copy();nodes,links=scene.world.node_tree.nodes,scene.world.node_tree.links
        out=next(n for n in nodes if n.type=='OUTPUT_WORLD');original=out.inputs[0].links[0].from_socket
        bg=nodes.new('ShaderNodeBackground');bg.inputs['Color'].default_value=(.65,.72,.80,1);bg.inputs['Strength'].default_value=.8
        path=nodes.new('ShaderNodeLightPath');mix=nodes.new('ShaderNodeMixShader');links.new(path.outputs['Is Camera Ray'],mix.inputs[0]);links.new(original,mix.inputs[1]);links.new(bg.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],out.inputs[0])
    for c in dict.fromkeys(chosen):scene.collection.children.link(c)
    scene.render.engine='CYCLES';scene.cycles.samples=CFG['samples'];scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=CFG['adaptive_threshold'];scene.cycles.use_denoising=True;scene.cycles.use_light_tree=True
    scene.cycles.max_bounces=12;scene.cycles.diffuse_bounces=6;scene.cycles.glossy_bounces=8;scene.cycles.transmission_bounces=12;scene.cycles.transparent_max_bounces=16;scene.cycles.sample_clamp_indirect=10
    scene.render.resolution_x,scene.render.resolution_y=CFG['resolution'];scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='16';scene.render.filepath=str(ROOT/job['file'])
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=(1.15 if job['id'] in {'suite','suite-reversa'} else .55) if not plan else -.35
    scene['reconstruction_scope']='Casa atual por fotos, não proposta industrial';scene['quality_config_sha256']=data.sha(data.CONFIG)
    return scene

def build():
    assert Path(bpy.data.filepath).resolve()==ROOT/CFG['base_blend'];assert data.sha(bpy.data.filepath)==CFG['base_sha256']
    generators={str(p.relative_to(ROOT)):data.sha(p) for p in sorted((ROOT/'scripts').glob('current_photoreal*.py'))}
    for key in CFG['protected_collections']:bpy.data.collections[key].use_fake_user=True
    before=protected();g.C.update({c.name:c for c in bpy.data.collections});g.M.update({m.name:m for m in bpy.data.materials})
    work=bpy.data.scenes.new('FIEL2_BUILD')
    for col in list(bpy.data.collections):work.collection.children.link(col)
    bpy.context.window.scene=work
    materials.build();changed=materials.apply_original();repairs=details.opening_repairs()
    ground,upper,fg,fu,roof,context=[geo.col(n) for n in ['Mobiliario_Terreo','Mobiliario_Superior','Luminarias_Terreo','Luminarias_Superior','Detalhes_Cobertura','Contexto']]
    furniture.living(ground,before);furniture.dining(ground,before);furniture.bar_chairs(ground,before)
    details.kitchen(ground,before);details.rear(ground,before,roof);details.laundry(ground,before);details.bedrooms(upper,before);details.bathrooms(upper,before);details.sanitary_refinement(upper,before);details.glass_stair_guard(upper);details.stair_risers(ground,upper)
    # Papel do lavabo pertence ao térreo, os demais complementos ao superior.
    for o in list(upper.objects):
        if 'Lavabo papel' in o.name:upper.objects.unlink(o);ground.objects.link(o)
    fixtures(fg,fu);trim_count=trims(ground,upper);exterior_col,neighbors_col=exterior.build()
    old_plants=[o for o in bpy.data.objects if o.type=='EMPTY' and o.name.startswith('R07 Jardim contexto')]
    omitted={part for root in old_plants for part in [root,*root.children_recursive]}
    for o in bpy.data.collections['R07_Contexto'].objects:
        if o not in omitted:context.objects.link(o)
    for o in list(bpy.data.objects):
        if o.type=='LIGHT':bpy.data.objects.remove(o,do_unlink=True)
    for o in [*ground.objects,*upper.objects,*roof.objects]:materials.metric_uv(o)
    w=world();light_col,plan_light=lights();collections=dict(ground=ground,upper=upper,fixtures_ground=fg,fixtures_upper=fu,roof_details=roof,context=context,exterior=exterior_col,neighbors=neighbors_col)
    proxies={}
    for key in ['ATUAL_Arquitetura','ATUAL_Escada','R07_Escada']:
        proxy=geo.col('Apresentacao_'+key);proxies[key]=proxy
        for o in bpy.data.collections[key].objects:
            if not any(t in o.name for t in ['Corrimao hall','Montante guarda-corpo']):proxy.objects.link(o)
    collections['stair_proxies']=proxies
    jobs=data.jobs()
    for job in jobs:setup(job,collections,w,light_col,plan_light)
    for scene in list(bpy.data.scenes):
        if scene.name not in {j['scene'] for j in jobs}:bpy.data.scenes.remove(scene)
    for o in list(bpy.data.objects):
        if o.type=='CAMERA' and o.name not in {s.camera.name for s in bpy.data.scenes}:bpy.data.objects.remove(o,do_unlink=True)
    bpy.context.window.scene=bpy.data.scenes['FIEL2_sala-foto'];bpy.context.view_layer.update()
    assert protected()==before,'Arquitetura estrutural modificada'
    for o in bpy.data.objects:
        if o.type=='MESH' and any(s.material and s.material==materials.M['Porcelanato bege polido'] for s in o.material_slots):materials.metric_uv(o)
    assert all(data.sha(ROOT/p)==h for p,h in generators.items()),'Gerador alterado durante a construção'
    bpy.ops.file.pack_all();dest=ROOT/CFG['output_blend'];dest.parent.mkdir(parents=True,exist_ok=True);temp=dest.with_name(dest.stem+'.building.blend')
    bpy.ops.wm.save_as_mainfile(filepath=str(temp),compress=True)
    # A promoção é feita pelo validador somente depois da reabertura deste arquivo temporário.
    receipt={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'status':'built_pending_reopen','blend':CFG['output_blend'],'temporary_blend':str(temp.relative_to(ROOT)),'temporary_sha256':data.sha(temp),'base_sha256':CFG['base_sha256'],'config_sha256':data.sha(data.CONFIG),'protected_geometry':before,'opening_repairs':repairs,'jobs':jobs,'materials_updated':changed,'new_objects':sorted({n for n in geo.CREATED if bpy.data.objects.get(n)}),'white_skirting_pieces':trim_count,'references':[{'file':str(p.relative_to(ROOT)),'sha256':data.sha(p)} for p in sorted((ROOT/CFG['reference_directory']).glob('*.webp'))],'generators':generators,'notes':CFG['notes']}
    (REPORT/'modelo.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print('CURRENT2_BUILD_OK',len(jobs),'views',len(before),'protected',len(repairs),'opening repairs',flush=True)

if __name__=='__main__':build()
