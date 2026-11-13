"""Variante industrial nativa sobre a revisão 10; não altera o arquivo base.

Executar pelo run_blender.py, abrindo o .blend base. --render-only reabre
a variante salva; --preview gera prévias, sem modificar o editável.
"""
import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blender_primitives as g
import audit_envelope


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def geometry():
    """Hash de cada malha/curva herdada, transformação local, pais e modificadores.

    Materiais e luzes são as alterações autorizadas. Alterações nas paredes,
    aberturas, escada e móveis existentes são detectadas por este contrato.
    """
    result = {}
    for obj in bpy.data.objects:
        if obj.type not in {'MESH', 'CURVE'}:
            continue
        shape = ([list(v.co) for v in obj.data.vertices] if obj.type == 'MESH'
                 else [[list(p.co) for p in s.bezier_points] for s in obj.data.splines])
        state = [obj.type, shape, list(obj.location), list(obj.rotation_euler), list(obj.scale),
                 obj.parent.name if obj.parent else None,
                 [(m.name, m.type) for m in obj.modifiers]]
        result[obj.name] = hashlib.sha256(json.dumps(state).encode()).hexdigest()
    return result


def materials():
    # A base salva não conserva materiais sem usuários, como este vaso opcional.
    if 'Ceramica preta' not in g.M:
        g.basic('Ceramica preta', (.014, .018, .015), .32)
    g.basic('IND Aço preto', (.012, .015, .016), .43, .72)
    g.basic('IND Grafite', (.018, .023, .025), .48)
    g.basic('IND Luz âmbar', (1, .53, .20), .35, emission=5)
    g.basic('IND Porcelana', (.62, .59, .51), .28)
    g.textured('IND Cimento', [(.095, .090, .080), (.18, .175, .16), (.28, .27, .25)], 'stone', .85, .001)
    g.textured('IND Piso cimento', [(.29, .28, .25), (.40, .39, .35)], 'stone', .38, .0004)
    g.textured('IND Nogueira', [(.027, .009, .004), (.10, .037, .014), (.23, .105, .038)], 'wood', .42, .0008)
    g.textured('IND Couro caramelo', [(.065, .018, .007), (.17, .053, .018), (.27, .105, .036)], 'leather', .44, .0003)
    g.textured('IND Tapete', [(.075, .068, .055), (.19, .17, .13)], 'stone', .95, .001)
    g.textured('IND Azul petróleo', [(.018, .037, .047), (.048, .085, .10)], 'stone', .88, .0005)
    g.textured('IND Linho', [(.23, .24, .22), (.44, .43, .36)], 'stone', .92, .0005)
    g.textured('IND Pedra oxidada', [(.025, .031, .030), (.11, .067, .030), (.23, .12, .045)], 'stone', .72, .003)


def assign(obj, material):
    obj.data.materials.clear()
    obj.data.materials.append(g.M[material])


def restyle():
    targets = {'AMB_sala', 'AMB_jantar', 'AMB_bar', 'AMB_cozinha', 'AMB_quarto_azul'}
    mapping = {'Sofa cinza': 'IND Couro caramelo', 'Estofado cadeira cinza': 'IND Couro caramelo',
               'Madeira bar': 'IND Nogueira', 'Rack amarelo': 'IND Nogueira',
               'Cinza parede TV': 'IND Cimento', 'Parede azul': 'IND Azul petróleo',
               'Armario cozinha cinza': 'IND Grafite', 'Lencol': 'IND Linho',
               'Metal preto': 'IND Aço preto', 'Azulejo branco': 'IND Grafite',
               'Ceramica creme': 'Ceramica preta'}
    for obj in list(bpy.data.objects):
        if obj.type not in {'MESH', 'CURVE'} or not hasattr(obj.data, 'materials'):
            continue
        target = any(c.name in targets for c in obj.users_collection)
        if target:
            for slot in obj.material_slots:
                old = slot.material.name if slot.material else ''
                if old in mapping:
                    slot.material = g.M[mapping[old]]
            n = obj.name
            if n.startswith(('Painel TV branco', 'Fundo cinza painel')):
                assign(obj, 'IND Cimento')
            elif n.startswith(('Rack frentes', 'Rack pés', 'Pé cadeira', 'Pé sofá',
                               'Armário bar perfil', 'Pilar beliche', 'Degrau escada beliche',
                               'Pé cama', 'Torneira', 'Puxador')):
                assign(obj, 'IND Aço preto')
            elif n.startswith(('Tampo vidro escuro', 'Armário bar prateleira', 'Escrivaninha quarto',
                               'Estrado cama', 'Base central mesa')):
                assign(obj, 'IND Nogueira')
            elif n.startswith('Armário bar fundo'):
                assign(obj, 'IND Grafite')
            elif n.startswith('Pedra bar original'):
                assign(obj, 'IND Pedra oxidada')
            elif n.startswith('Prateleira nicho'):
                assign(obj, 'IND Nogueira')
        if obj.name.startswith(('T0 limite oeste', 'T0 limite leste', 'Fundo bar',
                                'Separação churrasqueira lavanderia')) and obj.get('parede'):
            assign(obj, 'IND Cimento')
        if obj.name in {'Laje sala — dimensões estimadas', 'Laje faixa lateral', 'Piso churrasqueira'}:
            assign(obj, 'IND Piso cimento')
        if obj.name.startswith(('S1 limite posterior', 'S1 lateral leste')) and obj.get('parede'):
            assign(obj, 'IND Cimento')
        if obj.name.startswith(('Janela cozinha ', 'Janela quarto fundos ', 'Janela sala ')) and any(part in obj.name for part in ['caixilho','travessa','grade','acabamento']):
            assign(obj, 'IND Aço preto')


def collection(name):
    col = bpy.data.collections.new(name)
    # Uma coleção compartilhada mantém os novos elementos coerentes em todas as vistas.
    for scene in bpy.data.scenes:
        if scene.name != 'ESTUDOS_Superior':
            scene.collection.children.link(col)
    g.C[name] = col
    return name


def box(name, loc, size, mat, col, bevel=.008):
    return g.box('IND '+name, loc, size, mat, col, bevel)


def area(name, loc, target, power=35, size=.5):
    light = g.light('IND '+name, loc, power, color=(1, .73, .44), size=size, target=target)
    light.visible_glossy = False
    light.data.specular_factor = 0
    return light


def pendant(name, x, y, z, col, ceiling=2.68):
    g.rod('IND cabo '+name, (x,y,z+.23), (x,y,ceiling), .004, 'IND Aço preto', col)
    g.lathe('IND cúpula '+name, [(.20,0),(.18,.055),(.12,.15),(.04,.22)],
            (x,y,z), 'IND Aço preto', col)
    g.sphere('IND lâmpada '+name, (x,y,z+.025), (.055,.055,.045), 'IND Luz âmbar', col)
    area(name, (x,y,z-.025), (x,y,0), 32, .32)


def books(name, loc, col, count=5, axis='y'):
    for i in range(count):
        x,y,z=loc
        if axis=='y':y+=i*.045
        else:x+=i*.045
        box(name+str(i),(x,y,z),(.16,.035,.20) if axis=='y' else (.035,.16,.20),
            ['IND Linho','IND Grafite','IND Nogueira'][i%3], col, .002)


def living(cfg):
    c=collection('IND_Decor_Sala')
    box('tapete sala',(1.77,1.75,.014),(1.24,2.26,.022),'IND Tapete',c,.018)
    box('mesa centro tampo',(1.68,1.85,.36),(.48,1.02,.05),'IND Nogueira',c,.015)
    for x in [1.48,1.88]:
        for y in [1.42,2.28]:box('mesa centro aço',(x,y,.18),(.022,.022,.34),'IND Aço preto',c)
    for i in range(3):box('livro mesa centro',(1.68,1.9,.40+i*.022),(.25,.32,.02),'IND Linho',c,.002)
    for y in [.8,2.5]:
        pillow=box('almofada linho',(.69,y,.70),(.18,.40,.36),'IND Linho',c,.045)
        pillow.rotation_euler.y=-.12
    for z in [1.6,2.16]:
        box('prateleira sala',(.22,3.0,z),(.29,1.05,.035),'IND Nogueira',c)
        for y in [2.55,3.45]:box('suporte prateleira sala',(.15,y,z-.12),(.15,.025,.22),'IND Aço preto',c)
    books('livros sala',(.25,2.65,1.72),c)
    g.plant('IND planta prateleira',(.23,3.30,2.18),.36,c,hanging=True)
    # Marcenaria de rack com perfis pretos sobre a frente existente, sem mudar o volume.
    for y in [1.0+i*.075 for i in range(23)]:
        box('rack tela vertical',(2.696,y,.31),(.012,.008,.29),'IND Aço preto',c,.001)
    for z in [.18,.32,.45]:box('rack tela horizontal',(2.694,1.8,z),(.014,1.75,.008),'IND Aço preto',c,.001)
    # Pontos de ancoragem derivados do próprio móvel salvo.
    table=bpy.data.objects['MESA_JANTAR_original seis lugares'].matrix_world.translation
    for i in range(3):
        box('tábua mesa jantar',(table.x+(i-1)*.335,table.y,.798),(.33,1.70,.010),'IND Nogueira',c,.003)
    for x in [table.x-.41,table.x+.41]:
        for y in [table.y-.73,table.y+.73]:box('pé madeira mesa jantar',(x,y,.375),(.075,.075,.75),'IND Nogueira',c)
    for y in [table.y-.53,table.y+.53]:pendant('jantar',table.x,y,2.20,c)
    for obj in bpy.data.objects:
        if obj.name.startswith(('Anel pendente original','Base central mesa','Sapata mesa')):obj.hide_render=True
    for y in [1.3,3.1,4.8]:
        box('trilho sala',(1.60,y,2.64),(.95,.035,.035),'IND Aço preto',c)
        for x in [1.23,1.97]:
            g.cylinder('IND spot sala',(x,y,2.57),.042,.12,'IND Aço preto',c)
            area('spot sala',(x,y,2.49),(x-.2,y,.4),16,.22)
    for y in [.90,2.71]:area('arandela TV',(2.94,y,1.6),(2.7,y,1.6),7,.16)


def kitchen(cfg):
    c=collection('IND_Decor_Cozinha')
    for y in [5.70,6.48,7.13]:
        box('LED bancada cozinha',(5.205,y,1.73),(.018,.62,.014),'IND Luz âmbar',c,.002)
        area('bancada cozinha',(5.10,y,1.71),(5.20,y,.90),9,.35)
    box('prateleira entrada cozinha',(4.35,4.39,1.80),(1.18,.21,.035),'IND Nogueira',c)
    for x in [3.87,4.83]:box('suporte cozinha',(x,4.40,1.94),(.025,.19,.28),'IND Aço preto',c)
    books('livros cozinha',(3.95,4.40,1.92),c,4,'x')
    g.plant('IND ervas cozinha',(4.64,4.42,1.83),.30,c)
    for y in [5.70,7.10]:
        box('trilho cozinha',(4.36,y,2.61),(.75,.03,.035),'IND Aço preto',c)
        area('trilho cozinha',(4.36,y,2.54),(4.55,y,.8),22,.32)
    box('tábua cozinha',(5.21,5.75,.95),(.30,.37,.03),'IND Nogueira',c)
    for y in [5.48,5.59]:
        g.lathe('IND pote cozinha',[(.065,0),(.065,.16),(.06,.17)],(5.20,y,.95),'IND Porcelana',c)


def bar(cfg):
    from industrial_bar_policy import remove_bar_fridges
    remove_bar_fridges()
    c=collection('IND_Decor_Lazer')
    back=cfg['layout']['bar']['back_y'];cy=cfg['layout']['bar']['counter_y']
    for obj in bpy.data.objects:
        if obj.name.startswith(('Armário bar prateleira','Armário bar fundo')):
            for slot in obj.material_slots:
                if slot.material and slot.material.name=='Armario branco':slot.material=g.M['IND Nogueira']
    for x in [1.25,1.88,2.51]:
        box('LED prateleiras bar',(x,back-.43,1.86),(.55,.014,.014),'IND Luz âmbar',c,.001)
        area('bar luz pedra',(x,back-.48,1.82),(x,back-.10,1.30),11,.35)
        for i in range(3):
            xx=x-.17+i*.16
            g.lathe('IND taça bar',[(.05,0),(.012,.012),(.01,.09),(.055,.14),(.04,.22)],
                    (xx,back-.27,1.88),'Vidro transparente',c)
            g.lathe('IND cerâmica bar',[(.07,0),(.07,.12),(.08,.14)],
                    (xx,back-.28,2.50),'IND Porcelana',c)
    for x in [.60,1.90]:area('pendente bar',(x,cy+.15,2.18),(x,cy,.7),32,.32)
    for y in [8.65,9.65]:
        box('arandela externa base',(.092,y,1.85),(.03,.13,.24),'IND Aço preto',c)
        g.cylinder('IND arandela externa corpo',(.17,y,1.85),.055,.17,'IND Luz âmbar',c)
        for yy in [y-.07,y+.07]:box('arandela gaiola',(.22,yy,1.85),(.014,.014,.24),'IND Aço preto',c)
        area('arandela lazer',(.27,y,1.85),(.08,y,1.65),10,.20)
    for x in [.50,1.23,1.96,2.69]:
        # Os pontos existentes da cobertura são mantidos; novas travessas são decorativas.
        box('travessa cobertura',(x,9.08,2.87),(.045,2.82,.075),'IND Nogueira',c)
    g.plant('IND vaso bar',(.25,cy+.20,1.03),.42,c)


def bedroom(cfg):
    c=collection('IND_Decor_Quarto_Fundos');z=cfg['estimated_dimensions_m']['floor_height'];back=cfg['estimated_dimensions_m']['upper_back_y'];y=back-1.25
    box('tapete quarto',(3.94,y-.15,z+.018),(.80,1.75,.025),'IND Tapete',c,.018)
    # Duas prateleiras na parede da bancada, dentro do cômodo, sem tapar a janela.
    for height in [1.78,2.28]:
        box('prateleira escritório',(3.10,y,z+height),(.35,1.65,.035),'IND Nogueira',c)
        for yy in [y-.70,y+.70]:box('montante estante',(2.98,yy,z+1.72),(.025,.025,1.15),'IND Aço preto',c)
        box('LED escritório',(3.24,y,z+height-.025),(.014,1.5,.012),'IND Luz âmbar',c,.001)
        area('LED prateleira',(3.25,y,z+height-.05),(2.93,y,z+height-.5),12,.45)
    books('livros escritório',(3.13,y-.62,z+1.90),c,6)
    g.plant('IND planta escritório',(3.11,y+.53,z+2.30),.33,c,hanging=True)
    # Monitor vertical à parede, orientado para a cadeira; painel existente preservado.
    for yy in [y-.32,y+.32]:
        box('monitor moldura',(3.11,yy,z+1.12),(.055,.54,.36),'IND Aço preto',c)
        box('monitor tela',(3.142,yy,z+1.12),(.005,.49,.31),'IND Azul petróleo',c,.001)
        for i in range(7):
            box('tela linhas',(3.146,yy-.12+(i%2)*.04,z+1.23-i*.034),(.003,.25-i*.012,.007),
                'IND Linho' if i%3 else 'IND Nogueira',c,.001)
    box('teclado',(3.25,y,z+.78),(.15,.42,.025),'IND Aço preto',c,.003)
    g.cylinder('IND base cadeira',(3.77,y-.14,z+.24),.035,.43,'IND Aço preto',c)
    for a in range(5):
        ang=a*math.tau/5
        g.rod('IND pé estrela',(3.77,y-.14,z+.08),(3.77+math.cos(ang)*.25,y-.14+math.sin(ang)*.25,z+.06),.018,'IND Aço preto',c)
    box('assento escritório',(3.77,y-.14,z+.48),(.45,.46,.08),'IND Grafite',c,.03)
    box('encosto escritório',(3.96,y-.14,z+.83),(.065,.44,.58),'IND Grafite',c,.035)
    for yy in [y-.35,y+.07]:box('braço cadeira',(3.78,yy,z+.67),(.33,.035,.045),'IND Aço preto',c)
    for yy in [y-.62,y+.62]:
        g.rod('IND ripa quarto',(2.967,yy,z+.10),(2.967,yy,z+2.58),.012,'IND Nogueira',c)
    box('trilho escritório',(3.9,y,z+2.61),(.035,1.40,.035),'IND Aço preto',c)
    for yy in [y-.5,y+.5]:area('spot escritório',(3.9,yy,z+2.54),(3.15,yy,z+.80),19,.25)


def build(root, cfg, folder):
    base=root/cfg['base_blend'];assert Path(bpy.data.filepath).resolve()==base
    original_sha=sha(base)
    from industrial_bar_policy import remove_bar_fridges
    removed_bar_fridge=remove_bar_fridges()
    before=geometry()
    g.C.update({c.name:c for c in bpy.data.collections});g.M.update({m.name:m for m in bpy.data.materials})
    g.RNG.seed(1102026);g.LEAF_MESHES.clear()
    materials();restyle()
    house=json.loads((root/'config/planta-casa.json').read_text())
    bpy.context.view_layer.update()
    living(house);kitchen(house);bar(house);bedroom(house)
    for obj in bpy.data.objects:
        if obj.type=='LIGHT' and not obj.name.startswith('IND '):
            if obj.name.startswith(('Luz ambiente','Luz cozinha','Luz superior')):obj.data.energy*=.38
        if obj.name=='TV quarto fundos':obj.hide_render=True
    for world in bpy.data.worlds:
        if world.use_nodes:
            node=world.node_tree.nodes.get('Background')
            if node:node.inputs['Strength'].default_value=.22
    # As referências de estilo acompanham o repositório. Os novos materiais são
    # procedurais e não dependem de arquivos externos nem dessas imagens.
    jobs=[]
    for job in cfg['jobs']:
        scene=bpy.data.scenes[job['source_scene']].copy();scene.name=job['scene'];scene.use_fake_user=True
        camera=scene.camera.copy();camera.data=scene.camera.data.copy();g.C['Cameras'].objects.link(camera)
        camera.name=job['scene']+'_Camera';scene.camera=camera
        if 'position' in job:
            camera.location=job['position'];camera.rotation_euler=(Vector(job['target'])-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=job['lens']
        scene.render.resolution_x,scene.render.resolution_y=cfg['resolution'];scene.render.resolution_percentage=100
        scene.cycles.samples=cfg['samples'];scene.cycles.use_denoising=True;scene.cycles.seed=42
        scene['style_version']=cfg['version'];scene['base_sha256']=original_sha
        jobs.append(job['scene'])
    after=geometry();diff=[name for name,state in before.items() if after.get(name)!=state]
    assert not diff,diff
    envelope=audit_envelope.audit(house);assert envelope['all_passed']
    output=root/cfg['output_blend'];assert not output.exists(),f'Já existe: {output}; use --render-only ou outra versão'
    output.parent.mkdir(parents=True,exist_ok=True)
    bpy.context.window.scene=bpy.data.scenes['IND_Sala_Integrada']
    bpy.ops.wm.save_as_mainfile(filepath=str(output))
    assert sha(base)==original_sha
    report={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'version':cfg['version'],
            'base':cfg['base_blend'],'base_sha256':original_sha,'blend':cfg['output_blend'],
            'blend_sha256':sha(output),'geometry_objects_preserved':len(before),'geometry_differences':diff,
            'original_geometry_sha256':before,'new_objects':sorted(set(after)-set(before)),
            'authorized_bar_fridge_removal':removed_bar_fridge,
            'envelope':envelope,'scenes':jobs,'references':{str(p.relative_to(root)):sha(p) for p in sorted((root/cfg['references']).glob('*.png'))}}
    (folder/'modelo.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('INDUSTRIAL_BUILT',len(before),'geometrias preservadas',flush=True)


def render(root,cfg,folder,preview):
    file=Path(bpy.data.filepath);before=sha(file)
    model=json.loads((folder/'modelo.json').read_text());assert before==model['blend_sha256']
    current=geometry();assert all(current.get(n)==v for n,v in model['original_geometry_sha256'].items())
    envelope=audit_envelope.audit(json.loads((root/'config/planta-casa.json').read_text()));assert envelope['all_passed']
    collisions=[]
    for job in cfg['jobs']:
        scene=bpy.data.scenes[job['scene']]
        with bpy.context.temp_override(scene=scene,view_layer=scene.view_layers[0]):
            scene.view_layers[0].update();deps=bpy.context.evaluated_depsgraph_get()
            eye=scene.camera.evaluated_get(deps).matrix_world.translation
            for obj in scene.objects:
                if obj.type!='MESH' or obj.hide_render or not obj.visible_get(view_layer=scene.view_layers[0]):continue
                evaluated=obj.evaluated_get(deps);point=evaluated.matrix_world.inverted()@eye
                bounds=[Vector(v) for v in evaluated.bound_box]
                if all(min(v[i] for v in bounds)+.002<point[i]<max(v[i] for v in bounds)-.002 for i in range(3)):
                    collisions.append([scene.name,obj.name])
    assert not collisions,collisions
    device=g.configure_device('cpu');outputs={}
    target=root/cfg['render_directory']/('previas' if preview else '')
    target.mkdir(parents=True,exist_ok=True)
    for job in cfg['jobs']:
        scene=bpy.data.scenes[job['scene']];scene.cycles.samples=16 if preview else cfg['samples']
        scene.render.resolution_percentage=45 if preview else 100
        scene.render.filepath=str(target/job['file'])
        bpy.ops.render.render(write_still=True,scene=scene.name)
        p=Path(scene.render.filepath);outputs[str(p.relative_to(root))]={'sha256':sha(p),'bytes':p.stat().st_size,'scene':scene.name}
        print('INDUSTRIAL_RENDER',scene.name,flush=True)
    assert sha(file)==before and sha(root/cfg['base_blend'])==model['base_sha256']
    report={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'blend':str(file.relative_to(root)),
            'blend_sha256':before,'preview':preview,'device':device,'envelope':envelope,
            'base_preserved':True,'original_geometry_preserved':True,'camera_collisions':collisions,'outputs':outputs}
    (folder/('previas.json' if preview else 'renders.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=Path('.'))
    p.add_argument('--render-only',action='store_true');p.add_argument('--preview',action='store_true');p.add_argument('--build-only',action='store_true')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    root=args.project_root.resolve();cfg=json.loads((root/'config/estilo-industrial-v01.json').read_text())
    folder=root/cfg['report_directory'];folder.mkdir(parents=True,exist_ok=True)
    if not args.render_only:build(root,cfg,folder)
    if not args.build_only:render(root,cfg,folder,args.preview)


if __name__=='__main__':main()
